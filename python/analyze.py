#!/usr/bin/env python3
"""
analyze.py — Analisi statistiche e aggregazioni sul dataset pulito.
Produce file CSV pre-computati e alleggeriti nella cartella data/aggregated/.

Perché farlo? Per motivi di performance (e per seguire le guidelines di buone architetture).
Raggruppare i dati una volta sola e salvare il risultato in CSV leggeri permette al server Web di rispondere alle visualizzazioni in decimi di secondo senza dover costantemente fare calcoli complessi (SUM, COUNT) su 90k righe.
"""

import os
import sys
import pandas as pd

# ---------- Configurazione Percorsi ----------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEAN_CSV = os.path.join(BASE_DIR, "data", "cleaned", "aviation_clean.csv")
AGG_DIR = os.path.join(BASE_DIR, "data", "aggregated")


def load_clean() -> pd.DataFrame:
    """Carica il risultato della pulizia prodotta da clean.py"""
    if not os.path.isfile(CLEAN_CSV):
        print(f"[ERRORE] Dataset pulito non trovato: {CLEAN_CSV}", file=sys.stderr)
        sys.exit(1)
    df = pd.read_csv(CLEAN_CSV, low_memory=False)
    print(f"[analyze] Righe caricate: {len(df)}")
    return df


def accidents_per_year(df: pd.DataFrame):
    """
    Raggruppa gli eventi anno per anno.
    Questa metrica mostra il trend di sicurezza aerea nel tempo (grafico a linee nella dashboard).
    """
    agg = (
        df.groupby("year")
        .agg(
            incidenti=("event_id", "count"),                 # Conta il numero totale di file (event_id è univoco)
            vittime_fatali=("total_fatal_injuries", "sum"),  # Somma delle vittime
            feriti_gravi=("total_serious_injuries", "sum"),  # Somma dei feriti gravi
            feriti_lievi=("total_minor_injuries", "sum"),    # Somma dei feriti lievi
        )
        .reset_index() # Resetta l'indice Pandas per trasformare "year" nuovamente in colonna standard
    )
    out = os.path.join(AGG_DIR, "accidents_per_year.csv")
    agg.to_csv(out, index=False)
    print(f"[analyze] Salvato {out}")


def by_flight_phase(df: pd.DataFrame):
    """
    Distribuzione degli incidenti rispetto al momento (fase) in cui sono accaduti:
    es. Decollo (Takeoff), Atterraggio (Landing), Crociera (Cruise).
    """
    agg = (
        df.groupby("broad_phase_of_flight")
        .agg(
            incidenti=("event_id", "count"),
            vittime_fatali=("total_fatal_injuries", "sum"),
        )
        .reset_index()
        # Ordina decrescente in modo che la dashboard mostri subito la fase più letale
        .sort_values("incidenti", ascending=False)
    )
    out = os.path.join(AGG_DIR, "by_flight_phase.csv")
    agg.to_csv(out, index=False)
    print(f"[analyze] Salvato {out}")


def weather_vs_severity(df: pd.DataFrame):
    """
    Tabella pivot / matrice (crosstab) tra le Condizioni Metereologiche (IMC, VMC, Unknown) 
    e le Classi di Gravità (Fatal, Serious, Minor, None).
    Serve per alimentare la mappa termica o bar chart stratificate.
    """
    # pd.crosstab incrocia le occorrenze delle due colonne tra di loro
    ct = pd.crosstab(df["weather_condition"], df["severity_class"])
    ct = ct.reset_index()
    out = os.path.join(AGG_DIR, "weather_vs_severity.csv")
    ct.to_csv(out, index=False)
    print(f"[analyze] Salvato {out}")


def by_operation_type(df: pd.DataFrame):
    """
    Aggrega gli incidenti a seconda dello scopo del volo (Personale, Esercitazione, Commerciale, Trasporto)
    segmentando i risultati per gravità.
    """
    # Doppio raggruppamento
    agg = (
        df.groupby(["purpose_of_flight", "severity_class"])
        .agg(incidenti=("event_id", "count"))
        .reset_index()
    )
    out = os.path.join(AGG_DIR, "by_operation_type.csv")
    agg.to_csv(out, index=False)
    print(f"[analyze] Salvato {out}")


def by_us_state(df: pd.DataFrame):
    """
    Filtra tutto il dataset ed estrae soltanto gli incidenti occorsi nei territori riconosciuti USA
    per poter posizionare il report sulla mappa Choropleth interattiva di Plotly (Stati Americani).
    """
    # Esclude i record senza 'us_state', che sono di solito incidenti internazionali o nulli
    us = df[df["us_state"] != ""].copy()
    
    agg = (
        us.groupby("us_state")
        .agg(
            incidenti=("event_id", "count"),
            vittime_fatali=("total_fatal_injuries", "sum"),
        )
        .reset_index()
        .sort_values("incidenti", ascending=False)
    )
    out = os.path.join(AGG_DIR, "by_us_state.csv")
    agg.to_csv(out, index=False)
    print(f"[analyze] Salvato {out}")


def main():
    """Flusso principale dell'analisi seriale."""
    # Crea la directory di output qualora non esistesse
    os.makedirs(AGG_DIR, exist_ok=True)
    df = load_clean()

    # Richiama in sequenza le metodologie di computazione
    accidents_per_year(df)
    by_flight_phase(df)
    weather_vs_severity(df)
    by_operation_type(df)
    by_us_state(df)

    print("[analyze] Tutte le aggregazioni completate.")


if __name__ == "__main__":
    main()
