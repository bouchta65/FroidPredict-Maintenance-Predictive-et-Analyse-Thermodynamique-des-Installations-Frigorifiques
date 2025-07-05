# FroidPredict - Maintenance Prédictive et Analyse Thermodynamique des Installations Frigorifiques

FroidPredict est une application web innovante dédiée à la maintenance prédictive des installations frigorifiques industrielles, alliant analyse thermodynamique avancée et visualisation en temps réel des données de capteurs avec intégration Kafka pour le streaming de données.

## 🚀 Fonctionnalités principales

- **Streaming de données en temps réel** avec Apache Kafka
- **Surveillance en temps réel** des équipements frigorifiques (compresseurs, condenseurs, évaporateurs, etc.)
- **Génération de données factices** pour tests et démonstrations
- **Collecte et stockage** des données capteurs dans PostgreSQL via une API Python/Flask sécurisée
- **Analyse thermodynamique avancée** : calculs automatiques des points de cycle, COP, titres de vapeur, détection des phases, etc.
- **Détection d'anomalies** et prédiction de pannes grâce au Machine Learning
- **Alertes et notifications** en cas de dérive des paramètres critiques ou de risque de panne
- **Dashboard React interactif** : visualisation temps réel (diagrammes de Mollier, courbes de performance, historiques…)
- **Gestion des utilisateurs** et authentification sécurisée
- **Interface Kafka UI** pour monitoring des topics et messages

## 🛠️ Stack technique

- **Backend** : Python, Flask, SQLAlchemy, PostgreSQL
- **Streaming** : Apache Kafka, Zookeeper, Kafka UI
- **Frontend** : React, Chart.js/Plotly.js
- **Data Science/ML** : scikit-learn, pandas, numpy
- **Déploiement** : Docker, Docker Compose
- **Génération de données** : Faker, scripts de simulation

## 📊 Architecture Kafka

### Topics Kafka
- **sensor_data** : Données des capteurs en temps réel
- **alerts** : Alertes et notifications
- **maintenance** : Demandes de maintenance

### Producteurs
- Générateur de données factices
- API endpoints pour envoi de données
- Système de détection d'anomalies

### Consommateurs
- Processeur de données pour stockage en base
- Analyseur thermodynamique
- Système d'alertes

## 🎯 Objectif

Permettre aux industriels de :

- Prédire les défaillances avant qu'elles ne surviennent
- Optimiser la performance énergétique des installations
- Réduire les coûts de maintenance et les pertes opérationnelles
- Visualiser et comprendre le comportement thermodynamique de leurs machines
- Analyser les données en temps réel avec Kafka streaming

## 📦 Installation et Configuration

### Prérequis
- Python 3.11+
- Docker et Docker Compose
- Git

### 1. Cloner le dépôt
```bash
git clone <repository-url>
cd FroidPredict-Maintenance-Predictive-et-Analyse-Thermodynamique-des-Installations-Frigorifiques
```

### 2. Configurer l'environnement Python
```bash
# Créer un environnement virtuel
python -m venv .venv

# Activer l'environnement virtuel
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

### 3. Configurer les variables d'environnement
Copiez le fichier `.env` et modifiez les valeurs selon votre configuration

### 4. Démarrer les services avec Docker
```bash
# Démarrer Kafka, Zookeeper, PostgreSQL et Kafka UI
docker-compose up -d

# Ou utiliser le script batch sur Windows
start_kafka.bat
```

### 5. Démarrer l'application
```bash
# Démarrer l'API Flask
python app.py

# Ou utiliser le script batch sur Windows
run.bat
```

## 🔧 Utilisation

### Démarrage rapide

1. **Démarrer les services** :
   ```bash
   # Windows
   start_kafka.bat
   
   # Linux/Mac
   docker-compose up -d
   ```

2. **Démarrer l'API** :
   ```bash
   # Windows
   run.bat
   
   # Linux/Mac
   python app.py
   ```

3. **Générer des données factices** :
   ```bash
   # Windows
   generate_data.bat
   
   # Linux/Mac
   python generate_fake_data.py --mode batch --equipment 5 --batches 10
   ```

### Interfaces web disponibles

- **API FroidPredict** : http://localhost:5000
- **Kafka UI** : http://localhost:8080
- **PostgreSQL** : localhost:5432

### Endpoints API principaux

#### Kafka Integration
- `GET /api/kafka/health` - Vérifier l'état de Kafka
- `GET /api/kafka/config` - Configuration Kafka
- `POST /api/kafka/send/sensor` - Envoyer des données de capteur
- `POST /api/kafka/send/alert` - Envoyer une alerte
- `POST /api/kafka/generate/batch` - Générer des données par lot
- `POST /api/kafka/generate/start` - Démarrer la génération continue
- `POST /api/kafka/generate/stop` - Arrêter la génération

#### Equipment Management
- `GET /api/equipment` - Liste des équipements
- `POST /api/equipment` - Créer un équipement
- `PUT /api/equipment/{id}` - Modifier un équipement
- `DELETE /api/equipment/{id}` - Supprimer un équipement

#### Sensor Data
- `GET /api/sensors` - Données des capteurs
- `POST /api/sensors` - Ajouter des données de capteur
- `POST /api/sensors/bulk` - Ajouter des données en lot
- `GET /api/sensors/statistics/{equipment_id}` - Statistiques

## 📊 Génération de données factices

### Via l'API
```bash
# Générer des données par lot
curl -X POST http://localhost:5000/api/kafka/generate/batch \
  -H "Content-Type: application/json" \
  -d '{"num_equipment": 5, "num_batches": 10}'

# Démarrer la génération continue
curl -X POST http://localhost:5000/api/kafka/generate/start \
  -H "Content-Type: application/json" \
  -d '{"num_equipment": 5, "interval_seconds": 10}'
```

### Via les scripts
```bash
# Génération par lot
python generate_fake_data.py --mode batch --equipment 5 --batches 10

# Génération continue
python generate_fake_data.py --mode continuous --equipment 5 --interval 10

# Avec un taux d'anomalie élevé
python generate_fake_data.py --mode batch --equipment 5 --batches 10 --anomaly-chance 0.3
```

## 🔧 Configuration Kafka

### Topics créés automatiquement
- `sensor_data` : Données des capteurs (3 partitions)
- `alerts` : Alertes du système (3 partitions)  
- `maintenance` : Demandes de maintenance (3 partitions)

### Monitoring avec Kafka UI
Accédez à http://localhost:8080 pour :
- Visualiser les topics et messages
- Surveiller les producteurs/consommateurs
- Analyser les performances
- Gérer les configurations

## 🚀 Déploiement

### Développement
```bash
# Démarrer tous les services
docker-compose up -d

# Démarrer l'API en mode développement
python app.py
```

### Production
```bash
# Démarrer avec Docker Compose
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## 📈 Monitoring et Logs

### Logs de l'application
Les logs sont configurés avec le module `logging` de Python et affichent :
- Données reçues et traitées
- Alertes générées
- Erreurs et exceptions
- Santé des services Kafka

### Monitoring Kafka
- **Kafka UI** : Interface web pour monitoring
- **Logs des conteneurs** : `docker-compose logs kafka`
- **Métriques JMX** : Port 9997 pour intégration avec des outils de monitoring

## 🤝 Contribution

1. Fork le projet
2. Créer une branche pour votre fonctionnalité
3. Commit vos changements
4. Push vers la branche
5. Créer une Pull Request

## 📝 Exemples d'utilisation

### Envoyer des données de capteur
```python
import requests

data = {
    "equipment_id": 1,
    "sensor_type": "temperature",
    "sensor_location": "compressor_inlet",
    "value": 25.5,
    "unit": "°C"
}

response = requests.post("http://localhost:5000/api/kafka/send/sensor", json=data)
print(response.json())
```

### Créer une alerte
```python
import requests

alert = {
    "equipment_id": 1,
    "alert_type": "thermal_anomaly",
    "severity": "high",
    "title": "Température élevée détectée",
    "description": "La température du compresseur dépasse les seuils normaux"
}

response = requests.post("http://localhost:5000/api/kafka/send/alert", json=alert)
print(response.json())
```

## 🔍 Dépannage

### Problèmes courants

1. **Kafka ne se connecte pas** :
   - Vérifiez que Docker est démarré
   - Attendez que Zookeeper soit complètement démarré avant Kafka
   - Vérifiez les ports 9092 et 2181

2. **Erreurs de base de données** :
   - Vérifiez la configuration PostgreSQL
   - Assurez-vous que les tables sont créées

3. **Erreurs Python** :
   - Vérifiez l'environnement virtuel
   - Installez les dépendances : `pip install -r requirements.txt`

### Commandes utiles

```bash
# Vérifier l'état des services
docker-compose ps

# Voir les logs
docker-compose logs -f kafka

# Redémarrer un service
docker-compose restart kafka

# Nettoyer et redémarrer
docker-compose down
docker-compose up -d
```

---

*FroidPredict : l'intelligence thermodynamique et le streaming de données au service de la fiabilité industrielle !*
