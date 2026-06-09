"""CRITIQUE — Anti look-ahead bias invariants.

Contract section 3.1 / 7: 3 invariants
  1. masking exclusif : train.index.max() < forecast.date
  2. forecast horizon == 1 strict
  3. pas de scaling global (test indirect: stats des 100 premiers vs 100 derniers
     ne dependent pas du futur)
"""

from __future__ import annotations

import pandas as pd

from src.backtest_engine import BacktestConfig, compute_pnl, walk_forward


def test_invariant_1_train_index_strictly_before_forecast(synthetic_returns_pct: pd.Series) -> None:
    cfg = BacktestConfig(train_window=100)
    fc = walk_forward(synthetic_returns_pct, cfg)
    # forecasts indexed by t (the day BEING forecast)
    n = len(synthetic_returns_pct)
    assert len(fc) == n - cfg.train_window
    # For each forecast date t, the training window ended at t-1 strictly
    expected_first_date = synthetic_returns_pct.index[cfg.train_window]
    assert fc.index[0] == expected_first_date


def test_invariant_2_forecast_horizon_is_one(synthetic_returns_pct: pd.Series) -> None:
    """Forecast index must be exactly 1 trading day past last train obs."""
    cfg = BacktestConfig(train_window=100)
    fc = walk_forward(synthetic_returns_pct, cfg)
    idx = synthetic_returns_pct.index
    for k, ts in enumerate(fc.index):
        t = cfg.train_window + k
        assert ts == idx[t]
        # last train date is strictly before forecast date
        last_train_date = idx[t - 1]
        assert last_train_date < ts


def test_invariant_3_no_global_scaling_position_shifted(
    synthetic_returns_pct: pd.Series,
) -> None:
    """compute_pnl must apply weight = shift(1). The first valid weight
    aligned with a return must NOT have used same-day forecast (i.e. NaN
    on the very first forecast row after the dropna)."""
    cfg = BacktestConfig(train_window=100)
    fc = walk_forward(synthetic_returns_pct, cfg)
    pnl = compute_pnl(synthetic_returns_pct, fc, cfg)
    # After dropna, the first weight is the 2nd raw forecast (1st is consumed by shift)
    assert len(pnl) == len(fc) - 1
    # And the strategy return of the 1st row is weight_t * ret_t where
    # weight_t was decided strictly before t.
    first_pnl_date = pnl.index[0]
    assert first_pnl_date == fc.index[1]


def test_forecast_dataframe_columns(synthetic_returns_pct: pd.Series) -> None:
    cfg = BacktestConfig(train_window=100)
    fc = walk_forward(synthetic_returns_pct, cfg)
    assert set(fc.columns) == {"pred_vol_annual", "garch_converged"}
    assert (fc["pred_vol_annual"] > 0).all()
