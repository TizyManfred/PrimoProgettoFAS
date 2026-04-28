#!/usr/bin/env python3
"""
app.py — Dashboard interattiva Plotly Dash

Architettura:
- Layout: Componenti Python che generano HTML/CSS/JS
- Callbacks: Funzioni reattive che si eseguono quando input cambiano
- Dati: Caricati in memoria all'avvio per filtering dinamico
"""

import os
import pandas as pd
import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEAN_CSV = os.path.join(BASE_DIR, "data", "cleaned", "aviation_clean.csv")

app = dash.Dash(__name__, title="Aviation Dashboard",
                external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server


def load_data():
    """Carica dataset pulito in memoria."""
    if not os.path.exists(CLEAN_CSV):
        return pd.DataFrame()
    df = pd.read_csv(CLEAN_CSV, low_memory=False)
    df["make_model"] = (df["make"].fillna("") + " " + df["model"].fillna("")).str.strip()
    return df


df = load_data()

US_STATE_NAMES = {
    'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas', 'CA': 'California', 'CO': 'Colorado',
    'CT': 'Connecticut', 'DE': 'Delaware', 'FL': 'Florida', 'GA': 'Georgia', 'HI': 'Hawaii', 'ID': 'Idaho',
    'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa', 'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Louisiana',
    'ME': 'Maine', 'MD': 'Maryland', 'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi',
    'MO': 'Missouri', 'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada', 'NH': 'New Hampshire', 'NJ': 'New Jersey',
    'NM': 'New Mexico', 'NY': 'New York', 'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio', 'OK': 'Oklahoma',
    'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina', 'SD': 'South Dakota',
    'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah', 'VT': 'Vermont', 'VA': 'Virginia', 'WA': 'Washington',
    'WV': 'West Virginia', 'WI': 'Wisconsin', 'WY': 'Wyoming', 'DC': 'District of Columbia', 'PR': 'Puerto Rico'
}

WEATHER_LABELS = {
    'Vmc': 'Visuali (VMC)',
    'Imc': 'Strumentali (IMC)',
    'Unknown': 'Sconosciuto',
}

if not df.empty:
    years = sorted(df["year"].dropna().unique().tolist())
    aircrafts = sorted(df["aircraft_category"].dropna().unique().tolist())
    operations = sorted(df["purpose_of_flight"].dropna().unique().tolist())
    weathers = sorted(df["weather_condition"].dropna().unique().tolist())
    raw_states = df["us_state"].dropna().replace("", pd.NA).dropna().unique().tolist()
    us_states_list = sorted([s for s in raw_states if s in US_STATE_NAMES])
else:
    years, aircrafts, operations, weathers, us_states_list = [], [], [], [], []


app.layout = dbc.Container([
    dbc.Row(dbc.Col(html.H2("✈️ Aviation Accident Dashboard", 
                            className="text-center py-4 main-title text-dark mb-5"))),

    dbc.Row([
        dbc.Col(html.Div([
            dbc.Row([
                dbc.Col(html.H5("⚙️ FILTRI DATI", className="kpi-title m-0 mb-3"), md=12)
            ]),
            dbc.Row([
                dbc.Col([
                    html.Label("Periodo:", className="kpi-title"),
                    dcc.RangeSlider(
                        id='year-slider',
                        min=min(years) if years else 1980,
                        max=max(years) if years else 2023,
                        step=1,
                        value=[min(years), max(years)] if years else [1980, 2023], 
                        marks={y: str(y) for y in range(int(min(years) if years else 1980), int(max(years) if years else 2023)+1, 20)},
                        className="mt-2"
                    )
                ], md=2),

                dbc.Col([
                    html.Label("Tipo:", className="kpi-title"),
                    dcc.Dropdown(
                        id='aircraft-dropdown',
                        options=[{'label': x, 'value': x} for x in aircrafts], 
                        placeholder="Tutti i tipi...",
                        clearable=True
                    )
                ], md=2),

                dbc.Col([
                    html.Label("Modello:", className="kpi-title"),
                    dcc.Dropdown(
                        id='model-dropdown',
                        options=[], 
                        placeholder="Prima seleziona un tipo...",
                        clearable=True,
                        disabled=True
                    )
                ], md=2),

                dbc.Col([
                    html.Label("Scopo:", className="kpi-title"),
                    dcc.Dropdown(
                        id='operation-dropdown',
                        options=[{'label': x, 'value': x} for x in operations],
                        placeholder="Tutti gli scopi...",
                        clearable=True
                    )
                ], md=2),

                dbc.Col([
                    html.Label("Stile di Guida:", className="kpi-title"),
                    dcc.Dropdown(
                        id='weather-dropdown',
                        options=[{'label': WEATHER_LABELS.get(x, x), 'value': x} for x in weathers],
                        placeholder="Tutti...",
                        clearable=True
                    )
                ], md=2),

                dbc.Col([
                    html.Label("Stato USA:", className="kpi-title"),
                    dcc.Dropdown(
                        id='state-dropdown',
                        options=[{'label': f"{US_STATE_NAMES.get(s, s)} ({s})", 'value': s} for s in us_states_list],
                        placeholder="Tutti gli stati...",
                        clearable=True
                    )
                ], md=2),
            ])
        ], className="glass-panel mb-4 p-4", style={"position": "relative", "zIndex": 9999}))
    ]),

    dbc.Row([
        dbc.Col([
             dbc.Row([
                 dbc.Col(html.Div([
                     html.H6("INCIDENTI TOTALI", className="kpi-title"), 
                     html.H3(id="kpi-totale", className="kpi-value text-gradient-primary m-0") 
                 ], className="glass-panel kpi-card")),

                 dbc.Col(html.Div([
                     html.H6("VITTIME FATALI", className="kpi-title"), 
                     html.H3(id="kpi-vittime", className="kpi-value text-gradient-danger m-0")
                 ], className="glass-panel kpi-card")),

                 dbc.Col(html.Div([
                     html.H6("GUIDA STRUMENTALE (IMC)", className="kpi-title"), 
                     html.H3(id="kpi-imc", className="kpi-value text-gradient-warning m-0")
                 ], className="glass-panel kpi-card")),
             ], className="mb-4 g-4"),

             dbc.Row([
                 dbc.Col(html.Div(dcc.Graph(id='trend-chart', style={'height': '400px'}), className="glass-panel p-2"), md=6, className="mb-4"),
                 dbc.Col(html.Div(dcc.Graph(id='map-chart', style={'height': '400px'}), className="glass-panel p-2"), md=6, className="mb-4"),
             ], className="g-4"),

             dbc.Row([
                 dbc.Col(html.Div(dcc.Graph(id='phase-chart', style={'height': '350px'}), className="glass-panel p-2"), md=6, className="mb-4"),
                 dbc.Col(html.Div(dcc.Graph(id='flight-phase-pie', style={'height': '350px'}), className="glass-panel p-2"), md=6, className="mb-4"),
             ], className="g-4"),
        ], md=12)
    ])
], fluid=True, style={"minHeight": "100vh", "padding": "2rem"})


@app.callback(
    [Output("model-dropdown", "options"),
     Output("model-dropdown", "disabled"),
     Output("model-dropdown", "value"),
     Output("model-dropdown", "placeholder")],
    [Input("aircraft-dropdown", "value")]
)
def update_model_options(aircraft_type):
    """Popola dropdown modelli in base al tipo selezionato."""
    if not aircraft_type or df.empty:
        return [], True, None, "Prima seleziona un tipo..."

    filtered = df[df["aircraft_category"] == aircraft_type]
    models = sorted(filtered["make_model"].dropna().replace("", pd.NA).dropna().unique().tolist())

    options = [{'label': m, 'value': m} for m in models]
    return options, False, None, f"Scegli modello ({len(models)} disponibili)..."


@app.callback(
    [Output("kpi-totale", "children"),
     Output("kpi-vittime", "children"),
     Output("kpi-imc", "children"),
     Output("trend-chart", "figure"),
     Output("map-chart", "figure"),
     Output("phase-chart", "figure"),
     Output("flight-phase-pie", "figure")],
    [Input("year-slider", "value"),
     Input("aircraft-dropdown", "value"),
     Input("model-dropdown", "value"),
     Input("operation-dropdown", "value"),
     Input("weather-dropdown", "value"),
     Input("state-dropdown", "value")]
)
def update_dashboard(year_range, aircraft, model, operation, weather, us_state):
    """Callback principale: aggiorna tutti i componenti quando filtri cambiano."""

    if df.empty:
        empty_fig = px.scatter(title="Nessun dato disponibile", template="plotly_white")
        return "0", "0", "0%", empty_fig, empty_fig, empty_fig, empty_fig

    dff_base = df[(df["year"] >= year_range[0]) & (df["year"] <= year_range[1])]
    if aircraft:
        dff_base = dff_base[dff_base["aircraft_category"] == aircraft]
    if operation:
        dff_base = dff_base[dff_base["purpose_of_flight"] == operation]
    if weather:
        dff_base = dff_base[dff_base["weather_condition"] == weather]
    if us_state:
        dff_base = dff_base[dff_base["us_state"] == us_state]

    dff_main = dff_base.copy()
    if model:
        dff_main = dff_main[dff_main["make_model"] == model]

    totale = len(dff_main)
    vittime = int(dff_main["total_fatal_injuries"].sum())
    imc_count = int(dff_main["weather_condition"].str.contains("Imc", case=False, na=False).sum())
    imc_pct = f"{(imc_count / totale * 100):.1f}%" if totale > 0 else "0.0%"

    if totale == 0:
        empty_fig = px.scatter(title="Nessun record corrispondente ai filtri", template="plotly_white")
        return "0", "0", "0%", empty_fig, empty_fig, empty_fig, empty_fig

    agg_anno = dff_main.groupby("year").agg(incidenti=("event_id", "count")).reset_index()
    fig_trend = px.line(agg_anno, x="year", y="incidenti", 
                        title="Andamento Incidenti nel Tempo", markers=True, template="plotly_white",
                        labels={"year": "Anno", "incidenti": "Numero Incidenti"})
    fig_trend.update_traces(line_color="#1e3c72", marker_color="#1e3c72", line_width=3)
    fig_trend.update_layout(
        xaxis_title="Anno", yaxis_title="Numero Incidenti", 
        margin=dict(l=40, r=40, t=50, b=40),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Outfit', color='#2b2d42')
    )

    if us_state:
        state_name = US_STATE_NAMES.get(us_state, us_state)

        city_data = dff_main[dff_main["location"].notna() & (dff_main["location"] != "")].copy()
        city_data["city_label"] = city_data["location"].str.split(",").str[0].str.strip().str.title()

        city_data["latitude"] = pd.to_numeric(city_data["latitude"], errors="coerce")
        city_data["longitude"] = pd.to_numeric(city_data["longitude"], errors="coerce")

        city_agg = city_data.groupby("city_label").agg(
            incidenti=("event_id", "count"),
            lat=("latitude", "mean"),
            lon=("longitude", "mean")
        ).reset_index().sort_values("incidenti", ascending=False)

        city_geo = city_agg.dropna(subset=["lat", "lon"]).head(15)

        if not city_geo.empty:
            lat_center = city_agg.dropna(subset=["lat"])["lat"].median()
            lon_center = city_agg.dropna(subset=["lon"])["lon"].median()

            fig_map = go.Figure()

            fig_map.add_trace(go.Scattergeo(
                lat=city_geo["lat"],
                lon=city_geo["lon"],
                mode="markers+text",
                text=city_geo["city_label"],
                textposition="top center",
                textfont=dict(size=10, color="#2b2d42", family="Outfit"),
                marker=dict(
                    size=city_geo["incidenti"] / city_geo["incidenti"].max() * 30 + 5,
                    color=city_geo["incidenti"],
                    colorscale="Reds",
                    showscale=True,
                    colorbar=dict(title="Incidenti", thickness=12)
                ),
                hovertemplate="<b>%{text}</b><br>Incidenti: %{customdata}<extra></extra>",
                customdata=city_geo["incidenti"]
            ))

            fig_map.update_layout(
                title=f"Top Città per Incidenti — {state_name}",
                geo=dict(
                    scope="usa",
                    center=dict(lat=lat_center, lon=lon_center),
                    projection_scale=5,
                    showland=True, landcolor="rgb(240, 244, 248)",
                    showlakes=True, lakecolor="rgb(204, 224, 245)",
                    showcoastlines=True, coastlinecolor="#aab4c4",
                    showsubunits=True, subunitcolor="#c0c8d4",
                    bgcolor='rgba(0,0,0,0)'
                ),
                margin=dict(l=0, r=0, t=50, b=0),
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family='Outfit', color='#2b2d42')
            )
        else:
            fig_map = px.scatter(title=f"Nessuna coordinata disponibile per {state_name}", template="plotly_white")
    else:
        us_data = dff_main[dff_main["us_state"] != ""]
        if not us_data.empty:
            agg_mappa = us_data.groupby("us_state")["event_id"].count().reset_index()
            agg_mappa["state_name"] = agg_mappa["us_state"].map(US_STATE_NAMES).fillna(agg_mappa["us_state"])

            fig_map = px.choropleth(
                agg_mappa, 
                locations="us_state",
                locationmode="USA-states", 
                color="event_id",
                hover_name="state_name",
                scope="usa",
                title="Distribuzione Incidenti per Stato USA",
                color_continuous_scale="Agsunset",
                template="plotly_white",
                labels={"event_id": "Totale Incidenti", "us_state": "Stato"}
            )
            fig_map.update_layout(
                margin=dict(l=0, r=0, t=50, b=0),
                paper_bgcolor='rgba(0,0,0,0)',
                geo_bgcolor='rgba(0,0,0,0)',
                font=dict(family='Outfit', color='#2b2d42')
            )
        else:
            fig_map = px.scatter(title="Nessun dato USA presente post-filtraggio", template="plotly_white")

    if aircraft:
        full_agg = (
            dff_base.groupby("make_model")["event_id"].count()
            .reset_index()
            .sort_values("event_id", ascending=False)
        )

        top_10 = full_agg.head(10).copy()

        if model and model not in top_10["make_model"].values:
            selected_row = full_agg[full_agg["make_model"] == model]
            if not selected_row.empty:
                top_10 = pd.concat([top_10, selected_row])

        top_10["bar_color"] = ["#FFD700" if m == model else "#ea384d" for m in top_10["make_model"]]
        top_10 = top_10.sort_values("event_id", ascending=True)

        fig_phase = px.bar(
            top_10, x="event_id", y="make_model", orientation="h",
            title=f"Confronto Modelli con più Incidenti — {aircraft}",
            template="plotly_white",
            labels={"event_id": "Numero Incidenti", "make_model": "Modello"},
            color="bar_color",
            color_discrete_map="identity"
        )
        fig_phase.update_layout(showlegend=False)
    else:
        agg_phase = dff_base.groupby("aircraft_category")["event_id"].count().reset_index().sort_values("event_id", ascending=True)
        fig_phase = px.bar(
            agg_phase, x="event_id", y="aircraft_category", orientation="h",
            title="Incidenti per Tipo di Aeromobile",
            template="plotly_white",
            labels={"event_id": "Numero Incidenti", "aircraft_category": "Categoria Velivolo"}
        )
        fig_phase.update_traces(marker_color="#ea384d")
    fig_phase.update_layout(
        xaxis_title="Numero Incidenti", yaxis_title="",
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Outfit', color='#2b2d42'),
        margin=dict(l=20, r=20, t=50, b=20)
    )

    if "broad_phase_of_flight" in dff_main.columns:
        agg_phase_pie = dff_main.dropna(subset=["broad_phase_of_flight"]).groupby("broad_phase_of_flight")["event_id"].count().reset_index()
        fig_pie = px.pie(agg_phase_pie, names="broad_phase_of_flight", values="event_id", hole=0.4,
                         title="Incidenti per Fase di Volo", template="plotly_white",
                         labels={"event_id": "Report", "broad_phase_of_flight": "Fase"})
        fig_pie.update_traces(textposition='inside', textinfo='percent+label', marker=dict(colors=px.colors.qualitative.Pastel))
        fig_pie.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Outfit', color='#2b2d42'),
            margin=dict(l=20, r=20, t=50, b=20),
            showlegend=False
        )
    else:
        fig_pie = px.scatter(title="Dati Fase di Volo Non Disponibili", template="plotly_white")

    return f"{totale:,}", f"{vittime:,}", imc_pct, fig_trend, fig_map, fig_phase, fig_pie


if __name__ == '__main__':
    print("[app] Avvio dashboard su http://0.0.0.0:8050")
    app.run(host='0.0.0.0', port=8050, debug=False)
