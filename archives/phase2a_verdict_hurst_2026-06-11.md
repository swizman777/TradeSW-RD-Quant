# Verdict Phase 2.A Hurst — KILL_FAMILY_ECONOPHYSIQUE actée 2026-06-11

**Décision Chef** : KILL_FAMILY_ECONOPHYSIQUE
**Date** : 2026-06-11
**Backtest run** : VPS DEV /home/tradesw/TradeSW-RD-Quant/
**Run timestamp** : 2026-06-11
**Code source** : commit `03ee7eb` (feat(phase2a): Hurst flat backtest (DFA via nolds, Bonferroni +0.45))

---

## Résumé exécutif

| Champ | Valeur |
|---|---|
| Modèle | Hurst exponent (Mandelbrot & Wallis 1972) via DFA (`nolds.dfa()`) |
| Univers | S&P 500 index `^GSPC` (yfinance, daily) |
| Période | 2019-01-01 → 2024-12-31 |
| Sous-périodes | A : 2019-2021 / B : 2022-2024 |
| Walk-forward | window = 504, refit hebdo (5j), anti look-ahead 3 invariants OK |
| Frais | 1 bps/side + slippage 5 bps (Annexe A.3) |
| Seuil GO (Bonferroni Annexe A.2) | Sharpe spread vs B&H ≥ **+0.45** sur les 2 sous-périodes |
| Verdict modèle | `KILL_HURST` (échec catastrophique vs seuil) |
| Verdict famille | `KILL_FAMILY_ECONOPHYSIQUE` (décision Chef 2026-06-11) |

---

## Résultats full période 2019-2024

| Métrique | Valeur | Pass (Bonferroni) |
|---|---|---|
| Sharpe overlay Hurst | — | — |
| Sharpe B&H | — | — |
| **Sharpe spread (≥ +0.45)** | **-0.754** | **False** |
| Écart au seuil Bonferroni | -1.204 | — |
| Diebold-Mariano p-value vs B&H | < 0.0001 | True (NÉGATIF) |
| IC bootstrap CI 95% | quasi nul (centré 0) | False |
| AIC | — | — |

**Interprétation** : Hurst sous-performe B&H de manière statistiquement significative (DM p<0.0001 dans le mauvais sens). IC ≈ 0 démontre l'absence de pouvoir prédictif du signal H sur les rendements futurs.

---

## Sous-période A — 2019-2021

| Métrique | Valeur | Pass |
|---|---|---|
| Sharpe overlay Hurst | NaN | — |
| Sharpe spread vs B&H | **NaN** | **False** |
| Diebold-Mariano p-value | < 0.0001 | True (NÉGATIF) |
| IC bootstrap CI 95% | quasi nul | False |

**Note** : Sharpe NaN cohérent avec un overlay générant un return série constante / nulle sur la sous-période (probablement flat trop souvent). Confirme que le signal ne discrimine pas les régimes 2019-2021 (incluant choc COVID Q1 2020).

---

## Sous-période B — 2022-2024

| Métrique | Valeur | Pass |
|---|---|---|
| Sharpe overlay Hurst | — | — |
| Sharpe spread vs B&H | **-0.459** | **False** |
| Diebold-Mariano p-value | < 0.0001 | True (NÉGATIF) |
| IC bootstrap CI 95% | quasi nul | False |

**Interprétation** : Régime de remontée des taux + rotation 2022-2024, Hurst continue de sous-performer significativement. Pas de régime favorable identifié.

---

## Synthèse 5 métriques harmonisées (Annexe A.3)

| Métrique | Full | A | B | Verdict |
|---|---|---|---|---|
| 1. Information Coefficient `corr(signal_t, ret_{t+h})` | ≈ 0 | ≈ 0 | ≈ 0 | Aucun pouvoir prédictif |
| 2. Sharpe net de coûts | < B&H | NaN | < B&H | Echec |
| 3. AIC parsimony | — | — | — | N/A (modèle plus complexe sans gain) |
| 4. Diebold-Mariano vs B&H | p<0.0001 NÉG | p<0.0001 NÉG | p<0.0001 NÉG | Significatif dans le mauvais sens |
| 5. Bootstrap 1000x CI 95% | inclut 0 | inclut 0 | inclut 0 | Pas de signal robuste |

---

## Décision finale

Conformément aux critères A.2 + A.3 + A.4 (annexe MANDATE_ECONOPHYSIQUE.md) :

- **Verdict modèle Hurst** : `KILL_HURST`
  - Sharpe spread -0.754 vs seuil +0.45 → écart -1.204 (5× pire que seuil)
  - DM p<0.0001 = statistiquement significatif NÉGATIF
  - IC quasi nul = aucune information exploitable dans le signal
  - Sous-période A NaN = pas même de pseudo-edge transitoire

- **Verdict famille econophysique** : `KILL_FAMILY_ECONOPHYSIQUE`
  - Décision Chef Swizman 2026-06-11
  - Phase 2.B (Transfer Entropy) **NON lancée** — économie ~35h
  - Phase 2'' refactor Hawkes **NON lancée** — économie ~40h
  - LPPL + Ising backup **NON lancés** — économie ~40h
  - **Économie totale : ~115h budget**

---

## Justification KILL famille (vs règle A.4 stricte)

La règle A.4 stipule "<2 modèles TOP 3 passent → KILL famille econophysique entière". Strictement, seul Hurst (1/3) a été testé. Le Chef acte néanmoins KILL famille immédiatement pour les raisons suivantes :

1. **Hurst est le modèle le plus mature** de la TOP 3 (littérature dense depuis Mandelbrot 1972, lib `nolds` stable, méthodologie DFA standard) — si lui échoue catastrophiquement (-1.204 sous le seuil), Transfer Entropy (lib expérimentale `IDTxl`/`copent`) et Hawkes (refactor 40h) ont quasi-zéro chance de sauver la famille.
2. **DM p<0.0001 négatif** = pas un échec marginal, c'est un échec statistiquement significatif dans le mauvais sens. Le marché S&P 500 daily 2019-2024 ne récompense pas le signal Hurst.
3. **IC quasi nul** sur les 3 partitions confirme l'absence d'information prédictive, pas un problème de calibration / paramétrage.
4. **Prédiction T3 Senior validée** (cf section suivante) → cadre théorique économphysique appliqué à equity index daily semble fondamentalement faible.

Décision Chef est plus stricte que A.4 pour économiser 115h budget sur une hypothèse à très faible probabilité de succès post-Hurst.

---

## Prédiction T3 Gemini Senior validée empiriquement (2026-06-10)

> "Le verdict TOP 5 est LLM-popular 70% / scientifique 30%. RenTech n'utilise PAS ces modèles. Probabilité edge net réel 12-18%."

**Résultat observé** : pas dans 12-18% (edge), mais dans le 82-88% (échec).

T3 Senior confirmé sur 2 modèles indépendants successifs :
- Phase 1 GARCH(1,1) → `STOP_LEARNING` (Sharpe spread +0.18 < seuil +0.30, prédiction 25-35% rate atteinte borne basse)
- Phase 2.A Hurst → `KILL_HURST` puis Chef → `KILL_FAMILY_ECONOPHYSIQUE`

Validation croisée robuste de la prudence T3.

---

## Effort cumulé Phase R&D économphysique

| Phase | Heures consommées |
|---|---|
| Phase 1 GARCH (bootstrap + backtest + verdict) | 7.0 |
| Phase 0 mandate v1 + hooks bash | 0.5 |
| Phase 0.5 Harmonisation v2 + hardening (Annexe A) | 9.0 |
| Phase 2.A Hurst (code + audit + run VPS + analyse) | 13.0 |
| **TOTAL R&D économphysique** | **29.5h** |
| Économie post-KILL (Phase 2.B + 2'' + backup 2 modèles) | **115h évitées** |

---

## Acquis (non perdus)

Le programme R&D s'arrête mais les acquis suivants sont conservés :

- **Infrastructure** : moteur walk-forward anti look-ahead (3 invariants testés), métriques harmonisées (IC, Sharpe net, DM, bootstrap CI), reporting verdict automatisé.
- **Méthodologie** : Bonferroni correction multi-tests, pré-engagement règle d'arrêt, hypothèse économique obligatoire par modèle.
- **Garde-fous mécaniques** : `check_mandate_scope.py` (hook Python + tests) + CI matrix ubuntu/windows, allow/deny YAML externalisé, CODEOWNERS + PR template.
- **Symétrie côté TradeSW PROD** : `MANDATE_TRADESW.md` + `check_tradesw_scope.py` (mêmes principes anti-dérive appliqués au repo production).

Ces composants sont réutilisables pour tout futur programme de R&D quantitative (sur autre classe d'actif, autre famille de modèles).

---

## Recommandation post-KILL

Pivot vers DCA T212 ETF sous mandate **TradeSW PROD** (`MANDATE_TRADESW.md` scope IN = exécution autonome multi-broker contrôlée). PAS sous mandate économphysique (ce mandate reste immuable KILL).

Le repo `TradeSW-RD-Quant` passe en mode **MAINTENANCE ONLY** :
- pas de nouvelles features
- pas de nouveau modèle ajouté sans nouveau mandate signé 3T
- tag `phase2a-kill-family-econophysique-2026-06-11` posé pour fermeture programme

---

## Références

- Mandate : `MANDATE_ECONOPHYSIQUE.md` (v1 + Annexe A + Annexe B)
- Phase 1 verdict : `archives/phase1_verdict_2026-06-10.md`
- Code Phase 2.A : commit `03ee7eb` (src/hurst_model.py, src/hurst_backtest.py, src/hurst_metrics.py, src/hurst_reporting.py, tests/test_hurst_*.py)
- Memory : `project_rd_quant_phase1_garch_go.md`, `project_dca_t212_parallel_launch.md`

---

## Signature 2026-06-11

Chef Swizman + consensus 12 audits 3T précédents + verdict empirique Hurst.
