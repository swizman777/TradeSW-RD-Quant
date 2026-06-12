# TradeSW-RD-Quant — Programme R&D économphysique

> R&D isolé du repo TradeSW production. **AUCUN import croisé**, .venv dédié, pas de symlink.
> Mandate Chef Swizman du 2026-06-09 (validation 3T : T1 Claude GO, T2 Codex GO, T3 Gemini HOLD conditionnel).

## Status final — Programme R&D TERMINÉ 2026-06-11

**Décision Chef** : `KILL_FAMILY_ECONOPHYSIQUE` actée 2026-06-11.

| Phase | Modèle | Verdict | Date |
|---|---|---|---|
| Phase 1 | GARCH(1,1) | `STOP_LEARNING` (Sharpe spread +0.18 < +0.30) | 2026-06-10 |
| Phase 2.A | Hurst exponent (DFA) | `KILL_HURST` (Sharpe spread -0.754, 5× pire seuil +0.45) | 2026-06-11 |
| Phase 2.B | Transfer Entropy | **NON lancée** (économie 35h) | — |
| Phase 2'' | Hawkes refactor | **NON lancée** (économie 40h) | — |
| Phase 3' | LPPL + Ising | **NON lancées** (économie 40h) | — |

Programme R&D économphysique total : **29.5h consommées**, **115h économisées**.

**Repo passe en mode MAINTENANCE ONLY** : pas de nouvelles features, pas de nouveau modèle sans nouveau mandate signé 3T.

Détails complets :
- `archives/phase1_verdict_2026-06-10.md` — Phase 1 GARCH STOP_LEARNING
- `archives/phase2a_verdict_hurst_2026-06-11.md` — Phase 2.A Hurst KILL + KILL_FAMILY actée
- `MANDATE_ECONOPHYSIQUE.md` Annexe B — décision Chef 2026-06-11
- Tag git : `phase2a-kill-family-econophysique-2026-06-11`

Recommandation post-KILL : pivot DCA T212 sous mandate **TradeSW PROD** (`MANDATE_TRADESW.md`), pas sous ce mandate économphysique.

---

## Mandate immuable

Le périmètre complet de ce repo est fixé par **[`MANDATE_ECONOPHYSIQUE.md`](MANDATE_ECONOPHYSIQUE.md)** (créé 2026-06-10, immuable hors annexes 3T datées).

Résumé court :
- **Objet** : tester si des outils mathématiques venant d'autres domaines scientifiques (hydrologie, sismologie, théorie de l'info, géophysique, magnétisme) caractérisent des régimes de marché mieux que les indicateurs financiers classiques.
- **TOP 5 modèles retenus** : Hurst exponent, Transfer entropy, ETAS Hawkes, LPPL Sornette, Ising mean-field.
- **Hors scope** : DCA, Bogle, exécution broker (T212/IBKR/Binance), autonomie. Toute introduction de tels modules est refusée mécaniquement par `scripts/hooks/check_mandate_scope.sh` (pré-commit) et le workflow `.github/workflows/mandate_guard.yml` (CI).
- **Activation locale** : `pip install pre-commit && pre-commit install`.

Tout commit / push touchant un path hors WHITELIST est refusé. Override uniquement via `git commit --no-verify` + justification + notification Chef (audit a posteriori).

## Budget

- **40 heures MAX cumulées** (effort_log.md fait foi).
- **Deadline binaire** : 2026-07-10 (J+30 à partir de 2026-06-10).
- **Hard stop** : 60 heures (contrat section 5).

Voir `BUDGET_DEADLINE.txt` (hardcodé pour hook git futur).

## Périmètre fixe (contrat section 1)

- Univers : **S&P 500 index `^GSPC`** via yfinance, daily.
- Modèle : **GARCH(1,1) seul** (PAS d'ACO Phase 1).
- Sizing : **vol-targeting 10% annualisé** (contract).
- Backtest : walk-forward strict, 252 jours train, refit chaque jour.
- Période : 2019-01-01 → 2024-12-31 (5 ans).
- Validation : 2 sous-périodes 2019-2021 et 2022-2024.
- Frais : **1 bps par side** (0.01%), pas de slippage modélisé.
- Random seed : **42**.

## Reproduce

```bash
# Setup (une fois)
make install

# Re-download S&P 500 (1ère fois ou pour refresh)
make refresh-data

# Run backtest complet (forecasts, PnL, verdict, charts)
make backtest

# Tests + coverage
make test
make coverage      # cible >= 70%

# Lint + types
make lint
make format

# Verdict uniquement (si backtest_results.parquet déjà produit)
make report
```

Outputs principaux :

- `reports/backtest_results.parquet` — full daily PnL + weights + vol forecasts
- `reports/verdict.md` — décision GO/STOP avec chiffres
- `reports/equity_curve.png`
- `reports/vol_pred_vs_realized.png`

## Verdict Phase 1 GARCH(1,1) (2026-06-10 — BOUCLÉ)

| Métrique | Full 2019-2024 | 2019-2021 | 2022-2024 |
|---|---|---|---|
| Sharpe overlay | 0.745 | 1.113 | 0.500 |
| Sharpe B&H | 0.564 | 0.740 | 0.411 |
| Sharpe spread | +0.181 | +0.374 | +0.090 |
| Max DD overlay | -0.152 | -0.113 | -0.152 |
| Max DD B&H | -0.361 | -0.361 | -0.271 |
| RMSE vol | 0.0638 | 0.0943 | 0.0290 |
| Hit rate vol | 0.499 | 0.516 | 0.487 |
| **4/4 ?** | 2/4 | 3/4 | 2/4 |

**Décision Phase 1 : `STOP_LEARNING` — voir `archives/phase1_verdict_2026-06-10.md`.**

GARCH(1,1) validé comme **risk overlay** (DD ratio 0.42, réduction 58%) mais **pas générateur alpha** (Sharpe spread +0.18 < seuil +0.30). Budget consommé : 7h / 40h (82.5% économie).

## Verdict Phase 2.A Hurst (2026-06-11 — BOUCLÉ + KILL famille)

| Métrique | Full 2019-2024 | 2019-2021 (A) | 2022-2024 (B) |
|---|---|---|---|
| Sharpe spread vs B&H | **-0.754** | NaN | **-0.459** |
| Seuil Bonferroni requis | +0.45 | +0.45 | +0.45 |
| Écart au seuil | **-1.204** | — | -0.909 |
| DM p-value vs B&H | < 0.0001 | < 0.0001 | < 0.0001 |
| IC bootstrap CI 95% | quasi nul | quasi nul | quasi nul |

**Décision finale : `KILL_FAMILY_ECONOPHYSIQUE` — voir `archives/phase2a_verdict_hurst_2026-06-11.md`.**

Hurst Sharpe spread -0.754 = **5× pire** que seuil Bonferroni +0.45. DM p<0.0001 = statistiquement significatif NÉGATIF vs B&H. IC quasi nul = aucun pouvoir prédictif. Chef Swizman acte KILL famille immédiat (vs règle A.4 stricte qui aurait demandé 2 modèles testés) car Hurst est le modèle le plus mature de la TOP 3 et son échec catastrophique signe la faiblesse du cadre théorique économphysique appliqué à equity index daily.

Phase 2.B Transfer Entropy + Phase 2'' Hawkes refactor + Phase 3' LPPL/Ising **NON lancées** : économie 115h. Phase 2.A budget consommé : 13h / 30h hardcode.

## Critère success (contrat section 4 — 4 conditions cumulatives)

1. Sharpe overlay ≥ Sharpe B&H + 0.3
2. Max DD overlay ≤ 80% Max DD B&H
3. RMSE vol < std(realized vol)
4. Hit rate direction vol > 55%

**Robustesse** : les 4 critères DOIVENT passer sur les 2 sous-périodes :
- 2/2 sous-périodes → `GO_PHASE_2_ACO`
- 1/2 sous-période → `REVIEW_CHEF`
- 0/2 sous-période → `STOP`

## Critère arrêt T3 (contrat section 5)

| Sharpe overlay − Sharpe B&H | Décision |
|---|---|
| < 0.1 | **STOP DÉFINITIF**, repo archivé |
| 0.1 — 0.2 | **STOP apprentissage**, documenter |
| 0.2 — 0.3 | **HOLD**, audit externe Gemini avant ACO |
| ≥ 0.3 | **GO Phase 2 ACO** (proba estimée 25-35%) |

**STOP automatique** : effort cumulé > 60h ⇒ ARRÊT quel que soit le résultat partiel.

## Architecture (~700 LoC total)

```
src/
  ingestion.py        — yfinance + cache parquet
  garch_model.py      — arch wrapper + fallback std
  vol_targeting.py    — sizing avec shift(1) anti look-ahead
  backtest_engine.py  — walk_forward + compute_pnl
  metrics.py          — Sharpe, Max DD, RMSE, hit rate
  reporting.py        — matplotlib + verdict.md
scripts/
  run_backtest.py     — entrypoint full pipeline
  refresh_data.py     — force re-download
tests/
  test_walk_forward_no_lookahead.py   — CRITIQUE (3 invariants)
  test_sharpe.py, test_max_dd.py, test_rmse_vol.py
  test_garch_fit.py, test_vol_target_sizing.py
  test_fees_drag.py, test_load_spy.py
```

## Anti look-ahead bias (contrat section 3.1)

- `train = returns.iloc[t-252:t]` **strict exclusif** sur `t`
- `position = sizing.shift(1)` **obligatoire**
- Test `test_walk_forward_no_lookahead.py` asserte 3 invariants :
  1. `train.index.max() < forecast.date`
  2. Forecast horizon = 1 strict
  3. Pas de scaling global (la 1ère ligne PnL utilise un poids décidé avant t)

## SHA256 du cache parquet

À renseigner après le 1er `make refresh-data` :

```
GSPC_2019-01-01_2024-12-31.parquet  SHA256=<à remplir>
```

(commande : `make refresh-data` affiche le hash en stdout)

## Rôles (contrat section 10)

- **Chef** : Swizman — décisionnaire final, valide verdict J+30.
- **Auditeur/Opérateur** : Claude — review code, audit faisabilité.
- **Dev-Agent** : Codex — implémente selon ce contrat.
- **Validation externe** : Gemini Senior — audit final verdict si Sharpe spread ∈ [0.2, 0.3].

## Référence contrat

Source de vérité : `../TradeSW/prompts/CONTRAT_CODEX_RD_QUANT_PHASE1_GARCH.md`
Memory entry : `project_rd_quant_phase1_garch_go.md`
