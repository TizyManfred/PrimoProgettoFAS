#!/usr/bin/env python3
"""analyze.py — Analisi statistiche e aggregazioni sul dataset pulito."""

import os
import sys
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEAN_CSV = os.path.join(BASE_DIR, "data", "cleaned", "aviation_clean.csv")
AGG_DIR = os.path.join(BASE_DIR, "data", "aggregated")


def load_clean() -> pd.DataFrame:
    if not os.path.isfile(CLEAN_CSV):
        print(f"[ERRORE] Dataset pulito non trovato: {CLEAN_CSV}", file=sys.stderr)
        sys.exit(1)
    df = pd.read_csv(CLEAN_CSV, low_memory=False)
    print(f"[analyze] Righe caricate: {len(df)}")
    return df


def accidents_per_year(df: pd.DataFrame):
    agg = df.groupby("year").agg(incidenti=("event_id", "count"), vittime_fatali=("total_fatal_injuries", "sum"), feriti_gravi=("total_serious_injuries", "sum"), feriti_lievi=("total_minor_injuries", "sum")).reset_index()
    out = os.path.join(AGG_DIR, "accidents_per_year.csv")
    agg.to_csv(out, index=False)
    print(f"[analyze] Salvato {out}")


def by_flight_phase(df: pd.DataFrame):
    agg = df.groupby("broad_phase_of_flight").agg(incidenti=("event_id", "count"), vittime_fatali=("total_fatal_injuries", "sum")).reset_index().sort_values("incidenti", ascending=False)
    out = os.path.join(AGG_DIR, "by_flight_phase.csv")
    agg.to_csv(out, index=False)
    print(f"[analyze] Salvato {out}")


def weather_vs_severity(df: pd.DataFrame):
    ct = pd.crosstab(df["weather_condition"], df["severity_class"]).reset_index()
    out = os.path.join(AGG_DIR, "weather_vs_severity.csv")
    ct.to_csv(out, index=False)
    print(f"[analyze] Salvato {out}")


def by_operation_type(df: pd.DataFrame):
    agg = df.groupby(["purpose_of_flight", "severity_class"]).agg(incidenti=("event_id", "count")).reset_index()
    out = os.path.join(AGG_DIR, "by_operation_type.csv")
    agg.to_csv(out, index=False)
    print(f"[analyze] Salvato {out}")


def by_us_state(df: pd.DataFrame):
    us = df[df["us_state"] != ""].copy()
    agg = us.groupby("us_state").agg(incidenti=("event_id", "count"), vittime_fatali=("total_fatal_injuries", "sum")).reset_index().sort_values("incidenti", ascending=False)
    out = os.path.join(AGG_DIR, "by_us_state.csv")
    agg.to_csv(out, index=False)
    print(f"[analyze] Salvato {out}")


def main():
    os.makedirs(AGG_DIR, exist_ok=True)
    df = load_clean()
    accidents_per_year(df)
    by_flight_phase(df)
    weather_vs_severity(df)
    by_operation_type(df)
    by_us_state(df)
    print("[analyze] Tutte le aggregazioni completate.")


if __name__ == "__main__":
    main()
