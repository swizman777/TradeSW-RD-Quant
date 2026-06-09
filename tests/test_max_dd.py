"""Max drawdown edge cases."""

from __future__ import annotations

import math

import pandas as pd

from src.metrics import max_drawdown


def test_max_dd_known_series() -> None:
    """Equity path [1, 2, 1, 0.5, 1] => peak=2, trough=0.5 => DD = -0.75.

    Daily returns from equity: ret[t] = eq[t]/eq[t-1] - 1
        eq: [1,2,1,0.5,1] -> ret: [+1.0, -0.5, -0.5, +1.0]
    cumprod(1+r) = [2, 1, 0.5, 1]; cummax = [2, 2, 2, 2]; dd = [0, -0.5, -0.75, -0.5]
    => min = -0.75.
    """
    rets = pd.Series([1.0, -0.5, -0.5, 1.0])
    assert math.isclose(max_drawdown(rets), -0.75, abs_tol=1e-9)


def test_max_dd_monotonic_up_is_zero() -> None:
    rets = pd.Series([0.01] * 100)
    assert math.isclose(max_drawdown(rets), 0.0, abs_tol=1e-9)


def test_max_dd_empty_series_is_nan() -> None:
    assert math.isnan(max_drawdown(pd.Series(dtype=float)))


def test_max_dd_single_crash() -> None:
    rets = pd.Series([0.0, -0.2])
    assert math.isclose(max_drawdown(rets), -0.2, abs_tol=1e-9)
