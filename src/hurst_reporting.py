"""Phase 2.A Hurst reporting: verdict_hurst.md + charts.

Mandate Chef Swizman 2026-06-10 (CONTRAT_CODEX_PHASE2A_HURST.md).

Sections obligatoires du verdict (CONTRAT section 7) :
  1. Hypothese economique (verbatim section 0)
  2. Configuration backtest
  3. Metriques full period + 2 sous-periodes (5 metriques)
  4. Decision binaire : GO_PHASE_2B / STOP_LEARNING_HURST /
     KILL_FAMILY_ECONOPHYSIQUE
  5. Comparaison vs GARCH baseline Phase 1 (Sharpe spread +0.181 STOP_LEARNING)
  6. Charts : equity overlay vs B&H + regime timeline + bootstrap CI Sharpe

Bonferroni multi-tests (CONTRAT section 3) :
  - Sharpe spread requis = +0.45 (HARDCODE ci-dessous).
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

from src.hurst_metrics import summarise_hurst  # noqa: E402

REPORTS_DIR = Path(__file__).resolve().parent.parent / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# CONTRAT section 3 - Bonferroni hardcode
SHARPE_SPREAD_THRESHOLD_BONFERRONI = 0.45
GARCH_BASELINE_SHARPE_SPREAD = 0.181  # Phase 1 STOP_LEARNING reference


def _decision_from_summary(summary: dict[str, float]) -> str:
    """Apply Bonferroni Sharpe spread threshold (+0.45) on full-period summary."""
    spread = summary.get("sharpe_spread", float("nan"))
    if not (spread == spread):  # NaN check (no math import needed)
        return "STOP_LEARNING_HURST"
    if spread >= SHARPE_SPREAD_THRESHOLD_BONFERRONI:
        return "GO_PHASE_2B"
    if spread >= 0.0:
        return "STOP_LEARNING_HURST"
    return "KILL_FAMILY_ECONOPHYSIQUE"


def _format_metric_table(s: dict[str, float]) -> str:
    return (
        "| Metric | Value |\n"
        "|---|---|\n"
        f"| Sharpe net | {s['sharpe_net']:.3f} |\n"
        f"| Sharpe B&H | {s['sharpe_bh']:.3f} |\n"
        f"| Sharpe spread (Bonferroni >= +0.45) | {s['sharpe_spread']:.3f} |\n"
        f"| Information Coefficient | {s['ic']:.4f} |\n"
        f"| AIC | {s['aic']:.1f} |\n"
        f"| Diebold-Mariano stat | {s['dm_stat']:.3f} |\n"
        f"| DM p-value (two-sided) | {s['dm_pvalue']:.4f} |\n"
        f"| Sharpe bootstrap 95% CI | [{s['sharpe_boot_lo']:.3f}, {s['sharpe_boot_hi']:.3f}] |\n"
        f"| IC bootstrap 95% CI | [{s['ic_boot_lo']:.4g}, {s['ic_boot_hi']:.4g}] |\n"
    )


def write_verdict_hurst(
    summary_full: dict[str, float],
    summary_19_21: dict[str, float],
    summary_22_24: dict[str, float],
    path: Path,
) -> None:
    """Write the verdict_hurst.md (CONTRAT section 7 template)."""
    decision = _decision_from_summary(summary_full)
    spread = summary_full["sharpe_spread"]
    vs_garch = spread - GARCH_BASELINE_SHARPE_SPREAD

    lines = [
        "# Verdict Phase 2.A Hurst (DFA flat)",
        "",
        f"**Decision binaire** : `{decision}`",
        f"**Sharpe spread vs GARCH baseline** (Phase 1 STOP_LEARNING) : "
        f"{vs_garch:+.3f} (Hurst {spread:+.3f} - GARCH {GARCH_BASELINE_SHARPE_SPREAD:+.3f})",
        "",
        "## 1. Hypothese economique (verbatim CONTRAT section 0)",
        "",
        "> Pourquoi le marche laisserait cet edge sur la table en 2026 ?",
        "> Quel hedge fund teste/utilise ce modele aujourd'hui ?",
        "",
        "Reponse honnete :",
        "- Hurst exponent (Mandelbrot 1972) est mature et public. Tous les hedge "
        "funds quant l'ont teste en alpha direct -> edge alpha direct probablement "
        "arbitre.",
        "- Lo (1991) 'Long-term memory in stock market prices' a montre que beaucoup "
        "d'estimations Hurst etaient biaisees sur petits echantillons -> besoin "
        "DFA/R/S robustes.",
        "- L'usage actuel buy-side : filtre de regime, pas signal alpha direct "
        "(H > 0.55 -> momentum-favorable, H < 0.45 -> mean-rev favorable).",
        "- Edge espere 2026 : MARGINAL en stand-alone, mais possiblement detectable "
        "comme overlay binaire vol-targeted sur S&P 500 daily.",
        "",
        "## 2. Configuration backtest",
        "",
        "- Univers : S&P 500 (^GSPC) daily",
        "- Periode : 2019-01-01 -> 2024-12-31 (5 ans)",
        "- Walk-forward window : 504 jours (~2 ans)",
        "- Refit : hebdomadaire (step=5)",
        "- Strategie : overlay binaire long si Hurst > 0.55, flat sinon "
        "(pas de short Phase 2.A)",
        "- Couts : fees 1bps + slippage 5bps par cote (Annexe A.3 harmonisation)",
        "- Library : nolds.dfa() (Detrended Fluctuation Analysis)",
        "",
        "## 3. Metriques harmonisees (5 obligatoires Annexe A.3)",
        "",
        "### Full period 2019-2024",
        _format_metric_table(summary_full),
        "",
        "### Sous-periode A 2019-2021",
        _format_metric_table(summary_19_21),
        "",
        "### Sous-periode B 2022-2024",
        _format_metric_table(summary_22_24),
        "",
        "## 4. Decision binaire (Bonferroni)",
        "",
        f"- Seuil Sharpe spread Bonferroni : +{SHARPE_SPREAD_THRESHOLD_BONFERRONI:.2f}",
        f"- Sharpe spread observe (full) : {spread:+.3f}",
        f"- Verdict : `{decision}`",
        "",
        "## 5. Comparaison vs GARCH baseline Phase 1",
        "",
        f"- GARCH Phase 1 : Sharpe spread = +{GARCH_BASELINE_SHARPE_SPREAD:.3f} "
        "(STOP_LEARNING)",
        f"- Hurst Phase 2.A : Sharpe spread = {spread:+.3f}",
        f"- Difference : {vs_garch:+.3f}",
        "",
        "## 6. Charts produits",
        "",
        "- `equity_curve_hurst.png` : equity overlay net vs B&H",
        "- `regime_timeline.png` : timeline regime + Hurst exponent",
        "- `bootstrap_sharpe_ci.png` : histogramme bootstrap Sharpe + CI 95%",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def plot_equity_hurst(df: pd.DataFrame, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(11, 5))
    (1 + df["ret_strategy_net"]).cumprod().plot(ax=ax, label="Hurst overlay (net)")
    (1 + df["ret_bh"]).cumprod().plot(ax=ax, label="Buy & Hold")
    ax.set_title("Equity Curve - Hurst DFA flat overlay vs B&H")
    ax.set_ylabel("Cumulative growth (start = 1.0)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)


def plot_regime_timeline(df: pd.DataFrame, path: Path) -> None:
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 7), sharex=True)
    df["h_value"].plot(ax=ax1, label="Hurst (DFA alpha)")
    ax1.axhline(0.55, color="green", linestyle="--", alpha=0.5, label="0.55 momentum")
    ax1.axhline(0.45, color="red", linestyle="--", alpha=0.5, label="0.45 mean-rev")
    ax1.set_ylabel("Hurst exponent")
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    code = df["regime"].map({"momentum": 1, "random": 0, "mean_rev": -1}).astype(float)
    code.plot(ax=ax2, label="Regime code", drawstyle="steps-post")
    ax2.set_ylabel("-1=mean_rev 0=random 1=momentum")
    ax2.grid(True, alpha=0.3)
    fig.suptitle("Hurst regime timeline")
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)


def plot_bootstrap_sharpe(df: pd.DataFrame, path: Path) -> None:
    """Bootstrap distribution of Sharpe (reproducible seed=42)."""
    import numpy as np  # noqa: PLC0415

    r = df["ret_strategy_net"].dropna().values
    if len(r) < 50:
        return
    rng = np.random.default_rng(42)
    n_boot = 1000
    stats = np.empty(n_boot, dtype=float)
    for i in range(n_boot):
        sample = rng.choice(r, size=len(r), replace=True)
        std = sample.std(ddof=1)
        stats[i] = sample.mean() / std * np.sqrt(252) if std > 1e-12 else np.nan
    stats = stats[np.isfinite(stats)]
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.hist(stats, bins=40, alpha=0.7)
    lo, hi = np.quantile(stats, [0.025, 0.975])
    ax.axvline(float(lo), color="red", linestyle="--", label=f"2.5% = {lo:.2f}")
    ax.axvline(float(hi), color="red", linestyle="--", label=f"97.5% = {hi:.2f}")
    ax.set_title("Bootstrap Sharpe distribution (1000x, seed=42)")
    ax.set_xlabel("Annualised Sharpe")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)


def generate_verdict_hurst() -> None:
    """Entrypoint after `scripts/run_hurst_backtest.py` saved parquet."""
    results_path = REPORTS_DIR / "backtest_results_hurst.parquet"
    if not results_path.exists():
        raise FileNotFoundError(
            f"Run `make backtest_hurst` first; missing {results_path}"
        )
    df = pd.read_parquet(results_path)
    summary_full = summarise_hurst(df)
    mask_a = df.index < "2022-01-01"
    mask_b = df.index >= "2022-01-01"
    summary_a = summarise_hurst(df.loc[mask_a])
    summary_b = summarise_hurst(df.loc[mask_b])
    write_verdict_hurst(
        summary_full, summary_a, summary_b, REPORTS_DIR / "verdict_hurst.md"
    )
    plot_equity_hurst(df, REPORTS_DIR / "equity_curve_hurst.png")
    plot_regime_timeline(df, REPORTS_DIR / "regime_timeline.png")
    plot_bootstrap_sharpe(df, REPORTS_DIR / "bootstrap_sharpe_ci.png")
