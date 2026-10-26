"""Simulate buy-or-wait strategies on historical fare paths.

A trip's fares are stored as one row of a matrix F with 61 columns: F[i, d] is
the cheapest fare for trip i seen d days before departure (d = 1..60; column 0
is unused). Missing days are NaN: the traveler sees no price that day and can't
buy, but a missing day is never read as a price change.

A strategy is a boolean matrix B of the same shape: B[i, d] = True means "buy if
I'm still waiting on day d". It may only depend on information up to day d
(that is the no-lookahead rule, enforced by whoever builds B). If a trip never
triggers a buy, the traveler buys on the last day a price is seen.
"""

import numpy as np
import pandas as pd

MAX_DAYS = 60
START_DAYS = [60, 45, 30, 21, 14]
FIRST_SEARCH = pd.Timestamp("2022-04-16")
LAST_SEARCH = pd.Timestamp("2022-10-05")


def load_fare_matrix(con, full_window_only=True):
    """Return (trips, F).

    trips: DataFrame with origin, dest, flightDate (one row per trip).
    F: float array (n_trips, 61) of cheapest fares by days ahead.

    With full_window_only, keep only trips whose whole 60-day window falls
    inside the collection period. Otherwise keep every trip and use
    `eligible` to pick the ones that can be scored from a given start day.
    """
    where = ("flightDate BETWEEN DATE '2022-06-15' AND DATE '2022-10-06'"
             if full_window_only else "TRUE")
    long = con.sql(f"""
        SELECT origin, dest, flightDate, days_ahead, fare
        FROM cheapest
        WHERE {where} AND days_ahead BETWEEN 1 AND 60
    """).df()
    wide = long.pivot_table(index=["origin", "dest", "flightDate"], columns="days_ahead",
                            values="fare", aggfunc="first")
    wide = wide.reindex(columns=range(MAX_DAYS + 1))
    trips = wide.index.to_frame(index=False)
    return trips, wide.to_numpy(dtype=float)


def decision_date(trips, start):
    """The search date on which a traveler starting `start` days out decides."""
    return pd.to_datetime(trips.flightDate) - pd.Timedelta(days=start)


def eligible(trips, F, start):
    """Trips whose window from `start` days out to departure was collected,
    and which have a price on the start day."""
    flight = pd.to_datetime(trips.flightDate)
    in_window = ((decision_date(trips, start) >= FIRST_SEARCH)
                 & (flight - pd.Timedelta(days=1) <= LAST_SEARCH)).to_numpy()
    return in_window & ~np.isnan(F[:, start])


def buy_day(F, B, start):
    """Day each trip buys under strategy B, starting `start` days out.

    Walks from `start` down to 1 and returns the first observed day where B is
    True, or the last observed day if B never fires. NaN where the trip has no
    price on the start day (those trips are excluded from scoring).
    """
    n = F.shape[0]
    days = np.full(n, np.nan)
    last_seen = np.full(n, np.nan)
    for d in range(start, 0, -1):
        seen = ~np.isnan(F[:, d])
        last_seen[seen] = d
        fire = seen & B[:, d] & np.isnan(days)
        days[fire] = d
    days = np.where(np.isnan(days), last_seen, days)
    days[np.isnan(F[:, start])] = np.nan
    return days


def price_paid(F, days):
    out = np.full(F.shape[0], np.nan)
    ok = ~np.isnan(days)
    out[ok] = F[np.flatnonzero(ok), days[ok].astype(int)]
    return out


def hindsight_best(F, start):
    """Lowest fare seen from `start` days out to departure (needs the future)."""
    window = F[:, 1:start + 1]
    best = np.full(F.shape[0], np.nan)
    has_price = ~np.isnan(window).all(axis=1)
    best[has_price] = np.nanmin(window[has_price], axis=1)
    best[np.isnan(F[:, start])] = np.nan
    return best


def score(start_fare, paid):
    """Savings vs. buying on the start day, in $ and %, both ways of averaging."""
    ok = ~np.isnan(start_fare) & ~np.isnan(paid)
    p0, p = start_fare[ok], paid[ok]
    saved = p0 - p
    return pd.Series({
        "trips": ok.sum(),
        "avg_saved_usd": saved.mean(),
        "avg_saved_pct": (saved / p0).mean(),
        "total_saved_pct": saved.sum() / p0.sum(),
        "share_lost_money": (saved < 0).mean(),
        "share_saved_money": (saved > 0).mean(),
    })


def fixed_day_rule(F, n_days):
    """'Buy n_days before departure': fires on every day at or below n_days."""
    B = np.zeros_like(F, dtype=bool)
    B[:, 1:n_days + 1] = True
    return B
