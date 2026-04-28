#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p ../logs
LOG_FILE="../logs/setup.log"
exec > >(tee -i "$LOG_FILE") 2>&1
echo "[$(date +'%Y-%m-%d %H:%M:%S')] Verifica prerequisiti..."
PROJECT_ROOT=$(dirname "$(pwd)")


if [ ! -f "$PROJECT_ROOT/AviationData.csv" ]; then
    echo "[ERRORE] File AviationData.csv non trovato nella root del progetto."
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "[ERRORE] Python 3 non installato."
    exit 1
fi

VENV_DIR="$PROJECT_ROOT/.venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "[setup] Creazione virtual environment in $VENV_DIR..."
    python3 -m venv "$VENV_DIR"
fi
echo "[setup] Attivazione virtual environment..."
source "$VENV_DIR/bin/activate"
python -m pip install --upgrade pip --quiet --disable-pip-version-check
python -m pip install --quiet --disable-pip-version-check -r "$PROJECT_ROOT/python/requirements.txt"
mkdir -p "$PROJECT_ROOT/data/cleaned"
mkdir -p "$PROJECT_ROOT/data/aggregated"
echo "[$(date +'%Y-%m-%d %H:%M:%S')] Setup completato."
exit 0
