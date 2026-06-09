"""Volatility-targeting position sizing.

Contract section 3.1:
- position = sizing.shift(1) OBLIGATOIRE (sizing known at t, applied at t+1)

Contract section 3.3:
- Target vol: 10% annualised
"""

from __future__ import annotations

import numpy as np
import pandas as pd

DEFAULT_VOL_TARGET = 0.10  # 10% annualised (contract section 1)
MAX_LEVERAGE = 1.0  # long-only overlay, no leverage Phase 1
MIN_LEVERAGE = 0.0


def compute_position_size(
    predicted_vol_annualised: pd.Series,
    target_vol: float = DEFAULT_VOL_TARGET,
    max_leverage: float = MAX_LEVERAGE,
    min_leverage: float = MIN_LEVERAGE,
) -> pd.Series:
    """Compute target weights from predicted vol.

    weight_t = clip(target_vol / predicted_vol_t, min, max), THEN shift(1)
    so weight applied at t was decided strictly before t.

    Args:
        predicted_vol_annualised: pd.Series indexed by date; one-step-ahead
            forecast PRODUCED at t (i.e. decided using data up to t-1).
        target_vol: annualised vol target (decimal).
        max_leverage: cap (1.0 = no leverage Phase 1).
        min_leverage: floor (0.0 = no short).

    Returns:
        pd.Series of weights, same index, with .shift(1) applied (first row NaN).
    """
    if (predicted_vol_annualised <= 0).any():
        # arch fit can occasionally produce zero on degenerate windows
        predicted_vol_annualised = predicted_vol_annualised.replace(0, np.nan).ffill()

    raw_weight = target_vol / predicted_vol_annualised
    clipped = raw_weight.clip(lower=min_leverage, upper=max_leverage)

    # CRITIQUE: shift(1) - signal decided at t is APPLIED at t+1
    weights = clipped.shift(1)
    weights.name = "weight"
    return weights
