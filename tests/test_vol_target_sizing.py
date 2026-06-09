"""Vol-targeting sizing: shift(1) anti look-ahead + clip bounds."""

from __future__ import annotations

import math

import numpy as np
import pandas as pd

from src.vol_targeting import DEFAULT_VOL_TARGET, compute_position_size


def test_position_first_row_is_nan_due_to_shift() -> None:
    pred = pd.Series([0.20, 0.10, 0.05], index=pd.date_range("2020-01-01", periods=3))
    w = compute_position_size(pred)
    assert math.isnan(w.iloc[0])


def test_position_value_inversely_proportional_to_pred_vol() -> None:
    """weight at t = target / pred_vol at t-1, capped at max_leverage."""
    pred = pd.Series([0.20, 0.10], index=pd.date_range("2020-01-01", periods=2))
    w = compute_position_size(pred, target_vol=0.10, max_leverage=10.0)
    # second row = 0.10 / 0.20 = 0.5
    assert math.isclose(w.iloc[1], 0.5, abs_tol=1e-9)


def test_position_clipped_to_max_leverage() -> None:
    pred = pd.Series(
        [0.05, 0.05, 0.05], index=pd.date_range("2020-01-01", periods=3)
    )
    # target/pred = 0.10/0.05 = 2.0, but max_leverage=1.0
    w = compute_position_size(pred, target_vol=DEFAULT_VOL_TARGET, max_leverage=1.0)
    valid = w.dropna()
    assert (valid <= 1.0 + 1e-9).all()
    assert (valid >= 0.0).all()


def test_position_clipped_to_min_leverage() -> None:
    pred = pd.Series([0.50] * 5, index=pd.date_range("2020-01-01", periods=5))
    w = compute_position_size(pred, target_vol=0.10, min_leverage=0.0)
    # 0.10/0.50 = 0.20, well above 0, should be 0.20
    valid = w.dropna()
    assert math.isclose(valid.iloc[0], 0.20, abs_tol=1e-9)


def test_zero_pred_vol_is_handled() -> None:
    pred = pd.Series([0.0, 0.10, 0.10], index=pd.date_range("2020-01-01", periods=3))
    w = compute_position_size(pred)
    # No inf nor NaN propagated to the non-shifted rows beyond the first
    assert np.isfinite(w.dropna()).all()
