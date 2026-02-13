import dash
from dash import dcc, html
import plotly.express as px
from data_loader import load_all_data
import pandas as pd
import numpy as np

dash.register_page(__name__, path='/')

# =============================
# LAYOUT EN FONCTION
# =============================
def layout():
    """Charge les données seulement quand la page est visitée"""
    
    data = load_all_data()
    foncieres_all = data["foncieres_all"]
    
    # =============================
    # NETTOYAGE GLOBAL
    # =============================
    foncieres_all.columns = foncieres_all.columns.str.strip()
    foncieres_all["Valeur fonciere"] = (
        foncieres_all["Valeur fonciere"]
        .astype(str)
        .str.replace(",", ".")
        .astype(float)
    )
    foncieres_all["Code commune"] = foncieres_all["Code commune"].astype(str).str.zfill(5)
    foncieres_all["Code departement"] = foncieres_all["Code departement"].astype(str)
    foncieres_all["annee"] = foncieres_all["annee"].astype(str)
    
    # =============================
    # CARTE 1 — DEPARTEMENTS
    # =============================
    valeur_dep = (
        foncieres_all
        .groupby(["Code departement", "annee"])["Valeur fonciere"]
        .median()
        .reset_index(name="Valeur_mediane")
    )
    
    fig = px.choropleth(
        valeur_dep,
        geojson="https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/departements.geojson",
        locations="Code departement",
        featureidkey="properties.code",
        color="Valeur_mediane",
        animation_frame="annee",
        color_continuous_scale="YlOrRd"
    )
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    
    # =============================
    # RETOURNER LE LAYOUT
    # =============================
    return html.Div([
        html.H1("Comment les dynamiques de populations impactent les valeurs foncières ?"),
        
        html.Div([
            dcc.Graph(
                figure=fig,
                style={
                    "width": "100%",
                    "height": "80vh",
                    "display": "inline-block"
                }
            ),
        ], style={"height": "calc(100vh - 500px)"})
    ])
