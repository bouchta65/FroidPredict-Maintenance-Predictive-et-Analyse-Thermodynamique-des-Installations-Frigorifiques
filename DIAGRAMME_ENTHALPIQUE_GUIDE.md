# Guide du Diagramme Enthalpique - Installations Frigorifiques

## 📊 Présentation du Diagramme Enthalpique

Le diagramme enthalpique (P-h) est un outil thermodynamique fondamental pour l'analyse des cycles frigorifiques. Il représente la relation entre la **pression** (axe Y) et l'**enthalpie** (axe X) du fluide frigorigène.

### 🔄 Cycle Frigorifique Théorique

Le cycle frigorifique se compose de 4 transformations principales :

#### Point 1 : Sortie Évaporateur
- **État** : Vapeur surchauffée
- **Température** : T_évaporateur + surchauffe
- **Pression** : Pression basse du système
- **Processus** : Évaporation complète + surchauffe

#### Point 2 : Sortie Compresseur
- **État** : Vapeur haute pression haute température
- **Température** : T_refoulement compresseur
- **Pression** : Pression haute du système
- **Processus** : Compression isentropique (théorique)

#### Point 3 : Sortie Condenseur
- **État** : Liquide sous-refroidi
- **Température** : T_condenseur - sous-refroidissement
- **Pression** : Pression haute du système
- **Processus** : Condensation complète + sous-refroidissement

#### Point 4 : Sortie Détendeur
- **État** : Mélange liquide-vapeur
- **Température** : T_évaporateur
- **Pression** : Pression basse du système
- **Processus** : Détente isenthalpique

## 🌡️ Détermination des Températures

### Température d'Évaporation

La température d'évaporation est déterminée par :

1. **Charge thermique** : Plus la charge est élevée, plus la température d'évaporation doit être proche de la température souhaitée
2. **Type d'application** :
   - Conservation : -18°C à -25°C
   - Réfrigération : 0°C à 5°C
   - Climatisation : 7°C à 12°C
3. **Efficacité énergétique** : Une température d'évaporation plus élevée améliore le COP

#### Calcul Optimal
```
T_évap_optimale = T_chambre - ΔT_échangeur - ΔT_régulation
```

Où :
- T_chambre : Température souhaitée dans l'enceinte
- ΔT_échangeur : Différence de température évaporateur (5-10°C)
- ΔT_régulation : Marge de régulation (2-5°C)

### Température de Condensation

La température de condensation dépend de :

1. **Température ambiante** : T_condensation = T_ambiante + ΔT_condenseur
2. **Type de condenseur** :
   - Air forcé : ΔT = 10-15°C
   - Eau : ΔT = 5-8°C
   - Évaporatif : ΔT = 7-10°C
3. **Conditions de fonctionnement** : Propreté, débit d'air/eau

#### Calcul Optimal
```
T_cond_optimale = T_ambiante + ΔT_condenseur + ΔT_sécurité
```

Où :
- T_ambiante : Température de l'air ou de l'eau de refroidissement
- ΔT_condenseur : Différence de température condenseur
- ΔT_sécurité : Marge de sécurité (3-5°C)

## 📈 Analyse des Performances

### Coefficient de Performance (COP)
```
COP = Effet_frigorifique / Travail_compression
COP = (h1 - h4) / (h2 - h1)
```

### Puissance Frigorifique
```
P_froid = ṁ × (h1 - h4)
```

### Puissance Électrique
```
P_élec = ṁ × (h2 - h1) / η_compresseur
```

## 🚨 Alertes et Diagnostics

### Alertes Température Évaporateur
- **> -5°C** : Perte de capacité frigorifique
- **< -20°C** : Risque de givrage excessif
- **Fluctuations** : Problème de régulation

### Alertes Température Condenseur
- **> 50°C** : Risque de surchauffe
- **> 55°C** : Déclenchement sécurités
- **Instabilité** : Problème de refroidissement

### Alertes Pressions
- **HP > 16 bar** : Température condensation trop élevée
- **BP < 1.5 bar** : Fuite de fluide frigorigène
- **Ratio HP/BP > 8** : Efficacité réduite

### Alertes Surchauffe/Sous-refroidissement
- **Surchauffe < 3°C** : Risque de retour liquide
- **Surchauffe > 15°C** : Perte d'efficacité
- **Sous-refroidissement < 2°C** : Charge insuffisante
- **Sous-refroidissement > 8°C** : Surcharge possible

## 🔧 Actions Correctives

### Optimisation Température Évaporation
1. **Trop élevée** :
   - Vérifier charge en fluide frigorigène
   - Nettoyer évaporateur
   - Contrôler débit d'air
   - Vérifier détendeur

2. **Trop basse** :
   - Réduire ouverture détendeur
   - Vérifier programmation dégivrage
   - Contrôler ventilateurs évaporateur

### Optimisation Température Condensation
1. **Trop élevée** :
   - Nettoyer condenseur
   - Vérifier débit d'air/eau
   - Contrôler ventilateurs
   - Vérifier charge fluide

2. **Trop basse** :
   - Installer régulation pression condensation
   - Vérifier conditions ambiantes
   - Contrôler ventilateurs (vitesse variable)

## 📊 Utilisation du Dashboard

### Visualisation Temps Réel
- **Cycle frigorifique** : Visualisation des 4 points sur le diagramme P-h
- **Évolution temporelle** : Suivi des performances
- **Comparaison machines** : Analyse comparative

### Analyse Prédictive
- **Détection anomalies** : Écarts par rapport aux conditions optimales
- **Prédiction pannes** : Algorithmes de machine learning
- **Optimisation énergétique** : Recommandations d'amélioration

### Recommandations Automatiques
- **Maintenance préventive** : Planification basée sur les tendances
- **Optimisation réglages** : Ajustements automatiques
- **Alertes prioritaires** : Classification par criticité

## 🎯 Objectifs de Performance

### Indicateurs Clés
- **COP > 2.5** : Efficacité énergétique acceptable
- **Stabilité températures** : Variation < 2°C
- **Temps de démarrage** : < 10 minutes
- **Fréquence dégivrage** : Optimisée selon conditions

### Seuils d'Alerte
- **Critique** : Risque arrêt immédiat
- **Élevée** : Intervention sous 24h
- **Moyenne** : Surveillance renforcée
- **Faible** : Maintenance préventive

## 🌡️ Fluides Frigorigènes

### R404A (Configuration Actuelle)
- **Application** : Froid commercial/industriel
- **Température évaporation** : -40°C à 0°C
- **Pression service** : 2-15 bar
- **Caractéristiques** : Excellent pouvoir frigorifique

### Propriétés Thermodynamiques
- **Température critique** : 72.1°C
- **Pression critique** : 37.3 bar
- **Température d'ébullition** : -46.6°C (1 bar)
- **Densité liquide** : 1.04 kg/L (25°C)

---

*Ce guide technique accompagne le dashboard de maintenance prédictive pour optimiser les performances des installations frigorifiques.*
