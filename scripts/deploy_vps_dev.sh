#!/usr/bin/env bash
# Bootstrap TradeSW-RD-Quant on VPS DEV (/home/tradesw-dev/TradeSW-RD-Quant)
# Run this AS tradesw-dev user, after SSH:
#   ssh -p 49222 tradesw-dev@217.160.45.86
#   bash <(curl -sL https://raw.githubusercontent.com/swizman777/TradeSW-RD-Quant/main/scripts/deploy_vps_dev.sh)
# OR copy-paste this whole script in the SSH session.

set -euo pipefail

REPO_URL="git@github.com:swizman777/TradeSW-RD-Quant.git"
HTTPS_URL="https://github.com/swizman777/TradeSW-RD-Quant.git"
TARGET="/home/tradesw-dev/TradeSW-RD-Quant"

echo "=== 1. Clone repo (try SSH first, fallback HTTPS) ==="
if [ -d "$TARGET/.git" ]; then
    echo "Repo already exists at $TARGET — git pull instead"
    cd "$TARGET"
    git fetch origin main && git reset --hard origin/main
else
    cd /home/tradesw-dev
    if ! git clone "$REPO_URL" TradeSW-RD-Quant 2>/dev/null; then
        echo "SSH clone failed, trying HTTPS (requires gh auth or PAT)..."
        git clone "$HTTPS_URL" TradeSW-RD-Quant
    fi
fi

cd "$TARGET"
echo "=== Repo HEAD : $(git rev-parse --short HEAD) ==="

echo ""
echo "=== 2. Check Python 3.13 ==="
PYTHON_BIN="$(command -v python3.13 || command -v python3.12 || command -v python3)"
echo "Using $PYTHON_BIN ($($PYTHON_BIN --version))"

echo ""
echo "=== 3. Create venv ==="
if [ ! -d .venv ]; then
    "$PYTHON_BIN" -m venv .venv
fi
# shellcheck source=/dev/null
source .venv/bin/activate

echo ""
echo "=== 4. Upgrade pip + install package + dev deps ==="
pip install --quiet --upgrade pip
pip install -e ".[dev]"

echo ""
echo "=== 5. Run tests offline (no network) ==="
pytest tests/ -v --no-header 2>&1 | tail -30

echo ""
echo "=== 6. Lint check ==="
ruff check src/ tests/ || echo "ruff warnings present"
mypy src/ --ignore-missing-imports || echo "mypy warnings present"

echo ""
echo "=== 7. Done. Next steps ==="
echo "  - Run: make refresh-data       (downloads S&P 500 from yfinance)"
echo "  - Run: make backtest           (executes walk-forward GARCH)"
echo "  - Output: reports/verdict.md + 2 PNG"
echo "  - Effort target: 40h total, deadline 2026-07-10"
