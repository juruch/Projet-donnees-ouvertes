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
# CHARGEMENT DES DONNÉES
# =============================
data = load_all_data()
foncieres_all = data["foncieres_all"]
pop_dep_all = data.get("pop_dep_all")  # population par département et par année

# =============================
# AGRÉGATION PAR DÉPARTEMENT
# =============================
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

# -----------------------------
# Fusionner avec pop_dep_all (population totale par département et par année)
# -----------------------------
if pop_dep_all is not None and len(pop_dep_all) > 0:
    # Standardiser les noms de colonnes
    pop_dep_all_copy = pop_dep_all.copy()
    pop_dep_all_copy = pop_dep_all_copy.rename(columns={'Code_departement': 'Code departement'})
    
    # Vérifier les données avant fusion
    print("Échantillon de pop_dep_all:")
    print(pop_dep_all_copy.head())
    print(f"\nNombre de lignes dans pop_dep_all: {len(pop_dep_all_copy)}")
    print(f"Valeurs uniques de Ensemble_Total: {pop_dep_all_copy['Ensemble_Total'].unique()[:10]}")
    print(f"Années disponibles dans pop_dep_all: {sorted(pop_dep_all_copy['annee'].unique())}")
    
    # Vérifier les années dans df_dep
    print(f"\nAnnées dans df_dep: {sorted(df_dep['annee'].unique())}")
    
    df_dep = df_dep.merge(
        pop_dep_all_copy[['Code departement', 'annee', 'Ensemble_Total']],
        on=["Code departement", "annee"],
        how="left"
    )
    
    # Vérifier après fusion
    print(f"\nNombre de lignes après fusion: {len(df_dep)}")
    print(f"Nombre de valeurs non-null pour Ensemble_Total: {df_dep['Ensemble_Total'].notna().sum()}")
    
    # Identifier les départements sans population
    depts_sans_pop = df_dep[df_dep['Ensemble_Total'].isna()][['Code departement', 'annee', 'Nom_departement']].drop_duplicates()
    if len(depts_sans_pop) > 0:
        print(f"\n⚠ ATTENTION: {len(depts_sans_pop)} département(s)/année(s) sans population:")
        print(depts_sans_pop.head(20))
        
        # Pour les années sans données de population (2024, 2025), utiliser les données de 2023
        annees_manquantes = [a for a in df_dep['annee'].unique() if a not in pop_dep_all_copy['annee'].unique()]
        if annees_manquantes:
            print(f"\n💡 Années manquantes dans pop_dep_all: {annees_manquantes}")
            print("   → Utilisation des données de 2023 pour ces années")
            
            for annee_manquante in annees_manquantes:
                # Récupérer les données de 2023
                pop_2023 = pop_dep_all_copy[pop_dep_all_copy['annee'] == 2023].copy()
                pop_2023['annee'] = annee_manquante
                
                # Mettre à jour les valeurs manquantes pour cette année
                mask = (df_dep['annee'] == annee_manquante) & (df_dep['Ensemble_Total'].isna())
                for _, row in pop_2023.iterrows():
                    dept_mask = mask & (df_dep['Code departement'] == row['Code departement'])
                    df_dep.loc[dept_mask, 'Ensemble_Total'] = row['Ensemble_Total']
    
    # Remplir les valeurs restantes avec 0 (départements vraiment inexistants)
    df_dep['Ensemble_Total'] = df_dep['Ensemble_Total'].fillna(0)
    
    print(f"\n✓ Après correction:")
    print(f"   Nombre de valeurs > 0: {(df_dep['Ensemble_Total'] > 0).sum()}")
    print(f"   Nombre de valeurs = 0: {(df_dep['Ensemble_Total'] == 0).sum()}")
else:
    print("ATTENTION: pop_dep_all est None ou vide!")
    df_dep['Ensemble_Total'] = 0

# Convertir annee en int pour l'affichage
df_dep['annee'] = df_dep['annee'].astype(int)

# =============================
# FIGURE 1 — SCATTER Population vs Valeur médiane
# =============================
fig_scatter = px.scatter(
    df_dep,
    x="Ensemble_Total",            # population totale
    y="Valeur_mediane",            # valeur médiane
    color="annee",                 # couleur selon l'année
    size="Nb_transactions",        # taille selon le nombre de transactions
    hover_name="Nom_departement",  # hover : nom du département
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

# =============================
# FIGURE 2 — BARRES ANIMÉES Top 20 départements
# =============================
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
    title="🏆 Top 20 des départements par valeur foncière médiane",
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

# =============================
# LAYOUT DASH
# =============================
layout = html.Div([
    html.H1("Valeurs foncières par département"),

    # Scatter Population vs Valeur médiane
    dcc.Graph(figure=fig_scatter),

    html.Hr(),

    # Barres animées Top 20 départements
    dcc.Graph(figure=fig_bar)
])