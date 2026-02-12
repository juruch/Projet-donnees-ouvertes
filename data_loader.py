import os
import zipfile
import pandas as pd
import pickle

zip_folder = "data"
cache_file = "data/cache_data.pkl"
annees = range(2020, 2026)


def extract_all_zips():
    for annee in annees:
        zip_path = os.path.join(zip_folder, f"ValeursFoncieres-{annee}.zip")
        extract_path = os.path.join(zip_folder, f"dvf_{annee}")

        if os.path.exists(zip_path) and not os.path.exists(extract_path):
            os.makedirs(extract_path, exist_ok=True)
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)

    pop_dep_zip = os.path.join(zip_folder, "estim-pop-dep-sexe-gca-1975-2026.zip")
    pop_dep_extract = os.path.join(zip_folder, "pop_dep")

    if os.path.exists(pop_dep_zip) and not os.path.exists(pop_dep_extract):
        os.makedirs(pop_dep_extract, exist_ok=True)
        with zipfile.ZipFile(pop_dep_zip, 'r') as zip_ref:
            zip_ref.extractall(pop_dep_extract)

    pop_communes_zip = os.path.join(zip_folder, "base-pop-historiques-1876-2023.zip")
    pop_communes_extract = os.path.join(zip_folder, "pop_communes")

    if os.path.exists(pop_communes_zip) and not os.path.exists(pop_communes_extract):
        os.makedirs(pop_communes_extract, exist_ok=True)
        with zipfile.ZipFile(pop_communes_zip, 'r') as zip_ref:
            zip_ref.extractall(pop_communes_extract)


def load_all_data():

    if os.path.exists(cache_file):
        with open(cache_file, 'rb') as f:
            return pickle.load(f)

    dvf_list = []

    for annee in annees:
        extract_path = os.path.join(zip_folder, f"dvf_{annee}")
        files = [f for f in os.listdir(extract_path) if f.endswith('.txt')]

        if files:
            file_path = os.path.join(extract_path, files[0])

            df_temp = pd.read_csv(
                file_path,
                sep="|",
                usecols=[
                    "Valeur fonciere",
                    "Code departement",
                    "Code commune"
                ],
                low_memory=False
            )

            df_temp["annee"] = annee
            dvf_list.append(df_temp)

    foncieres_all = pd.concat(dvf_list, ignore_index=True)
    na_count = foncieres_all.isna().sum()
    foncieres_all = foncieres_all.loc[:, na_count < 1_000_000]
    foncieres_all['annee'] = foncieres_all['Date mutation'].dt.year

    foncieres_all['Date mutation'] = pd.to_datetime(
    foncieres_all['Date mutation'],
    format='%d/%m/%Y',
    errors='coerce')
    foncieres_all['annee'] = foncieres_all['Date mutation'].dt.year


    foncieres_all = foncieres_all[foncieres_all['Valeur fonciere'] > 0]

    # Population communes
    pop_communes_file = os.path.join(
        zip_folder,
        "pop_communes",
        "base-pop-historiques-1876-2023.xlsx"
    )

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

    data = {
        'foncieres_all': foncieres_all,
        'pop_communes': pop_communes
    }

    with open(cache_file, 'wb') as f:
        pickle.dump(data, f)

    return data
