"""Performance & forecast-quality metrics.

Contract section 3.4 — exact formulas hardcoded.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

TRADING_DAYS = 252


def sharpe(pnl: pd.Series) -> float:
    """Annualised Sharpe assuming daily returns, zero risk-free."""
    pnl = pnl.dropna()
    if len(pnl) < 2:
        return float("nan")
    std = pnl.std(ddof=1)
    if std < 1e-12 or not np.isfinite(std):
        return float("nan")
    return float(pnl.mean() / std * np.sqrt(TRADING_DAYS))


def max_drawdown(pnl: pd.Series) -> float:
    """Max drawdown (negative number, e.g. -0.25 = -25%)."""
    pnl = pnl.dropna()
    if len(pnl) == 0:
        return float("nan")
    equity = (1.0 + pnl).cumprod()
    dd = equity / equity.cummax() - 1.0
    return float(dd.min())


def rmse_vol(realized: pd.Series, predicted: pd.Series) -> float:
    """RMSE between realised vol and predicted vol (both decimal annualised)."""
    aligned = pd.concat([realized, predicted], axis=1, join="inner").dropna()
    if aligned.empty:
        return float("nan")
    diff = aligned.iloc[:, 0] - aligned.iloc[:, 1]
    return float(np.sqrt((diff**2).mean()))


def hit_rate_direction(realized: pd.Series, predicted: pd.Series) -> float:
    """Fraction of days where sign(d_predicted) == sign(d_realized)."""
    aligned = pd.concat([realized, predicted], axis=1, join="inner").dropna()
    if len(aligned) < 2:
        return float("nan")
    d_real = aligned.iloc[:, 0].diff()
    d_pred = aligned.iloc[:, 1].diff()
    mask = (d_real.notna()) & (d_pred.notna()) & (d_real != 0) & (d_pred != 0)
    if mask.sum() == 0:
        return float("nan")
    return float(((d_pred > 0) == (d_real > 0))[mask].mean())


def summarise(
    ret_strategy: pd.Series,
    ret_bh: pd.Series,
    realized: pd.Series,
    predicted: pd.Series,
) -> dict[str, float]:
    """One-shot summary for the verdict table."""
    return {
        "sharpe_overlay": sharpe(ret_strategy),
        "sharpe_bh": sharpe(ret_bh),
        "max_dd_overlay": max_drawdown(ret_strategy),
        "max_dd_bh": max_drawdown(ret_bh),
        "rmse_vol": rmse_vol(realized, predicted),
        "hit_rate_vol": hit_rate_direction(realized, predicted),
        "std_realized_vol": float(realized.dropna().std(ddof=1)),
    }
