"""Walk-forward Hurst-DFA backtest engine (Phase 2.A flat).

Mandate Chef Swizman 2026-06-10 (CONTRAT_CODEX_PHASE2A_HURST.md).

Differences vs Phase 1 GARCH `backtest_engine.py` (which is IMMUTABLE):
- window = 504 days (~2 years) instead of 252 - DFA needs more obs for
  stability (Lo 1991).
- refit = weekly (step=5) - DFA is expensive (O(N log N)), daily refit
  would balloon runtime.
- forecast = HurstForecast (regime label) instead of vol estimate.
- weight = regime_to_weight(regime).shift(1) - binary long/flat overlay.
- costs = fees + slippage (Annexe A.3 harmonisation, contract section 3).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from src.hurst_model import compute_hurst, regime_to_weight

DEFAULT_TRAIN_WINDOW = 504
"""Walk-forward training window (~2 trading years). CONTRAT section 1."""

DEFAULT_REFIT_STEP = 5
"""Refit every 5 trading days (weekly). CONTRAT section 1."""

DEFAULT_FEES_BPS = 1.0
"""Fees per side in bps (0.01%). CONTRAT section 3 (Annexe A.3 harmonisation)."""

DEFAULT_SLIPPAGE_BPS = 5.0
"""Slippage per side in bps (0.05%). CONTRAT section 3 (Annexe A.3)."""


@dataclass(frozen=True)
class HurstBacktestConfig:
    """Strategy parameters (immutable per run)."""

    train_window: int = DEFAULT_TRAIN_WINDOW
    refit_step: int = DEFAULT_REFIT_STEP
    fees_bps: float = DEFAULT_FEES_BPS
    slippage_bps: float = DEFAULT_SLIPPAGE_BPS


def walk_forward_hurst(
    returns_pct: pd.Series,
    config: HurstBacktestConfig | None = None,
) -> pd.DataFrame:
    """Run a walk-forward Hurst-DFA classification on a daily return series.

    For each t in [train_window, n) where (t - train_window) % refit_step == 0:
        train = returns_pct.iloc[t - train_window : t]   # STRICT EXCLUSIVE on t
        h, regime = compute_hurst(train)
    Between refits, regime/h are forward-filled (CONTRAT: refit hebdo).

    Args:
        returns_pct: pd.Series of returns in % (same convention as Phase 1).
        config: optional HurstBacktestConfig (defaults: 504 / 5 / 1bps / 5bps).

    Returns:
        DataFrame indexed by forecast date with columns:
          - h_value (float)
          - regime  (str)
          - hurst_converged (bool)
          - refit_today (bool) - True if this row triggered a fresh DFA.
    """
    cfg = config or HurstBacktestConfig()
    n = len(returns_pct)
    if n <= cfg.train_window:
        raise ValueError(
            f"Series too short: {n} <= train_window={cfg.train_window}"
        )

    idx = returns_pct.index
    h_values: list[float] = []
    regimes: list[str] = []
    converged: list[bool] = []
    refit_today: list[bool] = []
    forecast_idx: list[pd.Timestamp] = []

    # Last-known forecast (carried forward between refits)
    last_h = 0.5
    last_regime = "random"
    last_converged = False

    for t in range(cfg.train_window, n):
        steps_since_start = t - cfg.train_window
        is_refit_day = (steps_since_start % cfg.refit_step) == 0
        if is_refit_day:
            train_slice = returns_pct.iloc[t - cfg.train_window : t]
            # Anti look-ahead invariant (also asserted in tests)
            assert train_slice.index.max() < idx[t], "look-ahead bias detected"
            fc = compute_hurst(train_slice)
            last_h = fc.h_value
            last_regime = fc.regime
            last_converged = fc.converged
        h_values.append(last_h)
        regimes.append(last_regime)
        converged.append(last_converged)
        refit_today.append(is_refit_day)
        forecast_idx.append(idx[t])

    forecasts = pd.DataFrame(
        {
            "h_value": h_values,
            "regime": regimes,
            "hurst_converged": converged,
            "refit_today": refit_today,
        },
        index=pd.DatetimeIndex(forecast_idx, name="date"),
    )
    return forecasts


def compute_pnl_hurst(
    returns_pct: pd.Series,
    forecasts: pd.DataFrame,
    config: HurstBacktestConfig | None = None,
) -> pd.DataFrame:
    """Compute Hurst overlay PnL vs buy-and-hold.

    Cost model (CONTRAT section 3 / Annexe A.3):
        cost_per_unit_turnover = (fees_bps + slippage_bps) / 1e4   (per side)

    Strategy weights:
        target_weight_t = regime_to_weight(regime_t)
        weight_t = target_weight_t.shift(1)   # anti look-ahead (T1 invariant)

    Columns returned:
        ret_decimal      : daily return as decimal
        target_weight    : long/flat target (regime-based)
        weight           : .shift(1) applied target
        ret_strategy     : weight * ret_decimal (gross)
        turnover         : |weight.diff()|
        cost             : turnover * (fees_bps + slippage_bps) / 1e4
        ret_strategy_net : ret_strategy - cost
        ret_bh           : ret_decimal (buy & hold reference)
    """
    cfg = config or HurstBacktestConfig()

    aligned = forecasts.join(returns_pct.rename("ret_pct"), how="inner")
    aligned["ret_decimal"] = aligned["ret_pct"] / 100.0

    target = aligned["regime"].map(regime_to_weight).astype(float)
    target.name = "target_weight"
    aligned["target_weight"] = target

    # CRITIQUE anti-lookahead: signal decided at t applied at t+1
    aligned["weight"] = aligned["target_weight"].shift(1)

    aligned["ret_strategy"] = aligned["weight"] * aligned["ret_decimal"]
    aligned["turnover"] = aligned["weight"].diff().abs().fillna(0.0)
    total_cost_bps = cfg.fees_bps + cfg.slippage_bps
    aligned["cost"] = aligned["turnover"] * total_cost_bps / 1e4
    aligned["ret_strategy_net"] = aligned["ret_strategy"] - aligned["cost"]
    aligned["ret_bh"] = aligned["ret_decimal"]

    # Drop the unavoidable first NaN row from shift(1)
    aligned = aligned.dropna(subset=["weight"])
    return aligned


def realized_vol(returns_pct: pd.Series, window: int = 21) -> pd.Series:
    """Rolling realised vol annualised (decimal). Mirror Phase 1 helper."""
    return returns_pct.rolling(window).std() * np.sqrt(252) / 100.0
