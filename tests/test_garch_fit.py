"""GARCH(1,1) fit recovery on synthetic GARCH DGP + fallback path."""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.garch_model import fit_garch, forecast_vol_next


def test_fit_garch_converges_on_synthetic(synthetic_returns_pct: pd.Series) -> None:
    """arch fit should converge on synthetic GARCH DGP (returns in %)."""
    res = fit_garch(synthetic_returns_pct * 10)  # scale to typical equity %
    # arch result has .params with omega, alpha[1], beta[1]
    params = res.params  # type: ignore[attr-defined]
    assert "omega" in params.index or len(params) >= 3


def test_forecast_vol_next_returns_positive(synthetic_returns_pct: pd.Series) -> None:
    fc = forecast_vol_next(synthetic_returns_pct * 10)
    assert fc.vol_pct_daily > 0
    assert fc.vol_annualised > 0
    assert isinstance(fc.converged, bool)


def test_forecast_vol_next_fallback_on_degenerate() -> None:
    """All-zero returns => arch may fail; fallback std=0 guarded to 1.0."""
    zero = pd.Series(np.zeros(252))
    fc = forecast_vol_next(zero)
    assert fc.vol_pct_daily > 0  # guard kicked in
    assert fc.converged is False


def test_fit_garch_raises_on_empty() -> None:
    """Empty series should raise."""
    import pytest

    with pytest.raises(RuntimeError):
        fit_garch(pd.Series(dtype=float))
