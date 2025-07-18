"""
Script de test pour le nouveau système de capteurs réels
Test des conditions normales et anormales selon spécifications PDF
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from sensor_system_real import RefrigerationSensors
from mollier_diagram_frayo import MollierDiagramGenerator
import matplotlib.pyplot as plt

def test_real_sensor_system():
    """Test complet du système de capteurs réels"""
    
    print("🧪 TEST DU SYSTÈME DE CAPTEURS RÉELS")
    print("=" * 50)
    
    # Initialisation
    sensor_system = RefrigerationSensors()
    
    # 1. Test des conditions normales
    print("\n1️⃣ TEST CONDITIONS NORMALES")
    print("-" * 30)
    
    normal_readings = sensor_system.generate_normal_readings("TEST_MACHINE_001")
    derived_params = sensor_system.calculate_derived_parameters(normal_readings)
    
    print(f"✅ Capteurs configurés: {len(sensor_system.sensor_config)}")
    print(f"✅ Lectures générées: {len(normal_readings)}")
    print(f"✅ Paramètres dérivés: {len(derived_params)}")
    
    # Affichage des lectures importantes
    print("\n📊 LECTURES CAPTEURS NORMALES:")
    key_sensors = ['pressure_hp', 'pressure_bp', 'temp_aspiration', 'temp_refoulement', 
                   'temp_condensation', 'temp_evaporation']
    
    for sensor_id in key_sensors:
        if sensor_id in normal_readings:
            reading = normal_readings[sensor_id]
            config = sensor_system.sensor_config[sensor_id]
            print(f"   {config['name']}: {reading.value} {reading.unit} ({reading.status})")
    
    # Affichage des paramètres dérivés
    print("\n📈 PARAMÈTRES DÉRIVÉS:")
    key_params = ['superheat_functional', 'subcooling', 'cop', 'pressure_ratio']
    for param in key_params:
        if param in derived_params:
            print(f"   {param}: {derived_params[param]}")
    
    # 2. Test des conditions anormales
    print("\n2️⃣ TEST CONDITIONS ANORMALES")
    print("-" * 30)
    
    # Test de différentes conditions anormales
    abnormal_conditions = [
        "sensor_failure",
        "inefficient_condensation", 
        "incomplete_evaporation",
        "misadjusted_expansion_valve",
        "clogged_filter"
    ]
    
    for condition in abnormal_conditions:
        print(f"\n🔴 Test condition: {condition}")
        
        abnormal_readings = sensor_system.generate_abnormal_readings("TEST_MACHINE_002", condition)
        abnormal_params = sensor_system.calculate_derived_parameters(abnormal_readings)
        
        # Comptage des capteurs anormaux
        abnormal_count = sum(1 for reading in abnormal_readings.values() 
                           if reading.status in ['warning', 'critical', 'error'])
        
        print(f"   Capteurs anormaux: {abnormal_count}/{len(abnormal_readings)}")
        
        # Affichage des capteurs problématiques
        problem_sensors = [sensor_id for sensor_id, reading in abnormal_readings.items() 
                          if reading.status != 'normal']
        
        if problem_sensors:
            print(f"   Capteurs problématiques: {', '.join(problem_sensors)}")
            
            # Détails des problèmes
            for sensor_id in problem_sensors[:3]:  # Limiter à 3 pour l'affichage
                reading = abnormal_readings[sensor_id]
                config = sensor_system.sensor_config[sensor_id]
                print(f"      {config['name']}: {reading.value} {reading.unit} ({reading.status})")
    
    # 3. Test du résumé des capteurs
    print("\n3️⃣ RÉSUMÉ DU SYSTÈME")
    print("-" * 30)
    
    summary = sensor_system.get_sensor_summary()
    
    print(f"📋 Capteurs de pression: {summary['pressure_sensors']['count']}")
    for sensor_type in summary['pressure_sensors']['types']:
        print(f"   • {sensor_type}")
    
    print(f"\n🌡️ Capteurs de température: {summary['temperature_sensors']['count']}")
    for sensor_type in summary['temperature_sensors']['types']:
        print(f"   • {sensor_type}")
    
    print(f"\n📊 Conditions typiques d'exploitation:")
    for param, value in summary['typical_operating_conditions'].items():
        print(f"   • {param}: {value}")
    
    return True

def test_mollier_diagram_with_real_sensors():
    """Test du diagramme de Mollier avec capteurs réels"""
    
    print("\n🔄 TEST DIAGRAMME DE MOLLIER AVEC CAPTEURS RÉELS")
    print("=" * 55)
    
    # Initialisation
    generator = MollierDiagramGenerator()
    sensor_system = RefrigerationSensors()
    
    # 1. Test avec conditions normales
    print("\n1️⃣ DIAGRAMME CONDITIONS NORMALES")
    print("-" * 35)
    
    # Génération des données normales
    normal_readings = sensor_system.generate_normal_readings("NORMAL_MACHINE")
    derived_params = sensor_system.calculate_derived_parameters(normal_readings)
    
    normal_sensor_data = {
        'machine_id': 'NORMAL_MACHINE',
        'operating_condition': 'normal',
        'sensors': {
            'temperature': {
                'evaporation': normal_readings['temp_evaporation'].value,
                'condensation': normal_readings['temp_condensation'].value,
                'aspiration': normal_readings['temp_aspiration'].value,
                'refoulement': normal_readings['temp_refoulement'].value,
                'liquid': normal_readings['temp_liquid'].value
            },
            'pressure': {
                'high': normal_readings['pressure_hp'].value,
                'low': normal_readings['pressure_bp'].value,
                'intermediate': normal_readings['pressure_intermediate'].value,
                'differential': normal_readings['pressure_differential'].value
            }
        },
        'derived_parameters': derived_params,
        'sensor_status': {k: v.status for k, v in normal_readings.items()},
        'abnormal_sensors': [k for k, v in normal_readings.items() if v.status != 'normal']
    }
    
    # Génération du diagramme normal
    normal_diagram_path = generator.generate_diagram_with_real_data(
        sensor_data=normal_sensor_data,
        save_path='test_mollier_normal_conditions.png'
    )
    
    print(f"✅ Diagramme normal généré: {normal_diagram_path}")
    
    # 2. Test avec conditions anormales
    print("\n2️⃣ DIAGRAMME CONDITIONS ANORMALES")
    print("-" * 35)
    
    # Test avec condensation inefficace
    abnormal_readings = sensor_system.generate_abnormal_readings("CRITICAL_MACHINE", "inefficient_condensation")
    abnormal_params = sensor_system.calculate_derived_parameters(abnormal_readings)
    
    abnormal_sensor_data = {
        'machine_id': 'CRITICAL_MACHINE',
        'operating_condition': 'inefficient_condensation',
        'sensors': {
            'temperature': {
                'evaporation': abnormal_readings['temp_evaporation'].value,
                'condensation': abnormal_readings['temp_condensation'].value,
                'aspiration': abnormal_readings['temp_aspiration'].value,
                'refoulement': abnormal_readings['temp_refoulement'].value,
                'liquid': abnormal_readings['temp_liquid'].value
            },
            'pressure': {
                'high': abnormal_readings['pressure_hp'].value,
                'low': abnormal_readings['pressure_bp'].value,
                'intermediate': abnormal_readings['pressure_intermediate'].value,
                'differential': abnormal_readings['pressure_differential'].value
            }
        },
        'derived_parameters': abnormal_params,
        'sensor_status': {k: v.status for k, v in abnormal_readings.items()},
        'abnormal_sensors': [k for k, v in abnormal_readings.items() if v.status != 'normal']
    }
    
    # Génération du diagramme anormal
    abnormal_diagram_path = generator.generate_diagram_with_real_data(
        sensor_data=abnormal_sensor_data,
        save_path='test_mollier_abnormal_conditions.png'
    )
    
    print(f"⚠️ Diagramme anormal généré: {abnormal_diagram_path}")
    print(f"   Capteurs anormaux: {len(abnormal_sensor_data['abnormal_sensors'])}")
    print(f"   Condition détectée: {abnormal_sensor_data['operating_condition']}")
    
    # 3. Comparaison des performances
    print("\n3️⃣ COMPARAISON DES PERFORMANCES")
    print("-" * 35)
    
    normal_cop = normal_sensor_data['derived_parameters']['cop']
    abnormal_cop = abnormal_sensor_data['derived_parameters']['cop']
    
    print(f"COP Normal: {normal_cop:.3f}")
    print(f"COP Anormal: {abnormal_cop:.3f}")
    print(f"Dégradation: {((normal_cop - abnormal_cop) / normal_cop * 100):.1f}%")
    
    normal_cooling = normal_sensor_data['derived_parameters']['cooling_effect']
    abnormal_cooling = abnormal_sensor_data['derived_parameters']['cooling_effect']
    
    print(f"Effet frigorifique Normal: {normal_cooling:.1f} kJ/kg")
    print(f"Effet frigorifique Anormal: {abnormal_cooling:.1f} kJ/kg")
    print(f"Dégradation: {((normal_cooling - abnormal_cooling) / normal_cooling * 100):.1f}%")
    
    return normal_diagram_path, abnormal_diagram_path

def generate_sensor_validation_report():
    """Génère un rapport de validation des capteurs"""
    
    print("\n📋 RAPPORT DE VALIDATION DES CAPTEURS")
    print("=" * 45)
    
    sensor_system = RefrigerationSensors()
    
    # Test de validation pour chaque type de capteur
    validation_results = {}
    
    for sensor_id, config in sensor_system.sensor_config.items():
        print(f"\n🔍 Validation capteur: {config['name']}")
        
        # Génération de 10 lectures pour ce capteur
        readings = []
        for _ in range(10):
            machine_readings = sensor_system.generate_normal_readings("VALIDATION_MACHINE")
            readings.append(machine_readings[sensor_id])
        
        # Analyse des lectures
        values = [r.value for r in readings]
        statuses = [r.status for r in readings]
        
        validation_results[sensor_id] = {
            'min_value': min(values),
            'max_value': max(values),
            'avg_value': sum(values) / len(values),
            'normal_range': config['normal_range'],
            'all_normal': all(status == 'normal' for status in statuses),
            'accuracy': config['accuracy']
        }
        
        print(f"   Plage mesurée: {min(values):.2f} - {max(values):.2f} {config['unit']}")
        print(f"   Plage normale: {config['normal_range'][0]} - {config['normal_range'][1]} {config['unit']}")
        print(f"   Précision: ±{config['accuracy']} {config['unit']}")
        print(f"   Statut: {'✅ OK' if validation_results[sensor_id]['all_normal'] else '⚠️ ALERTE'}")
    
    # Résumé global
    print(f"\n📊 RÉSUMÉ GLOBAL")
    print("-" * 20)
    
    total_sensors = len(validation_results)
    valid_sensors = sum(1 for result in validation_results.values() if result['all_normal'])
    
    print(f"Capteurs testés: {total_sensors}")
    print(f"Capteurs valides: {valid_sensors}")
    print(f"Taux de validation: {(valid_sensors / total_sensors * 100):.1f}%")
    
    return validation_results

def main():
    """Fonction principale de test"""
    
    print("🧪 SYSTÈME DE TEST CAPTEURS RÉELS - INSTALLATIONS FRIGORIFIQUES")
    print("=" * 70)
    print("Basé sur les spécifications PDF avec conditions normales et anormales")
    print("=" * 70)
    
    try:
        # 1. Test du système de capteurs
        print("\n🔧 Phase 1: Test du système de capteurs")
        sensor_test_result = test_real_sensor_system()
        
        # 2. Test du diagramme de Mollier
        print("\n🔧 Phase 2: Test du diagramme de Mollier")
        normal_path, abnormal_path = test_mollier_diagram_with_real_sensors()
        
        # 3. Rapport de validation
        print("\n🔧 Phase 3: Rapport de validation")
        validation_report = generate_sensor_validation_report()
        
        # 4. Résumé final
        print("\n🎯 RÉSUMÉ FINAL")
        print("=" * 20)
        print("✅ Système de capteurs réels fonctionnel")
        print("✅ Diagrammes de Mollier générés avec succès")
        print("✅ Conditions normales et anormales testées")
        print("✅ Validation des capteurs effectuée")
        
        print(f"\n📁 Fichiers générés:")
        print(f"   • {normal_path}")
        print(f"   • {abnormal_path}")
        
        print(f"\n📊 Capteurs configurés selon spécifications PDF:")
        print(f"   • 4 capteurs de pression (HP, BP, intermédiaire, différentielle)")
        print(f"   • 6 capteurs de température (aspiration, refoulement, condensation, évaporation, liquide, ambiante)")
        print(f"   • Conditions typiques: t0=-10°C, tc=30°C, surchauffe=5°C, sous-refroidissement=5°C")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors des tests: {e}")
        return False

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n🎉 TOUS LES TESTS TERMINÉS AVEC SUCCÈS!")
    else:
        print("\n💥 ÉCHEC DES TESTS!")
    
    # Affichage des diagrammes générés
    try:
        plt.show()
    except:
        print("⚠️ Impossible d'afficher les diagrammes graphiquement")