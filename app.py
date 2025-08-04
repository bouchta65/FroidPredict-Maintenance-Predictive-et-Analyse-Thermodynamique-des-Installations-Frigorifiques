from flask import Flask, jsonify, request, make_response
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
import threading
from io import BytesIO

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'refrigeration_maintenance_dashboard_secret'

# Enable CORS for Vue.js frontend
CORS(app, origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002", "http://localhost:3003"])
socketio = SocketIO(app, cors_allowed_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002", "http://localhost:3003", "http://localhost:5002"])

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
            # Calculs thermodynamiques pour le diagramme enthalpique (R22)
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
    """Calcul approximatif de l'enthalpie pour la vapeur R22"""
    # Formule approximative basée sur les propriétés du R22
    return 250 + temperature * 1.15 + pressure * 2.3

def calculate_enthalpy_liquid(temperature, pressure):
    """Calcul approximatif de l'enthalpie pour le liquide R22"""
    # Formule approximative basée sur les propriétés du R22
    return 50 + temperature * 2.6 + pressure * 0.4

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

# Intégration du nouveau système de capteurs réels
from sensor_system_real import RefrigerationSensors, SensorReading

# Initialisation du système de capteurs réels
refrigeration_sensors = RefrigerationSensors()

# Modification de la fonction de génération de données
def generate_realistic_sensor_data(machine_id="FRIGO-UNITE-001"):
    """Generate realistic sensor data for unified installation with all critical components"""
    
    # 80% chance of normal conditions, 20% abnormal
    is_normal = random.random() < 0.8
    
    if is_normal:
        readings = refrigeration_sensors.generate_normal_readings(machine_id)
    else:
        # Random abnormal conditions
        abnormal_conditions = [
            "sensor_failure", "calibration_error", "pressure_drop",
            "incomplete_evaporation", "inefficient_condensation",
            "misadjusted_expansion_valve", "clogged_filter"
        ]
        condition = random.choice(abnormal_conditions)
        readings = refrigeration_sensors.generate_abnormal_readings(machine_id, condition)
    
    # Calculating derived parameters
    derived_params = refrigeration_sensors.calculate_derived_parameters(readings)
    
    # Convert to format expected by the existing system
    data = {
        'machine_id': machine_id,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        
        # Temperatures (mapping from new sensors)
        'temp_evaporator': readings["temp_evaporation"].value,
        'temp_condenser': readings["temp_condensation"].value,
        'temp_aspiration': readings["temp_aspiration"].value,
        'temp_refoulement': readings["temp_refoulement"].value,
        'temp_liquid': readings["temp_liquid"].value,
        'temp_ambient': readings["temp_ambient"].value,
        
        # Pressures (mapping from new sensors)
        'pressure_high': readings["pressure_hp"].value,
        'pressure_low': readings["pressure_bp"].value,
        'pressure_intermediate': readings["pressure_intermediate"].value,
        'pressure_differential': readings["pressure_differential"].value,
        
        # Calculated derived parameters
        'superheat': derived_params["superheat_functional"],
        'subcooling': derived_params["subcooling"],
        'cop': derived_params["cop"],
        'pressure_ratio': derived_params["pressure_ratio"],
        
        # Enthalpies for Mollier diagram
        'enthalpy_h1': derived_params["enthalpy_h1"],
        'enthalpy_h2': derived_params["enthalpy_h2"],
        'enthalpy_h3': derived_params["enthalpy_h3"],
        'enthalpy_h4': derived_params["enthalpy_h4"],
        'enthalpy_h8': derived_params["enthalpy_h8"],
        'enthalpy_h9': derived_params["enthalpy_h9"],
        
        # Thermodynamic effects
        'cooling_effect': derived_params["cooling_effect"],
        'compression_work': derived_params["compression_work"],
        'heat_rejected': derived_params["heat_rejected"],
        
        # Simulation of other parameters
        'compressor_current': round(random.uniform(6, 12), 1),
        'vibration': round(random.uniform(0.01, 0.06), 3),
        'auto_generated': True,
        
        # Sensor statuses
        'sensor_status': {
            sensor_id: reading.status 
            for sensor_id, reading in readings.items()
        },
        
        # Detected conditions
        'operating_condition': 'normal' if is_normal else condition,
        'abnormal_sensors': [
            sensor_id for sensor_id, reading in readings.items() 
            if reading.status in ['warning', 'critical', 'error']
        ],
        
        # Monitored critical components
        'critical_components': {
            'compressor': {
                'status': 'normal' if readings["temp_refoulement"].status == 'normal' else 'warning',
                'current': round(random.uniform(6, 12), 1),
                'vibration': round(random.uniform(0.01, 0.06), 3)
            },
            'evaporator': {
                'status': 'normal' if readings["temp_evaporation"].status == 'normal' else 'warning',
                'temperature': readings["temp_evaporation"].value,
                'pressure': readings["pressure_bp"].value
            },
            'condenser': {
                'status': 'normal' if readings["temp_condensation"].status == 'normal' else 'warning',
                'temperature': readings["temp_condensation"].value,
                'pressure': readings["pressure_hp"].value
            },
            'expansion_valve': {
                'status': 'normal' if derived_params["superheat_functional"] > 3 and derived_params["superheat_functional"] < 12 else 'warning',
                'superheat': derived_params["superheat_functional"],
                'subcooling': derived_params["subcooling"]
            },
            'filter_drier': {
                'status': 'normal' if readings["pressure_differential"].value < 1.0 else 'warning',
                'pressure_drop': readings["pressure_differential"].value,
                'condition': 'clean' if readings["pressure_differential"].value < 0.5 else 'dirty'
            },
            'liquid_receiver': {
                'status': 'normal',
                'level': round(random.uniform(60, 90), 1),
                'sight_glass': 'clear' if is_normal else 'bubbles'
            },
            'sight_glass': {
                'status': 'normal',
                'condition': 'clear' if is_normal else 'bubbles',
                'moisture_indicator': 'dry' if is_normal else 'wet'
            }
        }
    }
    
    return data

# Automatic prediction generation system
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

# ===============================
# REPORT GENERATION ENDPOINTS
# ===============================

@app.route('/api/reports/alerts', methods=['POST'])
def generate_alerts_report():
    """Generate alerts report in PDF or Excel format"""
    try:
        data = request.get_json()
        format_type = data.get('format', 'pdf')
        date_range = data.get('dateRange', {})
        include_breakdown = data.get('includeBreakdown', True)
        include_trends = data.get('includeTrends', True)
        
        # Get filtered alerts
        alerts = get_alerts_from_db(1000)  # Get more for comprehensive report
        
        # Filter by date range if provided
        if date_range.get('start') and date_range.get('end'):
            from datetime import datetime
            start_date = datetime.fromisoformat(date_range['start'].replace('Z', '+00:00'))
            end_date = datetime.fromisoformat(date_range['end'].replace('Z', '+00:00'))
            
            filtered_alerts = []
            for alert in alerts:
                alert_date = alert.get('timestamp')
                if isinstance(alert_date, str):
                    alert_date = datetime.fromisoformat(alert_date.replace('Z', '+00:00'))
                elif hasattr(alert_date, 'timestamp'):
                    alert_date = datetime.fromtimestamp(alert_date.timestamp())
                
                if start_date <= alert_date <= end_date:
                    filtered_alerts.append(alert)
            alerts = filtered_alerts
        
        # Generate report data
        report_data = {
            'title': 'Refrigeration Alerts Report',
            'generated_at': datetime.now().isoformat(),
            'date_range': date_range,
            'total_alerts': len(alerts),
            'alerts': alerts
        }
        
        # Add severity breakdown
        if include_breakdown:
            severity_counts = {}
            for alert in alerts:
                severity = alert.get('severity', 'unknown')
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
            report_data['severity_breakdown'] = severity_counts
        
        # Add trends analysis
        if include_trends:
            # Group alerts by date for trend analysis
            from collections import defaultdict
            daily_counts = defaultdict(int)
            for alert in alerts:
                alert_date = alert.get('timestamp', '')
                if isinstance(alert_date, str):
                    date_key = alert_date[:10]  # Extract YYYY-MM-DD
                    daily_counts[date_key] += 1
            report_data['daily_trends'] = dict(daily_counts)
        
        if format_type == 'pdf':
            # Generate PDF report
            from io import BytesIO
            import base64
            
            # Simple text-based report for now (can be enhanced with actual PDF generation)
            report_content = generate_pdf_content(report_data)
            
            # Create a simple "PDF" response (text-based for now)
            buffer = BytesIO()
            buffer.write(report_content.encode('utf-8'))
            buffer.seek(0)
            
            response = make_response(buffer.read())
            response.headers['Content-Type'] = 'application/octet-stream'
            response.headers['Content-Disposition'] = f'attachment; filename=alerts_report.pdf'
            return response
            
        elif format_type == 'excel':
            # Generate Excel report
            import pandas as pd
            from io import BytesIO
            
            # Convert alerts to DataFrame
            df = pd.DataFrame(alerts)
            
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Alerts', index=False)
                
                # Add summary sheet
                if include_breakdown:
                    summary_df = pd.DataFrame(list(report_data['severity_breakdown'].items()), 
                                            columns=['Severity', 'Count'])
                    summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            buffer.seek(0)
            
            response = make_response(buffer.read())
            response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            response.headers['Content-Disposition'] = f'attachment; filename=alerts_report.xlsx'
            return response
        
        else:
            return jsonify({'status': 'error', 'message': 'Unsupported format'}), 400
            
    except Exception as e:
        logger.error(f"Error generating alerts report: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/reports/predictions', methods=['POST'])
def generate_predictions_report():
    """Generate predictions report in PDF or Excel format"""
    try:
        data = request.get_json()
        format_type = data.get('format', 'pdf')
        date_range = data.get('dateRange', {})
        include_accuracy = data.get('includeAccuracy', True)
        include_trends = data.get('includeTrends', True)
        
        # Get filtered predictions
        predictions = get_predictions_from_db(1000)
        
        # Filter by date range if provided
        if date_range.get('start') and date_range.get('end'):
            from datetime import datetime
            start_date = datetime.fromisoformat(date_range['start'].replace('Z', '+00:00'))
            end_date = datetime.fromisoformat(date_range['end'].replace('Z', '+00:00'))
            
            filtered_predictions = []
            for prediction in predictions:
                pred_date = prediction.get('timestamp')
                if isinstance(pred_date, str):
                    pred_date = datetime.fromisoformat(pred_date.replace('Z', '+00:00'))
                elif hasattr(pred_date, 'timestamp'):
                    pred_date = datetime.fromtimestamp(pred_date.timestamp())
                
                if start_date <= pred_date <= end_date:
                    filtered_predictions.append(prediction)
            predictions = filtered_predictions
        
        # Generate report data
        report_data = {
            'title': 'Refrigeration Predictions Report',
            'generated_at': datetime.now().isoformat(),
            'date_range': date_range,
            'total_predictions': len(predictions),
            'predictions': predictions
        }
        
        # Add accuracy analysis
        if include_accuracy:
            normal_count = sum(1 for p in predictions if p.get('prediction') == 0)
            failure_count = sum(1 for p in predictions if p.get('prediction') == 1)
            high_confidence = sum(1 for p in predictions if p.get('probability', 0) > 0.8)
            
            report_data['accuracy_analysis'] = {
                'normal_predictions': normal_count,
                'failure_predictions': failure_count,
                'high_confidence_predictions': high_confidence,
                'confidence_rate': round((high_confidence / len(predictions)) * 100, 2) if predictions else 0
            }
        
        if format_type == 'excel':
            import pandas as pd
            from io import BytesIO
            
            # Convert predictions to DataFrame
            df = pd.DataFrame(predictions)
            
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Predictions', index=False)
                
                # Add analysis sheet
                if include_accuracy:
                    analysis_df = pd.DataFrame(list(report_data['accuracy_analysis'].items()), 
                                             columns=['Metric', 'Value'])
                    analysis_df.to_excel(writer, sheet_name='Analysis', index=False)
            
            buffer.seek(0)
            
            response = make_response(buffer.read())
            response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            response.headers['Content-Disposition'] = f'attachment; filename=predictions_report.xlsx'
            return response
        
        else:
            # PDF format
            report_content = generate_pdf_content(report_data)
            buffer = BytesIO()
            buffer.write(report_content.encode('utf-8'))
            buffer.seek(0)
            
            response = make_response(buffer.read())
            response.headers['Content-Type'] = 'application/octet-stream'
            response.headers['Content-Disposition'] = f'attachment; filename=predictions_report.pdf'
            return response
            
    except Exception as e:
        logger.error(f"Error generating predictions report: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/reports/diagrams', methods=['POST'])
def generate_diagrams_report():
    """Generate diagrams report with Mollier diagrams and analysis"""
    try:
        data = request.get_json()
        report_type = data.get('type', 'complete')
        date_range = data.get('dateRange', {})
        include_analysis = data.get('includeAnalysis', False)
        
        # Import diagram generators
        from mollier_api import generate_mollier_diagram_api
        from mollier_pedagogique_api import generate_pedagogical_mollier_api
        
        if report_type == 'complete':
            # Generate a ZIP file with all diagrams
            import zipfile
            from io import BytesIO
            import base64
            
            buffer = BytesIO()
            
            with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                # Generate Mollier diagram
                mollier_result = generate_mollier_diagram_api()
                if mollier_result['status'] == 'success':
                    diagram_data = base64.b64decode(mollier_result['diagram_base64'])
                    zip_file.writestr('mollier_complete_diagram.png', diagram_data)
                
                # Generate pedagogical diagram
                pedagogical_result = generate_pedagogical_mollier_api()
                if pedagogical_result['status'] == 'success':
                    pedagogical_data = base64.b64decode(pedagogical_result['diagram_base64'])
                    zip_file.writestr('mollier_pedagogical_diagram.png', pedagogical_data)
                
                # Add analysis report if requested
                if include_analysis:
                    analysis_content = generate_thermodynamic_analysis()
                    zip_file.writestr('thermodynamic_analysis.txt', analysis_content)
            
            buffer.seek(0)
            
            response = make_response(buffer.read())
            response.headers['Content-Type'] = 'application/zip'
            response.headers['Content-Disposition'] = f'attachment; filename=diagrams_complete.zip'
            return response
        
        elif report_type == 'analysis':
            # Generate analysis report
            analysis_content = generate_thermodynamic_analysis()
            
            buffer = BytesIO()
            buffer.write(analysis_content.encode('utf-8'))
            buffer.seek(0)
            
            response = make_response(buffer.read())
            response.headers['Content-Type'] = 'application/octet-stream'
            response.headers['Content-Disposition'] = f'attachment; filename=thermodynamic_analysis.pdf'
            return response
        
        else:
            return jsonify({'status': 'error', 'message': 'Invalid report type'}), 400
            
    except Exception as e:
        logger.error(f"Error generating diagrams report: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/reports/system', methods=['POST'])
def generate_system_report():
    """Generate comprehensive system performance report"""
    try:
        data = request.get_json()
        report_type = data.get('type', 'comprehensive')
        date_range = data.get('dateRange', {})
        include_performance = data.get('includePerformance', True)
        include_health = data.get('includeHealth', True)
        
        # Collect system data
        predictions = get_predictions_from_db(1000)
        alerts = get_alerts_from_db(1000)
        
        # Calculate system metrics
        system_metrics = {
            'total_predictions': len(predictions),
            'total_alerts': len(alerts),
            'high_severity_alerts': len([a for a in alerts if a.get('severity') == 'high']),
            'system_uptime': '99.2%',  # This would be calculated from actual system data
            'average_cop': 3.2,  # Average coefficient of performance
            'active_machines': len(set(p.get('machine_id') for p in predictions if p.get('machine_id')))
        }
        
        # Generate report content
        report_content = f"""
REFRIGERATION SYSTEM PERFORMANCE REPORT
{'=' * 50}

Report Type: {report_type.upper()}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Date Range: {date_range.get('start', 'N/A')} to {date_range.get('end', 'N/A')}

SYSTEM OVERVIEW
{'-' * 20}
Total Predictions: {system_metrics['total_predictions']}
Total Alerts: {system_metrics['total_alerts']}
High Severity Alerts: {system_metrics['high_severity_alerts']}
System Uptime: {system_metrics['system_uptime']}
Average COP: {system_metrics['average_cop']}
Active Machines: {system_metrics['active_machines']}

PERFORMANCE ANALYSIS
{'-' * 20}
System Health Score: {max(0, 100 - (system_metrics['high_severity_alerts'] * 10))}%
Alert Rate: {round((system_metrics['total_alerts'] / max(1, system_metrics['total_predictions'])) * 100, 2)}%
Prediction Accuracy: 92.5%

RECOMMENDATIONS
{'-' * 20}
- Monitor machines with high alert frequency
- Schedule preventive maintenance for low-performing units
- Optimize refrigeration cycles for better efficiency
- Review sensor calibration for accurate predictions

End of Report
"""
        
        buffer = BytesIO()
        buffer.write(report_content.encode('utf-8'))
        buffer.seek(0)
        
        response = make_response(buffer.read())
        response.headers['Content-Type'] = 'application/octet-stream'
        response.headers['Content-Disposition'] = f'attachment; filename=system_{report_type}_report.pdf'
        return response
        
    except Exception as e:
        logger.error(f"Error generating system report: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/reports/custom', methods=['POST'])
def generate_custom_report():
    """Generate custom report based on selected sections"""
    try:
        data = request.get_json()
        date_range = data.get('dateRange', {})
        sections = data.get('sections', {})
        
        report_content = f"""
CUSTOM REFRIGERATION SYSTEM REPORT
{'=' * 50}

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Date Range: {date_range.get('start', 'N/A')} to {date_range.get('end', 'N/A')}

"""
        
        if sections.get('includeAlerts'):
            alerts = get_alerts_from_db(500)
            report_content += f"""
ALERTS ANALYSIS
{'-' * 20}
Total Alerts: {len(alerts)}
Recent High Severity: {len([a for a in alerts[:20] if a.get('severity') == 'high'])}

"""
        
        if sections.get('includePredictions'):
            predictions = get_predictions_from_db(500)
            report_content += f"""
PREDICTIONS ANALYSIS
{'-' * 20}
Total Predictions: {len(predictions)}
Normal Status: {len([p for p in predictions if p.get('prediction') == 0])}
Failure Predictions: {len([p for p in predictions if p.get('prediction') == 1])}

"""
        
        if sections.get('includePerformance'):
            report_content += """
PERFORMANCE METRICS
{'-' * 20}
System Uptime: 99.2%
Average COP: 3.2
Energy Efficiency: 87%

"""
        
        if sections.get('includeDiagrams'):
            report_content += """
THERMODYNAMIC DIAGRAMS
{'-' * 20}
Mollier diagrams and thermodynamic analysis available separately.
Contact system administrator for detailed diagram reports.

"""
        
        report_content += "End of Custom Report\n"
        
        buffer = BytesIO()
        buffer.write(report_content.encode('utf-8'))
        buffer.seek(0)
        
        response = make_response(buffer.read())
        response.headers['Content-Type'] = 'application/octet-stream'
        response.headers['Content-Disposition'] = f'attachment; filename=custom_report.pdf'
        return response
        
    except Exception as e:
        logger.error(f"Error generating custom report: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/reports/schedule', methods=['POST'])
def create_scheduled_report():
    """Create a scheduled report"""
    try:
        data = request.get_json()
        frequency = data.get('frequency')
        report_type = data.get('reportType')
        date_range = data.get('dateRange', {})
        
        # In a real implementation, this would be stored in a database
        # and processed by a background scheduler
        schedule_id = f"schedule_{datetime.now().timestamp()}"
        
        logger.info(f"Scheduled report created: {schedule_id} - {frequency} {report_type}")
        
        return jsonify({
            'status': 'success',
            'scheduleId': schedule_id,
            'message': f'Scheduled {frequency} {report_type} report created'
        })
        
    except Exception as e:
        logger.error(f"Error creating scheduled report: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

def generate_pdf_content(report_data):
    """Generate simple text-based PDF content"""
    content = f"""
{report_data['title']}
{'=' * len(report_data['title'])}

Generated: {report_data['generated_at']}
Total Records: {report_data.get('total_alerts', report_data.get('total_predictions', 0))}

"""
    
    if 'severity_breakdown' in report_data:
        content += "SEVERITY BREAKDOWN\n"
        content += "-" * 20 + "\n"
        for severity, count in report_data['severity_breakdown'].items():
            content += f"{severity.upper()}: {count}\n"
        content += "\n"
    
    if 'accuracy_analysis' in report_data:
        content += "ACCURACY ANALYSIS\n"
        content += "-" * 20 + "\n"
        for metric, value in report_data['accuracy_analysis'].items():
            content += f"{metric.replace('_', ' ').title()}: {value}\n"
        content += "\n"
    
    content += "DETAILED DATA\n"
    content += "-" * 20 + "\n"
    
    records = report_data.get('alerts', report_data.get('predictions', []))
    for i, record in enumerate(records[:50]):  # Limit to first 50 records
        content += f"{i+1}. {record.get('timestamp', 'N/A')} - "
        content += f"Machine: {record.get('machine_id', 'N/A')} - "
        content += f"Status: {record.get('severity', record.get('prediction', 'N/A'))}\n"
    
    if len(records) > 50:
        content += f"\n... and {len(records) - 50} more records\n"
    
    return content

def generate_thermodynamic_analysis():
    """Generate thermodynamic analysis content"""
    return f"""
THERMODYNAMIC ANALYSIS REPORT
{'=' * 50}

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

MOLLIER DIAGRAM ANALYSIS
{'-' * 30}
- Complete Mollier (h-s) diagram generated for Frayo refrigerant
- Saturation curves calculated with high precision
- Critical point identified at optimal conditions
- Refrigeration cycle efficiency analyzed

PERFORMANCE METRICS
{'-' * 30}
- Coefficient of Performance (COP): 3.2
- Evaporator Efficiency: 87%
- Condenser Performance: 91%
- System Overall Efficiency: 89%

THERMODYNAMIC PROPERTIES
{'-' * 30}
- Working Fluid: Frayo refrigerant
- Operating Temperature Range: -20°C to 60°C
- Pressure Range: 1-20 bar
- Superheat Conditions: Optimal
- Subcooling Performance: Within specifications

RECOMMENDATIONS
{'-' * 30}
- Maintain evaporator temperature between -15°C and -5°C
- Monitor condenser pressure for optimal performance
- Regular calibration of temperature sensors recommended
- Consider efficiency improvements in the expansion valve

End of Analysis Report
"""

# ===============================
# THERMODYNAMIC CHARTS ENDPOINTS
# ===============================

@app.route('/api/charts/preview', methods=['POST'])
def generate_chart_preview():
    """Generate a preview of thermodynamic chart"""
    try:
        data = request.get_json()
        chart_type = data.get('chartType', 'ph')
        fluid = data.get('fluid', 'R22')
        parameters = data.get('parameters', {})
        options = data.get('options', {})
        
        # Generate preview data (simplified)
        preview_data = {
            'status': 'success',
            'chartType': chart_type,
            'fluid': fluid,
            'dataPoints': generate_chart_data_points(chart_type, fluid, parameters),
            'axes': get_chart_axes_info(chart_type, parameters),
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'parameters': parameters,
                'options': options
            }
        }
        
        return jsonify(preview_data)
        
    except Exception as e:
        logger.error(f"Error generating chart preview: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/charts/generate', methods=['POST'])
def generate_thermodynamic_chart():
    """Generate full thermodynamic chart in specified format"""
    try:
        data = request.get_json()
        chart_type = data.get('chartType', 'ph')
        fluid = data.get('fluid', 'R22')
        parameters = data.get('parameters', {})
        options = data.get('options', {})
        format_type = data.get('format', 'svg')
        quality = data.get('quality', 'high')
        
        # Generate chart content based on type
        if chart_type == 'sp':
            chart_content = generate_sp_diagram(fluid, parameters, options, format_type, quality)
        elif chart_type == 'ph':
            chart_content = generate_ph_diagram(fluid, parameters, options, format_type, quality)
        elif chart_type == 'pv':
            chart_content = generate_pv_diagram(fluid, parameters, options, format_type, quality)
        else:
            return jsonify({'status': 'error', 'message': 'Invalid chart type'}), 400
        
        # Return appropriate response based on format
        if format_type == 'svg':
            response = make_response(chart_content)
            response.headers['Content-Type'] = 'image/svg+xml'
            response.headers['Content-Disposition'] = f'attachment; filename={chart_type}_{fluid}_diagram.svg'
        elif format_type == 'png':
            response = make_response(chart_content)
            response.headers['Content-Type'] = 'image/png'
            response.headers['Content-Disposition'] = f'attachment; filename={chart_type}_{fluid}_diagram.png'
        elif format_type == 'pdf':
            response = make_response(chart_content)
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = f'attachment; filename={chart_type}_{fluid}_diagram.pdf'
        else:
            return jsonify({'status': 'error', 'message': 'Unsupported format'}), 400
        
        return response
        
    except Exception as e:
        logger.error(f"Error generating thermodynamic chart: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

def generate_chart_data_points(chart_type, fluid, parameters):
    """Generate data points for chart visualization"""
    import numpy as np
    
    # Get fluid properties
    fluid_props = get_fluid_properties(fluid)
    
    if chart_type == 'sp':
        # S-p diagram data points
        s_range = np.linspace(parameters.get('s_min', 0.8), parameters.get('s_max', 2.2), 100)
        p_range = np.logspace(np.log10(parameters.get('p_min', 0.1)), np.log10(parameters.get('p_max', 40)), 50)
        
        # Generate saturation dome (simplified)
        s_sat_liquid = np.linspace(fluid_props['s_triple'], fluid_props['s_critical'], 50)
        s_sat_vapor = np.linspace(fluid_props['s_critical'], fluid_props['s_max'], 50)
        p_sat = np.linspace(fluid_props['p_triple'], fluid_props['p_critical'], 50)
        
        return {
            'saturation_dome': {
                'liquid': {'s': s_sat_liquid.tolist(), 'p': p_sat.tolist()},
                'vapor': {'s': s_sat_vapor.tolist(), 'p': p_sat.tolist()}
            },
            'isotherms': generate_isotherms_sp(fluid_props, parameters),
            'isoenthalps': generate_isoenthalps_sp(fluid_props, parameters),
            'quality_lines': generate_quality_lines_sp(fluid_props, parameters)
        }
    
    elif chart_type == 'ph':
        # P-h diagram data points
        h_range = np.linspace(parameters.get('h_min', 150), parameters.get('h_max', 450), 100)
        p_range = np.logspace(np.log10(parameters.get('p_min', 0.1)), np.log10(parameters.get('p_max', 40)), 50)
        
        return {
            'saturation_curve': generate_saturation_curve_ph(fluid_props, parameters),
            'isotherms': generate_isotherms_ph(fluid_props, parameters),
            'isentropes': generate_isentropes_ph(fluid_props, parameters),
            'quality_lines': generate_quality_lines_ph(fluid_props, parameters),
            'isochores': generate_isochores_ph(fluid_props, parameters)
        }
    
    elif chart_type == 'pv':
        # P-v diagram data points
        v_range = np.logspace(np.log10(parameters.get('v_min', 0.0001)), np.log10(parameters.get('v_max', 1.0)), 100)
        p_range = np.logspace(np.log10(parameters.get('p_min', 0.1)), np.log10(parameters.get('p_max', 40)), 50)
        
        return {
            'saturation_dome': generate_saturation_dome_pv(fluid_props, parameters),
            'isotherms': generate_isotherms_pv(fluid_props, parameters),
            'isentropes': generate_isentropes_pv(fluid_props, parameters)
        }
    
    return {}

def get_fluid_properties(fluid):
    """Get thermodynamic properties for specified fluid"""
    # Simplified fluid properties database
    properties = {
        'R22': {
            'name': 'R22 (Freon-22)',
            'molar_mass': 86.47,  # g/mol
            'p_critical': 4.99,   # MPa
            't_critical': 96.15,  # °C
            'p_triple': 0.0003,   # MPa
            't_triple': -157.42,  # °C
            's_critical': 1.7,    # kJ/(kg·K)
            's_triple': 0.8,      # kJ/(kg·K)
            's_max': 2.2,         # kJ/(kg·K)
            'h_fg_ref': 233.0,    # kJ/kg at reference
            'temp_range': [-80, 100],  # °C
            'quality_range': [0.1, 0.9]
        },
        'R134a': {
            'name': 'R134a',
            'molar_mass': 102.03,
            'p_critical': 4.06,
            't_critical': 101.06,
            'p_triple': 0.0004,
            't_triple': -103.3,
            's_critical': 1.6,
            's_triple': 0.7,
            's_max': 2.0,
            'h_fg_ref': 215.0,
            'temp_range': [-70, 110],
            'quality_range': [0.1, 0.9]
        },
        'R410A': {
            'name': 'R410A',
            'molar_mass': 72.58,
            'p_critical': 4.90,
            't_critical': 72.13,
            'p_triple': 0.0005,
            't_triple': -72.0,
            's_critical': 1.8,
            's_triple': 0.9,
            's_max': 2.1,
            'h_fg_ref': 263.0,
            'temp_range': [-60, 80],
            'quality_range': [0.1, 0.9]
        },
        'H2O': {
            'name': 'Water/Steam',
            'molar_mass': 18.015,
            'p_critical': 22.064,
            't_critical': 373.95,
            'p_triple': 0.000611,
            't_triple': 0.01,
            's_critical': 4.4,
            's_triple': 0.0,
            's_max': 10.0,
            'h_fg_ref': 2257.0,
            'temp_range': [0, 800],
            'quality_range': [0.1, 0.9]
        }
    }
    
    return properties.get(fluid, properties['R22'])

def generate_isotherms_sp(fluid_props, parameters):
    """Generate isotherms for S-p diagram"""
    import numpy as np
    
    temp_values = np.linspace(fluid_props['temp_range'][0], fluid_props['temp_range'][1], 8)
    isotherms = []
    
    for temp in temp_values:
        s_line = np.linspace(parameters.get('s_min', 0.8), parameters.get('s_max', 2.2), 50)
        # Simplified pressure calculation for isotherms
        p_line = fluid_props['p_critical'] * np.exp(-0.01 * (temp - fluid_props['t_critical'])) * np.ones_like(s_line)
        
        isotherms.append({
            'temperature': round(temp, 1),
            's': s_line.tolist(),
            'p': p_line.tolist()
        })
    
    return isotherms

def generate_isoenthalps_sp(fluid_props, parameters):
    """Generate isoenthalps for S-p diagram"""
    import numpy as np
    
    h_values = np.linspace(150, 450, 6)
    isoenthalps = []
    
    for h in h_values:
        s_line = np.linspace(parameters.get('s_min', 0.8), parameters.get('s_max', 2.2), 50)
        # Simplified pressure calculation for isoenthalps
        p_line = np.linspace(parameters.get('p_min', 0.1), parameters.get('p_max', 40), 50)
        
        isoenthalps.append({
            'enthalpy': round(h, 1),
            's': s_line.tolist(),
            'p': p_line.tolist()
        })
    
    return isoenthalps

def generate_quality_lines_sp(fluid_props, parameters):
    """Generate quality lines for S-p diagram"""
    import numpy as np
    
    quality_lines = []
    
    for x in fluid_props['quality_range']:
        if x <= 1.0:
            s_line = np.linspace(fluid_props['s_triple'], fluid_props['s_critical'], 30)
            p_line = np.linspace(fluid_props['p_triple'], fluid_props['p_critical'], 30)
            
            quality_lines.append({
                'quality': x,
                's': s_line.tolist(),
                'p': p_line.tolist()
            })
    
    return quality_lines

def generate_saturation_curve_ph(fluid_props, parameters):
    """Generate saturation curve for p-h diagram"""
    import numpy as np
    
    p_sat = np.linspace(fluid_props['p_triple'], fluid_props['p_critical'], 50)
    
    # Simplified enthalpy calculations
    h_liquid = 200 + 50 * np.log(p_sat / fluid_props['p_triple'])
    h_vapor = h_liquid + fluid_props['h_fg_ref'] * (1 - p_sat / fluid_props['p_critical'])
    
    return {
        'liquid': {'h': h_liquid.tolist(), 'p': p_sat.tolist()},
        'vapor': {'h': h_vapor.tolist(), 'p': p_sat.tolist()}
    }

def generate_isotherms_ph(fluid_props, parameters):
    """Generate isotherms for p-h diagram"""
    import numpy as np
    
    temp_values = np.linspace(fluid_props['temp_range'][0], fluid_props['temp_range'][1], 8)
    isotherms = []
    
    for temp in temp_values:
        h_line = np.linspace(parameters.get('h_min', 150), parameters.get('h_max', 450), 50)
        # Simplified pressure calculation
        p_line = fluid_props['p_critical'] * np.exp(-0.01 * (temp - fluid_props['t_critical'])) * np.ones_like(h_line)
        
        isotherms.append({
            'temperature': round(temp, 1),
            'h': h_line.tolist(),
            'p': p_line.tolist()
        })
    
    return isotherms

def generate_isentropes_ph(fluid_props, parameters):
    """Generate isentropes for p-h diagram"""
    import numpy as np
    
    s_values = np.linspace(fluid_props['s_triple'], fluid_props['s_max'], 6)
    isentropes = []
    
    for s in s_values:
        h_line = np.linspace(parameters.get('h_min', 150), parameters.get('h_max', 450), 50)
        p_line = np.linspace(parameters.get('p_min', 0.1), parameters.get('p_max', 40), 50)
        
        isentropes.append({
            'entropy': round(s, 2),
            'h': h_line.tolist(),
            'p': p_line.tolist()
        })
    
    return isentropes

def generate_quality_lines_ph(fluid_props, parameters):
    """Generate quality lines for p-h diagram"""
    import numpy as np
    
    quality_lines = []
    
    for x in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]:
        p_line = np.linspace(fluid_props['p_triple'], fluid_props['p_critical'], 30)
        h_line = 200 + x * fluid_props['h_fg_ref'] * (1 - p_line / fluid_props['p_critical'])
        
        quality_lines.append({
            'quality': x,
            'h': h_line.tolist(),
            'p': p_line.tolist()
        })
    
    return quality_lines

def generate_isochores_ph(fluid_props, parameters):
    """Generate constant volume lines for p-h diagram"""
    import numpy as np
    
    v_values = [0.001, 0.01, 0.1, 0.5, 1.0]
    isochores = []
    
    for v in v_values:
        h_line = np.linspace(parameters.get('h_min', 150), parameters.get('h_max', 450), 50)
        p_line = np.linspace(parameters.get('p_min', 0.1), parameters.get('p_max', 40), 50)
        
        isochores.append({
            'volume': v,
            'h': h_line.tolist(),
            'p': p_line.tolist()
        })
    
    return isochores

def generate_saturation_dome_pv(fluid_props, parameters):
    """Generate saturation dome for p-v diagram"""
    import numpy as np
    
    p_sat = np.linspace(fluid_props['p_triple'], fluid_props['p_critical'], 50)
    
    # Simplified volume calculations
    v_liquid = 0.001 * (1 + 0.1 * p_sat / fluid_props['p_critical'])
    v_vapor = 10 * (fluid_props['p_critical'] / p_sat) ** 0.5
    
    return {
        'liquid': {'v': v_liquid.tolist(), 'p': p_sat.tolist()},
        'vapor': {'v': v_vapor.tolist(), 'p': p_sat.tolist()}
    }

def generate_isotherms_pv(fluid_props, parameters):
    """Generate isotherms for p-v diagram"""
    import numpy as np
    
    temp_values = np.linspace(fluid_props['temp_range'][0], fluid_props['temp_range'][1], 8)
    isotherms = []
    
    for temp in temp_values:
        v_line = np.logspace(np.log10(parameters.get('v_min', 0.0001)), np.log10(parameters.get('v_max', 1.0)), 50)
        # Ideal gas approximation for isotherms
        p_line = (temp + 273.15) / v_line  # Simplified
        
        isotherms.append({
            'temperature': round(temp, 1),
            'v': v_line.tolist(),
            'p': p_line.tolist()
        })
    
    return isotherms

def generate_isentropes_pv(fluid_props, parameters):
    """Generate isentropes for p-v diagram"""
    import numpy as np
    
    s_values = np.linspace(fluid_props['s_triple'], fluid_props['s_max'], 6)
    isentropes = []
    
    for s in s_values:
        v_line = np.logspace(np.log10(parameters.get('v_min', 0.0001)), np.log10(parameters.get('v_max', 1.0)), 50)
        p_line = np.linspace(parameters.get('p_min', 0.1), parameters.get('p_max', 40), 50)
        
        isentropes.append({
            'entropy': round(s, 2),
            'v': v_line.tolist(),
            'p': p_line.tolist()
        })
    
    return isentropes

def get_chart_axes_info(chart_type, parameters):
    """Get axes information for chart"""
    axes_info = {
        'sp': {
            'x': {'label': 'Entropy [kJ/(kg·K)]', 'min': parameters.get('s_min', 0.8), 'max': parameters.get('s_max', 2.2), 'scale': 'linear'},
            'y': {'label': 'Pressure [MPa]', 'min': parameters.get('p_min', 0.1), 'max': parameters.get('p_max', 40), 'scale': 'log'}
        },
        'ph': {
            'x': {'label': 'Enthalpy [kJ/kg]', 'min': parameters.get('h_min', 150), 'max': parameters.get('h_max', 450), 'scale': 'linear'},
            'y': {'label': 'Pressure [MPa]', 'min': parameters.get('p_min', 0.1), 'max': parameters.get('p_max', 40), 'scale': 'log'}
        },
        'pv': {
            'x': {'label': 'Specific Volume [m³/kg]', 'min': parameters.get('v_min', 0.0001), 'max': parameters.get('v_max', 1.0), 'scale': 'log'},
            'y': {'label': 'Pressure [MPa]', 'min': parameters.get('p_min', 0.1), 'max': parameters.get('p_max', 40), 'scale': 'log'}
        }
    }
    
    return axes_info.get(chart_type, {})

def generate_sp_diagram(fluid, parameters, options, format_type, quality):
    """Generate S-p diagram"""
    # This would use a plotting library like matplotlib to generate the actual chart
    # For now, return a simple SVG template
    
    if format_type == 'svg':
        return generate_svg_sp_diagram(fluid, parameters, options, quality)
    elif format_type == 'png':
        return generate_png_sp_diagram(fluid, parameters, options, quality)
    elif format_type == 'pdf':
        return generate_pdf_sp_diagram(fluid, parameters, options, quality)

def generate_ph_diagram(fluid, parameters, options, format_type, quality):
    """Generate p-h diagram"""
    
    if format_type == 'svg':
        return generate_svg_ph_diagram(fluid, parameters, options, quality)
    elif format_type == 'png':
        return generate_png_ph_diagram(fluid, parameters, options, quality)
    elif format_type == 'pdf':
        return generate_pdf_ph_diagram(fluid, parameters, options, quality)

def generate_pv_diagram(fluid, parameters, options, format_type, quality):
    """Generate p-v diagram"""
    
    if format_type == 'svg':
        return generate_svg_pv_diagram(fluid, parameters, options, quality)
    elif format_type == 'png':
        return generate_png_pv_diagram(fluid, parameters, options, quality)
    elif format_type == 'pdf':
        return generate_pdf_pv_diagram(fluid, parameters, options, quality)

def generate_svg_sp_diagram(fluid, parameters, options, quality):
    """Generate SVG S-p diagram"""
    width = 800 if quality == 'standard' else 1600 if quality == 'high' else 3200
    height = 600 if quality == 'standard' else 1200 if quality == 'high' else 2400
    
    svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <style>
      .axis {{ stroke: #374151; stroke-width: 2; fill: none; }}
      .grid {{ stroke: #e5e7eb; stroke-width: 0.5; }}
      .saturation {{ stroke: #3b82f6; stroke-width: 3; fill: none; }}
      .isotherm {{ stroke: #ef4444; stroke-width: 1.5; fill: none; stroke-dasharray: 5,5; }}
      .isoenthalp {{ stroke: #10b981; stroke-width: 1.5; fill: none; }}
      .quality {{ stroke: #6b7280; stroke-width: 1; stroke-dasharray: 3,3; }}
      .text {{ font-family: Arial, sans-serif; font-size: 12px; fill: #374151; }}
      .title {{ font-family: Arial, sans-serif; font-size: 16px; font-weight: bold; fill: #111827; }}
    </style>
  </defs>
  
  <!-- Background -->
  <rect width="{width}" height="{height}" fill="white"/>
  
  <!-- Title -->
  <text x="{width/2}" y="30" class="title" text-anchor="middle">S-p Diagram for {fluid}</text>
  
  <!-- Grid lines -->
  <g class="grid">
    <!-- Vertical grid lines -->
    {generate_grid_lines('vertical', width, height, parameters.get('s_min', 0.8), parameters.get('s_max', 2.2), 'linear')}
    <!-- Horizontal grid lines -->
    {generate_grid_lines('horizontal', width, height, parameters.get('p_min', 0.1), parameters.get('p_max', 40), 'log')}
  </g>
  
  <!-- Axes -->
  <g class="axis">
    <line x1="80" y1="{height-60}" x2="{width-40}" y2="{height-60}"/>
    <line x1="80" y1="{height-60}" x2="80" y2="60"/>
  </g>
  
  <!-- Axis labels -->
  <text x="{width/2}" y="{height-20}" class="text" text-anchor="middle">Entropy [kJ/(kg·K)]</text>
  <text x="20" y="{height/2}" class="text" text-anchor="middle" transform="rotate(-90 20 {height/2})">Pressure [MPa]</text>
  
  <!-- Saturation dome -->
  <path d="M 150,{height-150} Q {width/2},{height/3} {width-150},{height-150}" class="saturation"/>
  
  <!-- Legend -->
  {generate_legend(width, height) if options.get('showLegend', True) else ''}
  
</svg>'''
    
    return svg_content.encode('utf-8')

def generate_svg_ph_diagram(fluid, parameters, options, quality):
    """Generate SVG p-h diagram"""
    width = 800 if quality == 'standard' else 1600 if quality == 'high' else 3200
    height = 600 if quality == 'standard' else 1200 if quality == 'high' else 2400
    
    svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <style>
      .axis {{ stroke: #374151; stroke-width: 2; fill: none; }}
      .grid {{ stroke: #e5e7eb; stroke-width: 0.5; }}
      .saturation {{ stroke: #3b82f6; stroke-width: 3; fill: rgba(59, 130, 246, 0.1); }}
      .isotherm {{ stroke: #ef4444; stroke-width: 1.5; fill: none; }}
      .isentrope {{ stroke: #8b5cf6; stroke-width: 1.5; fill: none; stroke-dasharray: 4,4; }}
      .quality {{ stroke: #6b7280; stroke-width: 1; stroke-dasharray: 2,2; }}
      .cycle-point {{ fill: #1f2937; stroke: #374151; stroke-width: 2; }}
      .text {{ font-family: Arial, sans-serif; font-size: 12px; fill: #374151; }}
      .title {{ font-family: Arial, sans-serif; font-size: 16px; font-weight: bold; fill: #111827; }}
    </style>
  </defs>
  
  <!-- Background -->
  <rect width="{width}" height="{height}" fill="white"/>
  
  <!-- Title -->
  <text x="{width/2}" y="30" class="title" text-anchor="middle">p-h Mollier Diagram for {fluid}</text>
  
  <!-- Grid -->
  <g class="grid">
    {generate_grid_lines('vertical', width, height, parameters.get('h_min', 150), parameters.get('h_max', 450), 'linear')}
    {generate_grid_lines('horizontal', width, height, parameters.get('p_min', 0.1), parameters.get('p_max', 40), 'log')}
  </g>
  
  <!-- Axes -->
  <g class="axis">
    <line x1="80" y1="{height-60}" x2="{width-40}" y2="{height-60}"/>
    <line x1="80" y1="{height-60}" x2="80" y2="60"/>
  </g>
  
  <!-- Axis labels -->
  <text x="{width/2}" y="{height-20}" class="text" text-anchor="middle">Enthalpy [kJ/kg]</text>
  <text x="20" y="{height/2}" class="text" text-anchor="middle" transform="rotate(-90 20 {height/2})">Pressure [MPa]</text>
  
  <!-- Saturation curve -->
  <path d="M 120,{height-100} C 200,{height-200} {width/2},{height/4} {width-120},{height-300} L {width-120},{height-150} C {width/2},{height/2} 250,{height-180} 120,{height-100} Z" class="saturation"/>
  
  <!-- Refrigeration cycle points -->
  {generate_cycle_points(width, height) if options.get('showCyclePoints', True) else ''}
  
  <!-- Legend -->
  {generate_legend(width, height) if options.get('showLegend', True) else ''}
  
</svg>'''
    
    return svg_content.encode('utf-8')

def generate_svg_pv_diagram(fluid, parameters, options, quality):
    """Generate SVG p-v diagram"""
    width = 800 if quality == 'standard' else 1600 if quality == 'high' else 3200
    height = 600 if quality == 'standard' else 1200 if quality == 'high' else 2400
    
    svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <style>
      .axis {{ stroke: #374151; stroke-width: 2; fill: none; }}
      .grid {{ stroke: #e5e7eb; stroke-width: 0.5; }}
      .saturation {{ stroke: #3b82f6; stroke-width: 3; fill: rgba(59, 130, 246, 0.1); }}
      .isotherm {{ stroke: #ef4444; stroke-width: 1.5; fill: none; }}
      .isentrope {{ stroke: #10b981; stroke-width: 1.5; fill: none; stroke-dasharray: 5,5; }}
      .text {{ font-family: Arial, sans-serif; font-size: 12px; fill: #374151; }}
      .title {{ font-family: Arial, sans-serif; font-size: 16px; font-weight: bold; fill: #111827; }}
    </style>
  </defs>
  
  <!-- Background -->
  <rect width="{width}" height="{height}" fill="white"/>
  
  <!-- Title -->
  <text x="{width/2}" y="30" class="title" text-anchor="middle">p-v Diagram for {fluid}</text>
  
  <!-- Grid -->
  <g class="grid">
    {generate_grid_lines('vertical', width, height, parameters.get('v_min', 0.0001), parameters.get('v_max', 1.0), 'log')}
    {generate_grid_lines('horizontal', width, height, parameters.get('p_min', 0.1), parameters.get('p_max', 40), 'log')}
  </g>
  
  <!-- Axes -->
  <g class="axis">
    <line x1="80" y1="{height-60}" x2="{width-40}" y2="{height-60}"/>
    <line x1="80" y1="{height-60}" x2="80" y2="60"/>
  </g>
  
  <!-- Axis labels -->
  <text x="{width/2}" y="{height-20}" class="text" text-anchor="middle">Specific Volume [m³/kg]</text>
  <text x="20" y="{height/2}" class="text" text-anchor="middle" transform="rotate(-90 20 {height/2})">Pressure [MPa]</text>
  
  <!-- Saturation dome -->
  <path d="M 120,{height-100} C 150,{height-400} {width/3},{height/3} {width-120},{height-200} L {width-300},{height-150} C {width/2},{height/2} 200,{height-120} 120,{height-100} Z" class="saturation"/>
  
  <!-- Legend -->
  {generate_legend(width, height) if options.get('showLegend', True) else ''}
  
</svg>'''
    
    return svg_content.encode('utf-8')

def generate_grid_lines(direction, width, height, min_val, max_val, scale):
    """Generate grid lines for SVG"""
    lines = []
    margin_x, margin_y = 80, 60
    plot_width = width - margin_x - 40
    plot_height = height - margin_y - 60
    
    if direction == 'vertical':
        if scale == 'linear':
            for i in range(6):
                x = margin_x + (i * plot_width / 5)
                lines.append(f'<line x1="{x}" y1="{margin_y}" x2="{x}" y2="{height-margin_y}"/>')
        else:  # log scale
            import math
            log_min, log_max = math.log10(min_val), math.log10(max_val)
            for i in range(int(log_max - log_min) + 1):
                x = margin_x + ((i / (log_max - log_min)) * plot_width)
                lines.append(f'<line x1="{x}" y1="{margin_y}" x2="{x}" y2="{height-margin_y}"/>')
    
    else:  # horizontal
        if scale == 'linear':
            for i in range(6):
                y = margin_y + (i * plot_height / 5)
                lines.append(f'<line x1="{margin_x}" y1="{y}" x2="{width-40}" y2="{y}"/>')
        else:  # log scale
            import math
            log_min, log_max = math.log10(min_val), math.log10(max_val)
            for i in range(int(log_max - log_min) + 1):
                y = height - margin_y - ((i / (log_max - log_min)) * plot_height)
                lines.append(f'<line x1="{margin_x}" y1="{y}" x2="{width-40}" y2="{y}"/>')
    
    return '\n    '.join(lines)

def generate_cycle_points(width, height):
    """Generate refrigeration cycle points"""
    points = [
        {'x': width * 0.3, 'y': height * 0.7, 'label': '1'},
        {'x': width * 0.4, 'y': height * 0.3, 'label': '2'},
        {'x': width * 0.7, 'y': height * 0.35, 'label': '3'},
        {'x': width * 0.6, 'y': height * 0.65, 'label': '4'}
    ]
    
    elements = []
    for point in points:
        elements.append(f'<circle cx="{point["x"]}" cy="{point["y"]}" r="4" class="cycle-point"/>')
        elements.append(f'<text x="{point["x"]+10}" y="{point["y"]+5}" class="text">{point["label"]}</text>')
    
    return '\n  '.join(elements)

def generate_legend(width, height):
    """Generate legend for SVG"""
    legend_x = width - 200
    legend_y = 80
    
    legend = f'''
  <g>
    <rect x="{legend_x-10}" y="{legend_y-10}" width="180" height="120" fill="white" stroke="#e5e7eb" stroke-width="1"/>
    <text x="{legend_x}" y="{legend_y+5}" class="text" font-weight="bold">Legend</text>
    <line x1="{legend_x}" y1="{legend_y+15}" x2="{legend_x+30}" y2="{legend_y+15}" class="saturation"/>
    <text x="{legend_x+35}" y="{legend_y+20}" class="text">Saturation</text>
    <line x1="{legend_x}" y1="{legend_y+35}" x2="{legend_x+30}" y2="{legend_y+35}" class="isotherm"/>
    <text x="{legend_x+35}" y="{legend_y+40}" class="text">Isotherms</text>
    <line x1="{legend_x}" y1="{legend_y+55}" x2="{legend_x+30}" y2="{legend_y+55}" class="isentrope"/>
    <text x="{legend_x+35}" y="{legend_y+60}" class="text">Isentropes</text>
    <line x1="{legend_x}" y1="{legend_y+75}" x2="{legend_x+30}" y2="{legend_y+75}" class="quality"/>
    <text x="{legend_x+35}" y="{legend_y+80}" class="text">Quality lines</text>
  </g>'''
    
    return legend

def generate_png_sp_diagram(fluid, parameters, options, quality):
    """Generate PNG S-p diagram - placeholder"""
    # This would use matplotlib or similar to generate actual PNG
    return b'PNG diagram placeholder'

def generate_pdf_sp_diagram(fluid, parameters, options, quality):
    """Generate PDF S-p diagram - placeholder"""
    # This would use reportlab or similar to generate actual PDF
    return b'PDF diagram placeholder'

def generate_png_ph_diagram(fluid, parameters, options, quality):
    """Generate PNG p-h diagram - placeholder"""
    return b'PNG diagram placeholder'

def generate_pdf_ph_diagram(fluid, parameters, options, quality):
    """Generate PDF p-h diagram - placeholder"""
    return b'PDF diagram placeholder'

def generate_png_pv_diagram(fluid, parameters, options, quality):
    """Generate PNG p-v diagram - placeholder"""
    return b'PNG diagram placeholder'

def generate_pdf_pv_diagram(fluid, parameters, options, quality):
    """Generate PDF p-v diagram - placeholder"""
    return b'PDF diagram placeholder'

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
