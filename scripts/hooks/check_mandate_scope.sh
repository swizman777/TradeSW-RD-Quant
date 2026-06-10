#!/usr/bin/env bash
# check_mandate_scope.sh
# Refuse tout commit / push qui touche un path hors WHITELIST économphysique.
# Cf. MANDATE_ECONOPHYSIQUE.md sections 7 et 9.
#
# Override : `git commit --no-verify` (audit chef a posteriori).
# Usage local : appelé via .pre-commit-config.yaml (hook id check-mandate-scope).
# Usage CI    : .github/workflows/mandate_guard.yml exécute ce script
#               en lui injectant la liste des fichiers modifiés sur stdin.

set -euo pipefail

# WHITELIST : tout fichier dont le chemin matche cette regex est autorisé.
# - src/ racine couvre les modules Phase 1 GARCH existants (ingestion.py, garch_model.py, ...).
# - src/models/, src/data/, src/backtest/, src/analytics/, src/cli/ couvrent l'architecture cible Phase 2'.
# - tests/ couvre tous les tests (racine + sous-dossier models/).
# - notebooks/, data/, reports/, archives/ : R&D / outputs scientifiques.
# - fichiers racine : MANDATE, README, pyproject, Makefile, etc.
# - scripts/*.sh|.py : outils dont ce hook.
# - .github/ : CI.
WHITELIST_REGEX='^(src/[^/]+\.py$|src/(models|data|backtest|analytics|cli)/|tests/|notebooks/|data/|reports/|archives/|MANDATE_ECONOPHYSIQUE\.md$|README\.md$|pyproject\.toml$|Makefile$|\.gitignore$|\.python-version$|BUDGET_DEADLINE\.txt$|effort_log\.md$|scripts/.*\.(sh|py)$|\.pre-commit-config\.yaml$|\.github/)'

# Récupère la liste des fichiers à valider.
# - Si stdin a du contenu (utilisé par la CI), on prend stdin.
# - Sinon, on demande à git la liste des fichiers staged (mode pre-commit local).
if [ ! -t 0 ]; then
    # stdin existe (pipe). On le lit, mais s'il est vide on fallback git.
    STDIN_CONTENT=$(cat || true)
    if [ -n "$STDIN_CONTENT" ]; then
        FILES="$STDIN_CONTENT"
    else
        FILES=$(git diff --cached --name-only --diff-filter=ACMR 2>/dev/null || true)
    fi
else
    FILES=$(git diff --cached --name-only --diff-filter=ACMR 2>/dev/null || true)
fi

if [ -z "${FILES// /}" ]; then
    # Rien à valider, on laisse passer.
    exit 0
fi

VIOLATIONS=""
while IFS= read -r f; do
    # Skip lignes vides
    [ -z "$f" ] && continue
    if ! printf '%s\n' "$f" | grep -qE "$WHITELIST_REGEX"; then
        VIOLATIONS="${VIOLATIONS}
  - ${f}"
    fi
done <<< "$FILES"

if [ -n "$VIOLATIONS" ]; then
    echo "ERROR : MANDATE_ECONOPHYSIQUE.md scope violation."
    echo ""
    echo "Les fichiers suivants sont HORS WHITELIST (R&D économphysique uniquement) :"
    echo -e "$VIOLATIONS"
    echo ""
    echo "Whitelist autorisée :"
    echo "  - src/<module>.py (racine), src/{models,data,backtest,analytics,cli}/**"
    echo "  - tests/**, notebooks/**, data/**, reports/**, archives/**"
    echo "  - MANDATE_ECONOPHYSIQUE.md, README.md, pyproject.toml, Makefile, .gitignore,"
    echo "    .python-version, BUDGET_DEADLINE.txt, effort_log.md"
    echo "  - scripts/**/*.sh, scripts/**/*.py, .pre-commit-config.yaml, .github/**"
    echo ""
    echo "Si vraiment besoin, override : git commit --no-verify"
    echo "Mais MOTIVE explicitement dans le message de commit ET notifie le Chef."
    echo "Toute occurrence sera auditée a posteriori."
    exit 1
fi

exit 0
