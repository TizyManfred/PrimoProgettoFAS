#!/bin/bash
set -euo pipefail

echo "======================================"
echo " Aviation Accident Dashboard - Start"
echo "======================================"

cd "$(dirname "$0")"
chmod +x scripts/*.sh

./scripts/00_setup.sh
./scripts/01_clean.sh
./scripts/02_analyze.sh

echo "======================================"
echo " Pipeline dati completata con successo."
echo "======================================"

if [[ "${1:-}" != "--no-serve" ]]; then
    ./scripts/03_run_app.sh
else
    echo "Esecuzione completata (--no-serve rilevato)."
fi
