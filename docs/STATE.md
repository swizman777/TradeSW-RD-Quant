# STATE - TradeSW-RD-Quant

> Point d'entree unique de session pour Claude Auditeur / Codex Dev-Agent.
> Mis a jour 2026-06-12 par Codex post-livraison Phase 2.A code.

## Mandat actif

**Phase 2.A Hurst exponent flat** (CONTRAT_CODEX_PHASE2A_HURST.md)
- Mode FLAT (Plan C consensus 3T) : pas de refactor `BaseForecaster`.
- Test scientifique rigoureux pour valider/infirmer l'edge Hurst-DFA sur
  S&P 500 2019-2024.
- Hypothese economique : alpha direct probablement arbitre, espoir
  marginal en overlay binaire long/flat vol-targeted.

## Mode

- Branch : `main` (single-branch flow per Phase 0.5).
- Mandate immuable : `MANDATE_ECONOPHYSIQUE.md` + Annexe A.
- Scope guard : `scripts/hooks/check_mandate_scope.py` + `config/mandate_scope.yml`.
- CI : `.github/workflows/mandate_guard.yml` (matrix ubuntu+windows, GITHUB_ACTOR check).

## WIP (Work In Progress)

| # | Item | Etat |
|---|---|---|
| 1 | Phase 2.A Hurst code (src + tests) | LIVRE 2026-06-12 (commit a venir) |
| 2 | Chef : VPS DEV `git pull` + `pip install -e ".[dev]"` | PENDING |
| 3 | Chef : `make test` (15 tests Hurst) | PENDING |
| 4 | Chef : `make backtest_hurst` (S&P 500 2019-2024) | PENDING |
| 5 | Audit Claude sur `verdict_hurst.md` | PENDING |
| 6 | Decision T3 Chef : GO_PHASE_2B / STOP_LEARNING_HURST / KILL | PENDING |

## Derniere action grave

- 2026-06-10 : Phase 1 GARCH BOUCLEE `STOP_LEARNING` (Sharpe spread +0.181, tag `phase1-stop-learning-2026-06-10`).
- 2026-06-10 : Phase 0.5 Harmonisation livree (`8372706` MANDATE v2 Annexe A, hook Python, CODEOWNERS, PR template).
- 2026-06-12 : Phase 2.A code LIVRE - 5 modules src + 3 fichiers tests + Makefile cible `backtest_hurst` + pyproject `nolds==0.6.3`.

## Roles

| Role | Acteur | Permissions |
|---|---|---|
| Chef | Swizman | Decision GO/STOP/KILL, sensitive paths (`.github/`, `scripts/hooks/`) |
| Claude | Auditeur / Operateur | Review code post-commit, pas de Push direct sur main |
| Codex | Dev-Agent | Implementation selon contrats explicites, commit + push main |
| Gemini Senior | Audit | Audit final si Sharpe spread in [0.30, 0.45] zone HOLD |

## Phases passees

| # | Phase | Verdict | Date |
|---|---|---|---|
| 1 | Phase 1 GARCH baseline | `STOP_LEARNING` (Sharpe spread +0.181) | 2026-06-10 |
| 0.5 | Harmonisation MANDATE v2 | LIVREE | 2026-06-10 |

## Phases en cours

| # | Phase | Cible | Etat |
|---|---|---|---|
| 2.A | Hurst DFA flat | Decision binaire GO_PHASE_2B / STOP / KILL | CODE LIVRE 2026-06-12 |

## Phases futures (par mandate)

- 2.B : Transfer Entropy flat (si 2.A pas KILL)
- 2.C : ETAS (Hawkes) flat (selon Annexe A.4 regle d'arret agregee)
- 3 : Refactor architectural (`BaseForecaster`) IF au moins 1 famille passe Bonferroni

## Fichiers vivants

- `MANDATE_ECONOPHYSIQUE.md` - immuable, signature requise pour modification (Annexe A.8)
- `config/mandate_scope.yml` - allow/deny regex pour scope guard
- `pyproject.toml` - deps (nolds==0.6.3 ajoute Phase 2.A)
- `effort_log.md` - log effort cumulatif par phase
- `archives/` - verdicts archives (phase1_verdict_2026-06-10.md)
- `reports/` - artefacts backtest courant (parquet + verdict + charts)
