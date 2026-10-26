import numpy as np

from flight_pricing.stats import bootstrap, percentile_ci, savings_stats


def test_savings_stats():
    s = savings_stats(np.array([100.0, 300.0]), np.array([0.10, -0.10]))
    assert s.avg_saved_pct == 0.0
    assert np.isclose(s.total_saved_pct, (10 - 30) / 400)
    assert np.isclose(s.avg_saved_usd, -10.0)
    assert s.share_lost_money == 0.5


def test_cluster_bootstrap_keeps_clusters_together():
    # Two routes: every trip on route A saves 10%, every trip on route B saves 0%.
    fare = np.full(6, 100.0)
    pct = np.array([0.1, 0.1, 0.1, 0.0, 0.0, 0.0])
    route = np.array(["A", "A", "A", "B", "B", "B"])
    draws = bootstrap(fare, pct, clusters=route, n_boot=200)
    # Resampling whole routes can only give averages of 0, 5% or 10%.
    assert set(np.round(draws.avg_saved_pct, 6)) <= {0.0, 0.05, 0.1}


def test_cluster_ci_is_wider_when_trips_within_a_route_are_alike():
    rng = np.random.default_rng(1)
    route_effect = rng.normal(0, 0.05, size=40)
    route = np.repeat(np.arange(40), 50)
    pct = route_effect[route] + rng.normal(0, 0.01, size=route.size)
    fare = np.full(route.size, 100.0)
    iid = percentile_ci(bootstrap(fare, pct, n_boot=300))
    clu = percentile_ci(bootstrap(fare, pct, clusters=route, n_boot=300))
    width = lambda ci: ci.loc["avg_saved_pct", "high"] - ci.loc["avg_saved_pct", "low"]
    assert width(clu) > 3 * width(iid)
