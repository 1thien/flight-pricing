"""Bootstrap confidence intervals for strategy results."""

import numpy as np
import pandas as pd


def savings_stats(start_fare, pct):
    """Headline metrics from per-trip starting fares and % saved."""
    saved = pct * start_fare
    return pd.Series({
        "avg_saved_pct": pct.mean(),
        "total_saved_pct": saved.sum() / start_fare.sum(),
        "avg_saved_usd": saved.mean(),
        "share_lost_money": (pct < 0).mean(),
    })


def bootstrap(start_fare, pct, clusters=None, n_boot=2000, seed=0):
    """Resample and recompute savings_stats n_boot times.

    With `clusters` (e.g. route labels), whole clusters are resampled with
    replacement, so trips that share a route stay together. Without it, single
    trips are resampled (the ordinary bootstrap, which assumes independence).
    Returns a DataFrame with one row per bootstrap sample.
    """
    rng = np.random.default_rng(seed)
    n = len(pct)
    if clusters is None:
        groups = None
    else:
        codes, _ = pd.factorize(clusters)
        order = np.argsort(codes, kind="stable")
        bounds = np.searchsorted(codes[order], np.arange(codes.max() + 2))
        groups = [order[bounds[k]:bounds[k + 1]] for k in range(codes.max() + 1)]
    draws = []
    for _ in range(n_boot):
        if groups is None:
            idx = rng.integers(0, n, size=n)
        else:
            picked = rng.integers(0, len(groups), size=len(groups))
            idx = np.concatenate([groups[k] for k in picked])
        draws.append(savings_stats(start_fare[idx], pct[idx]))
    return pd.DataFrame(draws)


def percentile_ci(draws, level=0.95):
    """Percentile confidence interval for each column of bootstrap draws."""
    a = (1 - level) / 2
    return pd.DataFrame({"low": draws.quantile(a), "high": draws.quantile(1 - a)})
