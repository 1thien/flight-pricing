"""Fitted Q-iteration: learn the value of waiting directly from price paths.

For a trip on day t with state s (the same inputs as notebook 06), buying costs
cost(x_t), where x_t = log(fare / route's usual fare). Waiting leads to the next
day u < t with a price, where I act optimally again. The value of waiting is

    W_t(s) = E[ min(cost(x_u), W_u(s_u)) | s ]      (cost(x_1) if u is day 1)

which is the Bellman equation (section 6 of the math reference) with the
expectation estimated by regression instead of a price model. Because u < t,
the W_t can be fit in order t = 2, 3, ..., 60, each one using the already-fit
W_u. Policy: buy on day t if cost(x_t) <= W_t(s_t).
"""

import lightgbm as lgb
import numpy as np
import pandas as pd

from .features import FEATURES
from .model import make_trip_index

Q_PARAMS = dict(objective="regression", learning_rate=0.05, num_leaves=31, min_data_in_leaf=200,
                feature_fraction=0.8, bagging_fraction=0.8, bagging_freq=1, verbose=-1, seed=0,
                deterministic=True, force_row_wise=True)
Q_ROUNDS = 200
MIN_ROWS = 500


def route_median_fare(df, train_rows):
    return df[train_rows].groupby(["origin", "dest"], observed=True).fare.median()


def next_observed_day(F):
    """nxt[i, t] = the latest day u < t with a fare for trip i (0 if none)."""
    nxt = np.zeros(F.shape, dtype=int)
    last = np.zeros(F.shape[0], dtype=int)
    for t in range(1, F.shape[1]):
        nxt[:, t] = last
        last = np.where(~np.isnan(F[:, t]), t, last)
    return nxt


def cost_fn(objective):
    return (lambda x: x) if objective == "log" else np.exp


def fit_q_models(df, rows, X, nxt, row_trip, objective="log"):
    """Fit W_2, ..., W_60 on the given rows. Returns a dict day -> model.

    X[i, t] is the relative log fare for trip i on day t (NaN if unseen);
    row_trip maps each row of df to its trip index.
    """
    cost = cost_fn(objective)
    W = np.full(X.shape, np.nan)      # fitted value of waiting, filled day by day
    models, last_model = {}, None
    days = df.days_ahead.to_numpy()
    for t in range(2, 61):
        sel = np.flatnonzero(rows & (days == t))
        i = row_trip[sel]
        u = nxt[i, t]
        known = u >= 1
        sel, i, u = sel[known], i[known], u[known]
        y = cost(X[i, u])
        later = u >= 2
        y[later] = np.minimum(y[later], W[i[later], u[later]])
        ok = ~np.isnan(y)
        sel, i, y = sel[ok], i[ok], y[ok]
        if len(sel) >= MIN_ROWS:
            last_model = lgb.train(Q_PARAMS, lgb.Dataset(df.iloc[sel][FEATURES], y), Q_ROUNDS)
        models[t] = last_model        # too little data this far out: reuse the nearest day's model
        if last_model is not None and len(sel):
            W[i, t] = last_model.predict(df.iloc[sel][FEATURES])
    return models


def walk_forward_q(df, trips, F, test_months, objective="log"):
    """Buy matrix B (n_trips x 61) for every decision in the test months, with
    each month's models fit only on trips that departed before it."""
    trip_index = make_trip_index(trips)
    keys = pd.MultiIndex.from_frame(df[["origin", "dest", "flightDate"]].astype({"origin": str, "dest": str}))
    row_trip = trip_index.reindex(keys).to_numpy().astype(int)
    nxt = next_observed_day(F)
    cost = cost_fn(objective)
    route = pd.MultiIndex.from_frame(trips[["origin", "dest"]].astype(str))
    B = np.ones(F.shape, dtype=bool)   # no prediction (outside the test months) means buy, as in notebook 06
    for m in test_months:
        train = (df.flightDate < m.start_time).to_numpy()
        med = route_median_fare(df, train)
        med.index = med.index.set_levels([lvl.astype(str) for lvl in med.index.levels])
        ref = med.reindex(route).to_numpy()
        with np.errstate(invalid="ignore", divide="ignore"):
            X = np.log(F / ref[:, None])
        df["log_vs_route"] = X[row_trip, df.days_ahead.to_numpy()]
        df["log_vs_route"] = df["log_vs_route"].fillna(0.0)
        models = fit_q_models(df, train, X, nxt, row_trip, objective)
        test = ((df.searchDate >= m.start_time) & (df.searchDate <= m.end_time)).to_numpy()
        for t in range(2, 61):
            sel = np.flatnonzero(test & (df.days_ahead.to_numpy() == t))
            if len(sel) == 0 or models.get(t) is None:
                continue
            i = row_trip[sel]
            w = models[t].predict(df.iloc[sel][FEATURES])
            x = X[i, t]
            buy = ~(cost(x) > w)   # buy unless waiting is expected to be cheaper (unknown x: buy)
            B[i, t] = buy
    return B
