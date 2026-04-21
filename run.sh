#!/bin/bash
# run.sh — Entry point principale per l'esecuzione della pipeline FAS

set -euo pipefail

echo "======================================"
echo " Aviation Accident Dashboard - Start"
echo "======================================"

cd "$(dirname "$0")"

# Rende eseguibili gli script 
chmod +x scripts/*.sh

# Esegue in cascata le seguenti azioni: setup, pulizia e analisi
./scripts/00_setup.sh
./scripts/01_clean.sh
./scripts/02_analyze.sh

echo "======================================"
echo " Pipeline dati completata con successo."
echo "======================================"

# Avvia il server web a meno che non sia specificato --no-serve (utile per test e Docker build)
if [[ "${1:-}" != "--no-serve" ]]; then
    ./scripts/03_run_app.sh
else
    echo "Esecuzione completata (--no-serve rilevato)."
fi
