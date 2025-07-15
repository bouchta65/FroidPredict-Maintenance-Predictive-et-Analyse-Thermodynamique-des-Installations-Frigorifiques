from flask import Flask, jsonify, request
from flask_socketio import SocketIO
from flask_cors import CORS
import json
from datetime import datetime
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
import pickle
import os
import pandas as pd
import numpy as np
from pymongo import MongoClient
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'refrigeration_maintenance_dashboard_secret'

# Enable CORS for Vue.js frontend
CORS(app, origins=["http://localhost:3000"])
socketio = SocketIO(app, cors_allowed_origins=["http://localhost:3000", "http://localhost:5002"])

# Configuration MongoDB
try:
    # Try to connect to MongoDB (Docker or local)
    try:
        # First try with Docker MongoDB (with auth)
        client = MongoClient("mongodb://admin:password@localhost:27017/")
        client.admin.command('ping')  # Test connection
        db = client["refrigeration_maintenance"]
    except:
        # Fallback to local MongoDB (without auth)
        client = MongoClient("mongodb://localhost:27017/")
        client.admin.command('ping')  # Test connection
        db = client["refrigeration_maintenance"]
    
    predictions_collection = db["predictions"]
    alerts_collection = db["alerts"]
    sensors_collection = db["sensors_data"]
    logger.info("✅ Connexion MongoDB établie")
except Exception as e:
    logger.warning(f"⚠️ MongoDB non disponible: {e}")
    logger.info("📝 Utilisation du stockage en mémoire")
    # Fallback sur stockage en mémoire
    predictions_collection = None
    alerts_collection = None
    sensors_collection = None

# Stockage en mémoire comme backup
predictions = []
alerts = []
sensors_data = []

# Chargement du modèle pour installations frigorifiques
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model_logistic_refrigeration.pkl")

if os.path.exists(MODEL_PATH):
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)
    logger.info("✅ Modèle installations frigorifiques chargé avec succès")
else:
    # Créer un modèle pour installations frigorifiques
    logger.info("🔧 Création d'un nouveau modèle pour installations frigorifiques...")
    data = pd.DataFrame({
        "temp_evaporator": [-10.5, -8.0, -12.3, -15.8, -7.2, -11.0, -9.5, -13.1],
        "temp_condenser": [40.5, 38.0, 45.3, 42.8, 39.2, 44.0, 41.5, 46.1],
        "pressure_high": [12.5, 11.8, 14.2, 13.1, 12.0, 13.8, 12.7, 14.5],
        "pressure_low": [2.1, 2.3, 1.8, 1.9, 2.4, 1.7, 2.2, 1.6],
        "superheat": [8.5, 9.2, 7.8, 6.9, 9.8, 7.2, 8.9, 6.5],
        "subcooling": [5.2, 4.8, 6.1, 5.7, 4.5, 6.3, 5.0, 6.8],
        "compressor_current": [8.2, 7.9, 9.5, 8.8, 7.6, 9.2, 8.5, 9.8],
        "vibration": [0.02, 0.03, 0.025, 0.015, 0.035, 0.018, 0.028, 0.042],
        "status": [0, 0, 1, 1, 0, 1, 0, 1]
    })
    
    X = data[["temp_evaporator", "temp_condenser", "pressure_high", "pressure_low", 
              "superheat", "subcooling", "compressor_current", "vibration"]]
    y = data["status"]
    
    model = LogisticRegression(random_state=42, max_iter=1000)
    model.fit(X, y)
    
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)
    logger.info("✅ Nouveau modèle installations frigorifiques créé et sauvegardé")

def get_predictions_from_db(limit=50):
    """Récupère les prédictions depuis MongoDB ou mémoire"""
    if predictions_collection is not None:
        try:
            return list(predictions_collection.find().sort("timestamp", -1).limit(limit))
        except:
            pass
    return predictions[-limit:] if predictions else []

def get_alerts_from_db(limit=50):
    """Récupère les alertes depuis MongoDB ou mémoire"""
    if alerts_collection is not None:
        try:
            return list(alerts_collection.find().sort("timestamp", -1).limit(limit))
        except:
            pass
    return alerts[-limit:] if alerts else []

# API endpoints for Vue.js frontend
@app.route('/api/dashboard_data')
def get_dashboard_data():
    """Get dashboard data for Vue.js frontend"""
    recent_predictions = get_predictions_from_db(10)
    recent_alerts = get_alerts_from_db(10)
    
    # Clean MongoDB ObjectId for JSON serialization
    for prediction in recent_predictions:
        if '_id' in prediction:
            prediction['_id'] = str(prediction['_id'])
    
    for alert in recent_alerts:
        if '_id' in alert:
            alert['_id'] = str(alert['_id'])
    
    # Get real database counts, not local array lengths
    real_pred_count = predictions_collection.count_documents({}) if predictions_collection is not None else 0
    # Use same filter as alerts count API for consistency  
    real_alert_count = alerts_collection.count_documents({'status': 'active'}) if alerts_collection is not None else len([a for a in alerts if a.get('status', 'active') == 'active'])
    
    return jsonify({
        'status': 'success',
        'predictions': recent_predictions,
        'alerts': recent_alerts,
        'stats': {
            'total_predictions': real_pred_count,
            'total_alerts': real_alert_count,
            'mongodb_connected': predictions_collection is not None
        }
    })

@app.route('/api/predictions')
def api_get_predictions():
    """Get all predictions for Vue.js frontend"""
    all_predictions = get_predictions_from_db(100)
    
    # Clean MongoDB ObjectId for JSON serialization
    for prediction in all_predictions:
        if '_id' in prediction:
            prediction['_id'] = str(prediction['_id'])
    
    return jsonify({
        'status': 'success',
        'predictions': all_predictions
    })

@app.route('/api/alerts')
def api_get_alerts():
    """Get all alerts for Vue.js frontend"""
    all_alerts = get_alerts_from_db(100)
    
    # Clean MongoDB ObjectId for JSON serialization
    for alert in all_alerts:
        if '_id' in alert:
            alert['_id'] = str(alert['_id'])
    
    return jsonify({
        'status': 'success',
        'alerts': all_alerts
    })

@app.route('/api/refrigeration_prediction', methods=['POST'])
def receive_refrigeration_prediction():
    """Reçoit les données de prédiction pour installations frigorifiques"""
    try:
        data = request.json
        
        # Prédiction avec le modèle installations frigorifiques
        features = np.array([[
            data['temp_evaporator'],
            data['temp_condenser'],
            data['pressure_high'],
            data['pressure_low'],
            data['superheat'],
            data['subcooling'],
            data['compressor_current'],
            data['vibration']
        ]])
        
        prediction = int(model.predict(features)[0])
        probability = float(model.predict_proba(features)[0][1])
        
        # Ajout des résultats de prédiction
        data['prediction'] = prediction
        data['probability'] = probability
        data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Stockage dans MongoDB
        if predictions_collection is not None:
            try:
                predictions_collection.insert_one(data.copy())
            except Exception as e:
                logger.error(f"Erreur insertion MongoDB: {e}")
        
        # Stockage en mémoire
        predictions.append(data)
        if len(predictions) > 200:
            predictions.pop(0)
        
        # Stockage des données capteurs
        if sensors_collection is not None:
            try:
                sensors_collection.insert_one(data.copy())
                logger.info(f"✅ Données capteur sauvegardées pour machine {data['machine_id']}")
            except Exception as e:
                logger.error(f"❌ Erreur sauvegarde capteurs: {e}")
        
        # Mise à jour temps réel dashboard ET diagrammes
        socketio.emit('new_prediction', data)
        socketio.emit('new_sensor_data', data)  # Événement spécifique pour les diagrammes
        
        # Emit prediction count update
        total_predictions = len(predictions) if predictions_collection is None else predictions_collection.count_documents({})
        socketio.emit('prediction_count_updated', {'count': total_predictions, 'timestamp': data['timestamp']})
        
        # Vérification des conditions d'alerte spécifiques aux installations frigorifiques
        alerts_to_add = []
        
        # Alerte 1: Prédiction de défaillance
        if prediction == 1:
            alerts_to_add.append({
                'timestamp': data['timestamp'],
                'machine_id': data['machine_id'],
                'message': f"⚠️ Maintenance préventive requise - Installation frigorifique {data['machine_id']} - Probabilité: {probability:.1%}",
                'severity': 'high' if probability > 0.75 else 'medium',
                'type': 'prediction',
                'data': data
            })
        
        # Alerte 2: Températures critiques
        if data['temp_evaporator'] > -5:
            alerts_to_add.append({
                'timestamp': data['timestamp'],
                'machine_id': data['machine_id'],
                'message': f"🌡️ Température évaporateur élevée: {data['temp_evaporator']}°C - Risque de perte de capacité frigorifique",
                'severity': 'high',
                'type': 'temperature',
                'data': data
            })
        
        if data['temp_condenser'] > 50:
            alerts_to_add.append({
                'timestamp': data['timestamp'],
                'machine_id': data['machine_id'],
                'message': f"🌡️ Température condenseur critique: {data['temp_condenser']}°C - Risque de surchauffe",
                'severity': 'high',
                'type': 'temperature',
                'data': data
            })
        
        # Alerte 3: Pressions anormales
        if data['pressure_high'] > 16:
            alerts_to_add.append({
                'timestamp': data['timestamp'],
                'machine_id': data['machine_id'],
                'message': f"📈 Pression haute critique: {data['pressure_high']} bar - Risque de déclenchement des sécurités",
                'severity': 'high',
                'type': 'pressure',
                'data': data
            })
        
        if data['pressure_low'] < 1.5:
            alerts_to_add.append({
                'timestamp': data['timestamp'],
                'machine_id': data['machine_id'],
                'message': f"📉 Pression basse critique: {data['pressure_low']} bar - Risque de perte de fluide frigorigène",
                'severity': 'high',
                'type': 'pressure',
                'data': data
            })
        
        # Alerte 4: Surchauffe et sous-refroidissement
        if data['superheat'] < 3:
            alerts_to_add.append({
                'timestamp': data['timestamp'],
                'machine_id': data['machine_id'],
                'message': f"❄️ Surchauffe faible: {data['superheat']}°C - Risque de retour liquide compresseur",
                'severity': 'high',
                'type': 'superheat',
                'data': data
            })
        
        if data['superheat'] > 15:
            alerts_to_add.append({
                'timestamp': data['timestamp'],
                'machine_id': data['machine_id'],
                'message': f"🔥 Surchauffe excessive: {data['superheat']}°C - Perte d'efficacité énergétique",
                'severity': 'medium',
                'type': 'superheat',
                'data': data
            })
        
        # Alerte 5: Courant compresseur
        if data['compressor_current'] > 12:
            alerts_to_add.append({
                'timestamp': data['timestamp'],
                'machine_id': data['machine_id'],
                'message': f"⚡ Courant compresseur élevé: {data['compressor_current']}A - Surcharge détectée",
                'severity': 'high',
                'type': 'current',
                'data': data
            })
        
        # Alerte 6: Vibrations
        if data['vibration'] > 0.05:
            alerts_to_add.append({
                'timestamp': data['timestamp'],
                'machine_id': data['machine_id'],
                'message': f"📳 Vibrations excessives: {data['vibration']}g - Vérifier fixations et paliers",
                'severity': 'medium',
                'type': 'vibration',
                'data': data
            })
        
        # Alerte 7: Ratio de pression
        pressure_ratio = data['pressure_high'] / data['pressure_low']
        if pressure_ratio > 8:
            alerts_to_add.append({
                'timestamp': data['timestamp'],
                'machine_id': data['machine_id'],
                'message': f"⚖️ Ratio de pression élevé: {pressure_ratio:.1f} - Efficacité réduite",
                'severity': 'medium',
                'type': 'pressure_ratio',
                'data': data
            })
        
        # Traitement des alertes
        for alert in alerts_to_add:
            # Stockage MongoDB
            if alerts_collection is not None:
                try:
                    alerts_collection.insert_one(alert.copy())
                except Exception as e:
                    logger.error(f"Erreur insertion alerte MongoDB: {e}")
            
            # Stockage mémoire
            alerts.append(alert)
            if len(alerts) > 100:
                alerts.pop(0)
            
            # Émission temps réel
            socketio.emit('new_alert', alert)
        
        # Emit alert count update after processing all alerts
        if alerts_to_add:
            if alerts_collection is not None:
                try:
                    total_alerts = alerts_collection.count_documents({'status': 'active'})
                except:
                    total_alerts = len([a for a in alerts if a.get('status', 'active') == 'active'])
            else:
                total_alerts = len([a for a in alerts if a.get('status', 'active') == 'active'])
            
            socketio.emit('alert_count_updated', {'count': total_alerts, 'timestamp': data['timestamp']})
        
        return jsonify({
            "status": "success", 
            "prediction": prediction,
            "probability": probability,
            "alerts_generated": len(alerts_to_add)
        })
        
    except Exception as e:
        logger.error(f"Erreur traitement prédiction: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/system_status')
def system_status():
    """Retourne le statut du système"""
    return jsonify({
        "status": "running",
        "model_loaded": MODEL_PATH,
        "mongodb_connected": predictions_collection is not None,
        "predictions_count": len(predictions),
        "alerts_count": len(alerts)
    })

@app.route('/api/predictions/count')
def api_predictions_count():
    """Get predictions count for real-time updates"""
    try:
        if predictions_collection is not None:
            # Count from MongoDB
            count = predictions_collection.count_documents({})
        else:
            # Count from in-memory storage
            count = len(predictions)
        
        return jsonify({
            'status': 'success',
            'count': count,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error getting predictions count: {e}")
        return jsonify({
            'status': 'error',
            'count': 0,
            'message': str(e)
        })

@app.route('/api/alerts/count')
def api_alerts_count():
    """Get alerts count for real-time updates"""
    try:
        if alerts_collection is not None:
            # Count from MongoDB - only active alerts
            count = alerts_collection.count_documents({'status': 'active'})
        else:
            # Count from in-memory storage - only active alerts
            count = len([alert for alert in alerts if alert.get('status', 'active') == 'active'])
        
        return jsonify({
            'status': 'success',
            'count': count,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error getting alerts count: {e}")
        return jsonify({
            'status': 'error',
            'count': 0,
            'message': str(e)
        })

@app.route('/api/system/status')
def api_system_status():
    """Get detailed system status for real-time monitoring"""
    try:
        # Check MongoDB connection
        db_status = 'connected'
        try:
            if client:
                client.admin.command('ping')
        except:
            db_status = 'disconnected'
        
        # Calculate uptime (simplified - you might want to track actual uptime)
        uptime = 98.5 if db_status == 'connected' else 85.0
        
        # Get system metrics
        system_status_value = 'online' if db_status == 'connected' else 'degraded'
        
        return jsonify({
            'status': 'success',
            'system_status': system_status_value,
            'db_status': db_status,
            'uptime': uptime,
            'timestamp': datetime.now().isoformat(),
            'services': {
                'mongodb': db_status == 'connected',
                'api': True,
                'predictions': MODEL_PATH is not None,
                'alerts': True
            }
        })
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        return jsonify({
            'status': 'error',
            'system_status': 'offline',
            'db_status': 'disconnected',
            'uptime': 0,
            'message': str(e)
        })

@app.route('/api/enthalpy_diagram_data', methods=['GET'])
def get_enthalpy_diagram_data():
    """API pour obtenir les données du diagramme enthalpique"""
    try:
        # Récupération des données récentes des capteurs depuis MongoDB
        recent_data = []
        
        # Essayer d'abord les données de capteurs
        if sensors_collection is not None:
            try:
                sensor_data = list(sensors_collection.find().sort("timestamp", -1).limit(5))
                if sensor_data:
                    recent_data = sensor_data
                    logger.info(f"✅ {len(recent_data)} données capteurs récupérées pour le diagramme")
            except Exception as e:
                logger.warning(f"⚠️ Erreur récupération données capteurs: {e}")
        
        # Fallback sur les données de prédictions
        if not recent_data:
            recent_data = get_predictions_from_db(5)
            if recent_data:
                logger.info(f"✅ {len(recent_data)} données prédictions récupérées pour le diagramme")
        
        # Fallback sur données en mémoire
        if not recent_data and predictions:
            recent_data = predictions[-5:]
            logger.info(f"✅ {len(recent_data)} données mémoire récupérées pour le diagramme")
        
        if not recent_data:
            # Données par défaut si aucune donnée disponible
            recent_data = [{
                'temp_evaporator': -10.0,
                'temp_condenser': 40.0,
                'pressure_high': 12.5,
                'pressure_low': 2.1,
                'superheat': 8.0,
                'subcooling': 5.0,
                'machine_id': 'DEMO',
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }]
            logger.info("⚠️ Utilisation de données par défaut pour le diagramme")
        
        diagram_data = []
        for data in recent_data:
            # Calculs thermodynamiques pour le diagramme enthalpique (R404A)
            t_evap = data.get('temp_evaporator', -10)
            t_cond = data.get('temp_condenser', 40)
            superheat = data.get('superheat', 8)
            subcooling = data.get('subcooling', 5)
            
            # Points du cycle frigorifique
            # Point 1: Sortie évaporateur (vapeur surchauffée)
            t1 = t_evap + superheat
            p1 = data.get('pressure_low', 2.1)
            h1 = calculate_enthalpy_vapor(t1, p1)
            
            # Point 2: Sortie compresseur (vapeur haute pression)
            p2 = data.get('pressure_high', 12.5)
            # Compression isentropique approximée
            t2 = t1 + (p2/p1 - 1) * 30  # Approximation
            h2 = h1 + (t2 - t1) * 2.1  # Approximation cp vapeur
            
            # Point 3: Sortie condenseur (liquide sous-refroidi)
            t3 = t_cond - subcooling
            p3 = p2
            h3 = calculate_enthalpy_liquid(t3, p3)
            
            # Point 4: Sortie détendeur (mélange liquide-vapeur)
            t4 = t_evap
            p4 = p1
            h4 = h3  # Détente isenthalpique
            
            diagram_data.append({
                'machine_id': data.get('machine_id', 'Unknown'),
                'timestamp': data.get('timestamp', datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                'cycle_points': {
                    'point1': {'T': t1, 'P': p1, 'h': h1, 'description': 'Sortie évaporateur'},
                    'point2': {'T': t2, 'P': p2, 'h': h2, 'description': 'Sortie compresseur'},
                    'point3': {'T': t3, 'P': p3, 'h': h3, 'description': 'Sortie condenseur'},
                    'point4': {'T': t4, 'P': p4, 'h': h4, 'description': 'Sortie détendeur'}
                },
                'performance': {
                    'cop': calculate_cop(h1, h2, h4),
                    'cooling_capacity': h1 - h4,
                    'compression_work': h2 - h1,
                    'condensation_heat': h2 - h3
                }
            })
        
        return jsonify({
            'status': 'success',
            'diagram_data': diagram_data
        })
        
    except Exception as e:
        logger.error(f"Erreur génération diagramme enthalpique: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

def calculate_enthalpy_vapor(temperature, pressure):
    """Calcul approximatif de l'enthalpie pour la vapeur R404A"""
    # Formule approximative basée sur les propriétés du R404A
    return 250 + temperature * 1.2 + pressure * 2.5

def calculate_enthalpy_liquid(temperature, pressure):
    """Calcul approximatif de l'enthalpie pour le liquide R404A"""
    # Formule approximative basée sur les propriétés du R404A
    return 50 + temperature * 2.8 + pressure * 0.5

import threading
import time
import random

def calculate_cop(h1, h2, h4):
    """Calcul du coefficient de performance"""
    cooling_effect = h1 - h4
    work_input = h2 - h1
    return cooling_effect / work_input if work_input > 0 else 0

@app.route('/api/temperature_analysis', methods=['POST'])
def analyze_temperatures():
    """Analyse avancée des températures de condensation et évaporation"""
    try:
        data = request.json
        
        # Détermination de la température d'évaporation optimale
        ambient_temp = data.get('ambient_temperature', 25)
        cooling_load = data.get('cooling_load', 100)  # en %
        
        # Température d'évaporation optimale (fonction de la charge)
        t_evap_optimal = -15 + (cooling_load / 100) * 10
        
        # Température de condensation optimale (fonction température ambiante)
        t_cond_optimal = ambient_temp + 15  # Delta T condenseur
        
        # Analyse des températures actuelles
        current_t_evap = data.get('temp_evaporator', -10)
        current_t_cond = data.get('temp_condenser', 40)
        
        analysis = {
            'current_conditions': {
                'evaporator_temp': current_t_evap,
                'condenser_temp': current_t_cond,
                'ambient_temp': ambient_temp,
                'cooling_load': cooling_load
            },
            'optimal_conditions': {
                'evaporator_temp': t_evap_optimal,
                'condenser_temp': t_cond_optimal
            },
            'deviations': {
                'evaporator_deviation': current_t_evap - t_evap_optimal,
                'condenser_deviation': current_t_cond - t_cond_optimal
            },
            'recommendations': []
        }
        
        # Génération des recommandations
        if abs(analysis['deviations']['evaporator_deviation']) > 3:
            if analysis['deviations']['evaporator_deviation'] > 0:
                analysis['recommendations'].append({
                    'type': 'evaporator',
                    'message': 'Température évaporateur trop élevée - Vérifier la charge en fluide frigorigène',
                    'priority': 'high'
                })
            else:
                analysis['recommendations'].append({
                    'type': 'evaporator',
                    'message': 'Température évaporateur trop basse - Risque de givre, ajuster le dégivrage',
                    'priority': 'medium'
                })
        
        if abs(analysis['deviations']['condenser_deviation']) > 5:
            if analysis['deviations']['condenser_deviation'] > 0:
                analysis['recommendations'].append({
                    'type': 'condenser',
                    'message': 'Température condenseur trop élevée - Nettoyer les échangeurs, vérifier ventilation',
                    'priority': 'high'
                })
            else:
                analysis['recommendations'].append({
                    'type': 'condenser',
                    'message': 'Température condenseur optimisée - Conditions favorables',
                    'priority': 'low'
                })
        
        return jsonify({
            'status': 'success',
            'analysis': analysis
        })
        
    except Exception as e:
        logger.error(f"Erreur analyse températures: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Automatic prediction generation system
def generate_realistic_sensor_data(machine_id="AUTO_GEN"):
    """Generate realistic sensor data for automatic predictions"""
    base_time = datetime.now()
    
    # Simulate normal operating conditions with some random variation
    data = {
        'machine_id': f"{machine_id}_{random.randint(1,5)}",
        'timestamp': base_time.strftime("%Y-%m-%d %H:%M:%S"),
        'temp_evaporator': round(random.uniform(-15, -5), 1),
        'temp_condenser': round(random.uniform(35, 50), 1),
        'pressure_high': round(random.uniform(10, 16), 1),
        'pressure_low': round(random.uniform(1.5, 3.0), 1),
        'superheat': round(random.uniform(5, 12), 1),
        'subcooling': round(random.uniform(3, 8), 1),
        'compressor_current': round(random.uniform(6, 12), 1),
        'vibration': round(random.uniform(0.01, 0.06), 3),
        'auto_generated': True
    }
    
    # Occasionally generate conditions that trigger alerts (20% chance)
    if random.random() < 0.2:
        alert_type = random.choice(['high_temp', 'high_pressure', 'high_current', 'vibration'])
        
        if alert_type == 'high_temp':
            data['temp_condenser'] = round(random.uniform(52, 60), 1)
        elif alert_type == 'high_pressure':
            data['pressure_high'] = round(random.uniform(17, 20), 1)
        elif alert_type == 'high_current':
            data['compressor_current'] = round(random.uniform(13, 16), 1)
        elif alert_type == 'vibration':
            data['vibration'] = round(random.uniform(0.07, 0.12), 3)
    
    return data

def automatic_prediction_generator():
    """Background thread to generate predictions automatically"""
    logger.info("🤖 Starting automatic prediction generator...")
    
    while True:
        try:
            # Generate new sensor data
            sensor_data = generate_realistic_sensor_data()
            
            # Make prediction using the model
            features = [
                sensor_data['temp_evaporator'],
                sensor_data['temp_condenser'], 
                sensor_data['pressure_high'],
                sensor_data['pressure_low'],
                sensor_data['superheat'],
                sensor_data['subcooling'],
                sensor_data['compressor_current'],
                sensor_data['vibration']
            ]
            
            prediction = model.predict([features])[0]
            probability = model.predict_proba([features])[0][1] if hasattr(model, 'predict_proba') else 0.5
            
            # Add prediction info to data
            sensor_data['prediction'] = int(prediction)
            sensor_data['probability'] = float(probability)
            sensor_data['prediction_confidence'] = 'high' if probability > 0.7 or probability < 0.3 else 'medium'
            
            # Store in MongoDB
            if predictions_collection is not None:
                try:
                    predictions_collection.insert_one(sensor_data.copy())
                except Exception as e:
                    logger.warning(f"MongoDB storage failed: {e}")
            
            # Store in memory
            predictions.append(sensor_data)
            if len(predictions) > 200:
                predictions.pop(0)
            
            # Store sensor data
            if sensors_collection is not None:
                try:
                    sensors_collection.insert_one(sensor_data.copy())
                except Exception as e:
                    logger.warning(f"Sensor data storage failed: {e}")
            
            # Emit real-time updates
            socketio.emit('new_prediction', sensor_data)
            socketio.emit('new_sensor_data', sensor_data)
            
            # Emit prediction count update
            total_predictions = len(predictions) if predictions_collection is None else predictions_collection.count_documents({})
            socketio.emit('prediction_count_updated', {'count': total_predictions, 'timestamp': sensor_data['timestamp']})
            
            # Generate alerts if needed
            alerts_generated = []
            
            # Check for alert conditions
            if prediction == 1:
                alert = {
                    'timestamp': sensor_data['timestamp'],
                    'machine_id': sensor_data['machine_id'],
                    'message': f"🤖 AUTO: Maintenance préventive requise - {sensor_data['machine_id']} - Probabilité: {probability:.1%}",
                    'severity': 'high' if probability > 0.75 else 'medium',
                    'type': 'auto_prediction',
                    'status': 'active',
                    'data': sensor_data
                }
                alerts_generated.append(alert)
            
            # Temperature alerts
            if sensor_data['temp_condenser'] > 50:
                alert = {
                    'timestamp': sensor_data['timestamp'],
                    'machine_id': sensor_data['machine_id'],
                    'message': f"🌡️ AUTO: Température condenseur critique: {sensor_data['temp_condenser']}°C",
                    'severity': 'high',
                    'type': 'auto_temperature',
                    'status': 'active',
                    'data': sensor_data
                }
                alerts_generated.append(alert)
            
            # Pressure alerts
            if sensor_data['pressure_high'] > 16:
                alert = {
                    'timestamp': sensor_data['timestamp'],
                    'machine_id': sensor_data['machine_id'],
                    'message': f"📈 AUTO: Pression haute critique: {sensor_data['pressure_high']} bar",
                    'severity': 'high',
                    'type': 'auto_pressure',
                    'status': 'active',
                    'data': sensor_data
                }
                alerts_generated.append(alert)
            
            # Current alerts
            if sensor_data['compressor_current'] > 12:
                alert = {
                    'timestamp': sensor_data['timestamp'],
                    'machine_id': sensor_data['machine_id'],
                    'message': f"⚡ AUTO: Courant compresseur élevé: {sensor_data['compressor_current']}A",
                    'severity': 'high',
                    'type': 'auto_current',
                    'status': 'active',
                    'data': sensor_data
                }
                alerts_generated.append(alert)
            
            # Vibration alerts
            if sensor_data['vibration'] > 0.05:
                alert = {
                    'timestamp': sensor_data['timestamp'],
                    'machine_id': sensor_data['machine_id'],
                    'message': f"📳 AUTO: Vibrations excessives: {sensor_data['vibration']}g",
                    'severity': 'medium',
                    'type': 'auto_vibration',
                    'status': 'active',
                    'data': sensor_data
                }
                alerts_generated.append(alert)
            
            # Store and emit alerts
            for alert in alerts_generated:
                if alerts_collection is not None:
                    try:
                        alerts_collection.insert_one(alert.copy())
                    except Exception as e:
                        logger.warning(f"Alert storage failed: {e}")
                
                alerts.append(alert)
                if len(alerts) > 100:
                    alerts.pop(0)
                
                socketio.emit('new_alert', alert)
            
            # Emit alert count update after all alerts are processed
            if alerts_generated:
                if alerts_collection is not None:
                    try:
                        total_alerts = alerts_collection.count_documents({'status': 'active'})
                    except:
                        total_alerts = len([a for a in alerts if a.get('status', 'active') == 'active'])
                else:
                    total_alerts = len([a for a in alerts if a.get('status', 'active') == 'active'])
                
                socketio.emit('alert_count_updated', {'count': total_alerts, 'timestamp': sensor_data['timestamp']})
            
            if alerts_generated:
                logger.info(f"🚨 Generated {len(alerts_generated)} automatic alerts for {sensor_data['machine_id']}")
            
            logger.info(f"🤖 Auto-generated prediction for {sensor_data['machine_id']}: {'⚠️ Maintenance' if prediction else '✅ Normal'} (confidence: {probability:.1%})")
            
            # Wait 15-45 seconds before next generation (random interval)
            wait_time = random.randint(15, 45)
            time.sleep(wait_time)
            
        except Exception as e:
            logger.error(f"Error in automatic prediction generator: {e}")
            time.sleep(30)  # Wait 30 seconds on error

# API endpoint to control automatic generation
@app.route('/api/auto-prediction/toggle', methods=['POST'])
def toggle_auto_prediction():
    """Toggle automatic prediction generation"""
    global auto_prediction_enabled
    
    try:
        data = request.get_json()
        auto_prediction_enabled = data.get('enabled', True)
        
        return jsonify({
            'status': 'success',
            'auto_prediction_enabled': auto_prediction_enabled,
            'message': f"Automatic prediction {'enabled' if auto_prediction_enabled else 'disabled'}"
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/auto-prediction/status')
def auto_prediction_status():
    """Get automatic prediction status"""
    global auto_prediction_enabled
    
    return jsonify({
        'status': 'success',
        'auto_prediction_enabled': auto_prediction_enabled,
        'total_predictions': len(predictions),
        'total_alerts': len([alert for alert in alerts if alert.get('status', 'active') == 'active'])
    })

if __name__ == '__main__':
    # Création des dossiers nécessaires
    os.makedirs(os.path.join(BASE_DIR, "templates"), exist_ok=True)
    os.makedirs(os.path.join(BASE_DIR, "static"), exist_ok=True)
    
    # Global variable for auto prediction control
    auto_prediction_enabled = True
    
    # Start automatic prediction generator in background thread
    prediction_thread = threading.Thread(target=automatic_prediction_generator, daemon=True)
    prediction_thread.start()
    
    logger.info("🧊 Démarrage dashboard maintenance prédictive installations frigorifiques")
    logger.info("🤖 Système de génération automatique de prédictions activé")
    logger.info("🌐 http://localhost:5002")
    
    socketio.run(app, debug=True, host='0.0.0.0', port=5002)
    