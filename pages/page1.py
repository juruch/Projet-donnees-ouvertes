import dash
from dash import dcc, html
import plotly.express as px
from data_loader import load_all_data
import pandas as pd
from pages.constants import DEPT_NAMES

# =============================
# Enregistrement de la page
# =============================
dash.register_page(__name__, path="/page1")

# =============================
# LAYOUT EN FONCTION
# =============================
def layout():
    """Charge les données seulement quand la page est visitée"""
    
    # CHARGEMENT DES DONNÉES
    data = load_all_data()
    foncieres_all = data["foncieres_all"]
    pop_dep_all = data.get("pop_dep_all")
    
    # AGRÉGATION PAR DÉPARTEMENT
    df_dep = (
        foncieres_all
        .groupby(["Code departement", "annee"])
        .agg(
            Valeur_mediane=("Valeur fonciere", "median"),
            Nb_transactions=("Valeur fonciere", "count")
        )
        .reset_index()
    )
    
    # Ajouter le nom du département
    df_dep["Nom_departement"] = df_dep["Code departement"].map(DEPT_NAMES)
    
    # Fusionner avec pop_dep_all
    if pop_dep_all is not None and len(pop_dep_all) > 0:
        pop_dep_all_copy = pop_dep_all.copy()
        pop_dep_all_copy = pop_dep_all_copy.rename(columns={'Code_departement': 'Code departement'})
        
        df_dep = df_dep.merge(
            pop_dep_all_copy[['Code departement', 'annee', 'Ensemble_Total']],
            on=["Code departement", "annee"],
            how="left"
        )
        
        # Pour les années sans données de population, utiliser les données de 2023
        annees_manquantes = [a for a in df_dep['annee'].unique() if a not in pop_dep_all_copy['annee'].unique()]
        if annees_manquantes:
            for annee_manquante in annees_manquantes:
                pop_2023 = pop_dep_all_copy[pop_dep_all_copy['annee'] == 2023].copy()
                pop_2023['annee'] = annee_manquante
                
                mask = (df_dep['annee'] == annee_manquante) & (df_dep['Ensemble_Total'].isna())
                for _, row in pop_2023.iterrows():
                    dept_mask = mask & (df_dep['Code departement'] == row['Code departement'])
                    df_dep.loc[dept_mask, 'Ensemble_Total'] = row['Ensemble_Total']
        
        df_dep['Ensemble_Total'] = df_dep['Ensemble_Total'].fillna(0)
    else:
        df_dep['Ensemble_Total'] = 0
    
    # Convertir annee en int
    df_dep['annee'] = df_dep['annee'].astype(int)
    
    # FIGURE 1 — SCATTER Population vs Valeur médiane
    fig_scatter = px.scatter(
        df_dep,
        x="Ensemble_Total",
        y="Valeur_mediane",
        color="annee",
        size="Nb_transactions",
        hover_name="Nom_departement",
        hover_data={
            "Code departement": True,
            "Ensemble_Total": ":,.0f",
            "Valeur_mediane": ":,.0f",
            "Nb_transactions": ":,.0f",
            "annee": True
        },
        title="Relation entre Population et Valeur foncière médiane par département",
        labels={
            "Ensemble_Total": "Population totale",
            "Valeur_mediane": "Valeur foncière médiane (€)",
            "annee": "Année",
            "Nb_transactions": "Nombre de transactions"
        },
        template="plotly_white",
        height=600
    )
    
    fig_scatter.update_traces(marker=dict(line=dict(width=0.5, color='white')))
    
    # FIGURE 2 — BARRES ANIMÉES Top 20 départements
    top_20_depts = (
        df_dep.groupby("Code departement")["Valeur_mediane"]
        .mean()
        .sort_values(ascending=False)
        .head(20)
        .index
    )
    
    fig_bar = px.bar(
        df_dep[df_dep["Code departement"].isin(top_20_depts)],
        x="Valeur_mediane",
        y="Nom_departement",
        animation_frame="annee",
        orientation="h",
        color="Valeur_mediane",
        title="Top 20 des départements par valeur foncière médiane",
        labels={
            "Valeur_mediane": "Valeur médiane (€)",
            "Nom_departement": "Département"
        },
        template="plotly_white",
        height=700
    )
    
    fig_bar.update_layout(
        yaxis={"categoryorder": "total ascending"}
    )
    
    # RETOURNER LE LAYOUT
    return html.Div([
        html.H1("Valeurs foncières par département"),
        dcc.Graph(figure=fig_scatter),
        html.Hr(),
        dcc.Graph(figure=fig_bar)
    ])
