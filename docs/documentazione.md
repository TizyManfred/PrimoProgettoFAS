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

- **Controllo Requisiti**: verifica la presenza della corretta versione di Python e del dataset originale.
- **Isolamento**: crea la struttura delle directory necessarie (`data/cleaned/`, `data/aggregated/`, `logs/`).
- **Dipendenze**: installa i pacchetti necessari in un virtual environment per mantenere l'ambiente di sistema pulito.

---

### Fase 2: Pulizia e Normalizzazione Dati (`scripts/01_clean.sh` -> `python/clean.py`)

Questa fase trasforma il dataset grezzo in una base dati affidabile e coerente, pronta per l’analisi successiva.

- **Pulizia del dataset**: converte i dati grezzi in un formato strutturato e “pulito”.
- **Feature Engineering**: deriva nuove metriche complesse non presenti nel dataset originale.
- **Normalizzazione Geografica**: applica espressioni regolari avanzate per estrarre le sigle degli stati USA.
- **Consolidamento Categorie**: mappa acronimi multipli in categorie uniformi.
- **Output intermedio**: salva un dataset *cleaned* riutilizzabile dagli step successivi.

---

### Fase 3: Analisi e Aggregazione (`scripts/02_analyze.sh` -> `python/analyze.py`)

Questa fase prende in input il dataset già pulito e produce viste aggregate orientate all’analisi.

- **Elaborazione analitica**: carica il dataset *cleaned* e applica trasformazioni orientate all’analisi.
- **Aggregazioni mirate**: genera dataset parziali già aggregati per metriche specifiche (temporale, per stato, per categoria, ecc.).
- **Ottimizzazione per la dashboard**: prepara output leggeri e già strutturati per il layer di visualizzazione.
- **Output finale**: salva i dataset aggregati in `data/aggregated/`.

---

### Fase 4: Visualizzazione Interattiva (`scripts/03_run_app.sh` -> `python/app.py`)

L’applicazione web espone una dashboard interattiva basata sui dataset prodotti dalla pipeline.

- L’applicazione web viene avviata su un web server generato in Python.
- La dashboard consuma direttamente il dataset *cleaned* (ed eventualmente quelli aggregati) in memoria, permettendo calcoli reattivi in tempo reale su combinazioni di filtri dinamici.

---

## 3. Tecnologie Utilizzate

- **Bash**: Per l'orchestrazione della pipeline. Gli script utilizzano `set -e`, `set -u`, `set -o pipefail` per gestire gli errori.
- **Python 3**: Linguaggio per l'elaborazione dei dati ed il motore web.
- **Pandas & NumPy**: Scelti come pilastro per il cleaning data e le operazioni matematiche complesse sui DataFrame.
- **Plotly Dash**: Framework reattivo scelto per sviluppare la Web Application (Backend e Frontend) in puro Python.
- **Docker & Docker Compose**: Per la virtualizzazione e la distribuzione dell'applicazione eliminando il problema "it works on my machine".

---

## 4. Dettaglio del Codice Python

### `00_setup.sh`

Questo script è il punto di ingresso tecnico della pipeline: esegue i controlli preliminari sull’ambiente e prepara tutto ciò che serve agli step successivi. In pratica si assicura che Python, i dati e le directory siano in ordine prima di far partire qualsiasi elaborazione.

**Funzioni e feature principali**

- **Verifica prerequisiti**: controlla che siano presenti la versione corretta di Python e i dati di input necessari.
- **Creazione ambiente isolato**: configura un ambiente virtuale tramite `venv`, così da installare le dipendenze senza toccare il sistema globale.
- **Inizializzazione cartelle**: crea (se mancanti) le directory utilizzate dalla pipeline, ad esempio per dati puliti, dati aggregati e file di log.

---

### `01_clean.sh` e `02_analyze.sh`

Questi script fungono da “regia” per la parte analitica della pipeline: orchestrano l’esecuzione degli script Python dedicati a pulizia e analisi, tracciando tutto sui log e fermando la catena in caso di errori.

**Funzioni e feature principali**

- **Invocazione degli script Python**: eseguono, rispettivamente, gli script di pulizia e quelli di analisi/aggregazione dei dati.
- **Logging esteso**: instradano l’output verso la cartella `../logs` tramite `tee`, così da avere log persistenti e output leggibile a terminale in un colpo solo.
- **Gestione robusta degli errori**: verificano il codice di uscita dell’interprete Python e, se diverso da `0`, interrompono l’esecuzione per evitare sovrascritture o corruzione dei dati storici validi.

---

### `03_run_app.sh`

Questo script si occupa di avviare in modo sicuro l’applicazione web che espone la dashboard, verificando prima che le risorse di rete necessarie siano disponibili. In questo modo l’ambiente applicativo parte solo quando le condizioni sono corrette.

**Funzioni e feature principali**

- **Controllo disponibilità porta**: verifica che la porta prevista per il servizio (ad es. `8050`) sia libera, ad esempio tramite `lsof -i:8050`.
- **Avvio del webserver**: quando i controlli sono superati, avvia il processo che esegue il web server ospitando la dashboard, eventualmente in modalità demonizzata per mantenerlo in esecuzione in background.

---

### `run.sh`

Questo script è l’*entrypoint* della pipeline: coordina l’esecuzione di tutti gli step Bash, offrendo anche una modalità “solo build dati” utile in contesti di test e containerizzazione. È il comando unico che l’utente deve lanciare per far girare l’intero flusso.

**Funzioni e feature principali**

- **Coordinamento degli step**: invoca in sequenza le sotto–routine (`00_setup.sh`, `01_clean.sh`, `02_analyze.sh`, `03_run_app.sh`), per le quali ha i permessi di esecuzione (`+x`).
- **Flag di test `--no-serve`**: permette di eseguire solo la generazione dei micro–dati (pulizia e analisi), arrestando la pipeline prima dell’esposizione sulla porta; questo comportamento è particolarmente comodo in ambienti containerizzati come Docker, dove spesso si vuole testare la build senza avviare il servizio HTTP.

---

## 5. Dettaglio Script Shell e Bash Automation

### `00_setup.sh`

Script preparatorio che effettua tutti i controlli prima di procedere con la pipeline.

- **Verifica prerequisiti**: controlla che siano presenti la versione corretta di Python e i dati di input necessari.
- **Ambiente isolato**: crea la “bolla” dell’ambiente virtuale tramite `venv`, evitando di contaminare il sistema globale.
- **Preparazione cartelle**: inizializza eventuali directory richieste dagli step successivi (ad es. per dati puliti, aggregati, log).

---

### `01_clean.sh` e `02_analyze.sh`

Script di orchestrazione che pilotano l’interprete Python verso gli script analitici della pipeline.

- **Invocazione degli script Python**: eseguono, rispettivamente, gli script di pulizia e quelli di analisi/aggregazione dei dati.
- **Logging esteso**: instradano l’output verso `../logs` utilizzando `tee`, in modo da avere sia log persistenti sia output visibile a terminale.
- **Gestione degli errori**: se l’interprete Python termina con codice di uscita diverso da `0`, l’esecuzione viene interrotta, prevenendo sovrascritture o corruzione dei dati storici validi.

---

### `03_run_app.sh`

Script responsabile dell’avvio dell’applicazione web (dashboard).

- **Controllo porte**: verifica che la porta prevista per il servizio (es. `8050`) sia libera, ad esempio tramite `lsof -i:8050`.
- **Avvio webserver**: in condizioni corrette, avvia il processo che esegue il web server ospitando la dashboard, eventualmente in modalità demonizzata.

---

### `run.sh`

Script di *entrypoint* della pipeline.

- **Coordinamento degli step**: invoca in sequenza le sotto–routine (`00_setup.sh`, `01_clean.sh`, `02_analyze.sh`, `03_run_app.sh`), per le quali ha i permessi di esecuzione (`+x`).
- **Flag di test `--no-serve`**: consente di eseguire solo la build dei micro–dati (pulizia e analisi) arrestando la pipeline prima dell’esposizione sulla porta, approccio particolarmente utile in ambienti containerizzati (es. Docker).

---

## 6. L'Evoluzione verso DevOps: Docker e Distribuzione

Sebbene il programma potesse nascere e morire in ambiente locale Bash, si è compiuto lo sforzo progettuale di includere best practices di distribuzione.

Il **Dockerfile** sfrutta il "Layer Caching": 
- L'installazione dei numerosi pacchetti Python avviene a un livello separato del container (copiando solo `requirements.txt`). Così, piccole correzioni in locale sul codice non impattano i lunghi caricamenti del builder di PIP.
- Viene poi impacchettato l'ambiente di virtualizzazione (`ENV VIRTUAL_ENV`). Le pipeline bash pre-run di creazione dati sono messe dentro lo stato iniziale (`RUN ./run.sh --no-serve`), permettendo all'immagine compilata di possedere i set dati già lavorati per accelerare drasticamente il primo Boot su Cloud o Docker-Hub.

Il volume eventuale montato in `docker-compose.yml` è studiato per le sessioni development Live-Reloading in `dash`, velocizzando la visualizzazione dei cambiamenti Python a codice senza build container iterativi.