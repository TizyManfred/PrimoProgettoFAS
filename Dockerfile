# Usa Ubuntu 24.04 LTS come base
FROM ubuntu:24.04

# Variabili d'ambiente per apt non-interattivo
ENV DEBIAN_FRONTEND=noninteractive

# Installa Python 3, pip, venv e lsof
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    lsof \
    && rm -rf /var/lib/apt/lists/*

# Crea un virtual environment isolato (richiesto da Ubuntu >= 23.04)
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Working directory
WORKDIR /AnalisiIncidentiAerei

# Copia e installa le dipendenze Python prima del codice (ottimizza la cache Docker)
COPY python/requirements.txt python/requirements.txt
RUN pip install --no-cache-dir -r python/requirements.txt

# Copia il progetto e rende eseguibili gli script della pipeline
COPY . /AnalisiIncidentiAerei
RUN chmod +x run.sh scripts/*.sh

# Esegue la pipeline dati (pulizia + analisi) durante il build
RUN ./run.sh --no-serve

# Porta esposta dalla dashboard Dash
EXPOSE 8050

# Avvio della web app
CMD ["./scripts/03_run_app.sh"]
