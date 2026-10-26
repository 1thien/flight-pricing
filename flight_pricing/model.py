"""Walk-forward training of the 'will the fare drop?' models and the buy/wait policy.

For each test month m (by decision date):
  1. Training data: trips that departed before m (their outcomes are known).
  2. Tune the wait cutoff theta on the most recent departed trips (the last
     VAL_DAYS before m), using a model fit only on trips that departed earlier.
  3. Refit on all training trips and apply the model and theta to decisions in m.
Policy: each day, wait while P(drop ahead) > theta, otherwise buy.
"""

import lightgbm as lgb
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from .backtest import START_DAYS, buy_day, eligible, price_paid
from .features import CATEGORICAL, FEATURES, add_route_level

VAL_DAYS = 28
THETAS = np.round(np.arange(0.30, 0.96, 0.05), 2)
LGB_PARAMS = dict(objective="binary", learning_rate=0.05, num_leaves=31, min_data_in_leaf=500,
                  feature_fraction=0.8, bagging_fraction=0.8, bagging_freq=1, verbose=-1, seed=0,
                  deterministic=True, force_row_wise=True)
LGB_ROUNDS = 300
LOGIT_FEATURES = [f for f in FEATURES if f not in CATEGORICAL]


def fit_lgb(X, y):
    return lgb.train(LGB_PARAMS, lgb.Dataset(X[FEATURES], y), LGB_ROUNDS)


def fit_logit(X, y):
    model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=500))
    return model.fit(X[LOGIT_FEATURES].fillna(0.0), y)


def predict(model, X):
    if isinstance(model, lgb.Booster):
        return model.predict(X[FEATURES])
    return model.predict_proba(X[LOGIT_FEATURES].fillna(0.0))[:, 1]


def prob_matrix(df, p, trip_index, n_trips):
    """Put row-level probabilities into the (trip, days_ahead) layout of F."""
    P = np.full((n_trips, 61), np.nan)
    rows = trip_index.reindex(pd.MultiIndex.from_frame(df[["origin", "dest", "flightDate"]]
                                                       .astype({"origin": str, "dest": str})))
    ok = rows.notna().to_numpy()
    P[rows.to_numpy()[ok].astype(int), df.days_ahead.to_numpy()[ok]] = p[ok]
    return P


def policy_pct_saved(F, P, idx, start, theta):
    """Per-trip % saved by 'wait while P > theta' (no prediction counts as buy)."""
    B = ~(P[idx] > theta)
    paid = price_paid(F[idx], buy_day(F[idx], B, start))
    return (F[idx, start] - paid) / F[idx, start]


def tune_theta(F, P, trips, trip_mask, starts=START_DAYS):
    """Pick the cutoff that maximizes average % saved, pooled over start days.
    Returns (theta, score)."""
    best, best_score = 1.0, 0.0   # theta = 1 means never wait (buy now), saving 0
    for theta in THETAS:
        vals = []
        for s in starts:
            idx = np.flatnonzero(trip_mask & eligible(trips, F, s))
            if len(idx):
                vals.append(policy_pct_saved(F, P, idx, s, theta))
        score = np.nanmean(np.concatenate(vals)) if vals else -np.inf
        if score > best_score:
            best, best_score = theta, score
    return best, best_score


def make_trip_index(trips):
    return pd.Series(np.arange(len(trips)), index=pd.MultiIndex.from_frame(
        trips[["origin", "dest", "flightDate"]].astype({"origin": str, "dest": str,
                                                         "flightDate": "datetime64[ns]"})))


def walk_forward(dfs, trips, F, test_months, fit=fit_lgb):
    """Walk-forward over test months.

    dfs maps a label horizon (days) to its feature table. Within each fold, the
    horizon and the cutoff theta are both chosen on the validation trips (the
    most recent VAL_DAYS of departed trips), never on the test month.

    Returns (P_test, folds): out-of-sample probabilities for every decision in
    the test months, and per-month choices and models.
    """
    trip_index = make_trip_index(trips)
    flight = pd.to_datetime(trips.flightDate)
    P_test = np.full_like(F, np.nan)
    folds = []
    for m in test_months:
        start, end = m.start_time, m.end_time
        val_start = start - pd.Timedelta(days=VAL_DAYS)
        val_trips = ((flight >= val_start) & (flight < start)).to_numpy()

        # 1. Choose horizon and theta on validation trips, with models fit on older trips.
        best = None
        for h, df in dfs.items():
            has_label = df.drop_ahead.notna().to_numpy()
            fit_rows = (df.flightDate < val_start).to_numpy() & has_label
            val_rows = ((df.flightDate >= val_start) & (df.flightDate < start)).to_numpy()
            df["log_vs_route"] = add_route_level(df, fit_rows)
            early = fit(df[fit_rows], df.loc[fit_rows, "drop_ahead"].astype(int))
            P_val = prob_matrix(df[val_rows], predict(early, df[val_rows]), trip_index, len(trips))
            theta, score = tune_theta(F, P_val, trips, val_trips)
            if best is None or score > best[2]:
                best = (h, theta, score)
        h, theta, val_score = best

        # 2. Refit on every departed trip and predict the test month.
        df = dfs[h]
        train = (df.flightDate < start).to_numpy() & df.drop_ahead.notna().to_numpy()
        test_rows = ((df.searchDate >= start) & (df.searchDate <= end)).to_numpy()
        df["log_vs_route"] = add_route_level(df, train)
        model = fit(df[train], df.loc[train, "drop_ahead"].astype(int))
        P_m = prob_matrix(df[test_rows], predict(model, df[test_rows]), trip_index, len(trips))
        P_test = np.where(np.isnan(P_m), P_test, P_m)
        folds.append({"test_month": str(m), "horizon": h, "theta": theta,
                      "val_pct_saved": val_score, "train_rows": int(train.sum()),
                      "test_rows": int(test_rows.sum()), "model": model,
                      "test_data": df[test_rows].copy()})
    return P_test, pd.DataFrame(folds)


def policy_pct_by_fold(F, P, trips, folds, start, months):
    """Per-trip % saved for decisions made `start` days out, each test month
    using its own cutoff. Returns (trip indices, % saved)."""
    from .backtest import decision_date
    month = decision_date(trips, start).dt.to_period("M")
    idx = np.flatnonzero(eligible(trips, F, start) & month.isin(months).to_numpy())
    pct = np.full(len(idx), np.nan)
    for f in folds.itertuples():
        sel = month.to_numpy()[idx] == pd.Period(f.test_month)
        pct[sel] = policy_pct_saved(F, P, idx[sel], start, f.theta)
    return idx, pct
