"""Reporting: charts (matplotlib) + verdict markdown.

Contract section 4 + 5:
- 4 critères cumulatifs (Sharpe spread, DD ratio, RMSE vs std, hit rate)
- Validation 2 sous-périodes 2019-2021 + 2022-2024
- Critère arrêt T3 Senior par seuils Sharpe overlay
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

from src.metrics import summarise  # noqa: E402

REPORTS_DIR = Path(__file__).resolve().parent.parent / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def _verdict_from_sharpe_overlay(sharpe_overlay: float, sharpe_bh: float) -> str:
    """Critère arrêt T3 Senior (contract section 5)."""
    spread = sharpe_overlay - sharpe_bh
    if spread < 0.1:
        return "STOP_DEFINITIVE"
    if spread < 0.2:
        return "STOP_LEARNING"
    if spread < 0.3:
        return "HOLD_AUDIT"
    return "GO_PHASE_2_ACO"


def _check_4_criteria(summary: dict[str, float]) -> dict[str, bool]:
    """Contract section 4 — 4 cumulative success conditions."""
    return {
        "sharpe_spread_ge_03": (summary["sharpe_overlay"] - summary["sharpe_bh"]) >= 0.3,
        "max_dd_ratio_le_08": (
            abs(summary["max_dd_overlay"]) <= 0.8 * abs(summary["max_dd_bh"])
            if summary["max_dd_bh"] != 0
            else False
        ),
        "rmse_lt_std_realized": summary["rmse_vol"] < summary["std_realized_vol"],
        "hit_rate_gt_55": summary["hit_rate_vol"] > 0.55,
    }


def plot_equity(df: pd.DataFrame, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(11, 5))
    (1 + df["ret_strategy_net"]).cumprod().plot(ax=ax, label="GARCH overlay (net)")
    (1 + df["ret_bh"]).cumprod().plot(ax=ax, label="Buy & Hold")
    ax.set_title("Equity Curve — GARCH(1,1) vol-targeted overlay vs B&H")
    ax.set_ylabel("Cumulative growth (start = 1.0)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)


def plot_vol_pred_vs_realized(
    predicted: pd.Series, realized: pd.Series, path: Path
) -> None:
    fig, ax = plt.subplots(figsize=(11, 5))
    predicted.plot(ax=ax, label="Predicted vol (GARCH)", alpha=0.8)
    realized.plot(ax=ax, label="Realized vol (21d)", alpha=0.8)
    ax.set_title("Predicted vs Realized Volatility (annualised, decimal)")
    ax.set_ylabel("Vol")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)


def write_verdict_markdown(
    summary_full: dict[str, float],
    summary_19_21: dict[str, float],
    summary_22_24: dict[str, float],
    path: Path,
) -> None:
    crit_full = _check_4_criteria(summary_full)
    crit_a = _check_4_criteria(summary_19_21)
    crit_b = _check_4_criteria(summary_22_24)
    n_pass_a = sum(crit_a.values())
    n_pass_b = sum(crit_b.values())

    sub_periods_pass = int(all(crit_a.values())) + int(all(crit_b.values()))
    if sub_periods_pass == 2:
        global_decision = "GO_PHASE_2_ACO"
    elif sub_periods_pass == 1:
        global_decision = "REVIEW_CHEF"
    else:
        global_decision = "STOP"

    t3_decision = _verdict_from_sharpe_overlay(
        summary_full["sharpe_overlay"], summary_full["sharpe_bh"]
    )

    lines = [
        "# Verdict Phase 1 GARCH(1,1)",
        "",
        f"**Decision globale (4 criteres x 2 sous-periodes)** : `{global_decision}`",
        f"**Decision T3 Senior (Sharpe spread)** : `{t3_decision}`",
        "",
        "## Resume full period 2019-2024",
        _format_summary_table(summary_full, crit_full),
        "",
        f"## Sous-periode A 2019-2021 ({n_pass_a}/4 criteres)",
        _format_summary_table(summary_19_21, crit_a),
        "",
        f"## Sous-periode B 2022-2024 ({n_pass_b}/4 criteres)",
        _format_summary_table(summary_22_24, crit_b),
        "",
        "## Recommandation",
        _recommendation_text(global_decision, t3_decision),
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def _format_summary_table(s: dict[str, float], c: dict[str, bool]) -> str:
    return (
        "| Metric | Value | Pass |\n"
        "|---|---|---|\n"
        f"| Sharpe overlay | {s['sharpe_overlay']:.3f} | — |\n"
        f"| Sharpe B&H | {s['sharpe_bh']:.3f} | — |\n"
        f"| Sharpe spread (>= 0.30) | {s['sharpe_overlay'] - s['sharpe_bh']:.3f} | {c['sharpe_spread_ge_03']} |\n"
        f"| Max DD overlay | {s['max_dd_overlay']:.3f} | — |\n"
        f"| Max DD B&H | {s['max_dd_bh']:.3f} | — |\n"
        f"| DD ratio (<= 0.80) | {(abs(s['max_dd_overlay']) / abs(s['max_dd_bh'])) if s['max_dd_bh'] else float('nan'):.3f} | {c['max_dd_ratio_le_08']} |\n"
        f"| RMSE vol | {s['rmse_vol']:.4f} | {c['rmse_lt_std_realized']} |\n"
        f"| std(realised vol) | {s['std_realized_vol']:.4f} | — |\n"
        f"| Hit rate dir vol (> 55%) | {s['hit_rate_vol']:.3f} | {c['hit_rate_gt_55']} |\n"
    )


def _recommendation_text(global_decision: str, t3_decision: str) -> str:
    msgs = {
        "GO_PHASE_2_ACO": "Tous criteres passes 2/2 sous-periodes. Proceder Phase 2 ACO sous audit Chef.",
        "REVIEW_CHEF": "1/2 sous-periode passe. REVIEW Chef avant decision binaire.",
        "STOP": "0/2 sous-periode passe. STOP Phase 1, documenter apprentissage.",
        "STOP_DEFINITIVE": "Sharpe spread < 0.1. STOP DEFINITIF, repo archive.",
        "STOP_LEARNING": "Sharpe spread 0.1-0.2. STOP apprentissage, documenter.",
        "HOLD_AUDIT": "Sharpe spread 0.2-0.3. HOLD, audit externe Gemini avant ACO.",
    }
    return f"- Decision globale : {msgs.get(global_decision, '?')}\n- Decision T3 : {msgs.get(t3_decision, '?')}"


def generate_verdict() -> None:
    """Entrypoint Makefile `make report` — assumes backtest results saved."""
    results_path = REPORTS_DIR / "backtest_results.parquet"
    if not results_path.exists():
        raise FileNotFoundError(f"Run `make backtest` first; missing {results_path}")
    df = pd.read_parquet(results_path)
    realized = df["realized_vol_21d"]
    predicted = df["pred_vol_annual"]
    summary_full = summarise(df["ret_strategy_net"], df["ret_bh"], realized, predicted)
    mask_a = df.index < "2022-01-01"
    mask_b = df.index >= "2022-01-01"
    summary_a = summarise(
        df.loc[mask_a, "ret_strategy_net"],
        df.loc[mask_a, "ret_bh"],
        realized.loc[mask_a],
        predicted.loc[mask_a],
    )
    summary_b = summarise(
        df.loc[mask_b, "ret_strategy_net"],
        df.loc[mask_b, "ret_bh"],
        realized.loc[mask_b],
        predicted.loc[mask_b],
    )
    write_verdict_markdown(summary_full, summary_a, summary_b, REPORTS_DIR / "verdict.md")
    plot_equity(df, REPORTS_DIR / "equity_curve.png")
    plot_vol_pred_vs_realized(predicted, realized, REPORTS_DIR / "vol_pred_vs_realized.png")
