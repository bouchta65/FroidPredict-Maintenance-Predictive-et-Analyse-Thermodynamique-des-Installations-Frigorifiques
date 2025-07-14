from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO
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
socketio = SocketIO(app, cors_allowed_origins="*")

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

@app.route('/')
def index():
    recent_predictions = get_predictions_from_db(10)
    recent_alerts = get_alerts_from_db(10)
    return render_template('dashboard.html', 
                         predictions=recent_predictions, 
                         alerts=recent_alerts)

@app.route('/predictions')
def view_predictions():
    all_predictions = get_predictions_from_db(100)
    return render_template('predictions.html', predictions=all_predictions)

@app.route('/alerts')
def view_alerts():
    all_alerts = get_alerts_from_db(100)
    return render_template('alerts.html', alerts=all_alerts)

@app.route('/diagrams')
def view_diagrams():
    """Page pour visualiser les diagrammes de Mollier améliorés"""
    return render_template('mollier_frayo_improved.html')

@app.route('/mollier-frayo')
def view_mollier_frayo():
    """Page pour visualiser le diagramme de Mollier du fluide Frayo"""
    return render_template('mollier_frayo_improved.html')

@app.route('/mollier-frayo-improved')
def view_mollier_frayo_improved():
    """Page améliorée pour visualiser le diagramme de Mollier du fluide Frayo"""
    return render_template('mollier_frayo_improved.html')

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

@app.route('/api/mollier_frayo', methods=['GET'])
def get_mollier_frayo_diagram():
    """API pour générer le diagramme de Mollier pour le fluide Frayo"""
    try:
        from mollier_api import generate_mollier_diagram_api
        result = generate_mollier_diagram_api()
        return jsonify(result)
    except Exception as e:
        logger.error(f"Erreur génération diagramme Mollier Frayo: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Erreur génération diagramme: {str(e)}'
        }), 500

@app.route('/api/frayo_properties', methods=['GET'])
def get_frayo_properties():
    """API pour obtenir les propriétés thermodynamiques du fluide Frayo"""
    try:
        from mollier_api import get_frayo_properties_data
        result = get_frayo_properties_data()
        return jsonify(result)
    except Exception as e:
        logger.error(f"Erreur propriétés Frayo: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Erreur propriétés: {str(e)}'
        }), 500

@app.route('/api/mollier_pedagogique', methods=['GET'])
def get_mollier_pedagogique():
    """API pour générer le diagramme de Mollier pédagogique"""
    try:
        from mollier_pedagogique_api import generate_pedagogical_mollier_api
        result = generate_pedagogical_mollier_api()
        return jsonify(result)
    except Exception as e:
        logger.error(f"Erreur diagramme pédagogique: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Erreur génération: {str(e)}'
        }), 500

@app.route('/api/mollier_explanation', methods=['GET'])
def get_mollier_explanation():
    """API pour obtenir l'explication pédagogique du diagramme"""
    try:
        from mollier_pedagogique_api import get_pedagogical_explanation
        result = get_pedagogical_explanation()
        return jsonify(result)
    except Exception as e:
        logger.error(f"Erreur explication: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Erreur explication: {str(e)}'
        }), 500

@app.route('/api/mollier_complet', methods=['GET'])
def get_mollier_complet_diagram():
    """API pour générer le diagramme de Mollier complet et responsive"""
    try:
        from mollier_complet_api import generate_complete_mollier_api
        result = generate_complete_mollier_api()
        return jsonify(result)
    except Exception as e:
        logger.error(f"Erreur génération diagramme complet: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Erreur génération diagramme complet: {str(e)}'
        }), 500

@app.route('/api/frayo_properties_complet', methods=['GET'])
def get_frayo_properties_complet():
    """API pour obtenir les propriétés complètes du fluide Frayo avec données producteur"""
    try:
        from mollier_complet_api import get_complete_frayo_properties
        result = get_complete_frayo_properties()
        return jsonify(result)
    except Exception as e:
        logger.error(f"Erreur propriétés complètes: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Erreur propriétés complètes: {str(e)}'
        }), 500

@app.route('/api/mollier_specifications', methods=['GET'])
def get_mollier_specifications():
    """API pour obtenir les spécifications détaillées du diagramme"""
    try:
        from mollier_complet_api import get_diagram_specifications
        result = get_diagram_specifications()
        return jsonify(result)
    except Exception as e:
        logger.error(f"Erreur spécifications: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Erreur spécifications: {str(e)}'
        }), 500

@app.route('/mollier-complet')
def view_mollier_complet():
    """Redirection vers la page diagrams avec l'onglet complet"""
    return render_template('mollier_frayo_improved.html')

if __name__ == '__main__':
    # Création des dossiers nécessaires
    os.makedirs(os.path.join(BASE_DIR, "templates"), exist_ok=True)
    os.makedirs(os.path.join(BASE_DIR, "static"), exist_ok=True)
    
    logger.info("🧊 Démarrage dashboard maintenance prédictive installations frigorifiques")
    logger.info("🌐 http://localhost:5002")
    
    socketio.run(app, debug=True, host='0.0.0.0', port=5002)