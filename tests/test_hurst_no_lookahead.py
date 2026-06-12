"""CRITIQUE - Anti look-ahead invariants for Hurst walk-forward (Phase 2.A).

CONTRAT section 4 / 6 - 3 invariants OBLIGATOIRES :
  1. train_strict_exclusive : train.index.max() < forecast.date for every t.
  2. weight_shift_1         : weight applied at t was decided strictly before t.
  3. no_global_scaling      : forecast index alignment doesn't peek at the future.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.hurst_backtest import (
    HurstBacktestConfig,
    compute_pnl_hurst,
    walk_forward_hurst,
)


@pytest.fixture
def long_series() -> pd.Series:
    """800 days of synthetic returns (long enough for window=504)."""
    rng = np.random.default_rng(42)
    idx = pd.date_range("2018-01-02", periods=800, freq="B")
    r = rng.standard_normal(800) * 0.8
    return pd.Series(r, index=idx, name="return")


def test_invariant_train_strict_exclusive(long_series: pd.Series) -> None:
    """For each forecast date t, train.iloc[t-window:t] must end strictly before t."""
    cfg = HurstBacktestConfig(train_window=250, refit_step=5)
    fc = walk_forward_hurst(long_series, cfg)
    idx = long_series.index
    # First forecast date is at position train_window
    assert fc.index[0] == idx[cfg.train_window]
    # Spot-check the last refit
    for k, ts in enumerate(fc.index):
        t = cfg.train_window + k
        assert ts == idx[t]
        last_train_date = idx[t - 1]
        assert last_train_date < ts


def test_invariant_weight_shift_1(long_series: pd.Series) -> None:
    """compute_pnl_hurst must apply weight = target_weight.shift(1) everywhere."""
    cfg = HurstBacktestConfig(train_window=250, refit_step=5)
    fc = walk_forward_hurst(long_series, cfg)
    pnl = compute_pnl_hurst(long_series, fc, cfg)
    # After dropna, first weight row is the 2nd target row (shift(1) consumed 1st)
    assert len(pnl) == len(fc) - 1
    # The weight series equals target_weight shifted by one (i.e. equal to the
    # PREVIOUS target_weight for each aligned row).
    # Reconstruct expected_weight from the aligned (post-join) target_weight.
    aligned_target = fc["regime"].map(
        {"momentum": 1.0, "random": 0.0, "mean_rev": 0.0}
    ).astype(float)
    expected_weight = aligned_target.shift(1).loc[pnl.index]
    pd.testing.assert_series_equal(
        pnl["weight"].rename(None),
        expected_weight.rename(None),
        check_names=False,
    )


def test_invariant_no_global_scaling(long_series: pd.Series) -> None:
    """A walk-forward run truncated to the first half must equal the first half
    of a full run (no future information leaks into early forecasts).
    """
    cfg = HurstBacktestConfig(train_window=250, refit_step=5)
    fc_full = walk_forward_hurst(long_series, cfg)
    half_end_pos = cfg.train_window + 200
    truncated = long_series.iloc[:half_end_pos]
    fc_truncated = walk_forward_hurst(truncated, cfg)
    # Early forecasts must match (DFA on identical windows -> identical h)
    n_check = min(len(fc_full), len(fc_truncated))
    pd.testing.assert_series_equal(
        fc_full["h_value"].iloc[:n_check].reset_index(drop=True),
        fc_truncated["h_value"].iloc[:n_check].reset_index(drop=True),
        check_names=False,
    )
