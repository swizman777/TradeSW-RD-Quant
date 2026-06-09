"""S&P 500 daily ingestion via yfinance with local parquet cache.

Contract section 3.1: tz_localize(None) -> all UTC naive.
Contract section 7: cache parquet OBLIGATOIRE, 1 download initial.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_TICKER = "^GSPC"
DEFAULT_START = "2019-01-01"
DEFAULT_END = "2024-12-31"


def fetch_sp500_daily(
    ticker: str = DEFAULT_TICKER,
    start: str = DEFAULT_START,
    end: str = DEFAULT_END,
    force_refresh: bool = False,
) -> pd.DataFrame:
    """Fetch S&P 500 daily OHLCV via yfinance, cache to parquet.

    Returns columns: open, high, low, close, volume, return (log return %).
    """
    cache_path = DATA_DIR / f"{ticker.replace('^', '')}_{start}_{end}.parquet"
    if cache_path.exists() and not force_refresh:
        df = pd.read_parquet(cache_path)
        return df

    import yfinance as yf  # noqa: PLC0415  # lazy import to avoid network on test collect

    raw = yf.download(ticker, start=start, end=end, progress=False, auto_adjust=False)
    if raw is None or raw.empty:
        raise RuntimeError(f"yfinance returned empty for {ticker} [{start}..{end}]")

    # Flatten MultiIndex columns if present (yfinance >=0.2.40 behaviour)
    if isinstance(raw.columns, pd.MultiIndex):
        raw.columns = [c[0] for c in raw.columns]

    df = raw.rename(
        columns={
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Adj Close": "adj_close",
            "Volume": "volume",
        }
    )
    df.index = pd.DatetimeIndex(df.index).tz_localize(None)
    df.index.name = "date"

    # Log returns in % (contract 3.2 — stability for arch library)
    import numpy as np  # noqa: PLC0415

    df["return"] = np.log(df["close"] / df["close"].shift(1)) * 100.0
    df = df.dropna(subset=["return"])

    df.to_parquet(cache_path)
    return df


def cache_sha256(path: Path) -> str:
    """SHA256 hex digest of a cached parquet (for README provenance)."""
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()
