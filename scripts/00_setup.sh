#!/bin/bash
# 00_setup.sh — Verifica prerequisiti e prepara l'ambiente

set -euo pipefail

cd "$(dirname "$0")"
mkdir -p ../logs

LOG_FILE="../logs/setup.log"
exec > >(tee -i "$LOG_FILE") 2>&1

echo "[$(date +'%Y-%m-%d %H:%M:%S')] Avvio setup ambiente..."
PROJECT_ROOT=$(dirname "$(pwd)")

# Verifica CSV Grezzo
if [ ! -f "$PROJECT_ROOT/AviationData.csv" ]; then
    echo "[ERRORE] Il file AviationData.csv non è presente in $PROJECT_ROOT"
    echo "Assicurati di aver scaricato il dataset originale in quest'area."
    exit 1
fi
echo "✓ Dataset originale trovato."

# Verifica Python
if ! command -v python3 &> /dev/null; then
    echo "[ERRORE] python3 non è installato o non è nel PATH."
    exit 1
fi
echo "✓ Python trovato: $(python3 --version)"

# Verifica PIP
if ! command -v pip3 &> /dev/null && ! command -v pip &> /dev/null; then
    echo "[ERRORE] pip non è installato."
    exit 1
fi

# --- Gestione Virtual Environment locale ---
# Se non siamo già all'interno di un venv (es. Docker attiva il suo /opt/venv),
# ne creiamo uno locale .venv per non inquinare il sistema operativo host.
VENV_DIR="$PROJECT_ROOT/.venv"
if [ -z "${VIRTUAL_ENV:-}" ]; then
    if [ ! -d "$VENV_DIR" ]; then
        echo "Creazione virtual environment in $VENV_DIR..."
        python3 -m venv "$VENV_DIR"
        echo "✓ Virtual environment creato."
    else
        echo "✓ Virtual environment già esistente in $VENV_DIR."
    fi
    # shellcheck source=/dev/null
    source "$VENV_DIR/bin/activate"
    echo "✓ Virtual environment attivato: $VIRTUAL_ENV"
else
    echo "✓ Già all'interno di un virtual environment: $VIRTUAL_ENV"
fi
# ------------------------------------------

echo "Installazione dipendenze Python in corso..."
pip install --quiet --disable-pip-version-check -r "$PROJECT_ROOT/python/requirements.txt"
echo "✓ Dipendenze Python installate."

# Creazione cartelle
mkdir -p "$PROJECT_ROOT/data/cleaned" "$PROJECT_ROOT/data/aggregated" "$PROJECT_ROOT/logs" "$PROJECT_ROOT/docs"
echo "✓ Struttura directory creata."

echo "[$(date +'%Y-%m-%d %H:%M:%S')] Setup completato con successo."
exit 0
