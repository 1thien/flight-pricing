import numpy as np

from flight_pricing.rl import next_observed_day


def test_next_observed_day_skips_gaps():
    F = np.full((1, 8), np.nan)
    F[0, [1, 2, 5, 7]] = 100.0          # prices seen 1, 2, 5 and 7 days out
    nxt = next_observed_day(F)
    assert nxt[0, 7] == 5               # from day 7, the next price is on day 5 (6 is missing)
    assert nxt[0, 5] == 2
    assert nxt[0, 3] == 2
    assert nxt[0, 2] == 1
    assert nxt[0, 1] == 0               # nothing after the last day
