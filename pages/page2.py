import dash
from dash import dcc, html
import plotly.express as px
from data_loader import load_all_data
import pandas as pd

dash.register_page(__name__, path="/page2")

# =============================
# LAYOUT EN FONCTION
# =============================
def layout():
    """Charge les données seulement quand la page est visitée"""
    
    # CHARGEMENT DES DONNÉES
    data = load_all_data()
    foncieres_all = data["foncieres_all"]
    pop_communes = data["pop_communes"]
    
    # PRÉPARATION DES CODES INSEE
    foncieres_all["Code departement"] = (
        foncieres_all["Code departement"].astype(str).str.zfill(2)
    )
    foncieres_all["Code commune"] = (
        foncieres_all["Code commune"].astype(str).str.zfill(3)
    )
    foncieres_all["code_insee"] = (
        foncieres_all["Code departement"] +
        foncieres_all["Code commune"]
    )
    
    # Fusion des arrondissements de Paris
    foncieres_all.loc[
        foncieres_all["code_insee"].str.startswith("751"),
        "code_insee"
    ] = "75056"
    
    # TOP 100 COMMUNES (POP 2023)
    top_100_communes = (
        pop_communes
        .nlargest(100, "pop_2023")
        .copy()
    )
    
    # AGRÉGATION DVF PAR COMMUNE
    valeur_communes = (
        foncieres_all[
            foncieres_all["code_insee"].isin(top_100_communes["code_commune"])
        ]
        .groupby(["code_insee", "annee"])
        .agg(
            Valeur_mediane=("Valeur fonciere", "median"),
            Nb_transactions=("Valeur fonciere", "count")
        )
        .reset_index()
    )
    
    # FUSION AVEC POPULATION
    df_communes = valeur_communes.merge(
        top_100_communes[
            ["code_commune", "nom_commune", "pop_2023"]
        ],
        left_on="code_insee",
        right_on="code_commune",
        how="inner"
    )
    
    # FIGURE — SCATTER ANIMÉ
    fig_scatter = px.scatter(
        df_communes,
        x="pop_2023",
        y="Valeur_mediane",
        size="Nb_transactions",
        animation_frame="annee",
        hover_name="nom_commune",
        title="Valeurs foncières vs Population — Top 100 communes",
        labels={
            "pop_2023": "Population (2023)",
            "Valeur_mediane": "Valeur foncière médiane (€)",
            "annee": "Année",
            "Nb_transactions": "Nombre de transactions"
        },
        template="plotly_white",
        height=600,
        log_x=True,
        size_max=45
    )
    
    fig_scatter.update_layout(
        xaxis_title="Population (échelle logarithmique)",
        yaxis_title="Valeur foncière médiane (€)"
    )
    
    # RETOURNER LE LAYOUT
    return html.Div([
        html.H1("Valeurs foncières et population communale."),
        dcc.Graph(figure=fig_scatter)
    ])
