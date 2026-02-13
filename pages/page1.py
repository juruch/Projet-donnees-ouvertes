from dash import dcc, html
import plotly.express as px
import pandas as pd
from pages.constants import DEPT_NAMES

def layout(data):
    foncieres_all = data["foncieres_all"].copy()
    pop_dep_all = data.get("pop_dep_all")

    # Sécurités types
    foncieres_all["Code departement"] = foncieres_all["Code departement"].astype(str).str.zfill(2)
    foncieres_all["annee"] = pd.to_numeric(foncieres_all["annee"], errors="coerce")
    foncieres_all["Valeur fonciere"] = pd.to_numeric(foncieres_all["Valeur fonciere"], errors="coerce")
    foncieres_all = foncieres_all.dropna(subset=["annee", "Valeur fonciere"])

    # AGRÉGATION PAR DÉPARTEMENT
    df_dep = (
        foncieres_all
        .groupby(["Code departement", "annee"], as_index=False)
        .agg(
            Valeur_mediane=("Valeur fonciere", "median"),
            Nb_transactions=("Valeur fonciere", "count")
        )
    )

    df_dep["Nom_departement"] = df_dep["Code departement"].map(DEPT_NAMES).fillna(df_dep["Code departement"])
    df_dep["annee"] = df_dep["annee"].astype(int)

    # Fusionner avec pop_dep_all (si dispo)
    df_dep["Ensemble_Total"] = 0.0

    if pop_dep_all is not None and len(pop_dep_all) > 0:
        pop = pop_dep_all.copy()

        # Harmoniser noms de colonnes
        if "Code_departement" in pop.columns and "Code departement" not in pop.columns:
            pop = pop.rename(columns={"Code_departement": "Code departement"})

        pop["Code departement"] = pop["Code departement"].astype(str).str.zfill(2)
        pop["annee"] = pd.to_numeric(pop["annee"], errors="coerce")
        pop["Ensemble_Total"] = pd.to_numeric(pop.get("Ensemble_Total"), errors="coerce")

        pop = pop.dropna(subset=["annee"])
        pop["annee"] = pop["annee"].astype(int)

        df_dep = df_dep.merge(
            pop[["Code departement", "annee", "Ensemble_Total"]],
            on=["Code departement", "annee"],
            how="left"
        )

        # fallback: si pas de pop sur certaines années -> on copie 2023
        if 2023 in set(pop["annee"].unique()):
            pop_2023 = pop[pop["annee"] == 2023][["Code departement", "Ensemble_Total"]].copy()

            for a in sorted(df_dep["annee"].unique()):
                if a not in set(pop["annee"].unique()):
                    df_dep.loc[df_dep["annee"] == a, "Ensemble_Total"] = (
                        df_dep.loc[df_dep["annee"] == a, "Code departement"]
                        .map(pop_2023.set_index("Code departement")["Ensemble_Total"])
                    )

        df_dep["Ensemble_Total"] = df_dep["Ensemble_Total"].fillna(0)

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
    fig_scatter.update_traces(marker=dict(line=dict(width=0.5, color="white")))

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
        labels={"Valeur_mediane": "Valeur médiane (€)", "Nom_departement": "Département"},
        template="plotly_white",
        height=700
    )
    fig_bar.update_layout(yaxis={"categoryorder": "total ascending"})

    return html.Div([
        html.H1("Valeurs foncières par département"),
        dcc.Graph(figure=fig_scatter),
        html.Hr(),
        dcc.Graph(figure=fig_bar),
    ])
