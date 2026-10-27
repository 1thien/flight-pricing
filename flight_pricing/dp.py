"""Inputs for the dynamic-programming solver, and the policy it produces.

State: the relative fare x = log(fare / route's usual fare), where the route's
usual fare is the median over training trips. Days run t = 60 (far out) down
to 1 (last chance). Python estimates how x moves from day t to day t-1; MATLAB
(matlab/) solves the Bellman equation backward; Python applies the result.

Two price models:
  * empirical Markov chain: transition counts between grid bins, by day
  * jump process: each day the fare stays put with probability 1 - lam_t, or
    jumps by J ~ Normal(mu_t + kappa_t * x, sigma_t^2), fit by maximum likelihood
"""

import subprocess
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.io import loadmat, savemat

MATLAB = Path(r"C:\Program Files\MATLAB\R2026b\bin\matlab.exe")
MATLAB_DIR = Path(__file__).resolve().parents[1] / "matlab"
X_MIN, X_MAX = -1.0, 1.5
DAY_BUCKETS = [(2, 7), (8, 14), (15, 21), (22, 30), (31, 45), (46, 60)]


def route_reference(F, trips, mask):
    """Median fare per route over the masked (training) trips."""
    route = trips.origin.astype(str) + "-" + trips.dest.astype(str)
    masked = np.where(mask[:, None], F[:, 1:], np.nan)
    has_price = ~np.isnan(masked).all(axis=1)
    trip_median = np.full(len(F), np.nan)
    trip_median[has_price] = np.nanmedian(masked[has_price], axis=1)
    med = pd.Series(trip_median).groupby(route.to_numpy()).median()
    return route.map(med).to_numpy()


def relative_log_fare(F, ref):
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.log(F / ref[:, None])


def grid(K):
    edges = np.linspace(X_MIN, X_MAX, K + 1)
    return edges, (edges[:-1] + edges[1:]) / 2


def transition_matrices(X, mask, K, pool=2, alpha=0.1):
    """M[:, :, t]: probability of moving from bin i at day t to bin j at day t-1.

    Uses consecutive observed days of the masked trips, pools days t-pool..t+pool
    for stability, and adds alpha pseudo-counts on the 'stay' cell so rare rows
    default to 'no change'.
    """
    edges, _ = grid(K)
    b = np.clip(np.digitize(X, edges) - 1, 0, K - 1)
    counts = np.zeros((K, K, 61))
    for t in range(2, 61):
        ok = mask & ~np.isnan(X[:, t]) & ~np.isnan(X[:, t - 1])
        np.add.at(counts[:, :, t], (b[ok, t], b[ok, t - 1]), 1)
    M = np.zeros_like(counts)
    for t in range(2, 61):
        c = counts[:, :, max(2, t - pool):min(60, t + pool) + 1].sum(axis=2) + alpha * np.eye(K)
        M[:, :, t] = c / c.sum(axis=1, keepdims=True)
    return M


def fit_jump_model(X, mask):
    """Maximum-likelihood jump model per day bucket.

    P(jump) = lam is the share of days with a change. Given a jump, the size is
    Normal(mu + kappa * x, sigma^2); for a normal model, MLE of (mu, kappa) is
    least squares, and sigma^2 is the mean squared residual.
    Returns arrays indexed by day t (0..60).
    """
    params = {k: np.full(61, np.nan) for k in ("lam", "mu", "kappa", "sigma")}
    for lo, hi in DAY_BUCKETS:
        x_now, dx = [], []
        for t in range(max(lo, 2), hi + 1):
            ok = mask & ~np.isnan(X[:, t]) & ~np.isnan(X[:, t - 1])
            x_now.append(X[ok, t])
            dx.append(X[ok, t - 1] - X[ok, t])
        x_now, dx = np.concatenate(x_now), np.concatenate(dx)
        jump = np.abs(dx) > 1e-9
        if jump.sum() < 100:
            continue   # too little data this far out; filled from the nearest bucket below
        A = np.column_stack([np.ones(jump.sum()), x_now[jump]])
        (mu, kappa), *_ = np.linalg.lstsq(A, dx[jump], rcond=None)
        sigma = np.sqrt(np.mean((dx[jump] - A @ [mu, kappa]) ** 2))
        for t in range(lo, hi + 1):
            params["lam"][t], params["mu"][t] = jump.mean(), mu
            params["kappa"][t], params["sigma"][t] = kappa, sigma
    for k, v in params.items():   # days without data take the nearest fitted day's values
        params[k] = pd.Series(v).ffill().bfill().to_numpy()
    return params


def run_matlab(script, workdir):
    """Run a MATLAB script from matlab/ with `workdir` as the current folder."""
    cmd = f"addpath('{MATLAB_DIR.as_posix()}'); cd('{Path(workdir).as_posix()}'); {script}"
    out = subprocess.run([str(MATLAB), "-batch", cmd], capture_output=True, text=True)
    if out.returncode != 0:
        raise RuntimeError(out.stdout + out.stderr)
    return out.stdout


def save_inputs(path, **arrays):
    savemat(path, arrays, do_compression=True)


def load_outputs(path):
    return {k: v for k, v in loadmat(path).items() if not k.startswith("__")}


def walk_forward_dp(trips, F, test_months, workdir, K=60, model="jump", objective="price"):
    """Buy matrix B (n_trips x 61) from the DP policy, walk-forward by month.

    Each decision day uses the policy solved from trips that departed before
    the month of that day's search date, the same convention as the other
    strategies. Days outside the test months default to buy.
    """
    flight = pd.to_datetime(trips.flightDate)
    edges, centers = grid(K)
    Xs, Ms, params = [], [], {k: [] for k in ("lam", "mu", "kappa", "sigma")}
    for m in test_months:
        train = (flight < m.start_time).to_numpy()
        X = relative_log_fare(F, route_reference(F, trips, train))
        Xs.append(X)
        Ms.append(transition_matrices(X, train, K))
        for k, v in fit_jump_model(X, train).items():
            params[k].append(v)
    save_inputs(Path(workdir) / "dp_input.mat", edges=edges, centers=centers,
                M_markov=np.stack(Ms, axis=3), **{k: np.column_stack(v) for k, v in params.items()})
    run_matlab("solve_folds", workdir)
    C = load_outputs(Path(workdir) / "dp_output.mat")[f"C_{model}_{objective}"]

    days = np.arange(F.shape[1])
    search_month = (flight.to_numpy()[:, None] - days[None, :] * np.timedelta64(1, "D")).astype("datetime64[M]")
    B = np.ones(F.shape, dtype=bool)
    for f, m in enumerate(test_months):
        in_month = search_month == np.datetime64(str(m), "M")
        Bf = dp_buy_matrix(Xs[f], C[:, :, f], centers, objective)
        B[in_month] = Bf[in_month]
    B[:, 1] = True
    return B


def dp_buy_matrix(X, C, centers, objective="price"):
    """B[i, t] = True when buying now is no worse than the continuation value:
    cost(x) <= C_t(x), with C_t linearly interpolated between grid points.
    cost is exp(x) for objective 'price' and x for 'log' (see backward_induction.m)."""
    cost = np.exp if objective == "price" else (lambda v: v)
    B = np.zeros(X.shape, dtype=bool)
    for t in range(2, 61):
        x = X[:, t]
        ok = ~np.isnan(x)
        xc = np.clip(x[ok], centers[0], centers[-1])
        cont = np.interp(xc, centers, C[:, t])
        B[np.flatnonzero(ok), t] = cost(xc) <= cont
    B[:, 1] = True
    return B
