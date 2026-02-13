from dash import dcc, html
import plotly.express as px
import pandas as pd

def layout(data):
    foncieres_all = data["foncieres_all"].copy()
    pop_communes = data["pop_communes"].copy()

    foncieres_all["Code departement"] = foncieres_all["Code departement"].astype(str).str.zfill(2)
    foncieres_all["Code commune"] = foncieres_all["Code commune"].astype(str).str.zfill(3)

    foncieres_all["code_insee"] = foncieres_all["Code departement"] + foncieres_all["Code commune"]

    # Fusion arrondissements Paris
    foncieres_all.loc[foncieres_all["code_insee"].str.startswith("751"), "code_insee"] = "75056"

    # TOP 100 communes (pop 2023)
    top_100_communes = pop_communes.nlargest(100, "pop_2023").copy()

    # Agrégation DVF par commune
    foncieres_all["Valeur fonciere"] = pd.to_numeric(foncieres_all["Valeur fonciere"], errors="coerce")
    foncieres_all = foncieres_all.dropna(subset=["Valeur fonciere"])

    valeur_communes = (
        foncieres_all[foncieres_all["code_insee"].isin(top_100_communes["code_commune"])]
        .groupby(["code_insee", "annee"], as_index=False)
        .agg(
            Valeur_mediane=("Valeur fonciere", "median"),
            Nb_transactions=("Valeur fonciere", "count")
        )
    )

    df_communes = valeur_communes.merge(
        top_100_communes[["code_commune", "nom_commune", "pop_2023"]],
        left_on="code_insee",
        right_on="code_commune",
        how="inner"
    )

    df_communes["annee"] = pd.to_numeric(df_communes["annee"], errors="coerce").fillna(0).astype(int)

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

    return html.Div([
        html.H1("Valeurs foncières et population communale"),
        dcc.Graph(figure=fig_scatter)
    ])
