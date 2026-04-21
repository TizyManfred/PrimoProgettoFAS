# Relazione Tecnica: Aviation Accident Dashboard

## 1. Introduzione e Obiettivi del Progetto

Il progetto "Aviation Accident Dashboard" nasce con l'obiettivo di sviluppare una pipeline end-to-end per l'elaborazione, l'analisi e la visualizzazione dei dati relativi agli incidenti aerei, a partire dal dataset pubblico della NTSB (National Transportation Safety Board). 

Sviluppato per il corso di **Fondamenti di Amministrazione di Sistema**, il progetto mira a dimostrare competenze di bash, python scripting e docker. 

L'essenza del progetto non risiede solo nel visualizzare dati, ma nella **creazione di un flusso automatizzato (ETL - Extract, Transform, Load)** governato interamente da script bash, progettato per essere tollerante agli errori e facilmente containerizzabile tramite Docker.

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
    - **Normalizzazione Geografica**: Applica espressioni regolari avanzate per estrarre le sigle degli stati USA e raggruppa le città per evitare ridondanze.
    - **Consolidamento Categorie**: Mappa acronimi multipli (es. "UNK", "Unknown") in categorie uniformi.
- **Analisi e Aggregazione** (`scripts/02_analyze.sh` -> `python/analyze.py`):
    - Elabora il dato pulito e produce dataset parziali già aggregati per le metriche principali (andamento temporale, fase di volo, ecc.).
    - > [!NOTE]
      > **Evoluzione Tecnica**: Inizialmente questi dataset parziali venivano utilizzati direttamente dalla dashboard per semplificare il rendering dei grafici statici. Con l'aumento dell'interattività (filtri incrociati dinamici, zoom sulle mappe e drill-down sui modelli), l'utilizzo di file pre-aggregati è diventato eccessivamente complesso da gestire. Si è quindi optato per il caricamento del dataset integrale "clean" in `app.py`, permettendo calcoli reattivi in tempo reale su qualsiasi combinazione di filtri.

### Fase 3: Visualizzazione Interattiva (`scripts/03_run_app.sh` -> `python/app.py`)
- L'applicazione web viene avviata su un web server generato in Python. La dashboard consuma direttamente i dati preparati nella Fase 2, garantendo tempi di caricamento e rendering dei grafici millisecondi.

---

## 3. Tecnologie Utilizzate

- **Bash**: Linguaggio principale per l'orchestrazione della pipeline. Gli script utilizzano standard industriali (`set -e`, `set -u`, `set -o pipefail`) per una gestione rigorosa degli errori.
- **Python 3**: Linguaggio per l'elaborazione dei dati ed il motore web.
- **Pandas & NumPy**: Scelti come pilastro per il cleaning data e le operazioni matematiche complesse sui DataFrame.
- **Plotly Dash**: Framework reattivo scelto per sviluppare la Web Application (Backend e Frontend) in puro Python, senza dover ricorrere a complessi bridge Javascript/HTML.
- **Docker & Docker Compose**: Per la virtualizzazione e la distribuzione dell'applicazione eliminando il problema delle dipendenze incrociate o di sistema operativo ("it works on my machine").

---

## 4. Analisi delle Feature di Data Engineering

Il file `clean.py` applica trasformazioni significative al dataset grezzo per renderlo analizzabile:

### Estrazione Consolidata dello Stato USA
Per limitare il campo visivo alle mappe regionali, è stato necessario estrapolare la sigla (Es. "TX") da una stringa complessa ("HOUSTON, Tx"). Si è optato per un'analisi Regex case-insensitive e normalizzazione del risultato finale.
```python
df.loc[mask_us, "us_state"] = (
    df.loc[mask_us, "location"]
    .str.extract(r",\s*([a-zA-Z]{2})$", expand=False)
    .str.upper()
    .fillna("")
)
```

### Calcolo Sintetico della Gravità (`severity_class`)
Il dataset indica solo il numero di feriti per tipologia. Tramite `numpy.select` viene calcolata una classe sintetica utile per i filtri e le visualizzazioni a torta:
1.  Vittime fatali > 0 → **Fatal**
2.  Feriti gravi > 0 → **Serious**
3.  Feriti lievi > 0 → **Minor**

### Gestione Categorie e Raggruppamento Mappe
- Acronimi duplicati (`wsft` e `Weight-Shift`) vengono riuniti in un'unica categoria per non avere barre doppie nei grafici.
- Le coordinate vengono calcolate "per città", estrapolando il nome dal campo Location e aggregando i valori tramite la media (`mean`) di Latitudine e Longitudine. Questo previene la presenza di "molteplici bolle per la stessa città" nella mappa.

---

## 5. Visualizzazione Dati e Dashboard UX

L'approccio scelto per la Dashboard (nel file `python/app.py`) è mirato a trasformare numeri astratti in informazioni azionabili dall'utente.

### Flusso Interattivo
Una caratteristica avanzata sviluppata in questo progetto è la **connettività a cascata dei filtri**:
- Se il filtro "Tipo di Aeromobile" è vuoto, il filtro "Modello" è bloccato e disabilitato per prevenire query impossibili.
- Scegliendo un tipo (es. "Helicopter"), l'elenco dei modelli si popolerà dinamicamente solo con quelli compatibili.

### I Grafici Mostrati
1. **KPI Riassuntivi (In testa)**: Indicatori ad alto impatto visivo ("Incidenti Totali", "Vittime Fatali", "% Guida Strumentale/IMC") che mutano istantaneamente variando i filtri.
2. **Trend Storico**: Grafico a linea dinamico che traccia l'evoluzione degli schianti per anno solare. Utile per analizzare i pattern temporali.
3. **Mappa Geografica Adattativa**: 
    - Se nessun stato è selezionato, esegue il rendering in modalità "Choropleth" (sfumatura cromatica sull'intero territorio USA base alla concentrazione incidenti).
    - Qualora venga selezionato uno stato (es. "Texas"), il grafico ricalcola istantaneamente il layout operando uno zoom centrato su quello stato e mostra bolle scalari la cui dimensione indica l'intensità di occorrenza presso quella singola città (calcolando la media aggregata delle coordinate limitrofe).
4. **Ranking Categorie/Modelli (Grafico a Barre)**: Classifica orizzontale che mostra in modo intuitivo quali aeromobili risultano i più frequentemente coinvolti. Cambia forma (da categoria a modelli top-10) in base al livello di filtraggio applicato.
5. **Diagramma a Torta Fasi Generali Volo**: Rappresentazione proporzionale di quando avvengono gli eventi (Decollo, Crociera, Atterraggio, Manovra). Emerge storicamente una forte incidenza delle fasi preparative finali prima dell'arrivo sulla pista.

---

## 6. L'Evoluzione verso DevOps: Docker
Sebbene il programma potesse nascere e morire in ambiente locale Bash, si è compiuto lo sforzo progettuale di includere best practices di distribuzione.

Il **Dockerfile** sfrutta il caching ("Layer Caching"): l'installazione dei numerosi pacchetti Python pesanti avviene a un livello separato del container (dopo aver copiato solo `requirements.txt`). Così, test e rapide correzioni in locale o successive build impattano esclusivamente sul caricamento del livello di esecuzione finale.

Il volume montato nel file **docker-compose.yml** consente, durante lo sviluppo, un live-reload in caso di editing: non è necessario riavviare o ricostruire il container se si modifica un file Python, velocizzando enormemente lo sviluppo. Le limitazioni in porta e l'orchestration assicurano un contenimento dell'applicativo che risulta isolato e performante.
