import os
import zipfile
import pandas as pd
import pickle

# =============================
# CONFIG
# =============================
zip_folder = "data"
cache_file = "data/cache_data.pkl"
annees = range(2020, 2026)

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

    # Population communes
    pop_communes_zip = os.path.join(zip_folder, "base-pop-historiques-1876-2023.zip")
    pop_communes_extract = os.path.join(zip_folder, "pop_communes")
    if os.path.exists(pop_communes_zip) and not os.path.exists(pop_communes_extract):
        os.makedirs(pop_communes_extract, exist_ok=True)
        with zipfile.ZipFile(pop_communes_zip, 'r') as zip_ref:
            zip_ref.extractall(pop_communes_extract)

    # Population départements
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

    # Extraction des fichiers si besoin
    extract_all_zips()

    # -----------------------------
    # CACHE
    # -----------------------------
    if os.path.exists(cache_file):
        with open(cache_file, "rb") as f:
            return pickle.load(f)

    print("⚙️ Génération des données...")

    # -----------------------------
    # DVF
    # -----------------------------
    dvf_list = []
    for annee in annees:
        extract_path = os.path.join(zip_folder, f"dvf_{annee}")
        if not os.path.exists(extract_path):
            print(f"⚠️ Dossier manquant pour {annee}, skipping")
            continue

        files = [f for f in os.listdir(extract_path) if f.endswith(".txt")]
        if not files:
            continue

        file_path = os.path.join(extract_path, files[0])
        df_temp = pd.read_csv(
            file_path,
            sep="|",
            usecols=["Date mutation", "Valeur fonciere", "Code departement", "Code commune"],
            dtype={"Code departement": "string", "Code commune": "string"},
            low_memory=False
        )
        df_temp["annee_fichier"] = annee
        dvf_list.append(df_temp)

    if dvf_list:
        foncieres_all = pd.concat(dvf_list, ignore_index=True)
    else:
        foncieres_all = pd.DataFrame()

    if not foncieres_all.empty:
        foncieres_all["Date mutation"] = pd.to_datetime(
            foncieres_all["Date mutation"], format="%d/%m/%Y", errors="coerce"
        )
        foncieres_all["annee"] = foncieres_all["Date mutation"].dt.year

        def format_code_dept(code):
            code = str(code).strip()
            if code.isdigit() and len(code) < 3:
                return code.zfill(2)
            return code  # laisse 2A / 2B intact
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
    pop_communes_file = os.path.join(zip_folder, "pop_communes", "base-pop-historiques-1876-2023.xlsx")
    df_pop = pd.read_excel(pop_communes_file, sheet_name="pop_1876_2023", header=5)
    colonnes_a_garder = ["CODGEO", "REG", "DEP", "LIBGEO", "PMUN2020", "PMUN2021", "PMUN2022", "PMUN2023"]
    pop_communes = df_pop[colonnes_a_garder].copy()
    pop_communes.columns = [
        "code_commune", "code_region", "code_departement", "nom_commune",
        "pop_2020", "pop_2021", "pop_2022", "pop_2023"
    ]
    pop_communes["code_departement"] = pop_communes["code_departement"].astype(str).str.zfill(2)

    # -----------------------------
    # POPULATION DÉPARTEMENTS
    # -----------------------------
    pop_dep_file = os.path.join(zip_folder, "pop_departement", "estim-pop-dep-sexe-gca-1975-2026.xlsx")
    pop_dep_all = []

    for annee in range(2020, 2027):
        try:
            df = pd.read_excel(pop_dep_file, sheet_name=str(annee), header=[3,4])

            # Aplatir colonnes multi-index
            new_cols = []
            dept_count = 0
            for col in df.columns:
                if isinstance(col, tuple):
                    lvl0 = str(col[0]).strip()
                    lvl1 = str(col[1]).strip()
                    if "Départements" in lvl0 and "Unnamed" in lvl1:
                        new_cols.append("Code_departement" if dept_count==0 else "Nom_departement")
                        dept_count += 1
                    elif "Ensemble" in lvl0:
                        new_cols.append("Ensemble_Total" if "Total" in lvl1 else f"Ensemble_{lvl1}")
                    else:
                        new_cols.append(f"{lvl0}_{lvl1}" if lvl1 != "nan" else lvl0)
                else:
                    new_cols.append(str(col))
            df.columns = new_cols
            df["Code_departement"] = df["Code_departement"].astype(str).str.strip()

            # Colonnes à garder
            cols_to_keep = ["Code_departement", "Nom_departement", "Ensemble_Total"]
            for col in df.columns:
                if col.startswith("Ensemble_") and col != "Ensemble_Total":
                    cols_to_keep.append(col)
            cols_existantes = [c for c in cols_to_keep if c in df.columns]
            df = df[cols_existantes].copy()
            df["annee"] = annee
            pop_dep_all.append(df)

            print(f"✓ Population département {annee} : {len(cols_existantes)-2} colonnes ({', '.join([c for c in cols_existantes if 'Ensemble_' in c])})")
        except Exception as e:
            print(f"⚠ Erreur année {annee}: {e}")

    pop_dep_all = pd.concat(pop_dep_all, ignore_index=True)
    for col in pop_dep_all.columns:
        if col.startswith("Ensemble_"):
            pop_dep_all[col] = pd.to_numeric(pop_dep_all[col], errors="coerce")

    # -----------------------------
    # ENREGISTREMENT CACHE
    # -----------------------------
    data = {
        "foncieres_all": foncieres_all,
        "pop_communes": pop_communes,
        "pop_dep_all": pop_dep_all
    }

    os.makedirs(os.path.dirname(cache_file), exist_ok=True)
    with open(cache_file, "wb") as f:
        pickle.dump(data, f)

    print("✅ Données chargées et mises en cache.")

    return data
