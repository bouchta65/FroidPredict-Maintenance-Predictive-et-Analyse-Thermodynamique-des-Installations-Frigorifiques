#!/usr/bin/env python3
"""
Script de test pour générer des données de diagramme enthalpique
et envoyer des données de test vers l'API de prédiction
"""

import requests
import json
import random
import time
from datetime import datetime
import numpy as np

# Configuration
API_URL = "http://localhost:5001/api/refrigeration_prediction"
MACHINES = ["FRIGO_001", "FRIGO_002", "FRIGO_003", "FRIGO_004", "FRIGO_005"]

def generate_refrigeration_data(machine_id, normal_operation=True):
    """
    Génère des données réalistes pour une installation frigorifique
    
    Args:
        machine_id: Identifiant de la machine
        normal_operation: True pour fonctionnement normal, False pour défaillance
    """
    
    if normal_operation:
        # Conditions normales de fonctionnement
        base_data = {
            "temp_evaporator": np.random.normal(-12, 2),    # -8 à -16°C
            "temp_condenser": np.random.normal(42, 3),      # 35 à 50°C
            "pressure_high": np.random.normal(13, 1),       # 11 à 15 bar
            "pressure_low": np.random.normal(2.2, 0.3),     # 1.5 à 3 bar
            "superheat": np.random.normal(8, 1.5),          # 5 à 12°C
            "subcooling": np.random.normal(5, 1),           # 3 à 8°C
            "compressor_current": np.random.normal(8.5, 0.8), # 7 à 10A
            "vibration": np.random.normal(0.025, 0.01)      # 0.01 à 0.04g
        }
    else:
        # Conditions de défaillance
        base_data = {
            "temp_evaporator": np.random.normal(-8, 2),     # Plus élevée
            "temp_condenser": np.random.normal(48, 4),      # Plus élevée
            "pressure_high": np.random.normal(15, 1.5),     # Plus élevée
            "pressure_low": np.random.normal(1.8, 0.3),     # Plus basse
            "superheat": np.random.normal(12, 3),           # Plus élevée
            "subcooling": np.random.normal(3, 1),           # Plus basse
            "compressor_current": np.random.normal(10, 1.2), # Plus élevé
            "vibration": np.random.normal(0.045, 0.015)     # Plus élevée
        }
    
    # Ajouter des contraintes physiques réalistes
    base_data["temp_evaporator"] = max(-20, min(-5, base_data["temp_evaporator"]))
    base_data["temp_condenser"] = max(30, min(60, base_data["temp_condenser"]))
    base_data["pressure_high"] = max(8, min(20, base_data["pressure_high"]))
    base_data["pressure_low"] = max(1, min(4, base_data["pressure_low"]))
    base_data["superheat"] = max(2, min(20, base_data["superheat"]))
    base_data["subcooling"] = max(1, min(10, base_data["subcooling"]))
    base_data["compressor_current"] = max(5, min(15, base_data["compressor_current"]))
    base_data["vibration"] = max(0.005, min(0.1, base_data["vibration"]))
    
    # Ajouter les métadonnées
    base_data["machine_id"] = machine_id
    base_data["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    return base_data

def send_prediction_data(data):
    """Envoie les données vers l'API de prédiction"""
    try:
        response = requests.post(API_URL, json=data, timeout=10)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ {data['machine_id']}: Prédiction={result['prediction']}, "
                  f"Probabilité={result['probability']:.1%}, "
                  f"Alertes={result['alerts_generated']}")
            return True
        else:
            print(f"❌ Erreur API: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur envoi données: {e}")
        return False

def generate_scenario_data():
    """Génère des données pour différents scénarios"""
    scenarios = [
        {
            "name": "Fonctionnement Normal",
            "machines": MACHINES[:3],
            "normal": True,
            "description": "Conditions optimales de fonctionnement"
        },
        {
            "name": "Surcharge Thermique",
            "machines": [MACHINES[3]],
            "normal": False,
            "description": "Température condenseur élevée"
        },
        {
            "name": "Fuite Frigorigène",
            "machines": [MACHINES[4]],
            "normal": False,
            "description": "Pression basse, surchauffe élevée"
        }
    ]
    
    print("🧊 Génération de données de test pour installations frigorifiques")
    print("=" * 70)
    
    for scenario in scenarios:
        print(f"\n📊 Scénario: {scenario['name']}")
        print(f"📝 Description: {scenario['description']}")
        print("-" * 50)
        
        for machine in scenario['machines']:
            data = generate_refrigeration_data(machine, scenario['normal'])
            
            # Personnaliser selon le scénario
            if scenario['name'] == "Surcharge Thermique":
                data['temp_condenser'] = np.random.uniform(52, 58)
                data['pressure_high'] = np.random.uniform(16, 18)
                data['compressor_current'] = np.random.uniform(11, 13)
            elif scenario['name'] == "Fuite Frigorigène":
                data['pressure_low'] = np.random.uniform(1.0, 1.4)
                data['superheat'] = np.random.uniform(15, 22)
                data['subcooling'] = np.random.uniform(1, 3)
                data['temp_evaporator'] = np.random.uniform(-6, -4)
            
            # Afficher les données avant envoi
            print(f"🔧 Machine {machine}:")
            print(f"   T° évaporateur: {data['temp_evaporator']:.1f}°C")
            print(f"   T° condenseur: {data['temp_condenser']:.1f}°C")
            print(f"   Pression HP: {data['pressure_high']:.1f} bar")
            print(f"   Pression BP: {data['pressure_low']:.1f} bar")
            print(f"   Surchauffe: {data['superheat']:.1f}°C")
            print(f"   Sous-refroidissement: {data['subcooling']:.1f}°C")
            print(f"   Courant compresseur: {data['compressor_current']:.1f}A")
            print(f"   Vibrations: {data['vibration']:.3f}g")
            
            send_prediction_data(data)
            time.sleep(1)  # Pause entre les envois

def continuous_monitoring():
    """Simulation de surveillance continue"""
    print("\n🔄 Démarrage de la surveillance continue...")
    print("Appuyez sur Ctrl+C pour arrêter")
    
    try:
        while True:
            # Choisir une machine aléatoire
            machine = random.choice(MACHINES)
            
            # 80% de chance de fonctionnement normal
            is_normal = random.random() < 0.8
            
            data = generate_refrigeration_data(machine, is_normal)
            
            # Ajouter des variations temporelles réalistes
            hour = datetime.now().hour
            if 6 <= hour <= 18:  # Journée - plus de charge
                data['temp_evaporator'] += random.uniform(-1, 1)
                data['temp_condenser'] += random.uniform(2, 5)
                data['compressor_current'] += random.uniform(0.5, 1.5)
            else:  # Nuit - moins de charge
                data['temp_evaporator'] -= random.uniform(0, 2)
                data['temp_condenser'] -= random.uniform(1, 3)
                data['compressor_current'] -= random.uniform(0.2, 0.8)
            
            send_prediction_data(data)
            
            # Pause entre 5 et 15 secondes
            time.sleep(random.uniform(5, 15))
            
    except KeyboardInterrupt:
        print("\n⏹️ Arrêt de la surveillance")

def test_temperature_analysis():
    """Test de l'API d'analyse des températures"""
    print("\n🌡️ Test de l'analyse des températures")
    print("-" * 40)
    
    test_cases = [
        {"ambient_temperature": 25, "cooling_load": 100, "description": "Conditions standard"},
        {"ambient_temperature": 35, "cooling_load": 120, "description": "Canicule - surcharge"},
        {"ambient_temperature": 15, "cooling_load": 60, "description": "Hiver - charge réduite"},
        {"ambient_temperature": 28, "cooling_load": 80, "description": "Été modéré"}
    ]
    
    for test_case in test_cases:
        print(f"\n📋 Test: {test_case['description']}")
        try:
            response = requests.post(
                "http://localhost:5001/api/temperature_analysis",
                json=test_case,
                timeout=10
            )
            if response.status_code == 200:
                result = response.json()
                analysis = result['analysis']
                print(f"✅ T° évaporateur optimale: {analysis['optimal_conditions']['evaporator_temp']:.1f}°C")
                print(f"✅ T° condenseur optimale: {analysis['optimal_conditions']['condenser_temp']:.1f}°C")
                print(f"📊 Recommandations: {len(analysis['recommendations'])}")
            else:
                print(f"❌ Erreur API: {response.status_code}")
        except Exception as e:
            print(f"❌ Erreur test: {e}")

def main():
    """Fonction principale"""
    print("🧊 TESTEUR DIAGRAMME ENTHALPIQUE - INSTALLATIONS FRIGORIFIQUES")
    print("=" * 70)
    
    while True:
        print("\n📋 Options disponibles:")
        print("1. Générer des données de scénarios")
        print("2. Surveillance continue")
        print("3. Test analyse des températures")
        print("4. Quitter")
        
        choice = input("\n🔍 Choisissez une option (1-4): ").strip()
        
        if choice == "1":
            generate_scenario_data()
        elif choice == "2":
            continuous_monitoring()
        elif choice == "3":
            test_temperature_analysis()
        elif choice == "4":
            print("👋 Au revoir!")
            break
        else:
            print("❌ Option invalide")

if __name__ == "__main__":
    main()
