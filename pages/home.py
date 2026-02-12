import dash
from dash import dcc, html
import plotly.express as px
from data_loader import load_all_data
import pandas as pd
import numpy as np

dash.register_page(__name__, path='/')

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
# CARTE 2 — COMMUNES (VERSION STABLE)
# =============================

# =============================
# CARTE 2 — COMMUNES (FIX FINAL)
# =============================

communes_geo = pd.read_csv("data/communes-france-2025.csv", dtype=str)

communes_geo["code_insee"] = communes_geo["code_insee"].str.zfill(5)
communes_geo["lat"] = communes_geo["latitude_centre"].astype(float)
communes_geo["lon"] = communes_geo["longitude_centre"].astype(float)
communes_geo["population"] = communes_geo["population"].astype(float)

# Harmonisation des codes INSEE

# DVF
foncieres_all["code_insee"] = (
    foncieres_all["Code departement"].astype(str).str.zfill(2) +
    foncieres_all["Code commune"].astype(str).str.zfill(3)
)

# CSV communes
communes_geo["code_insee"] = communes_geo["code_insee"].astype(str).str.zfill(5)

# communes avec ≥ 50 ventes
transactions = (
    foncieres_all
    .groupby("code_insee")
    .size()
    .reset_index(name="nb")
)

communes_ok = transactions[transactions["nb"] >= 50]["code_insee"]

foncieres_filtre = foncieres_all[
    foncieres_all["code_insee"].isin(communes_ok)
]

# agrégation
communes_stats = (
    foncieres_filtre
    .groupby(["code_insee", "annee"])["Valeur fonciere"]
    .median()
    .reset_index(name="valeur_mediane")
)

# fusion coords (MAINTENANT ÇA MATCH)
df_map = communes_stats.merge(
    communes_geo,
    on="code_insee",
    how="inner"
)

# catégories pop
def categorie(pop):
    if pop < 2000: return "Village"
    if pop < 5000: return "Bourg"
    if pop < 20000: return "Petite ville"
    if pop < 50000: return "Ville moyenne"
    if pop < 200000: return "Grande ville"
    return "Métropole"

df_map["categorie"] = df_map["population"].apply(categorie)
df_map["taille"] = np.sqrt(df_map["valeur_mediane"])

# SCATTER GEO (comme carte 1 mais en points)
fig_com_map = px.scatter_geo(
    df_map,
    lat="lat",
    lon="lon",
    size="taille",
    color="categorie",
    animation_frame="annee",
    hover_name="nom_standard",
    hover_data=["valeur_mediane", "population"]
)

fig_com_map.update_geos(
    fitbounds="locations",
    visible=False
)
fig_com_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})


# =============================
# LAYOUT
# =============================
layout = html.Div([
    html.H1("Comment les dynamiques de populations impactent les valeurs foncières ?"),

    html.Div([
        dcc.Graph(figure=fig, style={"width":"50%","display":"inline-block"}),
        dcc.Graph(figure=fig_com_map, style={"width":"50%","display":"inline-block"})
    ])
])
