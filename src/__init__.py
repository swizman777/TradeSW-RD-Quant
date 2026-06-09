"""TradeSW R&D Quant — Phase 1 GARCH(1,1) overlay backtest on S&P 500.

Mandate: Chef Swizman 2026-06-09 (validation 3T)
Deadline: 2026-07-10 (J+30)
Budget: 40h max cumulative

REPO ISOLE: aucun import depuis TradeSW autorise.
"""

from __future__ import annotations

import random

import numpy as np

# Reproducibility (contract section 3.5)
SEED = 42
random.seed(SEED)
np.random.seed(SEED)

__version__ = "0.1.0"
