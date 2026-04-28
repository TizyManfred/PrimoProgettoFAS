# Relazione Tecnica e Documentazione del Codice: Aviation Accident Dashboard

## 1. Introduzione e Obiettivi del Progetto

Il progetto "Aviation Accident Dashboard" nasce con l'obiettivo di sviluppare una pipeline end-to-end per l'elaborazione, l'analisi e la visualizzazione dei dati relativi agli incidenti aerei, a partire dal dataset pubblico della NTSB (National Transportation Safety Board). 

Sviluppato per il corso di **Fondamenti di Amministrazione di Sistema**, il progetto mira a dimostrare competenze di bash, python scripting e docker. 

L'essenza del progetto non risiede solo nel visualizzare dati, ma nella **creazione di un flusso automatizzato (ETL - Extract, Transform, Load)** governato interamente da script bash, progettato per essere tollerante agli errori e facilmente containerizzabile tramite Docker.

> **Nota:** Per mantenere il codice sorgente pulito ed essenziale, i commenti prolissi sono stati rimossi dai file Python e dagli script Bash. Tutta la logica e il funzionamento dettagliato sono stati consolidati e spiegati in questo documento.

---

## 2. Architettura del Sistema e Logica Pipeline

Il progetto è suddiviso in componenti modulari (Microservizi logici), governati da un orchestratore principale (`run.sh`). La logica si articola in tre fasi principali:

### Fase 1: Setup e Verifica Ambiente (`scripts/00_setup.sh`)
- **Controllo Requisiti**: Verifica la presenza della corretta versione di Python e del dataset originale.
- **Isolamento**: Crea la struttura delle directory necessarie (`data/cleaned/`, `data/aggregated/`, `logs/`).
- **Dipendenze**: Installa i pacchetti necessari in un virtual environment per mantenere l'ambiente di sistema pulito.

### Fase 2: Elaborazione Dati (Data Pipeline)
Questa fase è il cuore analitico del progetto, scritta in Python per sfruttare le performance della libreria `pandas`.
- **Pulizia e Normalizzazione** (`scripts/01_clean.sh` -> `python/clean.py`):
    - Trasforma i dati grezzi in un formato "pulito".
    - **Feature Engineering**: Deriva nuove metriche complesse non presenti nel dataset originale.
    - **Normalizzazione Geografica**: Applica espressioni regolari avanzate per estrarre le sigle degli stati USA.
    - **Consolidamento Categorie**: Mappa acronimi multipli in categorie uniformi.
- **Analisi e Aggregazione** (`scripts/02_analyze.sh` -> `python/analyze.py`):
    - Elabora il dato pulito e produce dataset parziali già aggregati per metriche specifiche (temporale, per stato, ecc.).

### Fase 3: Visualizzazione Interattiva (`scripts/03_run_app.sh` -> `python/app.py`)
- L'applicazione web viene avviata su un web server generato in Python. La dashboard consuma direttamente il dataset clean in memoria, permettendo calcoli reattivi in tempo reale su combinazioni di filtri dinamici.

---

## 3. Tecnologie Utilizzate

- **Bash**: Per l'orchestrazione della pipeline. Gli script utilizzano `set -e`, `set -u`, `set -o pipefail` per gestire gli errori.
- **Python 3**: Linguaggio per l'elaborazione dei dati ed il motore web.
- **Pandas & NumPy**: Scelti come pilastro per il cleaning data e le operazioni matematiche complesse sui DataFrame.
- **Plotly Dash**: Framework reattivo scelto per sviluppare la Web Application (Backend e Frontend) in puro Python.
- **Docker & Docker Compose**: Per la virtualizzazione e la distribuzione dell'applicazione eliminando il problema "it works on my machine".

---

## 4. Dettaglio del Codice Python

Questa sezione documenta nel dettaglio il funzionamento dei file sorgenti.

### 4.1 `python/clean.py`
Questo script agisce come fase "Transform" dell'ETL:
*   **`rename_columns(df)`**: Converte i nomi delle colonne nel formato standard `snake_case` (es. `Event.Id` diventa `event_id`).
*   **`parse_dates(df)`**: Esegue il parsing di `event_date`, rimuovendo record non validi ed estraendo mese e anno per facilitare le aggregazioni.
*   **`fill_missing(df)`**: Gestisce i valori null (NaN); le variabili numeriche delle vittime vengono poste a 0, le variabili qualitative etichettate `"Unknown"`.
*   **`normalize_strings(df)`**: Rimuove spazi vuoti superflui e converte a "Title Case", uniformando le stringhe di testo.
*   **`group_categories(df)`**: Risolve problemi di varianti sintattiche (unendo `"Unk"`, `"Unknown"`, `"None"`).
*   **`add_derived_columns(df)`**:
    *   Calcola la gravità (`severity_class`) con `np.select`, valutando le soglie di vittime mortali vs feriti gravi.
    *   Sfrutta regex `r",\s*([a-zA-Z]{2})$"` sul campo `location` per estrapolare ed iniettare l'abbreviazione del singolo stato USA (`us_state`), fondamentale per le mappe regionalizzate.

### 4.2 `python/analyze.py`
Calcola aggregazioni specifiche basandosi sul CSV ripulito:
*   `accidents_per_year`: Tendenza storica.
*   `by_flight_phase`: Incidenti distribuiti durante le fasi (Takeoff, Cruise, Landing ecc.).
*   `weather_vs_severity`: Creazione di cross-tab per relazioni tra meteo IMC/VMC e tassi di fatalità.
*   `by_us_state`: Raggruppamento per geolocalizzazione USA.
*   Questa fase produce backup CSV persistenti molto utili in contesti esterni alla dashboard.

### 4.3 `python/app.py`
Il motore della UI interattiva.
*   **Caricamento Dati in RAM**: La funzione pre-carica i dati e crea mappature dinamiche (es `US_STATE_NAMES` per convertire la sigla "TX" su mappa visiva "Texas").
*   **Callback Ad Albero**: 
    1.  `update_model_options`: Questo callback incrocia i filtri "Tipo Aeromobile" e "Modello", bloccando/abilitando o filtrando le tendine in real-time così da scongiurare selezioni senza set di dati corrispondente.
    2.  `update_dashboard`: Callback primario. È connesso a ciascun dropdown/slider. Ogni variazione innesca lo smistamento condizionale tramite Pandas sull'intero dataset (`dff_main = dff_base.copy()`). In uscita, alimenta e ridisegna i KPI sommarli in cima (`kpi-totale`, `kpi-vittime`) e i quattro `dcc.Graph` centrali in meno di un secondo.
*   **Gestione Mappe (Dual-Mode)**: Nello sviluppo del grafico mappa, la logica include uno switch ("If us_state:"). Quando si analizza l'intero territorio mostra un layer `Choropleth` a zone di colore riempitive per ogni Stato. Ma qualora l'utente avesse filtrato uno stato specifico, re-inizializza il canvas passando a `Scattergeo`. In quest'ultimo ricalcola una Pivot sulle singole Coordinate, accorpandole ed ingrandendo sfericamente l'esplosione per la specifica `Città`.

---

## 5. Dettaglio Script Shell e Bash Automation

*   **`00_setup.sh`**: File preparatorio vituperante, fa accertamenti prima di operare (python e dati presenti) e crea la "bolla isolata" tramite istruzione `venv`.
*   **`01_clean.sh` & `02_analyze.sh`**: Pilotano l'interprete Python verso gli scrip precedentemente visti. Sono arricchiti con cattura di Logging estesa a `../logs` via instradamento `tee`. Se l'interprete da' codice != 0, le esecuzioni implodono a terminale evitando di sovrascrivere o corrompere i dati storici validi.
*   **`03_run_app.sh`**: Verifica di aver liberi i socket porte (`lsof -i:8050`). In condizioni eccellenti si tramuta nel processo demonizzato del Webserver Host Dashboard.
*   **`run.sh`**: Lo script entrypoint. Ha il permesso `+x` sulle sub routine. E' stato programmato con flag di testing `--no-serve` per eseguire solo le build dei microdati in pipeline arrestandosi prima della pubblicazione porta, tattica vitale in Docker.

---

## 6. L'Evoluzione verso DevOps: Docker e Distribuzione

Sebbene il programma potesse nascere e morire in ambiente locale Bash, si è compiuto lo sforzo progettuale di includere best practices di distribuzione.

Il **Dockerfile** sfrutta il "Layer Caching": 
- L'installazione dei numerosi pacchetti Python avviene a un livello separato del container (copiando solo `requirements.txt`). Così, piccole correzioni in locale sul codice non impattano i lunghi caricamenti del builder di PIP.
- Viene poi impacchettato l'ambiente di virtualizzazione (`ENV VIRTUAL_ENV`). Le pipeline bash pre-run di creazione dati sono messe dentro lo stato iniziale (`RUN ./run.sh --no-serve`), permettendo all'immagine compilata di possedere i set dati già lavorati per accelerare drasticamente il primo Boot su Cloud o Docker-Hub.

Il volume eventuale montato in `docker-compose.yml` è studiato per le sessioni development Live-Reloading in `dash`, velocizzando la visualizzazione dei cambiamenti Python a codice senza build container iterativi.
