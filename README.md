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

## Résultats Principaux

### 1. Corrélation Population-Prix
✓ **Corrélation positive significative** (r ≈ 0.4-0.5)
- Les départements plus peuplés ont des prix plus élevés
- Relation non-linéaire: effet de saturation dans les métropoles

### 2. Impact de la Structure par Âge
✓ **Proportion 20-39 ans:** Corrélation positive forte
- Segments d'âge actifs économiquement → demande immobilière élevée

✓ **Proportion 75+ ans:** Corrélation négative
- Départements vieillissants → prix moins dynamiques

✓ **Amélioration du modèle:** +15-25% en ajoutant la structure d'âge

### 3. Élasticité
✓ **Élasticité estimée:** ≈ 0.3-0.5
- **Interprétation:** +1% de population → +0.3 à 0.5% de prix
- Confirme l'effet significatif mais non-proportionnel

### 4. Dynamique de Croissance
✓ **Corrélation faible** entre taux de croissance pop et prix (r ≈ 0.1-0.2)
- Les effets se manifestent sur le long terme
- Importance des facteurs non-démographiques à court terme

### 5. Hétérogénéité Territoriale
✓ **Fortes disparités entre départements:**
- **Île-de-France:** Prix très élevés (>400k€) malgré croissance démographique modérée
- **Métropoles régionales:** Prix élevés (200-300k€) avec forte attractivité
- **Zones rurales:** Prix bas (<150k€) malgré déclin démographique limité

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

### Code
1. `final_notebook.py` - Notebook Python complet et commenté

## Limites et Perspectives

### Limites
- Modèles linéaires simples (relations plus complexes possibles)
- Nombreux facteurs non-démographiques non pris en compte:
  - Revenus, emploi, politique du logement
  - Taux d'intérêt, accès au crédit
  - Attractivité économique, infrastructures
- Données 2025 partielles (année en cours)
- Pas d'analyse spatiale (effets de voisinage)

### Perspectives d'Amélioration
1. **Données supplémentaires:**
   - Variables économiques (PIB, revenus, emploi)
   - Variables géographiques (distance aux métropoles)
   - Variables politiques (ZAN, réglementation)

2. **Modèles plus avancés:**
   - Random Forest, XGBoost (relations non-linéaires)
   - Modèles à effets fixes (panel data)
   - Modèles spatio-temporels

3. **Analyses complémentaires:**
   - Segmentation par type de bien (maison/appartement)
   - Analyse des migrations internes
   - Impact du télétravail post-COVID

## Réponse au Professeur

### Question 1: "Quels modèles de prédiction vous considérez ?"
**Réponse:** Nous utilisons 3 approches complémentaires:
1. **Régression linéaire simple** (baseline): Population → Prix
2. **Régression multiple**: Population + Structure d'âge → Prix
3. **Modèle Log-Log**: Pour estimer l'élasticité prix/population

Ces modèles sont entraînés sur 2020-2024 et testés sur 2025, puis utilisés pour prédire 2026.

### Question 2: "Pourquoi se restreindre aux 10 villes les plus peuplées ?"
**Réponse corrigée:** Nous avons étendu l'analyse aux **100 communes les plus peuplées** (pas seulement 10) pour avoir une représentation significative du territoire tout en conservant un volume de données gérable. Ces 100 communes représentent environ 30% de la population française et incluent toutes les métropoles majeures.

### Question 3: "Que voulez-vous dire par 'Comparer les valeurs de 2020 à 2026' ?"
**Réponse:** Notre analyse comporte deux volets:

**Pour les départements (2020-2026):**
- Analyse descriptive de l'évolution réelle 2020-2025
- Modélisation de la relation Population/Prix sur 2020-2024
- Test du modèle sur 2025 (validation)
- Prédiction pour 2026 basée sur les projections démographiques INSEE

**Pour les communes (2020-2023):**
- Analyse de la relation Population/Prix au niveau local
- Identification des patterns différents du niveau départemental
- Pas de prédiction car données démographiques limitées à 2023

Il s'agit donc d'une **analyse de régression** avec capacité prédictive, pas de classification.

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

**Contenu recommandé du dashboard:**
1. Carte interactive de France avec valeurs par département (slider temporel)
2. Graphiques d'évolution temporelle
3. Scatter plots avec filtres interactifs
4. Prédictions 2026 avec intervalles de confiance
5. Analyse communale pour les grandes villes

---

**Contact:** justine.ruch@u-bordeaux.fr
