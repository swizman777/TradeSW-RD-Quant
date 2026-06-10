# Verdict Phase 1 GARCH(1,1) — STOP_LEARNING

**Date** : 2026-06-10
**Backtest run** : VPS DEV /home/tradesw/TradeSW-RD-Quant/
**Data SHA256** : 2f81e7ef6357f58e2e79f257ffb1525f47550a705b58f5b41c52a10c26e8e5e3
**Decision globale (4 criteres x 2 sous-periodes)** : `STOP`
**Decision T3 Senior (Sharpe spread)** : `STOP_LEARNING`

## Resume full period 2019-2024

| Metric | Value | Pass |
|---|---|---|
| Sharpe overlay | 0.745 | — |
| Sharpe B&H | 0.564 | — |
| Sharpe spread (>= 0.30) | 0.181 | False |
| Max DD overlay | -0.152 | — |
| Max DD B&H | -0.361 | — |
| DD ratio (<= 0.80) | 0.422 | True |
| RMSE vol | 0.0638 | True |
| std(realised vol) | 0.1225 | — |
| Hit rate dir vol (> 55%) | 0.499 | False |

## Sous-periode A 2019-2021 (3/4 criteres)

| Metric | Value | Pass |
|---|---|---|
| Sharpe overlay | 1.113 | — |
| Sharpe B&H | 0.740 | — |
| Sharpe spread (>= 0.30) | 0.374 | True |
| Max DD overlay | -0.113 | — |
| Max DD B&H | -0.361 | — |
| DD ratio (<= 0.80) | 0.314 | True |
| RMSE vol | 0.0943 | True |
| std(realised vol) | 0.1742 | — |
| Hit rate dir vol (> 55%) | 0.516 | False |

## Sous-periode B 2022-2024 (2/4 criteres)

| Metric | Value | Pass |
|---|---|---|
| Sharpe overlay | 0.500 | — |
| Sharpe B&H | 0.411 | — |
| Sharpe spread (>= 0.30) | 0.090 | False |
| Max DD overlay | -0.152 | — |
| Max DD B&H | -0.271 | — |
| DD ratio (<= 0.80) | 0.562 | True |
| RMSE vol | 0.0290 | True |
| std(realised vol) | 0.0657 | — |
| Hit rate dir vol (> 55%) | 0.487 | False |

## Conclusions techniques

- Convergence GARCH(1,1) : **100% (1256/1256 fits)**
- Anti look-ahead bias : 3 invariants testés OK
- GARCH = risk overlay valide (DD ratio < 0.8 partout, protection 58%)
- GARCH ≠ générateur alpha (Sharpe spread +0.18 < +0.30 seuil contrat)
- Hit rate direction vol ~50% = GARCH calibre le niveau, ne prédit pas la direction
- Régime post-COVID (sous-période B) → effet s'évanouit, overfit COVID probable

## Prédiction T3 Gemini Senior (Phase 2 Faisabilité)

> "Probabilité d'atteindre Sharpe +0.3 OOS : 25-35%"

**Résultat observé : +0.18 → prédiction VALIDÉE chiffrement.**

## Décision Chef 2026-06-10

- Phase 1 GARCH : ARCHIVÉE, documentée
- Phase 2 ACO : **NON lancée** (critère arrêt T3 respecté)
- DCA T212 ETF parallèle : devient PRIORITÉ #1
- Budget consommé : **6.66h / 40h** (16%)
- Aucun argent réel investi

## Référence

- Contrat : `../TradeSW/prompts/CONTRAT_CODEX_RD_QUANT_PHASE1_GARCH.md`
- Memory : `project_rd_quant_phase1_garch_go.md`
- Audit 3T Phase 2 Faisabilité (2026-06-09) : T1+T2 OK GO, T3 HOLD conditionnel — réalité confirme T3.
