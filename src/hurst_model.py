"""Hurst exponent estimator via Detrended Fluctuation Analysis (DFA).

Phase 2.A - mandate Chef Swizman 2026-06-10 (CONTRAT_CODEX_PHASE2A_HURST.md).
Mode FLAT (Plan C consensus 3T) : pas de refactor BaseForecaster, fichier
autonome distinct de la baseline Phase 1 GARCH.

Hypothese economique obligatoire (CONTRAT section 0, verbatim Annexe A.5)
-----------------------------------------------------------------------
"Pourquoi le marche laisserait cet edge sur la table en 2026 ? Quel hedge
fund teste/utilise ce modele aujourd'hui ?"

Reponse honnete :
- Hurst exponent (Mandelbrot 1972) est mature et public. Tous les hedge
  funds quant l'ont teste en alpha direct -> edge alpha direct probablement
  arbitre.
- Lo (1991) "Long-term memory in stock market prices" a montre que beaucoup
  d'estimations Hurst etaient biaisees sur petits echantillons -> besoin
  DFA/R/S robustes.
- L'usage actuel buy-side : filtre de regime, pas signal alpha direct
  (H > 0.55 -> momentum-favorable, H < 0.45 -> mean-rev favorable,
  conditionne d'autres signaux).
- Edge espere 2026 : MARGINAL en stand-alone, mais possiblement detectable
  comme overlay binaire vol-targeted (long/flat selon regime Hurst) sur
  S&P 500 daily.

Implementation
--------------
- Library : nolds.dfa() (Detrended Fluctuation Analysis)
- Anti look-ahead : la fenetre passee en entree DOIT etre strict-exclusive
  sur la date predite (responsabilite de l'appelant via
  `train.iloc[t-504:t]`).
- Fallback : si nolds leve ou si fenetre < 200 obs, on retourne
  `HurstForecast(h_value=0.5, regime="random", converged=False)` (neutre,
  ne genere pas de signal).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

MIN_WINDOW = 200
"""Minimum number of observations for DFA to be considered reliable.

Lo (1991) shows DFA on <200 obs is heavily biased. Below this, the
fallback returns h=0.5 (random) with converged=False to avoid spurious
signals.
"""

H_MOMENTUM_THRESHOLD = 0.55
"""Hurst > 0.55 => persistent / trending regime => "momentum" label."""

H_MEAN_REV_THRESHOLD = 0.45
"""Hurst < 0.45 => anti-persistent / mean-reverting regime => "mean_rev" label."""


@dataclass(frozen=True)
class HurstForecast:
    """One-step-ahead Hurst-based regime classification.

    Attributes:
        h_value: Hurst exponent estimate in approximately [0, 1].
            0.5 = random walk, >0.55 = trending, <0.45 = mean-reverting.
        regime: classification label "momentum"|"mean_rev"|"random".
        converged: True if nolds.dfa() produced a finite estimate on a
            window of length >= MIN_WINDOW, False if the fallback fired.
    """

    h_value: float
    regime: str
    converged: bool


def _classify_regime(h: float) -> str:
    """Map a Hurst estimate to a regime label."""
    if not np.isfinite(h):
        return "random"
    if h > H_MOMENTUM_THRESHOLD:
        return "momentum"
    if h < H_MEAN_REV_THRESHOLD:
        return "mean_rev"
    return "random"


def compute_hurst(returns_window: pd.Series) -> HurstForecast:
    """Estimate the Hurst exponent on a window of returns via DFA.

    Anti look-ahead invariant (caller responsibility): ``returns_window``
    MUST be strict-exclusive on the forecast date ``t`` (typically
    ``returns.iloc[t-504:t]``).

    Args:
        returns_window: pd.Series of returns (decimal or % - DFA is
            scale-invariant on the integrated signal). Length should be
            >= MIN_WINDOW (200) for the estimate to be meaningful.

    Returns:
        HurstForecast with the DFA alpha (float), regime label, and a
        convergence flag. On any internal failure (nolds error, NaN
        cascade, too-short window) returns the neutral fallback
        ``HurstForecast(0.5, "random", False)``.
    """
    cleaned = returns_window.dropna()
    if len(cleaned) < MIN_WINDOW:
        return HurstForecast(h_value=0.5, regime="random", converged=False)

    try:
        import nolds  # noqa: PLC0415  # lazy import (heavy + optional in CI)

        h = float(nolds.dfa(cleaned.values))
    except Exception:  # noqa: BLE001 - any nolds internal failure -> fallback
        return HurstForecast(h_value=0.5, regime="random", converged=False)

    if not np.isfinite(h):
        return HurstForecast(h_value=0.5, regime="random", converged=False)

    return HurstForecast(
        h_value=h,
        regime=_classify_regime(h),
        converged=True,
    )


def regime_to_weight(regime: str) -> float:
    """Map a regime label to a strategy weight (Phase 2.A overlay binaire).

    CONTRAT section 5 (FLAT, no short Phase 2.A):
      - "momentum" -> 1.0 (long SPY)
      - "mean_rev" -> 0.0 (flat, no contrarian short Phase 2.A)
      - "random"   -> 0.0 (flat)

    Note : the contract pseudocode mentions a contre-signal for mean_rev,
    but the explicit constraint "Pas de short Phase 2.A" prevails. Phase
    2.A is therefore a long/flat overlay only; any short overlay is
    deferred to a later phase under a separate mandate.
    """
    if regime == "momentum":
        return 1.0
    return 0.0
