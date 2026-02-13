# Projet Données Ouvertes - Impact de la Population sur les Valeurs Foncières

**Étudiantes:** AIT ABDELKADER Anais / RUCH Justine  
**Formation:** MSS / CMI ISI  
**Date:** Février 2026

## Problématique

**Comment les dynamiques de populations impactent-elles les valeurs foncières en France ?**



## Sources de données

### Données immobilières : datagouv
- **Source :** [Site du gouvernement](https://www.data.gouv.fr/datasets/demandes-de-valeurs-foncieres),
- **Période :** 2020-2025 (données 2020 et 2025 partielles)
- **Volumétrie :** Environ 20 millions de transactions immobilières
- **Variables clés :**
    - Valeur foncière
    - Date de mutation
    - Localisation (code département, code commune)
    - Nature du bien

### Données démographiques : INSEE
**Données pour les départements**
- **Source :** [Institut national de la statistique et des études économiques](https://www.insee.fr/fr/statistiques/8721456)
- **Fichier :** Estimations de population par département, sexe et grande classe d'âge (1975-2026)
- **Période :** 2020-2026 (projections pour 2025-2026)
- **Variables clés :** 
  - Population totale par département
  - Répartition par tranches d'âge : 0-19 ans, 20-39 ans, 40-59 ans, 60-74 ans, 75 ans et plus
  - Répartition par sexe

**Données pour les communes**
- **Source :** [Institut national de la statistique et des études économiques](https://www.insee.fr/fr/statistiques/3698339)
- **Fichier :** Estimations de population par communes (1975-2023)
- **Période :** 2020-2023 
- **Variables clés :** 
  - Population totale par département
  - Répartition par tranches d'âge : 0-19 ans, 20-39 ans, 40-59 ans, 60-74 ans, 75 ans et plus
  - Répartition par sexe

### Données géographiques : datagouv
- **Source :** [Site du gouvernement](https://www.data.gouv.fr/datasets/communes-et-villes-de-france-en-csv-excel-json-parquet-et-feather),
- **Fichier :** Informations sur les communes de France
- **Variables clés :**
    - Code insee
    - Nom de la commune
    - Latitude
    - Longitude

## Utilisation du dashboard
Pour utiliser cette application vous devez d'abord cloner le code, de préférence dans un environnement. Il faut ensuite installer les librairies nécessaires pour faire tourner l'application, pour cela il vous suffit d'utiliser la commande suivante dans votre terminale :   
```bash 
pip install -r requirements.txt
```
Enfin pour lancer l'application il faut utiliser la commande :
```bash 
python app.py
```

---

##  Contributeurs

<table>
  <tr>
    <td align="center" style="padding: 10px;">
      <a href="https://github.com/anais-ait">
        <img src="https://secure.gravatar.com/avatar/7d204642ca72d0d776aedb48dbc2886667564dde24fd2d7dde26d07fa1c4a2ab?s=1600&d=identicon" width="100" height="100" alt="" style="border-radius:50%;"/><br />
        <sub><b>Anais Ait abdelkader</b></sub>
      </a><br />
      <sub>MSS</sub>
    </td>
    <td align="center" style="padding: 10px;">
      <a href="https://github.com/juruch">
        <img src="https://secure.gravatar.com/avatar/d53c9c96ab8323d7fb5c21de49ed73eeacb341d366be7e98acf024ae3bea8bff?s=1600&d=identicon" width="100" height="100" alt="" style="border-radius:50%;"/><br />
        <sub><b>Justine Ruch</b></sub>
      </a><br />
      <sub>CMI ISI</sub>
  </tr>
</table>

**Contacts :** 

anais.ait-abdelkader@u-bordeaux.fr 

justine.ruch@u-bordeaux.fr 
