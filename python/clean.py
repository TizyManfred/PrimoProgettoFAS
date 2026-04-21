#!/usr/bin/env python3
"""
clean.py — Pulizia e normalizzazione del dataset AviationData.csv
Produce: data/cleaned/aviation_clean.csv

Questo script è il primo step della pipeline dati. Si occupa di:
1. Caricare i dati grezzi.
2. Standardizzare i nomi delle colonne (snake_case).
3. Elaborare e validare le date.
4. Riempire i valori mancanti (NaN/Null) con default sensati per evitare rotture nell'analisi.
5. Creare nuove metriche e feature derivate, come la gravità dell'incidente o lo stato USA.
"""

import os
import sys
import pandas as pd
import numpy as np

# ---------- Configurazione Percorsi ----------
# BASE_DIR punta alla directory radice del progetto (PrimoProgetto)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_CSV = os.path.join(BASE_DIR, "AviationData.csv")
OUT_DIR = os.path.join(BASE_DIR, "data", "cleaned")
OUT_CSV = os.path.join(OUT_DIR, "aviation_clean.csv")


def load_raw(path: str) -> pd.DataFrame:
    """Carica il CSV grezzo."""
    print(f"[clean] Caricamento {path} ...")
    # L'encoding latin-1 previene errori di lettura causati da caratteri speciali presenti nel dataset NTSB
    # low_memory=False assicura che pandas legga interamente i tipi di dato senza "indovinarli" blocco per blocco
    df = pd.read_csv(path, encoding="latin-1", low_memory=False)
    print(f"[clean] Righe caricate: {len(df)}")
    return df


def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Rinomina le colonne dallo standard Camel.Case al più pythonico snake_case."""
    # Definiamo un dizionario esplicito per mappare solo le colonne di nostro interesse 
    # e renderne i nomi facili da usare nei dataframe.
    mapping = {
        "Event.Id": "event_id",
        "Investigation.Type": "investigation_type",
        "Accident.Number": "accident_number",
        "Event.Date": "event_date",
        "Location": "location",
        "Country": "country",
        "Latitude": "latitude",
        "Longitude": "longitude",
        "Airport.Code": "airport_code",
        "Airport.Name": "airport_name",
        "Injury.Severity": "injury_severity",
        "Aircraft.damage": "aircraft_damage",
        "Aircraft.Category": "aircraft_category",
        "Registration.Number": "registration_number",
        "Make": "make",
        "Model": "model",
        "Amateur.Built": "amateur_built",
        "Number.of.Engines": "number_of_engines",
        "Engine.Type": "engine_type",
        "FAR.Description": "far_description",
        "Schedule": "schedule",
        "Purpose.of.flight": "purpose_of_flight",
        "Air.carrier": "air_carrier",
        "Total.Fatal.Injuries": "total_fatal_injuries",
        "Total.Serious.Injuries": "total_serious_injuries",
        "Total.Minor.Injuries": "total_minor_injuries",
        "Total.Uninjured": "total_uninjured",
        "Weather.Condition": "weather_condition",
        "Broad.phase.of.flight": "broad_phase_of_flight",
        "Report.Status": "report_status",
        "Publication.Date": "publication_date",
    }
    df = df.rename(columns=mapping)
    return df


def parse_dates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Parsa la colonna event_date in un tipo 'datetime'.
    I record senza data vengono scartati perché impossibili da tracciare nel tempo.
    """
    # coerce trasforma le date non valide in NaT (Not a Time)
    df["event_date"] = pd.to_datetime(df["event_date"], errors="coerce")
    
    # Rimuoviamo ogni riga dove la data è risultata NaT
    df = df.dropna(subset=["event_date"])
    
    # Creiamo due colonne specifiche, molto più efficienti per i raggruppamenti statistici
    df["year"] = df["event_date"].dt.year.astype(int)
    df["month"] = df["event_date"].dt.month.astype(int)
    
    print(f"[clean] Righe valide dopo validazione date: {len(df)}")
    return df


def fill_missing(df: pd.DataFrame) -> pd.DataFrame:
    """
    Gestisce i famosi NaN (dati mancanti).
    Questo passaggio è fondamentale nel data science per non avere crash o deviazioni.
    """
    # 1. Se manca il dato sui feriti/vittime, assumiamo zero per consentire i calcoli matematici
    fill_zero = [
        "total_fatal_injuries",
        "total_serious_injuries",
        "total_minor_injuries",
        "total_uninjured",
    ]
    for col in fill_zero:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    # Convertiamo anche latitudine e longitudine in numerico per le mappe
    for col in ["latitude", "longitude"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # 2. Per le colonne di testo categoriche usiamo la label "Unknown" o "Sconosciuto"
    fill_unknown = [
        "weather_condition",
        "broad_phase_of_flight",
        "country",
        "purpose_of_flight",
        "aircraft_category",
        "engine_type",
        "aircraft_damage",
        "injury_severity",
    ]
    for col in fill_unknown:
        df[col] = df[col].fillna("Unknown").astype(str).str.strip()

    return df


def normalize_strings(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalizza le stringhe testuali evitando disallineamenti del tipo ' IMC' e 'imc'.
    Uniforma tutto con iniziali maiuscole (Title Case).
    """
    str_cols = [
        "weather_condition",
        "broad_phase_of_flight",
        "purpose_of_flight",
        "aircraft_category",
        "engine_type",
        "aircraft_damage",
        "country",
        "location",  # Aggiunto per normalizzare le città
    ]
    for col in str_cols:
        # str.strip() toglie spazi prima e dopo, str.title() mette la maiuscola ad ogni parola
        df[col] = df[col].astype(str).str.strip().str.title()
    return df


def group_categories(df: pd.DataFrame) -> pd.DataFrame:
    """
    Raggruppa acronimi e termini ridondanti che rappresentano la stessa categoria.
    Esempio: 'Unk' e 'Unknown' -> 'Unknown'
    """
    # Mappa universale per acronimi comuni
    generic_map = {
        "Unk": "Unknown",
        "Unknown": "Unknown",
        "None": "None",
    }
    
    # Mappe specifiche per categoria
    aircraft_map = {
        "Ultr": "Ultralight",
        "Wsft": "Weight-Shift",
    }
    aircraft_map.update(generic_map)
    
    # Applichiamo le mappature
    df["aircraft_category"] = df["aircraft_category"].replace(aircraft_map)
    df["engine_type"] = df["engine_type"].replace(generic_map)
    df["weather_condition"] = df["weather_condition"].replace(generic_map)
    
    return df


def add_derived_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Crea nuove colonne analitiche basandosi sui dati di partenza.
    Queste feature engineering aiuteranno la webapp a offrire visualizzazioni immediate.
    """
    # 1. Totale lesioni per evento (somma di fatali + gravi + lievi)
    df["total_injuries"] = (
        df["total_fatal_injuries"]
        + df["total_serious_injuries"]
        + df["total_minor_injuries"]
    )

    # 2. Assegna una classe sintetica di massima gravità all'incidente
    # np.select controlla le condizioni in ordine e sceglie il primo vero.
    conditions = [
        df["total_fatal_injuries"] > 0,
        df["total_serious_injuries"] > 0,
        df["total_minor_injuries"] > 0,
    ]
    choices = ["Fatal", "Serious", "Minor"]
    # Se nessuna condizione si verifica, di un incidente senza feriti sarà "None"
    df["severity_class"] = np.select(conditions, choices, default="None")

    # 3. Estrazione avanzata dello Stato Americano
    # Filtriamo solo le righe relative agli Stati Uniti
    mask_us = df["country"].str.contains("United States", case=False, na=False)
    df["us_state"] = ""
    # Tramite Regex, peschiamo la sigla a due lettere finale della location (ad es. "Texas, Tx" -> "TX")
    # Usiamo case=False perché normalize_strings ha reso la location Title Case (es. "Tx")
    df.loc[mask_us, "us_state"] = (
        df.loc[mask_us, "location"]
        .str.extract(r",\s*([a-zA-Z]{2})$", expand=False)
        .str.upper()
        .fillna("")
    )

    return df


def main():
    """Flusso principale dello script."""
    # Controllo che il file esista altrimenti causeremmo un crash fatale
    if not os.path.isfile(RAW_CSV):
        print(f"[ERRORE] File non trovato: {RAW_CSV}", file=sys.stderr)
        sys.exit(1)

    # Creazione della cartella per i dati puliti (se non esiste)
    os.makedirs(OUT_DIR, exist_ok=True)

    # Esecuzione in logica seriale delle regole di pulitura
    df = load_raw(RAW_CSV)
    df = rename_columns(df)
    df = parse_dates(df)
    df = fill_missing(df)
    df = normalize_strings(df)
    df = group_categories(df)
    df = add_derived_columns(df)

    # Salvataggio definitivo
    # index=False fa in modo di non salvare l'ID di riga di pandas (0, 1, 2) all'interno del CSV
    df.to_csv(OUT_CSV, index=False)
    print(f"[clean] Dataset pulito salvato in {OUT_CSV} ({len(df)} righe)")


if __name__ == "__main__":
    main()
