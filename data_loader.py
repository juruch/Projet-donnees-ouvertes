import os
import zipfile
import pandas as pd
import pickle

zip_folder = "data"
cache_file = "data/cache_data.pkl"
annees = range(2020, 2026)  # années DVF

# =============================
# EXTRACTION DES ZIP
# =============================
def extract_all_zips():
    # DVF
    for annee in annees:
        zip_path = os.path.join(zip_folder, f"ValeursFoncieres-{annee}.zip")
        extract_path = os.path.join(zip_folder, f"dvf_{annee}")
        if os.path.exists(zip_path) and not os.path.exists(extract_path):
            os.makedirs(extract_path, exist_ok=True)
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)

    # Populations communes
    pop_communes_zip = os.path.join(zip_folder, "base-pop-historiques-1876-2023.zip")
    pop_communes_extract = os.path.join(zip_folder, "pop_communes")
    if os.path.exists(pop_communes_zip) and not os.path.exists(pop_communes_extract):
        os.makedirs(pop_communes_extract, exist_ok=True)
        with zipfile.ZipFile(pop_communes_zip, 'r') as zip_ref:
            zip_ref.extractall(pop_communes_extract)

    # Populations départements (estim-pop-dep-sexe-gca-1975-2026.zip)
    pop_dep_zip = os.path.join(zip_folder, "estim-pop-dep-sexe-gca-1975-2026.zip")
    pop_dep_extract = os.path.join(zip_folder, "pop_departement")
    if os.path.exists(pop_dep_zip) and not os.path.exists(pop_dep_extract):
        os.makedirs(pop_dep_extract, exist_ok=True)
        with zipfile.ZipFile(pop_dep_zip, 'r') as zip_ref:
            zip_ref.extractall(pop_dep_extract)


# =============================
# CHARGEMENT DES DONNÉES
# =============================
def load_all_data():

    if os.path.exists(cache_file):
        with open(cache_file, 'rb') as f:
            return pickle.load(f)

    # -----------------------------
    # DVF
    # -----------------------------
    dvf_list = []
    for annee in annees:
        extract_path = os.path.join(zip_folder, f"dvf_{annee}")
        files = [f for f in os.listdir(extract_path) if f.endswith(".txt")]
        if not files:
            continue
        file_path = os.path.join(extract_path, files[0])
        df_temp = pd.read_csv(
            file_path,
            sep="|",
            usecols=["Date mutation", "Valeur fonciere", "Code departement", "Code commune"],
            low_memory=False
        )
        df_temp["annee_fichier"] = annee
        dvf_list.append(df_temp)

    foncieres_all = pd.concat(dvf_list, ignore_index=True)
    foncieres_all["Date mutation"] = pd.to_datetime(
        foncieres_all["Date mutation"], format="%d/%m/%Y", errors="coerce"
    )
    foncieres_all["annee"] = foncieres_all["Date mutation"].dt.year
    
    # Formater les codes départements correctement (2A, 2B, 971-976 doivent être préservés)
    def format_code_dept(code):
        code = str(code).strip()
        if code.isdigit() and len(code) < 3:
            return code.zfill(2)
        return code
    
    foncieres_all["Code departement"] = foncieres_all["Code departement"].apply(format_code_dept)
    
    foncieres_all["Valeur fonciere"] = (
        foncieres_all["Valeur fonciere"]
        .astype(str)
        .str.replace(",", ".", regex=False)
        .str.replace(" ", "", regex=False)
    )
    foncieres_all["Valeur fonciere"] = pd.to_numeric(foncieres_all["Valeur fonciere"], errors="coerce")
    foncieres_all = foncieres_all[
        (foncieres_all["Valeur fonciere"].notna()) &
        (foncieres_all["Valeur fonciere"] > 0) &
        (foncieres_all["annee"].notna())
    ]

    # -----------------------------
    # POPULATION COMMUNES
    # -----------------------------
    pop_communes_file = os.path.join(
        zip_folder, "pop_communes", "base-pop-historiques-1876-2023.xlsx"
    )
    df_pop = pd.read_excel(pop_communes_file, sheet_name="pop_1876_2023", header=5)
    colonnes_a_garder = ["CODGEO", "REG", "DEP", "LIBGEO", "PMUN2020", "PMUN2021", "PMUN2022", "PMUN2023"]
    pop_communes = df_pop[colonnes_a_garder].copy()
    pop_communes.columns = ["code_commune", "code_region", "code_departement", "nom_commune",
                            "pop_2020", "pop_2021", "pop_2022", "pop_2023"]
    pop_communes["code_departement"] = pop_communes["code_departement"].astype(str).str.zfill(2)

    # -----------------------------
    # POPULATION DÉPARTEMENTS
    # -----------------------------
    pop_dep_file = os.path.join(zip_folder, "pop_departement", "estim-pop-dep-sexe-gca-1975-2026.xlsx")
    pop_dep_all = []
    
    # Charger toutes les années disponibles de 2020 à 2026
    for annee in range(2020, 2027):
        try:
            # Lire le fichier Excel avec multi-index header
            df = pd.read_excel(pop_dep_file, sheet_name=str(annee), header=[3,4])
            
            # Aplatir les colonnes multi-index
            new_cols = []
            departements_count = 0
            for i, col in enumerate(df.columns):
                if isinstance(col, tuple):
                    level0 = str(col[0]).strip() if col[0] and 'Unnamed' not in str(col[0]) else ''
                    level1 = str(col[1]).strip() if col[1] and 'Unnamed' not in str(col[1]) else ''
                    
                    # Cas spécial pour les colonnes "Départements" (level1 est vide ou contient Unnamed)
                    if level0 == "Départements" and (not level1 or 'Unnamed' in str(col[1])):
                        if departements_count == 0:
                            new_cols.append("Code_departement")
                            departements_count += 1
                        else:
                            new_cols.append("Nom_departement")
                    # Si level1 est vide ou contient "Unnamed", utiliser seulement level0
                    elif not level1 or 'Unnamed' in str(col[1]):
                        new_cols.append(level0)
                    # Sinon combiner avec underscore
                    elif level0 and level1:
                        new_cols.append(f"{level0}_{level1}")
                    elif level0:
                        new_cols.append(level0)
                    elif level1:
                        new_cols.append(level1)
                    else:
                        new_cols.append('Unnamed')
                else:
                    new_cols.append(str(col))
            
            df.columns = new_cols
            
            # Nettoyer le code département - ATTENTION aux codes spéciaux
            # 2A, 2B (Corse), 971-976 (DOM-TOM) ne doivent PAS être modifiés
            df["Code_departement"] = df["Code_departement"].astype(str).str.strip()
            
            # Ne zfill que pour les codes numériques à 1 ou 2 chiffres
            def format_code_dept(code):
                code = str(code).strip()
                # Si c'est un nombre et qu'il fait moins de 3 caractères, on ajoute un zéro devant
                if code.isdigit() and len(code) < 3:
                    return code.zfill(2)
                # Sinon on garde tel quel (2A, 2B, 971, etc.)
                return code
            
            df["Code_departement"] = df["Code_departement"].apply(format_code_dept)
            df["annee"] = annee
            
            # La colonne Ensemble_Total devrait exister maintenant
            if "Ensemble_Total" in df.columns:
                df["Population_Totale"] = pd.to_numeric(df["Ensemble_Total"], errors='coerce')
            else:
                # Fallback: chercher une colonne qui contient "Ensemble" et "Total"
                ensemble_cols = [col for col in df.columns if 'Ensemble' in col and 'Total' in col]
                if ensemble_cols:
                    df["Population_Totale"] = pd.to_numeric(df[ensemble_cols[0]], errors='coerce')
                else:
                    print(f"ATTENTION: Colonne Ensemble_Total non trouvée pour l'année {annee}")
                    print(f"Colonnes disponibles: {df.columns.tolist()}")
                    df["Population_Totale"] = 0
            
            # Ne garder que les lignes où le code département est valide
            # Codes valides: 01-95 (2 chiffres), 2A, 2B (Corse), 971-976 (DOM-TOM)
            df = df[
                df["Code_departement"].str.match(r'^(\d{2}|2[AB]|\d{3})$', na=False)
            ]
            
            # Sélectionner les colonnes finales
            df = df[["Code_departement", "Nom_departement", "annee", "Population_Totale"]].copy()
            df = df.rename(columns={"Population_Totale": "Ensemble_Total"})
            
            pop_dep_all.append(df)
            print(f"✓ Données de population chargées pour l'année {annee}")
            
        except Exception as e:
            print(f"⚠ Impossible de charger les données pour l'année {annee}: {e}")
            continue
    
    if pop_dep_all:
        pop_dep_all = pd.concat(pop_dep_all, ignore_index=True)
        
        # Nettoyer les valeurs NaN
        pop_dep_all["Ensemble_Total"] = pd.to_numeric(pop_dep_all["Ensemble_Total"], errors='coerce').fillna(0)
    else:
        print("ERREUR: Aucune donnée de population n'a pu être chargée!")
        pop_dep_all = pd.DataFrame(columns=["Code_departement", "Nom_departement", "annee", "Ensemble_Total"])

    # -----------------------------
    # CACHE
    # -----------------------------
    data = {
        "foncieres_all": foncieres_all,
        "pop_communes": pop_communes,
        "pop_dep_all": pop_dep_all
    }

    with open(cache_file, "wb") as f:
        pickle.dump(data, f)

    return data