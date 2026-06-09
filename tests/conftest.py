"""Shared fixtures: synthetic return series so tests run offline."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

RNG_SEED = 42


@pytest.fixture
def synthetic_returns_pct() -> pd.Series:
    """500 days of synthetic GARCH-like returns in %, seed=42, vol clustering."""
    rng = np.random.default_rng(RNG_SEED)
    n = 500
    eps = rng.standard_normal(n)
    sigma = np.empty(n)
    sigma[0] = 1.0
    omega, alpha, beta = 0.05, 0.10, 0.85
    r = np.empty(n)
    for t in range(n):
        if t > 0:
            sigma[t] = np.sqrt(omega + alpha * r[t - 1] ** 2 + beta * sigma[t - 1] ** 2)
        r[t] = sigma[t] * eps[t]
    idx = pd.date_range("2020-01-02", periods=n, freq="B")
    return pd.Series(r, index=idx, name="return")


@pytest.fixture
def constant_returns_pct() -> pd.Series:
    """Constant positive return series for Sharpe edge-case tests."""
    idx = pd.date_range("2020-01-02", periods=100, freq="B")
    return pd.Series(0.05, index=idx, name="return")
