"""RMSE between realized and predicted vol."""

from __future__ import annotations

import math

import pandas as pd

from src.metrics import rmse_vol


def test_rmse_perfect_forecast_is_zero() -> None:
    s = pd.Series([0.1, 0.15, 0.20], index=pd.date_range("2020-01-01", periods=3))
    assert math.isclose(rmse_vol(s, s), 0.0, abs_tol=1e-12)


def test_rmse_known_value() -> None:
    """real=[1,2,3], pred=[2,2,2] => diffs=[1,0,1] => RMSE=sqrt(2/3) ~ 0.8165."""
    real = pd.Series([1.0, 2.0, 3.0], index=pd.date_range("2020-01-01", periods=3))
    pred = pd.Series([2.0, 2.0, 2.0], index=real.index)
    assert math.isclose(rmse_vol(real, pred), math.sqrt(2 / 3), abs_tol=1e-9)


def test_rmse_empty_is_nan() -> None:
    assert math.isnan(rmse_vol(pd.Series(dtype=float), pd.Series(dtype=float)))
