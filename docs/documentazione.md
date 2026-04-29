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

La componente Python rappresenta il cuore analitico del progetto. Mentre gli script Bash orchestrano l’esecuzione della pipeline, il lavoro effettivo di trasformazione, analisi e visualizzazione dei dati viene svolto in Python, sfruttando librerie come `pandas`, `numpy` e `dash`.

L’architettura Python è suddivisa in tre moduli principali, ognuno con una responsabilità ben definita: pulizia del dato, aggregazione analitica e pubblicazione della dashboard web. Questa separazione rende il codice più leggibile, riusabile e facile da manutenere.

### `python/clean.py`

Questo script implementa la fase di pulizia e normalizzazione del dataset originale. Il suo compito è convertire i dati grezzi in un dataset coerente, standardizzato e pronto per essere elaborato nei passaggi successivi.

**Funzioni e feature principali**

- **Caricamento del dataset raw**: importa il file originale in un DataFrame `pandas`.
- **Data cleaning**: gestisce valori mancanti, uniforma i tipi di dato e corregge eventuali incoerenze nel dataset.
- **Feature engineering**: genera nuove colonne derivate utili all’analisi, non presenti nel dataset sorgente.
- **Normalizzazione geografica**: estrae e standardizza le sigle degli stati USA tramite espressioni regolari.
- **Consolidamento delle categorie**: uniforma valori testuali, acronimi e categorie ripetute o scritte in modo non omogeneo.
- **Esportazione del dato pulito**: salva il risultato nella cartella `data/cleaned/` per renderlo disponibile allo step di analisi.

---

### `python/analyze.py`

Questo script riceve in input il dataset già pulito e produce una serie di viste aggregate orientate all’analisi esplorativa e alla visualizzazione. È il modulo che trasforma il dato normalizzato in micro–dataset già ottimizzati per la dashboard.

**Funzioni e feature principali**

- **Lettura del dataset cleaned**: carica il file prodotto da `clean.py`.
- **Aggregazioni statistiche**: calcola indicatori e raggruppamenti per dimensioni rilevanti, ad esempio temporali, geografiche o categoriali.
- **Produzione di dataset intermedi**: crea tabelle aggregate specifiche per supportare grafici, filtri e metriche di sintesi.
- **Ottimizzazione per la visualizzazione**: riduce il carico computazionale lato dashboard preparando in anticipo i dati più costosi da calcolare.
- **Esportazione degli output analitici**: salva i risultati nella cartella `data/aggregated/`.

---

### `python/app.py`

Questo script definisce e avvia l’applicazione web interattiva sviluppata con Plotly Dash. La dashboard costituisce il livello finale del progetto, in cui i dataset elaborati dalla pipeline vengono esposti tramite grafici, filtri e componenti reattivi.

**Funzioni e feature principali**

- **Inizializzazione dell’app Dash**: crea il server applicativo e configura la struttura principale della web app.
- **Caricamento dei dati**: importa in memoria il dataset pulito e/o i dataset aggregati necessari alla visualizzazione.
- **Definizione del layout**: organizza componenti HTML, grafici Plotly, dropdown, slider e controlli interattivi.
- **Callback reattive**: aggiorna dinamicamente i grafici e le metriche in risposta alle interazioni dell’utente.
- **Avvio del server web**: espone la dashboard sulla porta configurata (tipicamente `8050`), rendendola raggiungibile via browser.
- **Compatibilità con Docker**: il server viene eseguito su `0.0.0.0`, così da risultare accessibile anche dall’host quando l’app gira in un container.

---

### Ruolo complessivo della componente Python

Nel complesso, il codice Python realizza l’intera catena di valore del dato:

1. **Acquisizione e pulizia** del dataset sorgente.
2. **Trasformazione e aggregazione** in strutture analitiche compatte.
3. **Esposizione interattiva** dei risultati tramite una dashboard web.

Questa suddivisione in moduli specializzati consente di mantenere separati i livelli di preprocessing, analisi e presentazione, seguendo una struttura chiara e facilmente estendibile.

---

## 5. Dettaglio Script Shell e Bash Automation

### `00_setup.sh`

Script preparatorio che effettua tutti i controlli prima di procedere con la pipeline.

- **Verifica prerequisiti**: controlla che siano presenti la versione corretta di Python e i dati di input necessari.
- **Ambiente isolato**: crea la “bolla” dell’ambiente virtuale tramite `venv`, evitando di contaminare il sistema globale.
- **Preparazione cartelle**: inizializza eventuali directory richieste dagli step successivi (ad es. per dati puliti, aggregati, log).

---

### `01_clean.sh`

Script di orchestrazione dedicato alla fase di pulizia: invoca lo script Python `clean.py` e gestisce logging ed errori relativi a questo step della pipeline.

- **Invocazione dello script Python di pulizia**: esegue `python/clean.py`, che produce il dataset *cleaned* a partire dal dato grezzo.
- **Logging esteso**: instrada l’output (stdout e/o stderr) verso la cartella `../logs` tramite `tee`, così da avere log persistenti e output leggibile a terminale.
- **Gestione degli errori**: controlla il codice di uscita dell’interprete Python e, se diverso da `0`, interrompe l’esecuzione per evitare di proseguire con dati non validi o parziali.

---

### `02_analyze.sh`

Script di orchestrazione dedicato alla fase di analisi e aggregazione: invoca lo script Python `analyze.py` e garantisce tracciabilità e robustezza di questo step.

- **Invocazione dello script Python di analisi**: esegue `python/analyze.py`, che legge il dataset pulito e genera i dataset aggregati necessari alla dashboard.
- **Logging esteso**: come per `01_clean.sh`, convoglia l’output verso `../logs` tramite `tee`, per mantenere uno storico delle esecuzioni analitiche.
- **Gestione degli errori**: interrompe la pipeline se il processo Python restituisce un codice di uscita diverso da `0`, prevenendo la pubblicazione o il riuso di aggregati incoerenti.

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