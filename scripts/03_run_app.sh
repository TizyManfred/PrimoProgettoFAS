#!/bin/bash
set -euo pipefail

echo "[$(date +'%Y-%m-%d %H:%M:%S')] Avvio server Dashboard Web (Dash)..."

cd "$(dirname "$0")"
PROJECT_ROOT=$(dirname "$(pwd)")

if command -v lsof &> /dev/null; then
    if lsof -i :8050 -s TCP:LISTEN > /dev/null; then
        echo "[ERRORE] La porta 8050 risulta già occupata da un altro processo."
        exit 1
    fi
fi

python3 "$PROJECT_ROOT/python/app.py"
