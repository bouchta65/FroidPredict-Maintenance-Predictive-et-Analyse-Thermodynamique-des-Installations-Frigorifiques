# Diagramme de Mollier pour le Fluide Frayo

## 📊 Description Générale

Le diagramme de Mollier (h-s) généré représente les propriétés thermodynamiques du fluide frigorigène **Frayo**, spécialement adapté aux systèmes de refroidissement avec réservoir.

## 🧊 Caractéristiques du Fluide Frayo

### Propriétés Critiques
- **Nom du fluide** : Frayo (fluide frigorigène synthétique)
- **Température critique** : 101.06°C
- **Pression critique** : 37.29 bar
- **Masse molaire** : 97.6 g/mol
- **Constante des gaz** : 0.08314 kJ/kg·K

### Plages de Fonctionnement
- **Températures** : -20°C à 60°C
- **Pressions** : 0.5 à 20 bar
- **Applications** : Systèmes de climatisation, chambres froides, refroidissement industriel

## 📈 Éléments du Diagramme

### 1. Courbe de Saturation (Dôme)
- **Courbe liquide saturé** (gauche) : Limite entre zone liquide et zone diphasique
- **Courbe vapeur saturée** (droite) : Limite entre zone diphasique et zone vapeur
- **Point critique** : Convergence des deux courbes

### 2. Zones Colorées
- 🔵 **Zone Liquide** (Bleu) : Liquide sous-refroidi
- 🔴 **Zone Vapeur** (Rouge) : Vapeur surchauffée  
- 🟣 **Zone Diphasique** (Violet) : Mélange liquide-vapeur

### 3. Lignes Caractéristiques

#### Isobares (Lignes de Pression Constante)
Pressions représentées : 1, 2, 5, 8, 12, 16, 20 bar
- Lignes pointillées grises
- Permettent de suivre les transformations à pression constante

#### Isothermes (Lignes de Température Constante)
Températures représentées : -10, 0, 10, 20, 30, 40, 50°C
- Lignes fines grises
- Permettent de suivre les transformations à température constante

## 🔄 Cycle Frigorifique Représenté

Le diagramme inclut un cycle de compression frigorifique typique avec 4 points caractéristiques :

### Point 1 : Sortie Évaporateur
- **État** : Vapeur saturée sèche
- **Température** : -10°C (température d'évaporation)
- **Processus** : Évaporation complète du fluide

### Point 2 : Sortie Compresseur
- **État** : Vapeur surchauffée haute pression
- **Température** : ~60°C
- **Processus** : Compression isentropique (entropie constante)

### Point 3 : Sortie Condenseur
- **État** : Liquide saturé
- **Température** : 40°C (température de condensation)
- **Processus** : Condensation complète

### Point 4 : Sortie Détendeur
- **État** : Mélange liquide-vapeur
- **Processus** : Détente isenthalpique (enthalpie constante)

## 📊 Données Réservoir

### Points de Mesure Simulés
- **50 points de données** collectés depuis le réservoir
- **Distribution aléatoire** mais réaliste dans les plages de fonctionnement
- **Représentation** : Points dorés sur le diagramme

### Types de Données
1. **Liquide sous-refroidi** : T < T_saturation - 2°C
2. **Vapeur surchauffée** : T > T_saturation + 2°C  
3. **Mélange diphasique** : Zone de saturation avec titre vapeur variable

## 🎯 Applications Pratiques

### 1. Analyse des Performances
- **COP (Coefficient de Performance)** : Calcul basé sur les enthalpies
- **Efficacité énergétique** : Optimisation du cycle
- **Consommation électrique** : Estimation de la puissance compresseur

### 2. Diagnostic des Anomalies
- **Surchauffe excessive** : Point 2 trop éloigné de la courbe de saturation
- **Sous-refroidissement insuffisant** : Point 3 dans la zone diphasique
- **Fuite de fluide** : Déplacement des points de fonctionnement

### 3. Maintenance Prédictive
- **Suivi tendances** : Évolution des points de fonctionnement
- **Alertes préventives** : Détection précoce des dérives
- **Optimisation** : Ajustement des paramètres de régulation

## 🔧 Utilisation du Diagramme

### Lecture des Propriétés
1. **Localiser le point** de fonctionnement (intersection T, P)
2. **Lire l'enthalpie** sur l'axe vertical (kJ/kg)
3. **Lire l'entropie** sur l'axe horizontal (kJ/kg·K)
4. **Identifier la zone** (liquide, vapeur, diphasique)

### Calculs Thermodynamiques
```
Effets Frigorifiques :
- Effet frigorifique = h₁ - h₄
- Travail de compression = h₂ - h₁  
- Chaleur rejetée = h₂ - h₃
- COP = (h₁ - h₄) / (h₂ - h₁)
```

## 📱 Interface Web

### Fonctionnalités Disponibles
- **Génération automatique** : API REST `/api/mollier_frayo`
- **Téléchargement haute résolution** : PNG 300 DPI
- **Propriétés thermodynamiques** : API `/api/frayo_properties`
- **Interface responsive** : Accessible sur mobile et desktop

### Accès
- **URL** : `http://localhost:5002/mollier-frayo`
- **Navigation** : Menu principal → Diagramme Mollier Frayo
- **Temps de génération** : ~2-3 secondes

## 🚀 Évolutions Futures

### Améliorations Prévues
1. **Données temps réel** : Intégration capteurs IoT réservoir
2. **Analyse prédictive** : IA pour détection anomalies
3. **Export multi-formats** : PDF, SVG, EPS
4. **Comparaison fluides** : Diagrammes superposés R404A vs Frayo

### Personnalisation
- **Plages variables** : Adaptation selon installation
- **Cycles spécifiques** : Transcritique, cascade, etc.
- **Points de mesure** : Intégration données réelles capteurs

## 📞 Support

Pour toute question technique ou suggestion d'amélioration :
- **Documentation** : Voir `API_DOCUMENTATION.md`
- **Tests** : Exécuter `test_diagram_api.py`
- **Logs** : Consulter les logs Flask pour debug

---
*Diagramme généré automatiquement par le système de maintenance prédictive*  
*Version : 1.0 | Date : 2025*
