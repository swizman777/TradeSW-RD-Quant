"""Run the Phase 2.A Hurst walk-forward backtest end-to-end.

Usage:
    python scripts/run_hurst_backtest.py

Output:
    reports/backtest_results_hurst.parquet
    reports/verdict_hurst.md
    reports/equity_curve_hurst.png
    reports/regime_timeline.png
    reports/bootstrap_sharpe_ci.png

Mandate Chef Swizman 2026-06-10 (CONTRAT_CODEX_PHASE2A_HURST.md).
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.hurst_backtest import (
    HurstBacktestConfig,
    compute_pnl_hurst,
    realized_vol,
    walk_forward_hurst,
)
from src.hurst_reporting import REPORTS_DIR, generate_verdict_hurst
from src.ingestion import fetch_sp500_daily


def main() -> None:
    print("[1/4] Fetching S&P 500 daily (cache parquet, shared with Phase 1)...")
    df = fetch_sp500_daily()
    returns_pct: pd.Series = df["return"]
    print(
        f"      Rows: {len(returns_pct)}  Range: "
        f"{returns_pct.index.min().date()} -> {returns_pct.index.max().date()}"
    )

    print("[2/4] Walk-forward Hurst DFA (window=504, refit=5)...")
    cfg = HurstBacktestConfig()
    forecasts = walk_forward_hurst(returns_pct, cfg)
    print(
        f"      Forecasts: {len(forecasts)}  Convergence rate: "
        f"{forecasts['hurst_converged'].mean():.2%}  "
        f"Refits: {int(forecasts['refit_today'].sum())}"
    )

    print("[3/4] Computing PnL with shift(1) and fees+slippage...")
    pnl_df = compute_pnl_hurst(returns_pct, forecasts, cfg)
    pnl_df["realized_vol_21d"] = realized_vol(returns_pct).reindex(pnl_df.index)

    out_path: Path = REPORTS_DIR / "backtest_results_hurst.parquet"
    pnl_df.to_parquet(out_path)
    print(f"      Saved {out_path}")

    print("[4/4] Generating verdict_hurst + charts...")
    generate_verdict_hurst()
    print(f"      Verdict: {REPORTS_DIR / 'verdict_hurst.md'}")


if __name__ == "__main__":
    main()
