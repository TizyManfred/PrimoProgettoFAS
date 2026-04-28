# Usa Ubuntu 24.04 LTS come base
FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    lsof \
    && rm -rf /var/lib/apt/lists/*

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR /AnalisiIncidentiAerei

COPY python/requirements.txt python/requirements.txt
RUN pip install --no-cache-dir -r python/requirements.txt

COPY . /AnalisiIncidentiAerei
RUN chmod +x run.sh scripts/*.sh

RUN ./run.sh --no-serve

EXPOSE 8050

CMD ["./scripts/03_run_app.sh"]
