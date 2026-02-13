from dash import dcc, html
import plotly.express as px
import pandas as pd

def layout(data):
    foncieres_all = data["foncieres_all"].copy()

    # =============================
    # NETTOYAGE (évite de re-nettoyer le global)
    # =============================
    foncieres_all.columns = foncieres_all.columns.str.strip()

    # Valeur foncière déjà numeric si tu la convertis dans data_loader,
    # mais on sécurise :
    foncieres_all["Valeur fonciere"] = pd.to_numeric(foncieres_all["Valeur fonciere"], errors="coerce")
    foncieres_all = foncieres_all.dropna(subset=["Valeur fonciere"])

    foncieres_all["Code commune"] = foncieres_all["Code commune"].astype(str).str.zfill(5)
    foncieres_all["Code departement"] = foncieres_all["Code departement"].astype(str).str.strip()
    foncieres_all["annee"] = foncieres_all["annee"].astype(str)

    # =============================
    # CARTE 1 — DEPARTEMENTS
    # =============================
    valeur_dep = (
        foncieres_all
        .groupby(["Code departement", "annee"], as_index=False)["Valeur fonciere"]
        .median()
        .rename(columns={"Valeur fonciere": "Valeur_mediane"})
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
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

    return html.Div([
        html.H1("Comment les dynamiques de populations impactent les valeurs foncières ?"),
        dcc.Graph(figure=fig, style={"width": "100%", "height": "80vh"})
    ])
