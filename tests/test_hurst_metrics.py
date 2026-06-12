"""Unit tests for `src.hurst_metrics` (Phase 2.A).

CONTRAT section 6 - at least 3 tests:
  - test_ic_known_series         : perfectly correlated -> IC == 1.0
  - test_sharpe_net_with_costs   : costs strictly reduce net Sharpe
  - test_bootstrap_ci_reproducible : same seed -> identical CI bounds
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd

from src.hurst_backtest import HurstBacktestConfig, compute_pnl_hurst
from src.hurst_metrics import (
    bootstrap_ci,
    diebold_mariano,
    information_coefficient,
)


def test_ic_known_series() -> None:
    """Perfectly correlated signal and forward return -> IC == 1.0."""
    n = 200
    idx = pd.date_range("2020-01-02", periods=n, freq="B")
    signal = pd.Series(np.linspace(0.0, 1.0, n), index=idx)
    future_ret = signal.copy() + 0.0  # identical -> corr = 1
    ic = information_coefficient(signal, future_ret)
    assert math.isclose(ic, 1.0, abs_tol=1e-9)


def test_ic_anticorrelated_series() -> None:
    """Anti-correlated signal -> IC == -1.0 (sanity sign check)."""
    n = 200
    idx = pd.date_range("2020-01-02", periods=n, freq="B")
    signal = pd.Series(np.linspace(0.0, 1.0, n), index=idx)
    future_ret = -signal
    ic = information_coefficient(signal, future_ret)
    assert math.isclose(ic, -1.0, abs_tol=1e-9)


def test_ic_zero_variance_returns_nan() -> None:
    """Constant signal -> IC undefined -> NaN."""
    n = 100
    idx = pd.date_range("2020-01-02", periods=n, freq="B")
    signal = pd.Series(np.ones(n), index=idx)
    future_ret = pd.Series(np.random.default_rng(0).standard_normal(n), index=idx)
    ic = information_coefficient(signal, future_ret)
    assert math.isnan(ic)


def test_sharpe_net_with_costs_strictly_lower() -> None:
    """Adding fees+slippage must lower the net Sharpe vs gross.

    Build a synthetic forecast frame with a toggling regime so turnover > 0,
    then compare the strategy net Sharpe at 0 cost vs 6bps cost.
    """
    n = 300
    idx = pd.date_range("2020-01-02", periods=n, freq="B")
    rng = np.random.default_rng(7)
    ret_pct = pd.Series(rng.standard_normal(n) * 1.0, index=idx, name="return")
    # Regime toggles every 10 days -> non-zero turnover
    regimes = ["momentum" if (i // 10) % 2 == 0 else "random" for i in range(n)]
    fc = pd.DataFrame(
        {
            "h_value": np.where(np.array(regimes) == "momentum", 0.6, 0.5),
            "regime": regimes,
            "hurst_converged": [True] * n,
            "refit_today": [True] * n,
        },
        index=idx,
    )
    cfg_no_cost = HurstBacktestConfig(fees_bps=0.0, slippage_bps=0.0)
    cfg_with_cost = HurstBacktestConfig(fees_bps=1.0, slippage_bps=5.0)
    pnl_gross = compute_pnl_hurst(ret_pct, fc, cfg_no_cost)
    pnl_net = compute_pnl_hurst(ret_pct, fc, cfg_with_cost)
    # Average cost must be > 0 because toggling regime creates turnover
    assert pnl_net["cost"].sum() > 0
    # Net mean return must be lower than gross by the cost mean
    assert pnl_net["ret_strategy_net"].mean() < pnl_gross["ret_strategy_net"].mean()


def test_bootstrap_ci_reproducible() -> None:
    """Identical seed -> identical CI bounds (Reproductibilite clause)."""
    rng = np.random.default_rng(0)
    series = pd.Series(rng.standard_normal(500) * 0.01)
    ci_a = bootstrap_ci(series, statistic="sharpe", n_boot=200, seed=42)
    ci_b = bootstrap_ci(series, statistic="sharpe", n_boot=200, seed=42)
    assert math.isclose(ci_a.mean, ci_b.mean, rel_tol=1e-12)
    assert math.isclose(ci_a.lower, ci_b.lower, rel_tol=1e-12)
    assert math.isclose(ci_a.upper, ci_b.upper, rel_tol=1e-12)
    # And a different seed gives a different bound
    ci_c = bootstrap_ci(series, statistic="sharpe", n_boot=200, seed=99)
    assert not math.isclose(ci_a.lower, ci_c.lower, rel_tol=1e-9)


def test_diebold_mariano_identical_errors_is_nan_or_zero() -> None:
    """Two identical error series -> DM stat == 0 (or NaN on var=0 guard)."""
    n = 100
    idx = pd.date_range("2020-01-02", periods=n, freq="B")
    err = pd.Series(np.random.default_rng(0).standard_normal(n), index=idx)
    dm, p = diebold_mariano(err, err.copy(), horizon=1)
    # The loss differential is identically zero -> var=0 guard returns NaN
    assert math.isnan(dm) or math.isclose(dm, 0.0, abs_tol=1e-9)
    if math.isnan(dm):
        assert math.isnan(p)
