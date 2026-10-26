import numpy as np

from flight_pricing.dp import dp_buy_matrix, fit_jump_model, grid, transition_matrices


def test_transition_rows_are_probabilities():
    rng = np.random.default_rng(0)
    X = rng.normal(0, 0.3, size=(200, 61))
    M = transition_matrices(X, np.ones(200, bool), K=10)
    for t in range(2, 61):
        assert np.allclose(M[:, :, t].sum(axis=1), 1.0)
        assert (M[:, :, t] >= 0).all()


def test_jump_model_recovers_pull_back():
    # Simulate x_{t-1} = x_t + jump * (0.0 - 0.3 * x_t + noise), with jumps on half the days.
    rng = np.random.default_rng(1)
    n = 4000
    X = np.full((n, 61), np.nan)
    X[:, 60] = rng.normal(0, 0.3, n)
    for t in range(60, 1, -1):
        jump = rng.random(n) < 0.5
        X[:, t - 1] = X[:, t] + jump * (-0.3 * X[:, t] + rng.normal(0, 0.1, n))
    p = fit_jump_model(X, np.ones(n, bool))
    assert abs(p["lam"][30] - 0.5) < 0.03
    assert abs(p["kappa"][30] + 0.3) < 0.03
    assert abs(p["sigma"][30] - 0.1) < 0.01


def test_policy_buys_when_cost_below_continuation():
    _, centers = grid(4)
    C = np.full((4, 61), np.inf)
    C[:, 5] = 1.0                      # waiting from day 5 costs exactly the usual fare
    X = np.full((2, 61), np.nan)
    X[:, 5] = [-0.2, 0.2]              # one fare below usual, one above
    B = dp_buy_matrix(X, C, centers)
    assert list(B[:, 5]) == [True, False]
    assert B[:, 1].all()               # last day: always buy
