"""Walk-forward GARCH backtest engine with strict anti look-ahead masking.

Contract section 3.1 (CRITIQUE):
- train = returns.iloc[t-252:t]  STRICT EXCLUSIVE on t
- forecast horizon = 1 (next day only)
- position = sizing.shift(1)
- pas de scaling global

Contract section 3.3:
- fees: 1 bps per side (0.01%) on |dweight|
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from src.garch_model import forecast_vol_next
from src.vol_targeting import DEFAULT_VOL_TARGET, compute_position_size

DEFAULT_TRAIN_WINDOW = 252
DEFAULT_FEES_BPS = 1.0  # 1 bps per side (contract 3.3)


@dataclass(frozen=True)
class BacktestConfig:
    """Strategy parameters (immutable per run)."""

    train_window: int = DEFAULT_TRAIN_WINDOW
    target_vol: float = DEFAULT_VOL_TARGET
    fees_bps: float = DEFAULT_FEES_BPS
    max_leverage: float = 1.0
    min_leverage: float = 0.0


def walk_forward(
    returns_pct: pd.Series,
    config: BacktestConfig | None = None,
) -> pd.DataFrame:
    """Run walk-forward GARCH(1,1) forecast on a daily return series.

    For each t in [train_window, len(returns_pct)):
        train = returns_pct.iloc[t - train_window : t]   # EXCLUSIVE on t
        forecast vol(t)
    """
    cfg = config or BacktestConfig()
    n = len(returns_pct)
    if n <= cfg.train_window:
        raise ValueError(
            f"Series too short: {n} <= train_window={cfg.train_window}"
        )

    idx = returns_pct.index
    pred_vol_annual: list[float] = []
    converged: list[bool] = []
    forecast_idx: list[pd.Timestamp] = []

    for t in range(cfg.train_window, n):
        train_slice = returns_pct.iloc[t - cfg.train_window : t]  # EXCLUSIVE
        # Anti look-ahead invariant (also asserted in tests)
        assert train_slice.index.max() < idx[t], "look-ahead bias detected"
        fc = forecast_vol_next(train_slice)
        pred_vol_annual.append(fc.vol_annualised)
        converged.append(fc.converged)
        forecast_idx.append(idx[t])

    forecasts = pd.DataFrame(
        {
            "pred_vol_annual": pred_vol_annual,
            "garch_converged": converged,
        },
        index=pd.DatetimeIndex(forecast_idx, name="date"),
    )
    return forecasts


def compute_pnl(
    returns_pct: pd.Series,
    forecasts: pd.DataFrame,
    config: BacktestConfig | None = None,
) -> pd.DataFrame:
    """Compute overlay PnL vs buy-and-hold given forecasts.

    Returns columns:
        ret_decimal     : decimal daily return (returns_pct / 100)
        weight          : position sized from prev forecast (shift(1) applied)
        ret_strategy    : weight * ret_decimal  (gross)
        turnover        : |weight - weight.shift(1)|
        cost            : turnover * fees_bps / 1e4
        ret_strategy_net: ret_strategy - cost
        ret_bh          : ret_decimal (buy & hold)
    """
    cfg = config or BacktestConfig()

    aligned = forecasts.join(returns_pct.rename("ret_pct"), how="inner")
    aligned["ret_decimal"] = aligned["ret_pct"] / 100.0

    weights = compute_position_size(
        aligned["pred_vol_annual"],
        target_vol=cfg.target_vol,
        max_leverage=cfg.max_leverage,
        min_leverage=cfg.min_leverage,
    )
    aligned["weight"] = weights

    aligned["ret_strategy"] = aligned["weight"] * aligned["ret_decimal"]
    aligned["turnover"] = aligned["weight"].diff().abs().fillna(0.0)
    aligned["cost"] = aligned["turnover"] * cfg.fees_bps / 1e4
    aligned["ret_strategy_net"] = aligned["ret_strategy"] - aligned["cost"]
    aligned["ret_bh"] = aligned["ret_decimal"]

    # Drop the unavoidable first NaN row from shift(1)
    aligned = aligned.dropna(subset=["weight"])
    return aligned


def realized_vol(returns_pct: pd.Series, window: int = 21) -> pd.Series:
    """Rolling realised vol annualised (decimal) — contract 3.4."""
    return returns_pct.rolling(window).std() * np.sqrt(252) / 100.0
