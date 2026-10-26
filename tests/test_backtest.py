import numpy as np
import pandas as pd

from flight_pricing.backtest import (buy_day, eligible, fixed_day_rule, hindsight_best,
                                     price_paid, score)

nan = np.nan


def make_paths():
    F = np.full((3, 61), nan)
    F[0, 1:6] = [300, 280, 200, 250, 250]   # drops 3 days out
    F[1, [1, 2, 4, 5]] = [400, 390, 310, 300]  # no price 3 days out
    F[2, 1:5] = [100, 100, 100, 100]          # no price on the start day
    return F


def test_buy_now_and_excluded_trip():
    F = make_paths()
    days = buy_day(F, np.ones_like(F, bool), start=5)
    assert list(days[:2]) == [5, 5]
    assert np.isnan(days[2])


def test_fixed_rule_skips_missing_day():
    F = make_paths()
    days = buy_day(F, fixed_day_rule(F, 3), start=5)
    assert list(days[:2]) == [3, 2]
    assert list(price_paid(F, days)[:2]) == [200, 390]


def test_never_firing_rule_buys_on_last_seen_day():
    F = make_paths()
    days = buy_day(F, np.zeros_like(F, bool), start=5)
    assert list(days[:2]) == [1, 1]


def test_hindsight_and_score():
    F = make_paths()
    assert list(hindsight_best(F, 5)[:2]) == [200, 300]
    s = score(F[:, 5], price_paid(F, buy_day(F, fixed_day_rule(F, 3), start=5)))
    assert s.trips == 2
    assert s.avg_saved_usd == ((250 - 200) + (300 - 390)) / 2
    assert s.share_lost_money == 0.5


def test_eligible_needs_full_window_and_start_price():
    trips = pd.DataFrame({"flightDate": pd.to_datetime(
        ["2022-05-01", "2022-07-01", "2022-10-20", "2022-07-01"])})
    F = np.full((4, 61), 100.0)
    F[3, 30] = np.nan  # no price on the start day
    # May 1 minus 30 days is before collection began; Oct 20 departs after it ended.
    assert list(eligible(trips, F, 30)) == [False, True, False, False]
