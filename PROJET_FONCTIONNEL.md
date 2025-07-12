# 🧊 Système de Maintenance Prédictive pour Installations Frigorifiques

## État du Projet ✅

**Le projet fonctionne maintenant correctement!**

## Comment démarrer le projet

### Méthode 1: Script PowerShell (Recommandé)
```powershell
# 1. Vérifier les prérequis
.\check_prerequisites.ps1

# 2. Démarrer tous les services
.\run_all_services.ps1

# 3. Vérifier le statut des services
.\check_services_status.ps1
```

### Méthode 2: Démarrage manuel
```powershell
# 1. Démarrer les services Docker
docker-compose up -d

# 2. Attendre 15 secondes que les services se lancent
Start-Sleep -Seconds 15

# 3. Démarrer l'application Flask
python app.py

# 4. Démarrer le producteur Kafka (nouvelle fenêtre)
python kafka_producer.py

# 5. Démarrer le service de prédiction (nouvelle fenêtre)
python streamingpredict.py
```

## URLs d'accès

- **🌐 Dashboard Principal**: http://localhost:5002
- **📊 Interface Kafka**: http://localhost:8080
- **📈 Interface MongoDB**: http://localhost:8081

## Problèmes corrigés

### 1. Services Docker non démarrés
- **Problème**: Le script `run_all_services.bat` ne démarrait pas les services Docker
- **Solution**: Ajout de `docker-compose up -d` au début du script

### 2. Port incorrect
- **Problème**: Le script affichait port 5001 mais l'app utilise le port 5002
- **Solution**: Correction du port dans tous les scripts

### 3. Commande `timeout` non reconnue
- **Problème**: La commande `timeout` n'existe pas sur tous les systèmes Windows
- **Solution**: Remplacement par `ping -n X 127.0.0.1 >nul` ou `Start-Sleep` en PowerShell

### 4. Containers conflictuels
- **Problème**: Des containers avec les mêmes noms existaient déjà
- **Solution**: Nettoyage avec `docker rm -f` avant le démarrage

## Architecture du système

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Flask App     │    │  Kafka Producer │    │  Prediction     │
│   (port 5002)   │    │  (Sensor Data)  │    │  Service        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
         ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
         │    MongoDB      │    │     Kafka       │    │   Zookeeper     │
         │   (port 27017)  │    │   (port 9092)   │    │   (port 2181)   │
         └─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Fonctionnalités

✅ **Monitoring en temps réel** des installations frigorifiques
✅ **Prédiction de pannes** avec Machine Learning
✅ **Alertes automatiques** basées sur les seuils
✅ **Diagrammes enthalpiques** pour analyse thermodynamique
✅ **Interface web intuitive** avec graphiques en temps réel
✅ **Stockage des données** dans MongoDB
✅ **Streaming de données** via Kafka

## Prérequis

- Python 3.11+
- Docker Desktop
- Packages Python (installés automatiquement via requirements.txt)

## Dépannage

Si des problèmes persistent :

1. **Vérifier Docker Desktop** : Assurez-vous qu'il est démarré
2. **Nettoyer les containers** : `docker-compose down && docker system prune`
3. **Vérifier les ports** : `netstat -an | findstr "5002 8080 8081 27017 9092"`
4. **Vérifier les logs** : `docker-compose logs`

## Support

Les scripts PowerShell incluent une gestion d'erreurs et affichent des messages d'aide en cas de problème.
