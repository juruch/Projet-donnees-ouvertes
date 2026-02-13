import dash
from dash import dcc, html
import plotly.express as px
import plotly.graph_objects as go
from data_loader import load_all_data
import pandas as pd
import numpy as np

from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_absolute_error

dash.register_page(__name__, path='/page4', suppress_callback_exceptions=True)

# =============================
# LAYOUT EN FONCTION
# =============================
def layout():
    """Charge les données seulement quand la page est visitée"""
    
    # CHARGEMENT DES DONNÉES
    data = load_all_data()
    foncieres_all = data["foncieres_all"]
    pop_dep_all = data["pop_dep_all"]
    
    # AGRÉGATION PAR DÉPARTEMENT
    valeur_dep = (
        foncieres_all
        .groupby(["Code departement", "annee"])["Valeur fonciere"]
        .agg(['median'])
        .reset_index()
    )
    
    valeur_dep.columns = [
        "Code_departement",
        "annee",
        "Valeur_mediane"
    ]
    
    valeur_dep['Code_departement'] = valeur_dep['Code_departement'].astype(str).str.zfill(2)
    
    # STANDARDISATION DES DONNÉES DÉMOGRAPHIQUES
    pop_dep_clean = pop_dep_all.copy()
    
    if 'Code departement' in pop_dep_clean.columns:
        pop_dep_clean = pop_dep_clean.rename(columns={'Code departement': 'Code_departement'})
    
    pop_dep_clean['Code_departement'] = pop_dep_clean['Code_departement'].astype(str).str.zfill(2)
    
    # FUSION DATA
    df_complet = pd.merge(
        valeur_dep,
        pop_dep_clean,
        on=["Code_departement", "annee"],
        how="inner"
    )
    
    # CALCUL DES PROPORTIONS
    colonnes_requises = [
        'Ensemble_20 à 39 ans',
        'Ensemble_40 à 59 ans', 
        'Ensemble_75 ans et plus',
        'Ensemble_Total'
    ]
    
    colonnes_manquantes = [col for col in colonnes_requises if col not in df_complet.columns]
    if colonnes_manquantes:
        fig = go.Figure()
        fig.add_annotation(
            text=f"Erreur : colonnes de tranches d'âge manquantes<br>Assurez-vous d'utiliser data_loader_corrected.py",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color="red")
        )
        fig.update_layout(
            title="Données incomplètes",
            template="plotly_white",
            height=600
        )
    else:
        for col in colonnes_requises:
            df_complet[col] = pd.to_numeric(df_complet[col], errors='coerce')
        
        df_complet['prop_20_39'] = df_complet['Ensemble_20 à 39 ans'] / df_complet['Ensemble_Total']
        df_complet['prop_40_59'] = df_complet['Ensemble_40 à 59 ans'] / df_complet['Ensemble_Total']
        df_complet['prop_75_plus'] = df_complet['Ensemble_75 ans et plus'] / df_complet['Ensemble_Total']
        
        df_complet = df_complet.replace([np.inf, -np.inf], np.nan)
        df_complet = df_complet.dropna(subset=[
            'Valeur_mediane',
            'Ensemble_Total',
            'prop_20_39',
            'prop_40_59',
            'prop_75_plus'
        ])
        
        # TRAIN / TEST
        df_train = df_complet[df_complet['annee'] <= 2024].copy()
        df_test_2025 = df_complet[df_complet['annee'] == 2025].copy()
        
        if len(df_train) == 0 or len(df_test_2025) == 0:
            fig = go.Figure()
            fig.add_annotation(
                text="Erreur : données insuffisantes pour l'entraînement",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16, color="red")
            )
            fig.update_layout(title="Données insuffisantes", template="plotly_white", height=600)
        else:
            features = ['Ensemble_Total', 'prop_20_39', 'prop_40_59', 'prop_75_plus']
            
            X_train = df_train[features]
            y_train = df_train['Valeur_mediane']
            
            X_test = df_test_2025[features]
            y_test = df_test_2025['Valeur_mediane']
            
            # MODÈLE
            model_pred = LinearRegression()
            model_pred.fit(X_train, y_train)
            
            # PRÉDICTION 2025
            y_pred_2025 = model_pred.predict(X_test)
            
            df_test_2025['Valeur_pred'] = y_pred_2025
            df_test_2025['Erreur'] = df_test_2025['Valeur_mediane'] - df_test_2025['Valeur_pred']
            df_test_2025['Erreur_pct'] = (
                df_test_2025['Erreur'] / df_test_2025['Valeur_mediane']
            ) * 100
            
            # PRÉDICTIONS 2026
            df_2026 = pop_dep_clean[pop_dep_clean['annee'] == 2026].copy()
            
            if len(df_2026) > 0:
                for col in colonnes_requises:
                    if col in df_2026.columns:
                        df_2026[col] = pd.to_numeric(df_2026[col], errors='coerce')
                
                df_2026['prop_20_39'] = df_2026['Ensemble_20 à 39 ans'] / df_2026['Ensemble_Total']
                df_2026['prop_40_59'] = df_2026['Ensemble_40 à 59 ans'] / df_2026['Ensemble_Total']
                df_2026['prop_75_plus'] = df_2026['Ensemble_75 ans et plus'] / df_2026['Ensemble_Total']
                
                df_2026_clean = df_2026.dropna(subset=features).copy()
                
                if len(df_2026_clean) > 0:
                    X_2026 = df_2026_clean[features]
                    df_2026_clean['Valeur_pred_2026'] = model_pred.predict(X_2026)
                    
                    # COMPARAISON 2025 vs 2026
                    df_compare = pd.merge(
                        df_test_2025[['Code_departement', 'Valeur_mediane']],
                        df_2026_clean[['Code_departement', 'Nom_departement', 'Valeur_pred_2026']],
                        on='Code_departement',
                        how='inner'
                    )
                    
                    # AJOUT 2024
                    df_2024 = df_complet[df_complet['annee'] == 2024][
                        ['Code_departement', 'Valeur_mediane']
                    ].copy()
                    
                    df_2024 = df_2024.rename(columns={'Valeur_mediane': 'Valeur_2024'})
                    
                    df_compare_complet = pd.merge(
                        df_2024,
                        df_compare,
                        on='Code_departement',
                        how='inner'
                    )
                    
                    df_compare_complet = df_compare_complet.reset_index(drop=True)
                    df_compare_complet['dept_index'] = range(len(df_compare_complet))
                    
                    # FIGURE
                    fig = go.Figure()
                    
                    for idx, row in df_compare_complet.iterrows():
                        dept_idx = row['dept_index']
                        
                        fig.add_trace(go.Scatter(
                            x=[dept_idx, dept_idx, dept_idx],
                            y=[row['Valeur_2024'], row['Valeur_mediane'], row['Valeur_pred_2026']],
                            mode='lines+markers',
                            line=dict(color='lightgray', width=1),
                            marker=dict(size=0),
                            showlegend=False,
                            hoverinfo='skip',
                            name=''
                        ))
                    
                    fig.add_trace(go.Scatter(
                        x=df_compare_complet['dept_index'],
                        y=df_compare_complet['Valeur_2024'],
                        mode='markers',
                        name='2024 (réel)',
                        marker=dict(size=8, color='lightblue'),
                        text=df_compare_complet['Nom_departement'],
                        hovertemplate='<b>%{text}</b><br>2024: %{y:,.0f}€<extra></extra>'
                    ))
                    
                    fig.add_trace(go.Scatter(
                        x=df_compare_complet['dept_index'],
                        y=df_compare_complet['Valeur_mediane'],
                        mode='markers',
                        name='2025 (réel)',
                        marker=dict(size=8, color='steelblue'),
                        text=df_compare_complet['Nom_departement'],
                        hovertemplate='<b>%{text}</b><br>2025: %{y:,.0f}€<extra></extra>'
                    ))
                    
                    fig.add_trace(go.Scatter(
                        x=df_compare_complet['dept_index'],
                        y=df_compare_complet['Valeur_pred_2026'],
                        mode='markers',
                        name='2026 (prédit)',
                        marker=dict(size=8, color='coral'),
                        text=df_compare_complet['Nom_departement'],
                        hovertemplate='<b>%{text}</b><br>2026: %{y:,.0f}€<extra></extra>'
                    ))
                    
                    fig.update_layout(
                        title=f"Évolution des valeurs foncières en 2024, 2025 (réels) et 2026 (prédit)",
                        xaxis_title='Département',
                        yaxis_title='Valeur médiane (€)',
                        height=600,
                        template='plotly_white',
                        xaxis={'showticklabels': False},
                        hovermode='closest',
                        showlegend=True
                    )
                else:
                    fig = go.Figure()
                    fig.add_annotation(
                        text="Pas de données 2026 disponibles",
                        xref="paper", yref="paper",
                        x=0.5, y=0.5, showarrow=False,
                        font=dict(size=16)
                    )
                    fig.update_layout(title="Données 2026 manquantes", template="plotly_white", height=600)
            else:
                fig = go.Figure()
                fig.add_annotation(
                    text="Pas de données démographiques pour 2026",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, showarrow=False,
                    font=dict(size=16)
                )
                fig.update_layout(title="Données 2026 manquantes", template="plotly_white", height=600)
    
    # RETOURNER LE LAYOUT
    return html.Div([
        html.H1("Prédiction des prix immobiliers 2026"),
        dcc.Graph(figure=fig)
    ])
