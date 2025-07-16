# Guide d'Intégration des Capteurs Réels - Système Frigorifique

## 📋 Vue d'ensemble

Ce guide décrit l'intégration des capteurs réels dans le système de maintenance prédictive des installations frigorifiques, basée sur les spécifications PDF fournies.

## 🔧 Architecture des Capteurs

### Capteurs de Pression (4 capteurs minimum)

#### 1. **Pression Haute (HP)**
- **Position** : Après le compresseur ou dans le condenseur
- **Plage normale** : 8.0 - 20.0 bar
- **Précision** : ±0.1 bar
- **Utilisation** : Surveillance de la condensation

#### 2. **Pression Basse (BP)**
- **Position** : Avant le compresseur ou dans l'évaporateur
- **Plage normale** : 1.0 - 5.0 bar
- **Précision** : ±0.05 bar
- **Utilisation** : Surveillance de l'évaporation

#### 3. **Pression Intermédiaire**
- **Position** : À la sortie du détendeur
- **Plage normale** : 2.0 - 8.0 bar
- **Précision** : ±0.1 bar
- **Utilisation** : Systèmes à plusieurs étages

#### 4. **Pression Différentielle**
- **Position** : Surveillance du filtre déshydrateur
- **Plage normale** : 0.1 - 2.0 bar
- **Précision** : ±0.05 bar
- **Utilisation** : Détection d'obstruction

### Capteurs de Température (6-8 capteurs)

#### 1. **Température d'Aspiration**
- **Position** : À l'entrée du compresseur
- **Plage normale** : -15°C à +15°C
- **Précision** : ±0.5°C
- **Utilisation** : Calcul de la surchauffe

#### 2. **Température de Refoulement**
- **Position** : À la sortie du compresseur
- **Plage normale** : +30°C à +80°C
- **Précision** : ±1.0°C
- **Utilisation** : Surveillance compression

#### 3. **Température de Condensation**
- **Position** : À la sortie du condenseur
- **Plage normale** : +20°C à +50°C
- **Précision** : ±0.5°C
- **Utilisation** : Efficacité condensation

#### 4. **Température d'Évaporation**
- **Position** : À la sortie de l'évaporateur
- **Plage normale** : -25°C à +5°C
- **Précision** : ±0.5°C
- **Utilisation** : Efficacité évaporation

#### 5. **Température du Liquide**
- **Position** : Avant le détendeur
- **Plage normale** : +15°C à +45°C
- **Précision** : ±0.5°C
- **Utilisation** : Calcul sous-refroidissement

#### 6. **Température Ambiante**
- **Position** : À l'entrée/sortie du condenseur
- **Plage normale** : +10°C à +50°C
- **Précision** : ±1.0°C
- **Utilisation** : Conditions environnementales

## 📊 Conditions Typiques d'Exploitation

### Conditions Normales (selon PDF)
```
Température d'évaporation (t0) : -10°C
Température de condensation (tc) : +30°C
Surchauffe fonctionnelle : 5°C
Surchauffe ligne d'aspiration : 10°C
Température aspiration (Point 1) : +5°C
Température refoulement (Point 3) : +48°C
Sous-refroidissement : 5°C
Enthalpie entrée évaporateur (h8) : 395,69 kJ/kg
Enthalpie sortie évaporateur (h9) : 404,45 kJ/kg
```

### Conditions Anormales Détectées

#### 1. **Défaillance Capteur**
- **Symptômes** : Lectures erratiques, valeurs hors plage
- **Impact** : Perte de fiabilité des données
- **Action** : Remplacement capteur

#### 2. **Condensation Inefficace**
- **Symptômes** : Température condensation élevée, pression HP excessive
- **Impact** : Réduction COP, surconsommation énergétique
- **Action** : Nettoyage condenseur, vérification ventilation

#### 3. **Évaporation Incomplète**
- **Symptômes** : Température évaporation instable, surchauffe faible
- **Impact** : Réduction capacité frigorifique
- **Action** : Contrôle alimentation évaporateur

#### 4. **Détendeur Mal Réglé**
- **Symptômes** : Surchauffe excessive ou insuffisante
- **Impact** : Efficacité réduite, risque compresseur
- **Action** : Réglage détendeur thermostatique

#### 5. **Filtre Obstrué**
- **Symptômes** : Pression différentielle élevée
- **Impact** : Restriction circulation fluide
- **Action** : Remplacement filtre déshydrateur

## 🔄 Intégration dans le Système

### 1. Génération de Données Réalistes

```python
# Initialisation du système de capteurs
from sensor_system_real import RefrigerationSensors

sensor_system = RefrigerationSensors()

# Génération de lectures normales
normal_readings = sensor_system.generate_normal_readings("MACHINE_001")

# Génération de lectures anormales
abnormal_readings = sensor_system.generate_abnormal_readings(
    "MACHINE_001", 
    "inefficient_condensation"
)
```

### 2. Calcul des Paramètres Dérivés

```python
# Calcul automatique des paramètres thermodynamiques
derived_params = sensor_system.calculate_derived_parameters(readings)

# Paramètres calculés :
# - superheat_functional : Surchauffe fonctionnelle
# - superheat_aspiration : Surchauffe ligne aspiration
# - subcooling : Sous-refroidissement
# - cop : Coefficient de performance
# - cooling_effect : Effet frigorifique
# - compression_work : Travail de compression
# - pressure_ratio : Rapport de pression
```

### 3. Diagramme de Mollier avec Capteurs Réels

```python
# Génération du diagramme avec données réelles
from mollier_diagram_frayo import MollierDiagramGenerator

generator = MollierDiagramGenerator()
diagram_path = generator.generate_diagram_with_real_data(
    sensor_data=sensor_data,
    save_path='mollier_real_sensors.png'
)
```

### 4. Streaming Kafka avec Capteurs Réels

Le système Kafka a été modifié pour utiliser les capteurs réels :

```python
# Producteur Kafka avec capteurs réels
from kafka_producer import generate_refrigeration_data

# Génération automatique avec conditions variables
data = generate_refrigeration_data()

# Structure des données incluant :
# - sensors : Données brutes des capteurs
# - derived_parameters : Paramètres calculés
# - sensor_status : Statut de chaque capteur
# - abnormal_sensors : Liste des capteurs en anomalie
```

## 🎯 Fonctionnalités Principales

### 1. **Surveillance en Temps Réel**
- Surveillance continue des 10 capteurs principaux
- Détection automatique des anomalies
- Alertes en fonction des seuils définis

### 2. **Diagnostic Automatique**
- Identification des conditions anormales
- Classification des problèmes détectés
- Recommandations d'actions correctives

### 3. **Maintenance Prédictive**
- Analyse des tendances des capteurs
- Prédiction des défaillances
- Planification optimisée de la maintenance

### 4. **Visualisation Avancée**
- Diagrammes de Mollier en temps réel
- Adaptation visuelle aux conditions
- Indicateurs de performance

## 📈 Paramètres de Performance

### Indicateurs Clés
```
COP (Coefficient de Performance) : 2.5 - 4.0 (normal)
Effet Frigorifique : 180 - 220 kJ/kg (normal)
Rapport de Pression : 3.0 - 8.0 (normal)
Surchauffe Fonctionnelle : 3 - 7°C (normal)
Sous-refroidissement : 3 - 7°C (normal)
```

### Seuils d'Alerte
```
COP < 2.0 : Alerte performance
Surchauffe > 15°C : Alerte détendeur
Pression différentielle > 1.5 bar : Alerte filtre
Température refoulement > 70°C : Alerte compresseur
```

## 🚀 Utilisation

### Test du Système
```bash
# Exécution du test complet
python test_real_sensor_system.py

# Génération des diagrammes
python mollier_diagram_frayo.py

# Démarrage du producteur Kafka
python kafka_producer.py
```

### Intégration Dashboard
```python
# Dans app.py
from sensor_system_real import RefrigerationSensors

# Génération automatique de données avec capteurs réels
refrigeration_sensors = RefrigerationSensors()
sensor_data = refrigeration_sensors.generate_normal_readings("MACHINE_ID")
```

## 🔍 Validation et Tests

### Tests Automatisés
- ✅ Validation des plages de capteurs
- ✅ Test des conditions normales
- ✅ Test des conditions anormales
- ✅ Génération des diagrammes
- ✅ Calcul des paramètres dérivés

### Rapports de Validation
Le système génère automatiquement des rapports de validation incluant :
- Précision des capteurs
- Taux de détection des anomalies
- Performance du système global

## 📞 Support

Pour toute question technique :
- Documentation complète dans `sensor_system_real.py`
- Tests dans `test_real_sensor_system.py`
- Exemples d'utilisation dans `mollier_diagram_frayo.py`

---

*Système intégré selon spécifications PDF - Conditions normales et anormales*  
*Version : 2.0 | Date : 2025*