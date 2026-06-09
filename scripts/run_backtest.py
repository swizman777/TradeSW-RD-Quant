"""Run the full Phase 1 GARCH walk-forward backtest end-to-end.

Usage:
    python scripts/run_backtest.py

Output:
    reports/backtest_results.parquet
    reports/verdict.md
    reports/equity_curve.png
    reports/vol_pred_vs_realized.png
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.backtest_engine import BacktestConfig, compute_pnl, realized_vol, walk_forward
from src.ingestion import fetch_sp500_daily
from src.reporting import REPORTS_DIR, generate_verdict


def main() -> None:
    print("[1/4] Fetching S&P 500 daily (cache parquet)…")
    df = fetch_sp500_daily()
    returns_pct: pd.Series = df["return"]
    print(f"      Rows: {len(returns_pct)}  Range: {returns_pct.index.min().date()} → {returns_pct.index.max().date()}")

    print("[2/4] Walk-forward GARCH(1,1)…")
    cfg = BacktestConfig()
    forecasts = walk_forward(returns_pct, cfg)
    print(f"      Forecasts: {len(forecasts)}  Convergence rate: {forecasts['garch_converged'].mean():.2%}")

    print("[3/4] Computing PnL with shift(1) and fees…")
    pnl_df = compute_pnl(returns_pct, forecasts, cfg)
    pnl_df["realized_vol_21d"] = realized_vol(returns_pct).reindex(pnl_df.index)

    out_path: Path = REPORTS_DIR / "backtest_results.parquet"
    pnl_df.to_parquet(out_path)
    print(f"      Saved {out_path}")

    print("[4/4] Generating verdict + charts…")
    generate_verdict()
    print(f"      Verdict: {REPORTS_DIR / 'verdict.md'}")


if __name__ == "__main__":
    main()
