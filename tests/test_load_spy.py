"""Ingestion contract — uses a local fixture to avoid network calls in CI.

The real fetch_sp500_daily is tested manually by Chef via `make refresh-data`.
This test verifies the cache-read code path against a small mock parquet.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from src import ingestion


def test_cache_read_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """If cache exists, fetch_sp500_daily must read it without network."""
    fake_data = pd.DataFrame(
        {
            "open": np.linspace(100, 110, 10),
            "high": np.linspace(101, 111, 10),
            "low": np.linspace(99, 109, 10),
            "close": np.linspace(100, 110, 10),
            "volume": np.full(10, 1_000_000),
            "return": np.linspace(-0.5, 0.5, 10),
        },
        index=pd.date_range("2024-01-02", periods=10, freq="B"),
    )
    fake_data.index.name = "date"

    monkeypatch.setattr(ingestion, "DATA_DIR", tmp_path)
    cache_path = tmp_path / "GSPC_2019-01-01_2024-12-31.parquet"
    fake_data.to_parquet(cache_path)

    out = ingestion.fetch_sp500_daily()
    assert len(out) == 10
    assert "return" in out.columns


def test_cache_sha256_deterministic(tmp_path: Path) -> None:
    p = tmp_path / "x.bin"
    p.write_bytes(b"hello world")
    h1 = ingestion.cache_sha256(p)
    h2 = ingestion.cache_sha256(p)
    assert h1 == h2
    assert len(h1) == 64  # sha256 hex
