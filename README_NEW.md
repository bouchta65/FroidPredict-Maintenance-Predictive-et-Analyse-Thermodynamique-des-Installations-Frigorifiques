# FroidPredict - Maintenance Prédictive et Analyse Thermodynamique des Installations Frigorifiques

FroidPredict est une application web innovante dédiée à la maintenance prédictive des installations frigorifiques industrielles, alliant analyse thermodynamique avancée et visualisation en temps réel des données de capteurs.

## 🚀 Fonctionnalités principales

- **Surveillance en temps réel** des équipements frigorifiques (compresseurs, condenseurs, évaporateurs, etc.)
- **Collecte et stockage** des données capteurs dans une base de données via une API Python/Flask sécurisée
- **Analyse thermodynamique avancée** : calculs automatiques des points de cycle, COP, titres de vapeur, détection des phases, etc.
- **Détection d'anomalies** et prédiction de pannes grâce au Machine Learning
- **Alertes et notifications** en cas de dérive des paramètres critiques ou de risque de panne
- **Dashboard interactif** : visualisation temps réel (diagrammes de Mollier, courbes de performance, historiques…)
- **Gestion des utilisateurs** et authentification sécurisée

## 🛠️ Stack technique

- **Backend** : Python, Flask, SQLAlchemy, SQLite/PostgreSQL
- **Frontend** : HTML, CSS, JavaScript, Chart.js, Plotly.js
- **Data Science/ML** : scikit-learn, pandas, numpy
- **Déploiement** : Docker, scripts de simulation de données

## 📦 Installation et Configuration

### Prérequis
- Python 3.11 ou supérieur
- Git

### Installation rapide

1. **Cloner le dépôt**
```bash
git clone <repository-url>
cd FroidPredict-Maintenance-Predictive-et-Analyse-Thermodynamique-des-Installations-Frigorifiques
```

2. **Créer un environnement virtuel**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Configurer l'environnement**
```bash
cp .env.example .env
# Éditer .env avec vos paramètres
```

5. **Lancer l'application**
```bash
python app.py
```

### Installation automatique

Un script de setup automatique est disponible :

```bash
python setup.py
```

Ce script va :
- Créer la base de données et les tables
- Créer un utilisateur admin
- Générer des données d'exemple
- Configurer l'environnement

## 🎯 Démarrage rapide

### 1. Lancer l'application
```bash
python app.py
```

### 2. Accéder à l'interface
- **API Backend** : http://localhost:5000
- **Frontend** : http://localhost:5000/../frontend/index.html
- **Documentation API** : http://localhost:5000/api

### 3. Connexion admin
- **Nom d'utilisateur** : admin
- **Mot de passe** : admin123

### 4. Simulation de données
```bash
# Simulation temps réel
python simulate.py --mode realtime --duration 60

# Simulation historique
python simulate.py --mode historical --days 7

# Simulation de panne
python simulate.py --mode failure --failure-type gradual
```

## 📊 API Endpoints

### Équipements
- `GET /api/equipment/` - Liste des équipements
- `POST /api/equipment/` - Créer un équipement
- `GET /api/equipment/{id}` - Détails d'un équipement
- `PUT /api/equipment/{id}` - Modifier un équipement
- `DELETE /api/equipment/{id}` - Supprimer un équipement

### Capteurs
- `GET /api/sensors/` - Données des capteurs
- `POST /api/sensors/` - Ajouter des données de capteur
- `POST /api/sensors/bulk` - Ajouter plusieurs données
- `GET /api/sensors/latest/{equipment_id}` - Dernières données

### Alertes
- `GET /api/alerts/` - Liste des alertes
- `POST /api/alerts/` - Créer une alerte
- `POST /api/alerts/{id}/acknowledge` - Acquitter une alerte
- `POST /api/alerts/{id}/resolve` - Résoudre une alerte

### Dashboard
- `GET /api/dashboard/overview` - Vue d'ensemble
- `GET /api/dashboard/thermodynamic/{equipment_id}` - Analyse thermodynamique
- `GET /api/dashboard/mollier/{equipment_id}` - Diagramme de Mollier
- `GET /api/dashboard/performance/{equipment_id}` - Métriques de performance

### Authentification
- `POST /api/auth/login` - Connexion
- `POST /api/auth/register` - Inscription
- `GET /api/auth/profile` - Profil utilisateur

## 🔧 Configuration

### Variables d'environnement (.env)
```env
DATABASE_URL=sqlite:///froidpredict.db
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
FLASK_ENV=development
DEBUG=True
```

### Configuration PostgreSQL
```env
DATABASE_URL=postgresql://username:password@localhost:5432/froidpredict
```

## 🐳 Déploiement avec Docker

### Build et run
```bash
# Build l'image
docker build -t froidpredict .

# Run le conteneur
docker run -p 5000:5000 froidpredict
```

### Docker Compose
```bash
# Lancer tous les services
docker-compose up -d

# Arrêter les services
docker-compose down
```

## 🎮 Simulation de données

### Simulation temps réel
```bash
python simulate.py --mode realtime --equipment-id 1 --duration 60 --interval 30
```

### Simulation historique
```bash
python simulate.py --mode historical --equipment-id 1 --days 30
```

### Simulation de pannes
```bash
python simulate.py --mode failure --equipment-id 1 --failure-type gradual
```

## 📈 Fonctionnalités avancées

### Analyse thermodynamique
- Calcul automatique du COP (Coefficient de Performance)
- Analyse des cycles frigorifiques
- Génération de diagrammes de Mollier
- Détection des anomalies thermodynamiques

### Machine Learning
- Détection d'anomalies avec Isolation Forest
- Prédiction de pannes avec Random Forest
- Entraînement automatique des modèles
- Évaluation continue des performances

### Visualisation
- Graphiques temps réel avec Chart.js
- Diagrammes thermodynamiques avec Plotly
- Dashboard interactif responsive
- Alertes en temps réel

## 🛡️ Sécurité

- Authentification JWT
- Hachage des mots de passe
- Validation des entrées
- Protection CORS
- Gestion des rôles utilisateurs

## 📝 Structure du projet

```
FroidPredict/
├── app.py                 # Application Flask principale
├── requirements.txt       # Dépendances Python
├── setup.py              # Script d'installation
├── simulate.py           # Script de simulation
├── .env                  # Variables d'environnement
├── Dockerfile            # Configuration Docker
├── docker-compose.yml    # Services Docker
├── models/               # Modèles de données
│   ├── sensor_data.py
│   ├── equipment.py
│   ├── alert.py
│   └── user.py
├── routes/               # Routes API
│   ├── sensor_routes.py
│   ├── equipment_routes.py
│   ├── alert_routes.py
│   ├── auth_routes.py
│   └── dashboard_routes.py
├── services/             # Services métier
│   ├── anomaly_detector.py
│   ├── thermodynamic_analyzer.py
│   └── predictive_model.py
├── utils/                # Utilitaires
│   └── data_simulator.py
└── frontend/             # Interface utilisateur
    └── index.html
```

## 🎯 Objectifs

Permettre aux industriels de :
- Prédire les défaillances avant qu'elles ne surviennent
- Optimiser la performance énergétique des installations
- Réduire les coûts de maintenance et les pertes opérationnelles
- Visualiser et comprendre le comportement thermodynamique de leurs machines

## 📊 Exemples de visualisations

- Diagramme de Mollier dynamique avec traçage automatique du cycle frigorifique
- Courbes d'évolution du COP, pressions, températures, etc.
- Carte des alertes et historiques de maintenance
- Graphiques de performance en temps réel

## 🤝 Contribution

Les contributions sont les bienvenues ! Veuillez :
1. Fork le projet
2. Créer une branche pour votre fonctionnalité
3. Committer vos changements
4. Pousser vers la branche
5. Ouvrir une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.

## 🆘 Support

Pour toute question ou problème :
- Créer une issue sur GitHub
- Consulter la documentation
- Contacter l'équipe de développement

---

*FroidPredict : l'intelligence thermodynamique au service de la fiabilité industrielle !*
