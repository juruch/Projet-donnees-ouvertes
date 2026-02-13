import dash
from dash import dcc, html
import plotly.express as px
from data_loader import load_all_data
import pandas as pd
import numpy as np

# =============================
# Enregistrement de la page
# =============================
dash.register_page(__name__, path='/page3', suppress_callback_exceptions=True)

# =============================
# CHARGEMENT DES DONNÉES
# =============================
data = load_all_data()
foncieres_all = data["foncieres_all"]
pop_dep_all = data.get("pop_dep_all")

# =============================
# AGRÉGATION PAR DÉPARTEMENT ET ANNÉE
# =============================
valeur_dep = (
    foncieres_all
    .groupby(["Code departement", "annee"])["Valeur fonciere"]
    .agg(['median', 'mean', 'count'])
    .reset_index()
)
valeur_dep.columns = ['Code_departement', 'annee', 'Valeur_mediane', 'Valeur_moyenne', 'Nb_transactions']

print(f"Données agrégées : {len(valeur_dep)} observations (département × année)")

# =============================
# FUSION AVEC LES DONNÉES DÉMOGRAPHIQUES
# =============================
if pop_dep_all is not None and len(pop_dep_all) > 0:
    # Standardiser les noms de colonnes dans pop_dep_all
    pop_dep_clean = pop_dep_all.copy()
    
    # Renommer si nécessaire pour assurer la cohérence
    if 'Code departement' in pop_dep_clean.columns:
        pop_dep_clean = pop_dep_clean.rename(columns={'Code departement': 'Code_departement'})
    
    # S'assurer que les codes départements sont au même format (string avec zéro devant)
    pop_dep_clean['Code_departement'] = pop_dep_clean['Code_departement'].astype(str).str.zfill(2)
    valeur_dep['Code_departement'] = valeur_dep['Code_departement'].astype(str).str.zfill(2)
    
    # Fusion
    df_dep = pd.merge(
        valeur_dep,
        pop_dep_clean,
        on=["Code_departement", "annee"],
        how="inner"
    )
    
    print(f"Dataset fusionné : {len(df_dep):,} observations")
    print(f"Période : {df_dep['annee'].min():.0f}-{df_dep['annee'].max():.0f}")
    print(f"Départements : {df_dep['Code_departement'].nunique()}")
    
    # =============================
    # CALCUL DES PROPORTIONS PAR ÂGE
    # =============================
    # Vérifier que les colonnes existent
    age_cols = {
        "0_19": "Ensemble_0 à 19 ans",
        "20_39": "Ensemble_20 à 39 ans",
        "40_59": "Ensemble_40 à 59 ans",
        "60_74": "Ensemble_60 à 74 ans",
        "75_plus": "Ensemble_75 ans et plus"
    }
    
    # S'assurer que Ensemble_Total existe et est numérique
    if "Ensemble_Total" in df_dep.columns:
        df_dep["Ensemble_Total"] = pd.to_numeric(df_dep["Ensemble_Total"], errors="coerce")
        
        for prop_name, col_name in age_cols.items():
            if col_name in df_dep.columns:
                df_dep[col_name] = pd.to_numeric(df_dep[col_name], errors="coerce")
                df_dep[f"prop_{prop_name}"] = df_dep[col_name] / df_dep["Ensemble_Total"]
            else:
                print(f"⚠️  Colonne manquante : {col_name}")
                df_dep[f"prop_{prop_name}"] = 0
        
        # Calculer les parts spécifiques
        df_dep["part_jeunes_actifs"] = df_dep["prop_20_39"] + df_dep["prop_40_59"]
        df_dep["part_seniors"] = df_dep["prop_60_74"] + df_dep["prop_75_plus"]
        
        # Supprimer les lignes avec des valeurs manquantes
        df_dep = df_dep.dropna(subset=["part_jeunes_actifs", "part_seniors", "Valeur_mediane"])
        
        # =============================
        # CRÉATION DES PROFILS DÉMOGRAPHIQUES
        # =============================
        df_typo = df_dep.copy()
        
        # Calculer les médianes par année
        medians = (
            df_typo
            .groupby("annee")[["part_jeunes_actifs", "part_seniors"]]
            .median()
            .rename(columns={
                "part_jeunes_actifs": "part_jeunes_actifs_median", 
                "part_seniors": "part_seniors_median"
            })
            .reset_index()
        )
        
        # Fusionner les médianes
        df_typo = df_typo.merge(medians, on="annee", how="left")
        
        # Créer les profils démographiques
        df_typo["profil"] = "Intermédiaire"
        
        df_typo.loc[
            (df_typo["part_jeunes_actifs"] > df_typo["part_jeunes_actifs_median"]) &
            (df_typo["part_seniors"] < df_typo["part_seniors_median"]),
            "profil"
        ] = "Jeunes actifs dynamiques"
        
        df_typo.loc[
            (df_typo["part_seniors"] > df_typo["part_seniors_median"]) &
            (df_typo["part_jeunes_actifs"] < df_typo["part_jeunes_actifs_median"]),
            "profil"
        ] = "Vieillissant"
        
        # Statistiques des profils
        print(f"\nRépartition des profils démographiques :")
        print(df_typo.groupby("profil").size())
        
        # Convertir l'année en entier pour l'animation
        df_typo['annee'] = df_typo['annee'].astype(int)
        
        # =============================
        # FIGURE 1 - BOXPLOT INTERACTIF
        # =============================
        fig = px.box(
            df_typo,
            x="profil",
            y="Valeur_mediane",
            color="profil",
            animation_frame="annee",
            title="Valeur foncière médiane selon le profil démographique (jeunes actifs vs seniors)",
            labels={
                "Valeur_mediane": "Valeur médiane (€)", 
                "profil": "Profil démographique"
            },
            template="plotly_white",
            height=650,
            category_orders={
                "profil": ["Jeunes actifs dynamiques", "Intermédiaire", "Vieillissant"]
            }
        )
        
        fig.update_layout(
            showlegend=True,
            xaxis_title="Profil démographique",
            yaxis_title="Valeur foncière médiane (€)"
        )
        
        # =============================
        # FIGURE 2 - TOP 20 DÉPARTEMENTS LES PLUS JEUNES
        # =============================
        # Vérifier que Nom_departement existe
        if "Nom_departement" not in df_dep.columns:
            # Utiliser le code département comme nom si le nom n'existe pas
            df_dep["Nom_departement"] = df_dep["Code_departement"]
        
        # On garde les colonnes utiles
        df_y = df_dep[["annee", "Nom_departement", "part_jeunes_actifs"]].dropna().copy()
        
        # Convertir l'année en entier
        df_y['annee'] = df_y['annee'].astype(int)
        
        # Classement par année : rang (1 = le plus jeune)
        df_y["rang"] = df_y.groupby("annee")["part_jeunes_actifs"].rank(method="first", ascending=False)
        
        # Top 20 par année
        top20 = df_y[df_y["rang"] <= 20].copy()
        
        if len(top20) > 0:
            # Pour un bar chart horizontal : on inverse l'ordre dans chaque année
            top20 = top20.sort_values(["annee", "part_jeunes_actifs"], ascending=[True, True])
            
            fig2 = px.bar(
                top20,
                x="part_jeunes_actifs",
                y="Nom_departement",
                orientation="h",
                animation_frame="annee",
                range_x=[top20["part_jeunes_actifs"].min()*0.98, top20["part_jeunes_actifs"].max()*1.02],
                title="Top 20 des départements les plus jeunes selon l'année",
                labels={
                    "part_jeunes_actifs": "Part des jeunes actifs ", 
                    "Nom_departement": "Département"
                },
                template="plotly_white",
                height=700,
                color="part_jeunes_actifs",
                color_continuous_scale="Viridis"
            )
            
            # Force un ordre stable des barres pour chaque frame (top->bottom)
            fig2.update_layout(yaxis={"categoryorder":"total ascending"})
        else:
            fig2 = px.scatter(title="Données insuffisantes pour le top 20")
    else:
        print("⚠️  Colonne Ensemble_Total manquante")
        fig = px.scatter(title="Données démographiques incomplètes - colonne Ensemble_Total manquante")
        fig2 = px.scatter(title="Données démographiques incomplètes")
        
else:
    print("ERREUR : Impossible de charger les données démographiques")
    # Créer des graphiques vides
    fig = px.scatter(title="Données démographiques non disponibles")
    fig2 = px.scatter(title="Données démographiques non disponibles")

# =============================
# LAYOUT DASH
# =============================
layout = html.Div([
    html.H1("Analyse démographique et valeurs foncières"),
    dcc.Graph(figure=fig),
    html.Hr(),
    dcc.Graph(figure=fig2)
])