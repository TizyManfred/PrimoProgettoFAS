#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p ../logs

LOG_FILE="../logs/analyze.log"
exec > >(tee -i "$LOG_FILE") 2>&1

echo "[$(date +'%Y-%m-%d %H:%M:%S')] Avvio analisi dati..."
PROJECT_ROOT=$(dirname "$(pwd)")

if ! python3 "$PROJECT_ROOT/python/analyze.py"; then
    echo "[ERRORE] Lo script di analisi (analyze.py) ha restituito un errore."
    exit 1
fi

echo "[$(date +'%Y-%m-%d %H:%M:%S')] Analisi dati completata. I CSV sono in data/aggregated/"
exit 0
