import dash
from dash import dcc, html, Input, Output
import os
import zipfile
import pandas as pd
import pickle

# Dossier où se trouvent les zips
zip_folder = "data"
cache_file = "data/cache_data.pkl"

# Liste des années DVF
annees = range(2020, 2026)

def extract_all_zips():
    """Extrait tous les fichiers zip nécessaires"""
    # Dézipper les fichiers DVF
    for annee in annees:
        zip_path = os.path.join(zip_folder, f"ValeursFoncieres-{annee}.zip")
        extract_path = os.path.join(zip_folder, f"dvf_{annee}")
        
        if os.path.exists(zip_path) and not os.path.exists(extract_path):
            os.makedirs(extract_path, exist_ok=True)
            print(f"Extraction de {zip_path}...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)

    # Dézipper population départements
    pop_dep_zip = os.path.join(zip_folder, "estim-pop-dep-sexe-gca-1975-2026.zip")
    pop_dep_extract = os.path.join(zip_folder, "pop_dep")

    if os.path.exists(pop_dep_zip) and not os.path.exists(pop_dep_extract):
        os.makedirs(pop_dep_extract, exist_ok=True)
        print(f"Extraction de {pop_dep_zip}...")
        with zipfile.ZipFile(pop_dep_zip, 'r') as zip_ref:
            zip_ref.extractall(pop_dep_extract)

    # Dézipper population communes
    pop_communes_zip = os.path.join(zip_folder, "base-pop-historiques-1876-2023.zip")
    pop_communes_extract = os.path.join(zip_folder, "pop_communes")

    if os.path.exists(pop_communes_zip) and not os.path.exists(pop_communes_extract):
        os.makedirs(pop_communes_extract, exist_ok=True)
        print(f"Extraction de {pop_communes_zip}...")
        with zipfile.ZipFile(pop_communes_zip, 'r') as zip_ref:
            zip_ref.extractall(pop_communes_extract)

def load_all_data():
    """Charge toutes les données et les met en cache"""
    
    # Vérifier si le cache existe
    if os.path.exists(cache_file):
        print("Chargement depuis le cache...")
        with open(cache_file, 'rb') as f:
            return pickle.load(f)
    
    print("Première chargement des données (cela peut prendre du temps)...")
    
    # Chargement des données DVF
    print("Chargement des données DVF...")
    dvf_list = []

    for annee in annees:
        extract_path = os.path.join(zip_folder, f"dvf_{annee}")
        
        if os.path.exists(extract_path):
            files = [f for f in os.listdir(extract_path) if f.endswith('.txt')]
            
            if files:
                file_path = os.path.join(extract_path, files[0])
                print(f"  - Chargement {annee}...")
                
                df_temp = pd.read_csv(
                    file_path,
                    sep="|",
                    low_memory=False
                )
                
                df_temp["annee"] = annee
                dvf_list.append(df_temp)

    foncieres_all = pd.concat(dvf_list, ignore_index=True) if dvf_list else pd.DataFrame()
    print(f"✓ Données DVF chargées : {len(foncieres_all)} lignes")

    # Chargement des données population départements
    print("Chargement des données population départements...")
    pop_dep_list = []
    pop_dep_file = os.path.join(zip_folder, "pop_dep", "estim-pop-dep-sexe-gca-1975-2026.xlsx")

    if os.path.exists(pop_dep_file):
        for annee in annees:
            pop_dep = pd.read_excel(
                pop_dep_file,
                sheet_name=str(annee),
                header=[3, 4]
            )

            pop_dep.columns = [
                f"{col[0]}_{col[1]}" if col[1] and 'Unnamed' not in str(col[1]) else col[0]
                for col in pop_dep.columns
            ]
            
            pop_dep["annee"] = annee
            pop_dep_list.append(pop_dep)

        pop_dep_all = pd.concat(pop_dep_list, ignore_index=True)
        print(f"✓ Données population départements chargées : {len(pop_dep_all)} lignes")
    else:
        pop_dep_all = pd.DataFrame()

    # Chargement des données population communes
    print("Chargement des données population communes...")
    pop_communes_file = os.path.join(zip_folder, "pop_communes", "base-pop-historiques-1876-2023.xlsx")

    if os.path.exists(pop_communes_file):
        df = pd.read_excel(
            pop_communes_file,
            sheet_name="pop_1876_2023",
            header=5
        )

        colonnes_a_garder = [
            'CODGEO', 'REG', 'DEP', 'LIBGEO',
            'PMUN2023', 'PMUN2022', 'PMUN2021', 'PMUN2020'
        ]

        pop_communes = df[colonnes_a_garder].copy()

        pop_communes.columns = [
            'code_commune', 'code_region', 'code_departement', 'nom_commune',
            'pop_2023', 'pop_2022', 'pop_2021', 'pop_2020'
        ]
        print(f"✓ Données population communes chargées : {len(pop_communes)} lignes")
    else:
        pop_communes = pd.DataFrame()

    # Sauvegarder dans le cache
    data = {
        'foncieres_all': foncieres_all,
        'pop_dep_all': pop_dep_all,
        'pop_communes': pop_communes
    }
    
    print("Sauvegarde dans le cache...")
    with open(cache_file, 'wb') as f:
        pickle.dump(data, f)
    
    print("✓ Toutes les données sont chargées et en cache !")
    
    return data

# Extraction des zips (une seule fois)
extract_all_zips()

# Chargement des données avec cache
data = load_all_data()
foncieres_all = data['foncieres_all']
pop_dep_all = data['pop_dep_all']
pop_communes = data['pop_communes']

# Création de l'application Dash
app = dash.Dash(__name__, suppress_callback_exceptions=True)

# Importer les modules des pages après l'instanciation de l'application
from pages import home
from pages.navigation import create_nav_bar

# Layout de l'application
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),  # Pour gérer la navigation
    create_nav_bar(),  # Appeler la fonction pour créer la barre de navigation
    html.Div(id='page-content')  # Contenu dynamique
])

@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    return home.layout  # Retourner le layout de home.py

# Lancement de l'application
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)