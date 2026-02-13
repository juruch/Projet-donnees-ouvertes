from dash import dcc, html
import plotly.graph_objects as go
import pandas as pd
import numpy as np

from sklearn.linear_model import LinearRegression

def layout(data):
    foncieres_all = data["foncieres_all"].copy()
    pop_dep_all = data.get("pop_dep_all")

    if pop_dep_all is None or len(pop_dep_all) == 0:
        fig = go.Figure()
        fig.add_annotation(
            text="Pas de données démographiques disponibles (pop_dep_all).",
            xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False, font=dict(size=16)
        )
        fig.update_layout(title="Données manquantes", template="plotly_white", height=600)
        return html.Div([html.H1("Prédiction des prix immobiliers 2026"), dcc.Graph(figure=fig)])

    # --- types ---
    foncieres_all["Code departement"] = foncieres_all["Code departement"].astype(str).str.zfill(2)
    foncieres_all["annee"] = pd.to_numeric(foncieres_all["annee"], errors="coerce")
    foncieres_all["Valeur fonciere"] = pd.to_numeric(foncieres_all["Valeur fonciere"], errors="coerce")
    foncieres_all = foncieres_all.dropna(subset=["Code departement", "annee", "Valeur fonciere"])
    foncieres_all["annee"] = foncieres_all["annee"].astype(int)

    # --- agrégation DVF médiane ---
    valeur_dep = (
        foncieres_all
        .groupby(["Code departement", "annee"], as_index=False)["Valeur fonciere"]
        .median()
        .rename(columns={
            "Code departement": "Code_departement",
            "Valeur fonciere": "Valeur_mediane"
        })
    )
    valeur_dep["Code_departement"] = valeur_dep["Code_departement"].astype(str).str.zfill(2)

    # --- nettoyage pop ---
    pop = pop_dep_all.copy()
    if "Code departement" in pop.columns and "Code_departement" not in pop.columns:
        pop = pop.rename(columns={"Code departement": "Code_departement"})

    pop["Code_departement"] = pop["Code_departement"].astype(str).str.zfill(2)
    pop["annee"] = pd.to_numeric(pop["annee"], errors="coerce")
    pop = pop.dropna(subset=["annee"])
    pop["annee"] = pop["annee"].astype(int)

    # --- merge ---
    df_complet = pd.merge(
        valeur_dep,
        pop,
        on=["Code_departement", "annee"],
        how="inner"
    )

    # --- features ---
    colonnes_requises = [
        "Ensemble_20 à 39 ans",
        "Ensemble_40 à 59 ans",
        "Ensemble_75 ans et plus",
        "Ensemble_Total"
    ]

    colonnes_manquantes = [c for c in colonnes_requises if c not in df_complet.columns]
    if colonnes_manquantes:
        fig = go.Figure()
        fig.add_annotation(
            text="Colonnes manquantes :<br>" + "<br>".join(colonnes_manquantes),
            xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color="red")
        )
        fig.update_layout(title="Données incomplètes", template="plotly_white", height=600)
        return html.Div([html.H1("Prédiction des prix immobiliers 2026"), dcc.Graph(figure=fig)])

    for col in colonnes_requises:
        df_complet[col] = pd.to_numeric(df_complet[col], errors="coerce")

    df_complet["prop_20_39"] = df_complet["Ensemble_20 à 39 ans"] / df_complet["Ensemble_Total"]
    df_complet["prop_40_59"] = df_complet["Ensemble_40 à 59 ans"] / df_complet["Ensemble_Total"]
    df_complet["prop_75_plus"] = df_complet["Ensemble_75 ans et plus"] / df_complet["Ensemble_Total"]

    df_complet = df_complet.replace([np.inf, -np.inf], np.nan)
    df_complet = df_complet.dropna(subset=["Valeur_mediane", "Ensemble_Total", "prop_20_39", "prop_40_59", "prop_75_plus"])

    # train/test
    df_train = df_complet[df_complet["annee"] <= 2024].copy()
    df_test_2025 = df_complet[df_complet["annee"] == 2025].copy()

    if len(df_train) == 0 or len(df_test_2025) == 0:
        fig = go.Figure()
        fig.add_annotation(
            text="Données insuffisantes pour entraîner/tester (train<=2024, test=2025).",
            xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False, font=dict(size=16, color="red")
        )
        fig.update_layout(title="Données insuffisantes", template="plotly_white", height=600)
        return html.Div([html.H1("Prédiction des prix immobiliers 2026"), dcc.Graph(figure=fig)])

    features = ["Ensemble_Total", "prop_20_39", "prop_40_59", "prop_75_plus"]
    X_train = df_train[features]
    y_train = df_train["Valeur_mediane"]

    model = LinearRegression()
    model.fit(X_train, y_train)

    # prédiction 2026 (si dispo)
    df_2026 = pop[pop["annee"] == 2026].copy()
    if len(df_2026) == 0:
        fig = go.Figure()
        fig.add_annotation(
            text="Pas de données démographiques 2026 dans pop_dep_all.",
            xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False, font=dict(size=16)
        )
        fig.update_layout(title="Données 2026 manquantes", template="plotly_white", height=600)
        return html.Div([html.H1("Prédiction des prix immobiliers 2026"), dcc.Graph(figure=fig)])

    for col in colonnes_requises:
        df_2026[col] = pd.to_numeric(df_2026[col], errors="coerce")

    df_2026["prop_20_39"] = df_2026["Ensemble_20 à 39 ans"] / df_2026["Ensemble_Total"]
    df_2026["prop_40_59"] = df_2026["Ensemble_40 à 59 ans"] / df_2026["Ensemble_Total"]
    df_2026["prop_75_plus"] = df_2026["Ensemble_75 ans et plus"] / df_2026["Ensemble_Total"]
    df_2026 = df_2026.replace([np.inf, -np.inf], np.nan).dropna(subset=features)

    if len(df_2026) == 0:
        fig = go.Figure()
        fig.add_annotation(
            text="Données 2026 présentes mais inexploitables (NaN/Inf après calcul).",
            xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False, font=dict(size=16)
        )
        fig.update_layout(title="Données 2026 invalides", template="plotly_white", height=600)
        return html.Div([html.H1("Prédiction des prix immobiliers 2026"), dcc.Graph(figure=fig)])

    df_2026["Valeur_pred_2026"] = model.predict(df_2026[features])

    # comparaison 2024 vs 2025 vs 2026 (prédit)
    df_2025 = df_complet[df_complet["annee"] == 2025][["Code_departement", "Valeur_mediane"]].copy()
    df_2024 = df_complet[df_complet["annee"] == 2024][["Code_departement", "Valeur_mediane"]].copy()
    df_2024 = df_2024.rename(columns={"Valeur_mediane": "Valeur_2024"})
    df_2025 = df_2025.rename(columns={"Valeur_mediane": "Valeur_2025"})

    keep_cols_2026 = ["Code_departement", "Valeur_pred_2026"]
    if "Nom_departement" in df_2026.columns:
        keep_cols_2026.append("Nom_departement")

    df_compare = df_2026[keep_cols_2026].merge(df_2025, on="Code_departement", how="inner").merge(df_2024, on="Code_departement", how="inner")

    if "Nom_departement" not in df_compare.columns:
        df_compare["Nom_departement"] = df_compare["Code_departement"]

    df_compare = df_compare.reset_index(drop=True)
    df_compare["dept_index"] = range(len(df_compare))

    fig = go.Figure()

    # lignes verticales
    for _, row in df_compare.iterrows():
        x = row["dept_index"]
        fig.add_trace(go.Scatter(
            x=[x, x, x],
            y=[row["Valeur_2024"], row["Valeur_2025"], row["Valeur_pred_2026"]],
            mode="lines",
            line=dict(width=1, color="lightgray"),
            showlegend=False,
            hoverinfo="skip"
        ))

    fig.add_trace(go.Scatter(
        x=df_compare["dept_index"], y=df_compare["Valeur_2024"],
        mode="markers", name="2024 (réel)",
        marker=dict(size=8),
        text=df_compare["Nom_departement"],
        hovertemplate="<b>%{text}</b><br>2024: %{y:,.0f}€<extra></extra>"
    ))

    fig.add_trace(go.Scatter(
        x=df_compare["dept_index"], y=df_compare["Valeur_2025"],
        mode="markers", name="2025 (réel)",
        marker=dict(size=8),
        text=df_compare["Nom_departement"],
        hovertemplate="<b>%{text}</b><br>2025: %{y:,.0f}€<extra></extra>"
    ))

    fig.add_trace(go.Scatter(
        x=df_compare["dept_index"], y=df_compare["Valeur_pred_2026"],
        mode="markers", name="2026 (prédit)",
        marker=dict(size=8),
        text=df_compare["Nom_departement"],
        hovertemplate="<b>%{text}</b><br>2026: %{y:,.0f}€<extra></extra>"
    ))

    fig.update_layout(
        title="Évolution des valeurs foncières : 2024 & 2025 (réel) vs 2026 (prédit)",
        xaxis_title="Département",
        yaxis_title="Valeur médiane (€)",
        template="plotly_white",
        height=650,
        xaxis={"showticklabels": False},
        hovermode="closest",
        showlegend=True
    )

    return html.Div([
        html.H1("Prédiction des prix immobiliers 2026"),
        dcc.Graph(figure=fig)
    ])
