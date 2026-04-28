#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p ../logs

LOG_FILE="../logs/clean.log"
exec > >(tee -i "$LOG_FILE") 2>&1

echo "[$(date +'%Y-%m-%d %H:%M:%S')] Avvio pulizia dati..."
PROJECT_ROOT=$(dirname "$(pwd)")

if ! python3 "$PROJECT_ROOT/python/clean.py"; then
    echo "[ERRORE] Lo script di pulizia (clean.py) ha restituito un errore."
    exit 1
fi

echo "[$(date +'%Y-%m-%d %H:%M:%S')] Pulizia dati completata."
exit 0
