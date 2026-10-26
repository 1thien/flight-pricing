"""Model inputs and labels for each (trip, day) decision point.

Every feature uses only fares seen on or before the decision day. In a window
ordered by days_ahead ascending, the past is FOLLOWING (more days ahead) and
the future is PRECEDING (fewer days ahead). Only the label looks at the future.
"""

import numpy as np

DROP = 0.05     # a "meaningful drop" is at least 5%
HORIZON = 7     # ...within the next 7 days
DEADLINES = (21, 14, 7)
LAST_SEARCH = "2022-10-05"
ULCC = ("Spirit Airlines", "Frontier Airlines")

NUMERIC = ["days_ahead", "days_to_deadline", "log_change_prev", "log_change_week",
           "log_vs_min_so_far", "log_vs_max_so_far", "days_observed", "n_options",
           "seatsRemaining", "flight_dow", "search_dow"]
FLAGS = ["isNonStop", "isBasicEconomy", "ulcc"]
FOLD_FEATURES = ["log_vs_route"]   # computed per fold from training data only
CATEGORICAL = ["origin", "dest"]
FEATURES = NUMERIC + FLAGS + FOLD_FEATURES + CATEGORICAL


def build_features(con, horizon=HORIZON):
    """One row per trip and decision day (2 to 60 days out), with the label
    `drop_ahead`: did the fare fall at least DROP within the next `horizon` days?"""
    d1, d2, d3 = DEADLINES
    df = con.sql(f"""
        WITH x AS (
            SELECT *,
                lead(fare) OVER past1 AS prev_fare,
                avg(fare) OVER (t RANGE BETWEEN 6 FOLLOWING AND 8 FOLLOWING) AS fare_week_ago,
                min(fare) OVER (t ROWS BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING) AS min_so_far,
                max(fare) OVER (t ROWS BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING) AS max_so_far,
                count(*) OVER (t ROWS BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING) AS days_observed,
                min(fare) OVER (t RANGE BETWEEN {horizon} PRECEDING AND 1 PRECEDING) AS future_min
            FROM cheapest
            WINDOW t AS (PARTITION BY origin, dest, flightDate ORDER BY days_ahead),
                   past1 AS (PARTITION BY origin, dest, flightDate ORDER BY days_ahead)
        )
        SELECT origin, dest, flightDate, searchDate, days_ahead, fare,
               days_ahead - CASE WHEN days_ahead > {d1} THEN {d1} WHEN days_ahead > {d2} THEN {d2}
                                 WHEN days_ahead > {d3} THEN {d3} ELSE 0 END AS days_to_deadline,
               ln(fare / prev_fare) AS log_change_prev,
               ln(fare / fare_week_ago) AS log_change_week,
               ln(fare / min_so_far) AS log_vs_min_so_far,
               ln(fare / max_so_far) AS log_vs_max_so_far,
               days_observed, n_options, seatsRemaining,
               dayofweek(flightDate) AS flight_dow, dayofweek(searchDate) AS search_dow,
               isNonStop::INT AS isNonStop, isBasicEconomy::INT AS isBasicEconomy,
               (split_part(airlines, '||', 1) IN {ULCC})::INT AS ulcc,
               -- Unknown (NULL) when the next HORIZON days weren't fully collected:
               -- collection ended on LAST_SEARCH, and a drop after that would
               -- otherwise look like "no drop" (right-censoring).
               CASE WHEN searchDate + least({horizon}, days_ahead - 1)::INT > DATE '{LAST_SEARCH}'
                    THEN NULL
                    ELSE (future_min <= fare * (1 - {DROP}))::INT END AS drop_ahead
        FROM x
        WHERE days_ahead BETWEEN 2 AND 60
        -- A fixed row order keeps LightGBM's row sampling, and so its results,
        -- reproducible from run to run.
        ORDER BY origin, dest, flightDate, days_ahead DESC
    """).df()
    df["flightDate"] = df.flightDate.astype("datetime64[ns]")
    df["searchDate"] = df.searchDate.astype("datetime64[ns]")
    for c in CATEGORICAL:
        df[c] = df[c].astype("category")
    return df


def add_route_level(df, train_mask):
    """log(fare / route's median fare), with the median taken from training rows only."""
    route_median = df[train_mask].groupby(["origin", "dest"], observed=True).fare.median()
    med = df.join(route_median.rename("route_median"), on=["origin", "dest"]).route_median
    out = np.log(df.fare / med)
    return out.fillna(0.0)
