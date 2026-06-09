# Effort Log Phase 1 GARCH

Budget total : **40h max cumulé** (deadline 2026-07-10).
Hard stop automatique : **60h** (contrat section 5).

| Session | Date | Tâche | Heures session | Cumul |
|---|---|---|---|---|
| 1 | 2026-06-10 | Bootstrap repo (Phase 1.A) : structure, pyproject, .gitignore, Makefile, BUDGET_DEADLINE, 6 modules src/ (ingestion, garch_model, vol_targeting, backtest_engine, metrics, reporting), 2 scripts CLI, 8 fichiers de tests pytest, README, effort_log | ~6 | 6 |

## Phase 1.B — TODO (prochaine session)

- [ ] Chef lance `make install` puis `make refresh-data` (fetch S&P 500 réel)
- [ ] Chef lance `make test` puis `make coverage` (vérifier ≥70%)
- [ ] Chef lance `make backtest` (production des verdicts + charts)
- [ ] Audit Claude sur résultats verdict.md
- [ ] Selon spread Sharpe : STOP / HOLD / GO Phase 2 ACO
- [ ] Documenter SHA256 cache parquet dans README après 1er download

## Notes

- Aucun import depuis TradeSW (contrainte 1) — vérifié.
- shift(1) appliqué dans `vol_targeting.compute_position_size` (contrainte 2).
- GARCH returns en % via `df["return"] * 100` dans `ingestion.fetch_sp500_daily`.
- Random seed 42 fixé en tête de `src/__init__.py`.
- Frais 1 bps hardcodés dans `BacktestConfig.fees_bps`.
- Vol target 10% hardcodé dans `vol_targeting.DEFAULT_VOL_TARGET`.
- Train window 252 dans `BacktestConfig.train_window` (paramétrable).
