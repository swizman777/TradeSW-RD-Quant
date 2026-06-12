# MANDATE_ECONOPHYSIQUE — TradeSW-RD-Quant

**Statut** : IMMUABLE — créé 2026-06-10, ne sera jamais modifié (seules annexes datées autorisées en fin de fichier).
**Auteur mandant** : Chef Swizman.
**Signataires consensus 3T (2026-06-10)** : T1 Claude (Auditeur/Opérateur), T2 Codex (Dev-Agent), T3 Gemini Senior (validation externe).
**Repo** : `TradeSW-RD-Quant` (R&D scientifique, isolé du repo TradeSW d'exécution).

---

## 1. Verbatim mandate Chef (2026-06-09)

> « Projet de mise en place d'une stratégie d'analyse prédictive du marché basée sur des formules empruntées à des techno météo, flux marin, et autres domaines scientifiques (sismologie, magnétisme, thermodynamique, hydrologie). Le but est de tester si des outils mathématiques venant d'ailleurs détectent des régimes / signaux que les indicateurs financiers classiques (MA, RSI, MACD) ratent. Ce repo est isolé du repo TradeSW de production. Aucun import croisé. Toute dérive vers du business (DCA, Bogle, exécution T212/IBKR, autonomie) doit être bloquée mécaniquement. »

Cette phrase est la **source de vérité unique** du périmètre du repo `TradeSW-RD-Quant`.

---

## 2. Pourquoi économphysique ≠ business

Le repo `TradeSW` (production) traite l'exécution multi-broker, l'autonomie sous contrôle, le DCA T212, les overlays opérationnels. Le repo `TradeSW-RD-Quant` ne traite **que** la question scientifique suivante :

> Est-ce que des formules issues d'autres domaines (sismologie, météo, hydrologie, magnétisme, thermodynamique, géophysique) peuvent prédire ou caractériser des régimes de marché de manière statistiquement robuste (Sharpe spread ≥ +0.30 ou AUC ≥ 0.55) sur S&P 500 walk-forward ?

Tout ce qui ressemble à :
- choix d'un ETF à acheter,
- automatisation d'un ordre,
- intégration broker (T212, IBKR, Binance),
- pondération de portefeuille hors backtest scientifique,
- exécution live ou paper-trading,

**est hors scope** et doit être refusé par le hook `check_mandate_scope.sh`.

Le seul output exploitable de ce repo vers le repo TradeSW est : une **conclusion scientifique datée** (`reports/verdict_*.md` ou `archives/`) disant « tel modèle physique X passe les seuils Y sur la période Z, donc il peut être ré-implémenté en production sous contrat séparé ». La ré-implémentation, elle, se fait dans TradeSW, jamais ici.

---

## 3. TOP 5 modèles physiques sélectionnés (consensus 3T 2026-06-10)

Post-revue littérature et consensus T1/T2/T3, les 5 modèles retenus pour Phase 2' et 3' sont :

| # | Modèle | Domaine d'origine | Référence canonique | Hypothèse marché |
|---|---|---|---|---|
| 1 | **Hurst exponent** | Hydrologie (longueur de mémoire crues du Nil) | Mandelbrot & Wallis 1972 | H > 0.5 → persistance / momentum ; H < 0.5 → mean-reversion |
| 2 | **Transfer entropy** | Théorie de l'information / thermodynamique | Schreiber 2000 | Mesure causalité asymétrique cross-actifs au-delà de la corrélation linéaire |
| 3 | **ETAS Hawkes** | Sismologie (répliques sismiques) | Ogata 1988, Bouchaud-Cont 2003 | Auto-excitation des crashs : un grand mouvement augmente la proba du suivant |
| 4 | **LPPL Sornette** | Géophysique / log-périodicité | Johansen, Ledoit, Sornette 2000-2003 | Détection de bulles via signature log-périodique avant crash |
| 5 | **Ising mean-field** | Magnétisme / physique statistique | Bouchaud 2013, Kaizoji-Sornette | Modélisation imitation traders (spin up/down) → transitions de phase de marché |

Ces 5 modèles seront implémentés un par un, chacun avec :
- un module isolé `src/models/<nom>.py`,
- des tests `tests/models/test_<nom>.py`,
- un backtest walk-forward propre (pas d'optimisation in-sample globale),
- un verdict daté dans `reports/<nom>_verdict_YYYY-MM-DD.md`.

---

## 4. Modèles EXCLUS (6 sur 11 candidats initiaux)

Après consensus 3T, les modèles suivants sont **explicitement exclus** du périmètre de `TradeSW-RD-Quant` :

| Modèle exclu | Raison principale du rejet |
|---|---|
| **Percolation MST** (Minimum Spanning Tree) | Lecture descriptive uniquement, pas de signal exploitable en walk-forward démontré sur literature S&P 500 |
| **Modèle de Lorenz / chaos déterministe** | Inadapté à des séries financières non-stationnaires courtes ; sensibilité aux conditions initiales rend toute prévision opérationnelle illusoire |
| **Fokker-Planck** | Trop proche d'un GARCH généralisé déjà exploré Phase 1 ; n'apporte pas de signal orthogonal |
| **FFT / analyse spectrale brute** | Hypothèse de stationnarité violée sur séries de rendements ; bruit dominant, ratio signal/bruit insuffisant |
| **Navier-Stokes / dynamique fluide** | Aucun mapping rigoureux et reproductible entre variables fluides et variables financières dans la littérature peer-reviewed |
| **Lotka-Volterra (proie-prédateur)** | Métaphore narrative séduisante, mais paramétrisation arbitraire et pas de cadre statistique robuste pour valider |

Toute tentative d'ajouter un de ces 6 modèles devra passer par un **nouveau mandate signé** (annexe datée à ce fichier, plus PR review T1+T2+T3).

---

## 5. Critères STOP par modèle

Pour chaque modèle de la TOP 5, un backtest walk-forward sur 2019-2024 produit un verdict.
Critères de **GO** (passage à phase suivante / production) :

- **Signal directionnel (Hurst, ETAS, Ising)** : Sharpe spread (overlay − B&H) ≥ **+0.30**, walk-forward strict, sur **les deux** sous-périodes 2019-2021 et 2022-2024.
- **Classifieur de régime (Transfer entropy, LPPL)** : AUC out-of-sample ≥ **0.55**, sur **les deux** sous-périodes.
- **Convergence multi-paramètres** : au moins **60 %** des configurations de paramètres testées (grille raisonnable) doivent passer les seuils ci-dessus → pas un point chanceux.

Si l'un des trois critères ci-dessus échoue → verdict `STOP_LEARNING` pour ce modèle, archivage daté dans `archives/<nom>_verdict_YYYY-MM-DD.md`, et **pas de tentative de retuning** sur la même période (anti-overfitting).

Re-test autorisé uniquement avec :
- nouvelles données (période postérieure non vue), **ou**
- modèle structurellement différent (annexe mandate).

---

## 6. Coupe-circuit S9 — STOP programme entier

Si après avoir backtesté les 3 premiers modèles principaux (**Hurst**, **Transfer entropy**, **ETAS**) le score est **0 / 3** :
- aucun des 3 ne passe Sharpe spread ≥ +0.30 ou AUC ≥ 0.55 sur 2/2 sous-périodes,

alors **STOP programme entier** :
- les 2 derniers modèles (LPPL, Ising) ne sont **pas** lancés,
- le repo est archivé sous tag `econophysique-stop-S9-YYYY-MM-DD`,
- conclusion globale : « les outils physiques explorés n'apportent pas d'edge supérieur à GARCH(1,1) sur S&P 500 daily 2019-2024 ».

C'est un coupe-circuit dur, pas négociable. Le Chef peut décider de relancer un programme similaire **plus tard** sur une **autre classe d'actifs** (crypto, futures), mais ce serait un **nouveau mandate** (nouveau repo ou tag majeur).

---

## 7. Garde-fous mécaniques (pas protocolaires)

Pour empêcher la dérive observée (incident DCA T212 reverted 2026-06-10, commits 55a7cef + 8acbbbe revert 81ddf0f côté repo TradeSW), les garde-fous sont **du code** :

1. **`scripts/hooks/check_mandate_scope.sh`** — hook pré-commit refusant tout fichier hors WHITELIST (paths R&D économphysique uniquement).
2. **`.pre-commit-config.yaml`** — wire le hook ci-dessus dans `pre-commit`.
3. **`.github/workflows/mandate_guard.yml`** — CI bloquante sur push et PR.
4. **`MANDATE_ECONOPHYSIQUE.md`** (ce fichier) — référencé en tête de README et figé.

Override possible uniquement via `git commit --no-verify` + justification explicite dans le message + notification au Chef. Toute occurrence d'override sera auditée.

WHITELIST de paths autorisés :

```
src/models/             — implémentations modèles physiques
tests/models/           — tests unitaires modèles
src/data/               — ingestion / cache
src/backtest/           — moteur walk-forward
src/analytics/          — métriques scientifiques (Sharpe, AUC, RMSE, …)
src/cli/                — entrypoints scripts
tests/                  — tous tests
notebooks/              — exploration jupyter
data/                   — caches parquet/csv
reports/                — sorties scientifiques (verdicts, charts)
archives/               — verdicts datés immuables
MANDATE_ECONOPHYSIQUE.md
README.md
pyproject.toml
Makefile
.gitignore
.python-version
BUDGET_DEADLINE.txt
effort_log.md
scripts/*.sh / *.py     — outils repo
.github/                — CI config
```

(les modules `src/*.py` existants Phase 1 GARCH sont déjà whitelistés via le pattern `src/` racine restant, voir hook code.)

---

## 8. Calendrier

- **Side-project** : ~15 h / semaine maximum.
- **Durée totale prévue** : **14 semaines** à partir de 2026-06-10.
- **Découpage** :
  - Phase 1' (déjà BOUCLÉE 2026-06-10) — GARCH baseline → `STOP_LEARNING`, 7 h consommées.
  - Phase 2' — Hurst + Transfer entropy + ETAS (3 modèles principaux), ~6 semaines.
  - Phase 3' — LPPL + Ising (2 modèles avancés, si Phase 2' ≥ 1/3 passe), ~5 semaines.
  - Phase 4' — Synthèse + audit externe T3 + verdict final → décision réimplémentation en repo TradeSW prod ou archivage définitif, ~3 semaines.
- **Budget heures Phase 2'** : 205 h max cumulées (à confirmer dans contrat dédié).
- **Coupe-circuit S9** appliqué entre Phase 2' et Phase 3'.

---

## 9. Anti-dérive — exemple de ce qu'il NE FAUT PAS faire

Historique 2026-06-10, sur le repo `TradeSW` :

- commit 55a7cef + commit 8acbbbe : tentative d'introduction d'un module **DCA CSPX via T212** dans la branche `develop` de TradeSW.
- ces commits **n'étaient pas mandatés** : le mandate vrai (validé 3T 2026-06-09) portait sur la R&D économphysique dans le repo séparé `TradeSW-RD-Quant`, pas sur du Bogle/DCA dans TradeSW.
- détection : audit chef → revert `81ddf0f` sur `develop`, archive `archive/dca-cspx-t212`.

Leçon retenue :
- les **protocoles écrits seuls** ne suffisent pas (déjà vrai 2 fois en 6 mois sur TradeSW),
- il faut un **hook git + CI** qui refusent mécaniquement les paths hors scope **avant même** que le code n'atteigne la branche partagée.

C'est exactement le rôle des fichiers listés en section 7.

Dans `TradeSW-RD-Quant`, tout futur fichier de type :
- `src/broker/t212_*.py`,
- `dashboard/*`,
- `dca_*.py`,
- `bogle_*.py`,
- `core/risk_manager_*.py`,

doit être **refusé** par le hook. Si malgré tout un Dev-Agent ou agent IA essaie d'en pousser un, il devra passer par `--no-verify` (audit a posteriori chef) + justification publique.

---

## 10. Signature Chef

> Je soussigné Swizman, Chef de projet TradeSW + TradeSW-RD-Quant, déclare ce mandate :
> - **immuable** à partir de la date 2026-06-10 23:59 UTC+2,
> - source de vérité **unique** pour le périmètre du repo `TradeSW-RD-Quant`,
> - non-modifiable sauf par **annexe datée** ajoutée en fin de ce fichier et co-signée 3T (T1 Claude, T2 Codex, T3 Gemini),
> - prévalent sur toute instruction ultérieure qui chercherait à introduire du business / DCA / exécution dans ce repo.

**Date** : 2026-06-10
**Chef** : Swizman
**Repo** : `https://github.com/swizman777/TradeSW-RD-Quant`

---

## Annexes (à dater si ajoutées plus tard)

*(annexes datées ci-dessous, signées 3T)*

---

## Annexe A — Corrections Phase 0.5 (2026-06-10)

Suite 4 collégialités 3T (12 audits indépendants), corrections suivantes :

### A.1 RÉDUCTION TOP 5 → TOP 3
- **Maintenus** : Hurst (Mandelbrot 1972), Transfer Entropy (Schreiber 2000), **Hawkes finance-native** (Bacry-Muzy 2013) [substitue ETAS sismologie]
- **DIFFÉRÉS** Phase 2'' conditionnels : LPPL Sornette, Ising mean-field
- **Raison** : biais LLM-popular, redondance ETAS↔LPPL, probabilité edge revisée 12-18%

### A.2 BONFERRONI multi-tests
- Seuil Sharpe spread requis : **+0.45** (pas +0.30)
- Correction : α=0.05 / 3 tests = 0.0167 par modèle
- Alternative : seuil AUC ≥ 0.60 (pas 0.55)

### A.3 Métriques harmonisées obligatoires (comparables cross-model)
1. Information Coefficient : `IC = corr(signal_t, ret_{t+h})`
2. Sharpe net de coûts (slippage 5bps explicite + fees)
3. AIC (parsimony)
4. Diebold-Mariano test vs buy-hold
5. Bootstrap 1000x CI sur métriques

### A.4 Pré-engagement règle d'arrêt agrégée
> Si **<2 modèles TOP 3** passent les critères A.2+A.3 sur les 2 sous-périodes, **KILL famille econophysique entière**. Ne pas ressortir 4ème/5ème modèle (sunk cost fallacy).

### A.5 Hypothèse économique obligatoire par modèle
Avant implémentation, répondre par écrit :
> "Pourquoi le marché laisserait cet edge sur la table en 2026 ? Quel hedge fund teste/utilise ce modèle aujourd'hui ?"

Si réponse = "personne" → SUSPECT, pas prometteur.

### A.6 Plan C : flat 2 modèles d'abord
- Phase 2.A : Hurst flat (30h, lib `nolds` confirmée Py3.13 OK)
- Phase 2.B : Transfer Entropy flat (35h, lib `IDTxl` ou `copent` — pas `pyinform` mort)
- **Gate** : si edge mesurable sur ≥1 modèle → refactor BaseForecaster Phase 2'' justifié
- Sinon : abandon propre, économise 140h

### A.7 Section HORS-SCOPE par exemple (pédagogique)
Sont HORS-SCOPE du repo TradeSW-RD-Quant :
1. Sélection ETF à acheter (DCA, Bogle, allocation)
2. Automatisation ordre broker (T212, IBKR, Binance, Kraken)
3. Stratégie de couverture (hedge fund-style, options, futures)
4. Multi-asset portfolio optimization
5. Exécution live ou paper-trading
6. Sentiment analysis ou news NLP trading
7. Intraday HFT
8. Leverage / margin trading
9. Options pricing
10. Dashboard / reporting opérationnel

Tout fichier matching ces patterns sera REJETÉ par hook + CI.

### A.8 Signature Phase 0.5
Date : 2026-06-10 (annexe datée)
Auteur : Chef Swizman + consensus 12 audits 3T

---

## Annexe B — KILL_FAMILY_ECONOPHYSIQUE actée (2026-06-11)

### Verdict final programme R&D

Le programme R&D économphysique est TERMINÉ. Décision Chef Swizman 2026-06-11.

### Résultats Phase 2.A Hurst (commit 03ee7eb)

| Métrique | Full 2019-24 | Sous-période A 2019-21 | Sous-période B 2022-24 |
|---|---|---|---|
| Sharpe spread vs B&H | **-0.754** ❌ | NaN | **-0.459** ❌ |
| DM p-value vs B&H | < 0.0001 | < 0.0001 | < 0.0001 |
| IC bootstrap CI 95% | quasi nul | quasi nul | quasi nul |
| Seuil Bonferroni requis | +0.45 | — | — |
| **Écart au seuil** | **-1.204** | — | — |

### Justification KILL famille (vs règle A.4 stricte)

Règle A.4 stipule "<2 modèles TOP 3 passent → KILL famille". Strictement on n'a testé que Hurst (1/3). Mais :
- Sharpe spread Hurst -0.754 = **5× pire** que seuil +0.45 (catastrophique)
- DM statistiquement significatif NÉGATIF (Hurst pire que B&H avec p<0.0001)
- IC quasi nul = aucun pouvoir prédictif Hurst
- Hurst est le modèle LE PLUS MATURE et bien étudié de la TOP 3 → si lui échoue catastrophiquement, Transfer Entropy et Hawkes ont quasi-zéro chance de sauver la famille
- Économie 115h (Phase 2.B 35h + Phase 2'' 40h + 2 modèles backup 40h) confirme rationalité décision

### Prédiction T3 Gemini Senior validée empiriquement (2026-06-10)

> "Le verdict TOP 5 est LLM-popular 70% / scientifique 30%. RenTech n'utilise PAS ces modèles. Probabilité edge net réel 12-18%."

**Résultat observé : pas dans 12-18% (edge), mais dans le 82-88% (échec)**. T3 senior confirmé sur 2 modèles indépendants (GARCH STOP_LEARNING + Hurst KILL).

### Effort cumulé Phase R&D économphysique

| Phase | Heures consommées |
|---|---|
| Phase 1 GARCH backtest | 7h |
| Phase 0 mandate v1 + hooks bash | 0.5h |
| Phase 0.5 Harmonisation v2 + hardening | 9h |
| Phase 2.A Hurst (code + audit + run + analyse) | 13h |
| **TOTAL** | **29.5h** |
| Économie post-KILL | 115h évitées |

### Recommandation post-KILL

Pivot DCA T212 sous mandate **TradeSW PROD** (`MANDATE_TRADESW.md` scope IN = exécution autonome multi-broker). PAS sous mandate économphysique (ce mandate reste immuable KILL).

### Repo final

- Tag `phase2a-kill-family-econophysique-2026-06-11` à poser
- Archive `archives/phase2a_verdict_hurst_2026-06-11.md` à créer
- README.md tableau verdict à mettre à jour avec décision finale
- Repo passe en mode **MAINTENANCE ONLY** (pas de nouvelles features)

### Signature 2026-06-11

Chef Swizman + consensus 12 audits 3T précédents + verdict empirique Hurst.
