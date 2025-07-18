"""
Producteur Kafka pour données d'installations frigorifiques avec capteurs réels
Intégration du système de capteurs selon spécifications PDF
"""

import json
import time
import random
from datetime import datetime
from kafka import KafkaProducer
from sensor_system_real import RefrigerationSensors

# Configuration Kafka
KAFKA_BROKER = 'localhost:9092'
TOPIC_NAME = 'refrigeration-sensors'

# Initialisation du système de capteurs réels
refrigeration_sensors = RefrigerationSensors()

# Machines surveillées (selon architecture réelle)
MACHINES = [
    "COMPRESSOR_001", "COMPRESSOR_002", "COMPRESSOR_003",
    "EVAPORATOR_001", "EVAPORATOR_002", 
    "CONDENSER_001", "CONDENSER_002",
    "COOLING_UNIT_001", "COOLING_UNIT_002"
]

def generate_refrigeration_data_with_real_sensors():
    """Génère des données avec le système de capteurs réels"""
    
    # Sélection aléatoire d'une machine
    machine_id = random.choice(MACHINES)
    
    # Détermination des conditions (80% normales, 20% anormales)
    is_normal = random.random() < 0.8
    
    if is_normal:
        # Génération de lectures normales
        readings = refrigeration_sensors.generate_normal_readings(machine_id)
        condition = "normal"
    else:
        # Génération de lectures anormales
        abnormal_conditions = [
            "sensor_failure", "calibration_error", "pressure_drop",
            "incomplete_evaporation", "inefficient_condensation",
            "misadjusted_expansion_valve", "clogged_filter"
        ]
        condition = random.choice(abnormal_conditions)
        readings = refrigeration_sensors.generate_abnormal_readings(machine_id, condition)
    
    # Calcul des paramètres dérivés
    derived_params = refrigeration_sensors.calculate_derived_parameters(readings)
    
    # Conversion vers format Kafka
    kafka_data = {
        'machine_id': machine_id,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'operating_condition': condition,
        
        # Données des capteurs réels
        'sensors': {
            'pressure': {
                'high': readings["pressure_hp"].value,
                'low': readings["pressure_bp"].value,
                'intermediate': readings["pressure_intermediate"].value,
                'differential': readings["pressure_differential"].value
            },
            'temperature': {
                'aspiration': readings["temp_aspiration"].value,
                'refoulement': readings["temp_refoulement"].value,
                'condensation': readings["temp_condensation"].value,
                'evaporation': readings["temp_evaporation"].value,
                'liquid': readings["temp_liquid"].value,
                'ambient': readings["temp_ambient"].value
            }
        },
        
        # Paramètres dérivés calculés
        'derived_parameters': {
            'superheat_functional': derived_params["superheat_functional"],
            'superheat_aspiration': derived_params["superheat_aspiration"],
            'subcooling': derived_params["subcooling"],
            'cop': derived_params["cop"],
            'pressure_ratio': derived_params["pressure_ratio"],
            'cooling_effect': derived_params["cooling_effect"],
            'compression_work': derived_params["compression_work"],
            'heat_rejected': derived_params["heat_rejected"]
        },
        
        # Enthalpies pour diagramme de Mollier
        'enthalpies': {
            'h1': derived_params["enthalpy_h1"],
            'h2': derived_params["enthalpy_h2"],
            'h3': derived_params["enthalpy_h3"],
            'h4': derived_params["enthalpy_h4"],
            'h8': derived_params["enthalpy_h8"],
            'h9': derived_params["enthalpy_h9"]
        },
        
        # Statuts des capteurs
        'sensor_status': {
            sensor_id: reading.status 
            for sensor_id, reading in readings.items()
        },
        
        # Capteurs en anomalie
        'abnormal_sensors': [
            sensor_id for sensor_id, reading in readings.items() 
            if reading.status in ['warning', 'critical', 'error']
        ],
        
        # Données pour compatibilité avec le système existant
        'temp_evaporator': readings["temp_evaporation"].value,
        'temp_condenser': readings["temp_condensation"].value,
        'pressure_high': readings["pressure_hp"].value,
        'pressure_low': readings["pressure_bp"].value,
        'superheat': derived_params["superheat_functional"],
        'subcooling': derived_params["subcooling"],
        'compressor_current': round(random.uniform(6, 12), 1),
        'vibration': round(random.uniform(0.01, 0.06), 3)
    }
    
    return kafka_data

def generate_refrigeration_data():
    """Génère des données de capteurs pour installations frigorifiques"""
    # Utilisation du nouveau système de capteurs réels
    return generate_refrigeration_data_with_real_sensors()

def simulate_sensor_variations():
    """Simule des variations réalistes selon les conditions d'exploitation"""
    
    # Variation selon l'heure (charge thermique)
    hour = datetime.now().hour
    
    if 6 <= hour <= 18:  # Journée - plus de charge
        load_factor = 1.2
        ambient_temp_adjustment = 5
    else:  # Nuit - moins de charge
        load_factor = 0.8
        ambient_temp_adjustment = -3
    
    # Variation selon la saison (simulation)
    month = datetime.now().month
    seasonal_adjustment = 0
    
    if month in [6, 7, 8]:  # Été
        seasonal_adjustment = 8
    elif month in [12, 1, 2]:  # Hiver
        seasonal_adjustment = -8
    elif month in [3, 4, 5, 9, 10, 11]:  # Intersaison
        seasonal_adjustment = 0
    
    return {
        'load_factor': load_factor,
        'ambient_temp_adjustment': ambient_temp_adjustment,
        'seasonal_adjustment': seasonal_adjustment
    }

def main():
    """Fonction principale du producteur Kafka"""
    
    # Initialisation du producteur Kafka
    try:
        producer = KafkaProducer(
            bootstrap_servers=[KAFKA_BROKER],
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda v: v.encode('utf-8') if v else None
        )
        print("✅ Producteur Kafka initialisé avec succès")
        print(f"📡 Broker: {KAFKA_BROKER}")
        print(f"📊 Topic: {TOPIC_NAME}")
        print(f"🏭 Machines surveillées: {len(MACHINES)}")
        
        # Affichage du résumé des capteurs
        sensor_summary = refrigeration_sensors.get_sensor_summary()
        print(f"\n📋 CONFIGURATION CAPTEURS:")
        print(f"   • Capteurs de pression: {sensor_summary['pressure_sensors']['count']}")
        print(f"   • Capteurs de température: {sensor_summary['temperature_sensors']['count']}")
        print(f"   • Conditions typiques: {len(sensor_summary['typical_operating_conditions'])} paramètres")
        
    except Exception as e:
        print(f"❌ Erreur initialisation Kafka: {e}")
        return
    
    print("\n🚀 Démarrage de la génération de données...")
    print("Appuyez sur Ctrl+C pour arrêter")
    
    try:
        message_count = 0
        
        while True:
            # Génération des données avec capteurs réels
            data = generate_refrigeration_data()
            
            # Ajout des variations temporelles
            variations = simulate_sensor_variations()
            
            # Application des variations
            data['load_factor'] = variations['load_factor']
            data['sensors']['temperature']['ambient'] += variations['ambient_temp_adjustment']
            data['sensors']['temperature']['condensation'] += variations['seasonal_adjustment']
            
            # Ajout d'un ID de message
            data['message_id'] = f"MSG_{message_count:06d}"
            message_count += 1
            
            # Envoi via Kafka
            try:
                future = producer.send(
                    topic=TOPIC_NAME,
                    key=data['machine_id'],
                    value=data
                )
                
                # Attente de confirmation
                record_metadata = future.get(timeout=10)
                
                # Affichage du statut
                status_emoji = "⚠️" if data['operating_condition'] != 'normal' else "✅"
                sensor_issues = len(data['abnormal_sensors'])
                
                print(f"{status_emoji} [{data['timestamp']}] {data['machine_id']} | "
                      f"Condition: {data['operating_condition']} | "
                      f"Capteurs anormaux: {sensor_issues} | "
                      f"COP: {data['derived_parameters']['cop']:.2f} | "
                      f"Partition: {record_metadata.partition}")
                
                # Affichage détaillé des problèmes détectés
                if sensor_issues > 0:
                    print(f"   📊 Capteurs problématiques: {', '.join(data['abnormal_sensors'])}")
                    print(f"   🌡️ T_évap: {data['sensors']['temperature']['evaporation']:.1f}°C | "
                          f"T_cond: {data['sensors']['temperature']['condensation']:.1f}°C")
                    print(f"   📈 P_haute: {data['sensors']['pressure']['high']:.1f}bar | "
                          f"P_basse: {data['sensors']['pressure']['low']:.1f}bar")
                
            except Exception as e:
                print(f"❌ Erreur envoi Kafka: {e}")
            
            # Attente avant le prochain message (5-15 secondes)
            wait_time = random.randint(5, 15)
            time.sleep(wait_time)
            
    except KeyboardInterrupt:
        print("\n⏹️ Arrêt du producteur Kafka")
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
    finally:
        producer.close()
        print("✅ Producteur Kafka fermé proprement")

if __name__ == "__main__":
    main()