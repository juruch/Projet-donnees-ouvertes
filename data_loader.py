import os
import pickle
import pandas as pd

# =============================
# CONFIG
# =============================
DATA_FOLDER = "data"
CACHE_FILE = os.path.join(DATA_FOLDER, "cache_data.pkl")
ANNEES = range(2020, 2026)

def _ensure_cache_dir():
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)

# =============================
# CHARGEMENT GLOBAL
# =============================
def load_all_data():
    _ensure_cache_dir()

    # -----------------------------
    # CACHE
    # -----------------------------
    if os.path.exists(CACHE_FILE):
        print(f"📦 Cache trouvé: {CACHE_FILE}")
        with open(CACHE_FILE, "rb") as f:
            return pickle.load(f)

    print("⚙️ Pas de cache, génération…")

    # -----------------------------
    # DVF
    # -----------------------------
    dvf_list = []

    for annee in ANNEES:
        extract_path = os.path.join(DATA_FOLDER, f"dvf_{annee}")

        if not os.path.exists(extract_path):
            print(f"⚠️ Dossier manquant: {extract_path}")
            continue

        files = [f for f in os.listdir(extract_path) if f.endswith(".txt")]
        if not files:
            print(f"⚠️ Aucun .txt dans {extract_path}")
            continue

        file_path = os.path.join(extract_path, files[0])
        print(f"📄 Lecture DVF {annee}: {file_path}")

        try:
            df_temp = pd.read_csv(
                file_path,
                sep="|",
                usecols=["Date mutation", "Valeur fonciere", "Code departement", "Code commune"],
                dtype="string",
                engine="c",
                low_memory=True
            )
            df_temp["annee_fichier"] = str(annee)
            dvf_list.append(df_temp)
        except Exception as e:
            print(f"⚠️ Erreur DVF {annee} : {e}")

    foncieres_all = pd.concat(dvf_list, ignore_index=True) if dvf_list else pd.DataFrame()

    # Nettoyage DVF
    if not foncieres_all.empty:
        foncieres_all["Date mutation"] = pd.to_datetime(
            foncieres_all["Date mutation"],
            format="%d/%m/%Y",
            errors="coerce"
        )
        foncieres_all["annee"] = foncieres_all["Date mutation"].dt.year

        def format_code_dept(code):
            code = str(code).strip()
            if code.isdigit() and len(code) < 3:
                return code.zfill(2)
            return code

        foncieres_all["Code departement"] = foncieres_all["Code departement"].apply(format_code_dept)

        foncieres_all["Valeur fonciere"] = (
            foncieres_all["Valeur fonciere"]
            .str.replace(",", ".", regex=False)
            .str.replace(" ", "", regex=False)
        )
        foncieres_all["Valeur fonciere"] = pd.to_numeric(foncieres_all["Valeur fonciere"], errors="coerce")
        foncieres_all = foncieres_all[foncieres_all["Valeur fonciere"].notna()].copy()
    else:
        print("⚠️ Aucune donnée DVF chargée (foncieres_all vide).")

    # -----------------------------
    # POP COMMUNES
    # -----------------------------
    pop_communes_file = os.path.join(
        DATA_FOLDER,
        "pop_communes",
        "base-pop-historiques-1876-2023.xlsx"
    )

    pop_communes = pd.DataFrame()
    if os.path.exists(pop_communes_file):
        print(f"📄 Lecture pop communes: {pop_communes_file}")
        df_pop = pd.read_excel(pop_communes_file, sheet_name="pop_1876_2023", header=5)

        colonnes = ["CODGEO", "REG", "DEP", "LIBGEO", "PMUN2020", "PMUN2021", "PMUN2022", "PMUN2023"]
        pop_communes = df_pop[colonnes].copy()
        pop_communes.columns = [
            "code_commune", "code_region", "code_departement", "nom_commune",
            "pop_2020", "pop_2021", "pop_2022", "pop_2023"
        ]
        pop_communes["code_departement"] = pop_communes["code_departement"].astype(str).str.zfill(2)
    else:
        print(f"⚠️ Fichier pop communes manquant: {pop_communes_file}")

    # -----------------------------
    # POP DÉPARTEMENTS
    # -----------------------------
    pop_dep_file = os.path.join(
        DATA_FOLDER,
        "pop_departement",
        "estim-pop-dep-sexe-gca-1975-2026.xlsx"
    )

    pop_dep_all = []
    if os.path.exists(pop_dep_file):
        print(f"📄 Lecture pop départements: {pop_dep_file}")

        for annee in range(2020, 2027):
            try:
                df = pd.read_excel(pop_dep_file, sheet_name=str(annee), header=[3, 4])

                new_cols = []
                dept_count = 0
                for col in df.columns:
                    if isinstance(col, tuple):
                        lvl0, lvl1 = str(col[0]), str(col[1])
                        if "Départements" in lvl0 and "Unnamed" in lvl1:
                            new_cols.append("Code_departement" if dept_count == 0 else "Nom_departement")
                            dept_count += 1
                        elif "Ensemble" in lvl0:
                            new_cols.append("Ensemble_Total" if "Total" in lvl1 else f"Ensemble_{lvl1}")
                        else:
                            new_cols.append(f"{lvl0}_{lvl1}")
                    else:
                        new_cols.append(str(col))

                df.columns = new_cols
                df["Code_departement"] = df["Code_departement"].astype(str).str.strip()

                cols = [c for c in df.columns if c.startswith("Ensemble_")]
                df = df[["Code_departement", "Nom_departement"] + cols].copy()
                df["annee"] = annee
                pop_dep_all.append(df)

            except Exception as e:
                print(f"⚠️ Population département {annee}: {e}")

    else:
        print(f"⚠️ Fichier pop départements manquant: {pop_dep_file}")

    pop_dep_all = pd.concat(pop_dep_all, ignore_index=True) if pop_dep_all else pd.DataFrame()

    for col in pop_dep_all.columns:
        if col.startswith("Ensemble_"):
            pop_dep_all[col] = pd.to_numeric(pop_dep_all[col], errors="coerce")

    # -----------------------------
    # CACHE SAVE
    # -----------------------------
    data = {
        "foncieres_all": foncieres_all,
        "pop_communes": pop_communes,
        "pop_dep_all": pop_dep_all
    }

    with open(CACHE_FILE, "wb") as f:
        pickle.dump(data, f)

    print(f"✅ Cache écrit: {CACHE_FILE}")
    return data
