"""Force re-download S&P 500 daily and refresh parquet cache.

Usage:
    python scripts/refresh_data.py
"""

from __future__ import annotations

from src.ingestion import DATA_DIR, cache_sha256, fetch_sp500_daily


def main() -> None:
    df = fetch_sp500_daily(force_refresh=True)
    print(f"Rows: {len(df)}  Range: {df.index.min().date()} → {df.index.max().date()}")
    for f in DATA_DIR.glob("*.parquet"):
        print(f"  {f.name}  SHA256={cache_sha256(f)}")


if __name__ == "__main__":
    main()
