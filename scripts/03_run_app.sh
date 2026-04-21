#!/bin/bash
# 03_run_app.sh — Avvia la web application (Dashboard Dash)

set -euo pipefail

echo "[$(date +'%Y-%m-%d %H:%M:%S')] Avvio server Dashboard Web (Dash)..."

cd "$(dirname "$0")"
PROJECT_ROOT=$(dirname "$(pwd)")

# Verifica rapida disponibilità porta 8050
if command -v lsof &> /dev/null; then
    if lsof -i :8050 -s TCP:LISTEN > /dev/null; then
        echo "[ERRORE] La porta 8050 risulta già occupata da un altro processo."
        echo "Controlla di non avere già app in esecuzione o modifica la porta in app.py."
        exit 1
    fi
fi

# Avvia l'app in locale
python3 "$PROJECT_ROOT/python/app.py"
