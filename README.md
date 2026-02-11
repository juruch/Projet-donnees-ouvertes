# Projet Données Ouvertes - Impact de la Population sur les Valeurs Foncières

**Étudiantes:** AIT ABDELKADER Anais / RUCH Justine  
**Formation:** MSS / CMI ISI  
**Date:** Février 2026

## Problématique

**Comment les dynamiques de populations impactent-elles les valeurs foncières en France ?**

## Sources de Données

### 1. Données Immobilières - DVF (Demandes de Valeurs Foncières)
- **Source:** data.gouv.fr
- **Période:** 2020-2025
- **Contenu:** ~20 millions de transactions immobilières
- **Variables clés:** Valeur foncière, date, localisation (département, commune)

### 2. Données Démographiques - INSEE
- **Source:** INSEE
- **Fichier:** `estim-pop-dep-sexe-gca-1975-2026.xlsx`
- **Période:** 2020-2026
- **Contenu:** Population par département et tranche d'âge
- **Variables clés:** 
  - Population totale
  - Répartition par âge (0-19, 20-39, 40-59, 60-74, 75+)
  - Répartition par sexe

### 3. Données Communales
- **Source:** INSEE
- **Fichier:** `base-pop-historiques-1876-2023.xlsx`
- **Période:** 2020-2023
- **Contenu:** Population des communes françaises

## Structure de l'Analyse

### Partie 1: Chargement et Préparation des Données
- Chargement des 6 fichiers DVF (2020-2025)
- Nettoyage: conversion dates, valeurs foncières, codes départements
- Chargement des 7 années de données démographiques (2020-2026)
- Agrégation par département et année

### Partie 2: Fusion des Données
- Fusion DVF + démographie par (département, année)
- Calcul des proportions par tranche d'âge
- Calcul des taux de croissance annuels

### Partie 3: Analyse Exploratoire
- Statistiques descriptives
- Corrélations Population/Prix
- Corrélations Structure d'âge/Prix
- Analyse des taux de croissance

### Partie 4: Visualisations
1. Évolution temporelle des prix (médian vs moyen)
2. Scatter plot Population vs Valeur foncière
3. Heatmap des corrélations
4. Comparaison des taux de croissance

### Partie 5: Modélisation
1. **Modèle 1:** Régression linéaire simple (Population → Prix)
2. **Modèle 2:** Régression multiple (Population + Structure d'âge → Prix)
3. **Modèle 3:** Modèle Log-Log pour estimer l'élasticité
4. **Prédictions:** 2025-2026 par département

### Partie 6: Visualisation des Prédictions
- Graphiques interactifs des prédictions vs réel
- Top départements avec plus forte hausse attendue

### Partie 7: Analyse Communale
- Focus sur les 100 communes les plus peuplées
- Relation Population/Prix au niveau local

### Partie 8: Export des Résultats
- Résultats des modèles (CSV)
- Prédictions 2026 (CSV)
- Données pour dashboard (CSV)


## Fichiers Générés

### Graphiques (PNG + HTML)
1. `evolution_prix.png` - Évolution temporelle des prix médians et moyens
2. `scatter_pop_prix.html` - Scatter plot interactif Population vs Prix
3. `heatmap_correlation.png` - Matrice de corrélation
4. `taux_croissance.html` - Comparaison taux de croissance interactif
5. `predictions_evolution.html` - Prédictions 2025-2026 interactives
6. `communes_top100.html` - Analyse communale animée

### Données (CSV)
1. `resultats_modeles.csv` - Résumé des performances des modèles
2. `predictions_2026.csv` - Prédictions par département pour 2026
3. `donnees_dashboard.csv` - Dataset complet pour dashboard interactif

## Instructions d'Utilisation

### Exécution du Notebook
```bash
python final_notebook.py
```

### Prérequis
```python
numpy
pandas
matplotlib
seaborn
plotly
scikit-learn
openpyxl  # pour lire les fichiers Excel
```

### Fichiers Nécessaires
- `ValeursFoncieres-2020.txt` à `ValeursFoncieres-2025.txt`
- `estim-pop-dep-sexe-gca-1975-2026.xlsx`
- `base-pop-historiques-1876-2023.xlsx`

### Temps d'Exécution Estimé
- Chargement données: ~5-10 minutes
- Analyses et visualisations: ~2-3 minutes
- **Total: ~15 minutes**

## Dashboard

Le dashboard interactif utilise les fichiers générés:
- `donnees_dashboard.csv` - Données principales
- Fichiers HTML interactifs (Plotly)

---

**Contacts :** justine.ruch@u-bordeaux.fr 
anais.ait-abdelkader@u-bordeaux.fr 
