"""Fees should reduce net returns vs gross by turnover * fees_bps / 1e4."""

from __future__ import annotations

import math

import pandas as pd

from src.backtest_engine import BacktestConfig, compute_pnl, walk_forward


def test_fees_reduce_net_return(synthetic_returns_pct: pd.Series) -> None:
    cfg = BacktestConfig(train_window=100, fees_bps=1.0)
    fc = walk_forward(synthetic_returns_pct, cfg)
    pnl = compute_pnl(synthetic_returns_pct, fc, cfg)
    # cost is non-negative everywhere
    assert (pnl["cost"] >= 0).all()
    # net == gross - cost
    diff = (pnl["ret_strategy"] - pnl["ret_strategy_net"] - pnl["cost"]).abs().max()
    assert diff < 1e-12


def test_zero_fees_means_zero_cost(synthetic_returns_pct: pd.Series) -> None:
    cfg = BacktestConfig(train_window=100, fees_bps=0.0)
    fc = walk_forward(synthetic_returns_pct, cfg)
    pnl = compute_pnl(synthetic_returns_pct, fc, cfg)
    assert math.isclose(pnl["cost"].sum(), 0.0, abs_tol=1e-12)


def test_turnover_definition(synthetic_returns_pct: pd.Series) -> None:
    cfg = BacktestConfig(train_window=100)
    fc = walk_forward(synthetic_returns_pct, cfg)
    pnl = compute_pnl(synthetic_returns_pct, fc, cfg)
    # turnover = |weight - weight.shift(1)| with first NaN replaced by 0
    expected = pnl["weight"].diff().abs().fillna(0.0)
    assert (pnl["turnover"] - expected).abs().max() < 1e-12
