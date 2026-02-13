from dash import dcc, html
import plotly.express as px
import pandas as pd
import numpy as np

def layout(data):
    foncieres_all = data["foncieres_all"].copy()
    pop_dep_all = data.get("pop_dep_all")

    # --- sécurités types ---
    foncieres_all["Code departement"] = foncieres_all["Code departement"].astype(str).str.zfill(2)
    foncieres_all["annee"] = pd.to_numeric(foncieres_all["annee"], errors="coerce")
    foncieres_all["Valeur fonciere"] = pd.to_numeric(foncieres_all["Valeur fonciere"], errors="coerce")
    foncieres_all = foncieres_all.dropna(subset=["Code departement", "annee", "Valeur fonciere"])
    foncieres_all["annee"] = foncieres_all["annee"].astype(int)

    # --- AGRÉGATION DVF ---
    valeur_dep = (
        foncieres_all
        .groupby(["Code departement", "annee"], as_index=False)["Valeur fonciere"]
        .agg(["median", "mean", "count"])
        .reset_index()
    )
    valeur_dep.columns = ["Code_departement", "annee", "Valeur_mediane", "Valeur_moyenne", "Nb_transactions"]
    valeur_dep["Code_departement"] = valeur_dep["Code_departement"].astype(str).str.zfill(2)
    valeur_dep["annee"] = valeur_dep["annee"].astype(int)

    # --- si pas de données démographiques ---
    if pop_dep_all is None or len(pop_dep_all) == 0:
        fig = px.scatter(title="Données démographiques non disponibles")
        fig2 = px.scatter(title="Données démographiques non disponibles")
        return html.Div([html.H1("Analyse démographique et valeurs foncières"), dcc.Graph(figure=fig), html.Hr(), dcc.Graph(figure=fig2)])

    pop = pop_dep_all.copy()

    # Harmoniser colonne code
    if "Code departement" in pop.columns and "Code_departement" not in pop.columns:
        pop = pop.rename(columns={"Code departement": "Code_departement"})
    elif "Code_departement" not in pop.columns and "Code departement" not in pop.columns:
        # dernier recours : si ton fichier a déjà Code_departement ailleurs
        pass

    pop["Code_departement"] = pop["Code_departement"].astype(str).str.zfill(2)
    pop["annee"] = pd.to_numeric(pop["annee"], errors="coerce")
    pop = pop.dropna(subset=["annee"])
    pop["annee"] = pop["annee"].astype(int)

    # --- merge ---
    df_dep = pd.merge(
        valeur_dep,
        pop,
        on=["Code_departement", "annee"],
        how="inner"
    )

    # colonnes d’âge possibles
    age_cols = {
        "0_19": "Ensemble_0 à 19 ans",
        "20_39": "Ensemble_20 à 39 ans",
        "40_59": "Ensemble_40 à 59 ans",
        "60_74": "Ensemble_60 à 74 ans",
        "75_plus": "Ensemble_75 ans et plus"
    }

    if "Ensemble_Total" not in df_dep.columns:
        fig = px.scatter(title="Données démographiques incomplètes - colonne Ensemble_Total manquante")
        fig2 = px.scatter(title="Données démographiques incomplètes")
        return html.Div([html.H1("Analyse démographique et valeurs foncières"), dcc.Graph(figure=fig), html.Hr(), dcc.Graph(figure=fig2)])

    df_dep["Ensemble_Total"] = pd.to_numeric(df_dep["Ensemble_Total"], errors="coerce")

    # proportions
    for prop_name, col_name in age_cols.items():
        if col_name in df_dep.columns:
            df_dep[col_name] = pd.to_numeric(df_dep[col_name], errors="coerce")
            df_dep[f"prop_{prop_name}"] = df_dep[col_name] / df_dep["Ensemble_Total"]
        else:
            df_dep[f"prop_{prop_name}"] = 0.0

    df_dep["part_jeunes_actifs"] = df_dep["prop_20_39"] + df_dep["prop_40_59"]
    df_dep["part_seniors"] = df_dep["prop_60_74"] + df_dep["prop_75_plus"]

    df_dep = df_dep.replace([np.inf, -np.inf], np.nan)
    df_dep = df_dep.dropna(subset=["part_jeunes_actifs", "part_seniors", "Valeur_mediane", "annee"])

    # --- PROFILS par année (médianes annuelles) ---
    df_typo = df_dep.copy()

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
    df_typo = df_typo.merge(medians, on="annee", how="left")

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

    df_typo["annee"] = df_typo["annee"].astype(int)

    # FIG 1 — BOXPLOT
    fig = px.box(
        df_typo,
        x="profil",
        y="Valeur_mediane",
        color="profil",
        animation_frame="annee",
        title="Valeur foncière médiane selon le profil démographique (jeunes actifs vs seniors)",
        labels={"Valeur_mediane": "Valeur médiane (€)", "profil": "Profil démographique"},
        template="plotly_white",
        height=650,
        category_orders={"profil": ["Jeunes actifs dynamiques", "Intermédiaire", "Vieillissant"]}
    )

    # FIG 2 — TOP 20 départements les plus jeunes
    # (si tu as une colonne Nom_departement dans pop_dep_all : on l’utilise)
    if "Nom_departement" in df_dep.columns:
        df_dep["Nom_departement"] = df_dep["Nom_departement"].fillna(df_dep["Code_departement"])
    else:
        df_dep["Nom_departement"] = df_dep["Code_departement"]

    df_y = df_dep[["annee", "Nom_departement", "part_jeunes_actifs"]].dropna().copy()
    df_y["rang"] = df_y.groupby("annee")["part_jeunes_actifs"].rank(method="first", ascending=False)
    top20 = df_y[df_y["rang"] <= 20].copy()

    if len(top20) > 0:
        fig2 = px.bar(
            top20,
            x="part_jeunes_actifs",
            y="Nom_departement",
            orientation="h",
            animation_frame="annee",
            title="Top 20 des départements les plus jeunes selon l'année",
            labels={"part_jeunes_actifs": "Part des jeunes actifs", "Nom_departement": "Département"},
            template="plotly_white",
            height=700,
            color="part_jeunes_actifs",
            color_continuous_scale="Viridis"
        )
        fig2.update_layout(yaxis={"categoryorder": "total ascending"})
    else:
        fig2 = px.scatter(title="Données insuffisantes pour le top 20")

    return html.Div([
        html.H1("Analyse démographique et valeurs foncières"),
        dcc.Graph(figure=fig),
        html.Hr(),
        dcc.Graph(figure=fig2)
    ])
