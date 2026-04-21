# Aviation Accident Dashboard

Dashboard interattiva per l'analisi degli incidenti aerei del dataset pubblico NTSB,
sviluppata per il corso di **Fondamenti di Amministrazione di Sistema**.

---

## Avvio Rapido

### Metodo 1 — Esecuzione locale (Bash + Python)

```bash
cd PrimoProgetto
chmod +x run.sh
bash run.sh
```

La dashboard sarà disponibile su: **http://localhost:8050**

### Metodo 2 — Docker (consigliato)

```bash
docker compose up --build
```

La dashboard sarà disponibile su: **http://localhost:8050**

---

## Struttura del Progetto

```
PrimoProgetto/
├── AviationData.csv          ← Dataset NTSB originale
├── run.sh                    ← Entry point principale
├── Dockerfile
├── docker-compose.yml
│
├── scripts/
│   ├── 00_setup.sh           ← Verifica prerequisiti e installa dipendenze
│   ├── 01_clean.sh           ← Avvia la pulizia dati
│   ├── 02_analyze.sh         ← Avvia le analisi statistiche
│   └── 03_run_app.sh         ← Avvia la web app
│
├── python/
│   ├── requirements.txt
│   ├── clean.py              ← Pulizia e normalizzazione dataset
│   ├── analyze.py            ← Aggregazioni statistiche
│   └── app.py                ← Dashboard Dash (Python puro, no HTML)
│
├── data/                     ← Generato dalla pipeline
│   ├── cleaned/
│   └── aggregated/
│
├── logs/                     ← Log di esecuzione
└── docs/
    └── documentazione.md     ← Documentazione tecnica completa
```

## Prerequisiti Locali

- Python 3.10+
- pip3
- Bash (macOS / Linux)
- (Opzionale) Docker e Docker Compose
