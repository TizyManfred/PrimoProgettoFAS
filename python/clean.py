#!/usr/bin/env python3
"""
clean.py — Pulizia e normalizzazione del dataset AviationData.csv
Produce: data/cleaned/aviation_clean.csv

Pipeline:
1. Carica dati grezzi
2. Standardizza colonne (snake_case)
3. Elabora e valida date
4. Gestisce valori mancanti
5. Crea metriche derivate (gravità, stato USA)
"""

import os
import sys
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_CSV = os.path.join(BASE_DIR, "AviationData.csv")
OUT_DIR = os.path.join(BASE_DIR, "data", "cleaned")
OUT_CSV = os.path.join(OUT_DIR, "aviation_clean.csv")


def load_raw(path: str) -> pd.DataFrame:
    print(f"[clean] Caricamento {path} ...")
    df = pd.read_csv(path, encoding="latin-1", low_memory=False)
    print(f"[clean] Righe caricate: {len(df)}")
    return df


def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    mapping = {
        "Event.Id": "event_id", "Investigation.Type": "investigation_type", "Accident.Number": "accident_number",
        "Event.Date": "event_date", "Location": "location", "Country": "country", "Latitude": "latitude",
        "Longitude": "longitude", "Airport.Code": "airport_code", "Airport.Name": "airport_name",
        "Injury.Severity": "injury_severity", "Aircraft.damage": "aircraft_damage",
        "Aircraft.Category": "aircraft_category", "Registration.Number": "registration_number",
        "Make": "make", "Model": "model", "Amateur.Built": "amateur_built",
        "Number.of.Engines": "number_of_engines", "Engine.Type": "engine_type",
        "FAR.Description": "far_description", "Schedule": "schedule", "Purpose.of.flight": "purpose_of_flight",
        "Air.carrier": "air_carrier", "Total.Fatal.Injuries": "total_fatal_injuries",
        "Total.Serious.Injuries": "total_serious_injuries", "Total.Minor.Injuries": "total_minor_injuries",
        "Total.Uninjured": "total_uninjured", "Weather.Condition": "weather_condition",
        "Broad.phase.of.flight": "broad_phase_of_flight", "Report.Status": "report_status",
        "Publication.Date": "publication_date",
    }
    return df.rename(columns=mapping)


def parse_dates(df: pd.DataFrame) -> pd.DataFrame:
    df["event_date"] = pd.to_datetime(df["event_date"], errors="coerce")
    df = df.dropna(subset=["event_date"])
    df["year"] = df["event_date"].dt.year.astype(int)
    df["month"] = df["event_date"].dt.month.astype(int)
    print(f"[clean] Righe valide dopo validazione date: {len(df)}")
    return df


def fill_missing(df: pd.DataFrame) -> pd.DataFrame:
    fill_zero = ["total_fatal_injuries", "total_serious_injuries", "total_minor_injuries", "total_uninjured"]
    for col in fill_zero:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
    for col in ["latitude", "longitude"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    fill_unknown = ["weather_condition", "broad_phase_of_flight", "country", "purpose_of_flight", "aircraft_category", "engine_type", "aircraft_damage", "injury_severity"]
    for col in fill_unknown:
        df[col] = df[col].fillna("Unknown").astype(str).str.strip()
    return df


def normalize_strings(df: pd.DataFrame) -> pd.DataFrame:
    str_cols = ["weather_condition", "broad_phase_of_flight", "purpose_of_flight", "aircraft_category", "engine_type", "aircraft_damage", "country", "location"]
    for col in str_cols:
        df[col] = df[col].astype(str).str.strip().str.title()
    return df


def group_categories(df: pd.DataFrame) -> pd.DataFrame:
    generic_map = {"Unk": "Unknown", "Unknown": "Unknown", "None": "None"}
    aircraft_map = {"Ultr": "Ultralight", "Wsft": "Weight-Shift", **generic_map}
    df["aircraft_category"] = df["aircraft_category"].replace(aircraft_map)
    df["engine_type"] = df["engine_type"].replace(generic_map)
    df["weather_condition"] = df["weather_condition"].replace(generic_map)
    return df


def add_derived_columns(df: pd.DataFrame) -> pd.DataFrame:
    df["total_injuries"] = df["total_fatal_injuries"] + df["total_serious_injuries"] + df["total_minor_injuries"]
    conditions = [df["total_fatal_injuries"] > 0, df["total_serious_injuries"] > 0, df["total_minor_injuries"] > 0]
    choices = ["Fatal", "Serious", "Minor"]
    df["severity_class"] = np.select(conditions, choices, default="None")
    mask_us = df["country"].str.contains("United States", case=False, na=False)
    df["us_state"] = ""
    df.loc[mask_us, "us_state"] = df.loc[mask_us, "location"].str.extract(r",\s*([a-zA-Z]{2})$", expand=False).str.upper().fillna("")
    return df


def main():
    if not os.path.isfile(RAW_CSV):
        print(f"[ERRORE] File non trovato: {RAW_CSV}", file=sys.stderr)
        sys.exit(1)
    os.makedirs(OUT_DIR, exist_ok=True)
    df = load_raw(RAW_CSV)
    df = rename_columns(df)
    df = parse_dates(df)
    df = fill_missing(df)
    df = normalize_strings(df)
    df = group_categories(df)
    df = add_derived_columns(df)
    df.to_csv(OUT_CSV, index=False)
    print(f"[clean] Dataset pulito salvato in {OUT_CSV} ({len(df)} righe)")


if __name__ == "__main__":
    main()
