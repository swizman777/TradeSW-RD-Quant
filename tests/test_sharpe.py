"""Sharpe ratio edge cases."""

from __future__ import annotations

import math

import numpy as np
import pandas as pd

from src.metrics import sharpe


def test_sharpe_constant_returns_is_inf_or_nan() -> None:
    """Constant returns => std=0 => NaN (we return NaN, not inf)."""
    s = pd.Series([0.001] * 100)
    assert math.isnan(sharpe(s))


def test_sharpe_zero_returns_is_nan() -> None:
    s = pd.Series([0.0] * 100)
    assert math.isnan(sharpe(s))


def test_sharpe_known_value() -> None:
    """Known case: mean=0.001/day, std=0.01 => Sharpe = 0.1 * sqrt(252) ≈ 1.587."""
    rng = np.random.default_rng(42)
    n = 10000
    r = pd.Series(rng.normal(0.001, 0.01, n))
    val = sharpe(r)
    # Expected ~ 1.587 but allow generous bound due to finite sample
    assert 1.3 < val < 1.9


def test_sharpe_empty_series_is_nan() -> None:
    assert math.isnan(sharpe(pd.Series(dtype=float)))
