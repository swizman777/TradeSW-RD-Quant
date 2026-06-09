"""GARCH(1,1) wrapper around Kevin Sheppard's arch library.

Contract section 3.2:
- Library: arch>=7.2.0 (Oxford)
- Returns in % (x100) for numerical stability
- fit(disp="off", show_warning=False)
- Fallback train.std() if convergence fails
- Forecast horizon=1, reindex=False
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class GarchForecast:
    """One-step-ahead conditional vol forecast (annualised, decimal).

    Attributes:
        vol_pct_daily: predicted daily sigma in %  (raw scale of arch returns)
        vol_annualised: vol_pct_daily / 100 * sqrt(252)
        converged: True if arch optimizer converged, False if fallback used
    """

    vol_pct_daily: float
    vol_annualised: float
    converged: bool


def fit_garch(returns_pct: pd.Series) -> object:
    """Fit GARCH(1,1) on returns expressed in %.

    Args:
        returns_pct: pd.Series of returns multiplied by 100 (e.g. 1.2 = 1.2%)

    Returns:
        Fitted arch ARCHModelResult.

    Raises:
        RuntimeError: on convergence failure (caller should fallback).
    """
    from arch import arch_model  # noqa: PLC0415

    try:
        model = arch_model(
            returns_pct.dropna(),
            vol="GARCH",
            p=1,
            q=1,
            mean="Zero",
            dist="normal",
            rescale=False,
        )
        result = model.fit(disp="off", show_warning=False, update_freq=0)
        return result
    except Exception as exc:  # noqa: BLE001 — wraps arch internal errors
        raise RuntimeError(f"GARCH fit failed: {exc}") from exc


def forecast_vol_next(returns_pct: pd.Series) -> GarchForecast:
    """One-step-ahead vol forecast with fallback to historical std.

    Returns:
        GarchForecast (always returns a value; converged flag indicates path).
    """
    try:
        result = fit_garch(returns_pct)
        fcast = result.forecast(horizon=1, reindex=False)  # type: ignore[attr-defined]
        var_next = float(fcast.variance.values[-1, 0])
        if not np.isfinite(var_next) or var_next <= 0:
            raise RuntimeError("non-finite or non-positive variance")
        vol_daily_pct = float(np.sqrt(var_next))
        return GarchForecast(
            vol_pct_daily=vol_daily_pct,
            vol_annualised=vol_daily_pct / 100.0 * np.sqrt(252),
            converged=True,
        )
    except Exception:
        # Fallback: historical std on the same window (contract 3.2)
        std_pct = float(returns_pct.dropna().std(ddof=1))
        if not np.isfinite(std_pct) or std_pct <= 0:
            std_pct = 1.0  # ultimate guard
        return GarchForecast(
            vol_pct_daily=std_pct,
            vol_annualised=std_pct / 100.0 * np.sqrt(252),
            converged=False,
        )
