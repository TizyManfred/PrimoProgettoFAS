# Usa Ubuntu 24.04 LTS come base
FROM ubuntu:24.04

# Variabili d'ambiente per apt non-interattivo
ENV DEBIAN_FRONTEND=noninteractive

# Installa Python 3, pip, venv e lsof (per il controllo porta)
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    lsof \
    && rm -rf /var/lib/apt/lists/*

# Crea e attiva un virtual environment (richiesto su Ubuntu >= 23.04)
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Working directory
WORKDIR /AnalisiIncidentiAerei

# STEP 1: Copia prima solo requirements.txt per sfruttare il layer cache di Docker
# In questo modo, modifiche al codice non invalidano il layer di installazione delle dipendenze
COPY python/requirements.txt python/requirements.txt

# STEP 2: Installa le dipendenze Python (layer cachato separatamente dal codice)
RUN pip install --no-cache-dir -r python/requirements.txt

# STEP 3: Copia il resto del progetto solo dopo aver installato le dipendenze
COPY . /AnalisiIncidentiAerei

# Rende eseguibili gli script bash
RUN chmod +x run.sh scripts/*.sh

# Esegue la pipeline dati (pulizia + analisi) durante il build
RUN ./run.sh --no-serve

# Porta esposta dalla dashboard Dash
EXPOSE 8050

# Avvio della web app
CMD ["./scripts/03_run_app.sh"]
