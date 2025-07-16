"""
Système de capteurs réels pour installations frigorifiques
Basé sur les spécifications du PDF avec conditions normales et anormales
"""

import numpy as np
import random
from datetime import datetime
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

@dataclass
class SensorReading:
    """Lecture d'un capteur avec validation"""
    value: float
    timestamp: datetime
    sensor_id: str
    unit: str
    status: str = "normal"  # normal, warning, critical, error
    calibration_date: Optional[datetime] = None

class RefrigerationSensors:
    """Système de capteurs pour installations frigorifiques selon spécifications PDF"""
    
    def __init__(self):
        # Configuration des capteurs selon spécifications
        self.sensor_config = {
            # Capteurs de pression (4 capteurs minimum)
            "pressure_hp": {
                "name": "Pression haute (HP)",
                "location": "Après compresseur/condenseur",
                "unit": "bar",
                "normal_range": (8.0, 16.0),
                "warning_range": (16.0, 18.0),
                "critical_range": (18.0, 22.0),
                "accuracy": 0.1
            },
            "pressure_bp": {
                "name": "Pression basse (BP)",
                "location": "Avant compresseur/évaporateur",
                "unit": "bar",
                "normal_range": (1.5, 4.0),
                "warning_range": (1.0, 1.5),
                "critical_range": (0.5, 1.0),
                "accuracy": 0.05
            },
            "pressure_intermediate": {
                "name": "Pression intermédiaire",
                "location": "Sortie détendeur",
                "unit": "bar",
                "normal_range": (1.2, 3.8),
                "warning_range": (0.8, 1.2),
                "critical_range": (0.5, 0.8),
                "accuracy": 0.05
            },
            "pressure_differential": {
                "name": "Pression différentielle",
                "location": "Surveillance filtre déshydrateur",
                "unit": "bar",
                "normal_range": (0.0, 0.5),
                "warning_range": (0.5, 1.0),
                "critical_range": (1.0, 2.0),
                "accuracy": 0.02
            },
            
            # Capteurs de température (6-8 capteurs)
            "temp_aspiration": {
                "name": "Température d'aspiration",
                "location": "Entrée compresseur",
                "unit": "°C",
                "normal_range": (-5.0, 15.0),
                "warning_range": (15.0, 25.0),
                "critical_range": (25.0, 35.0),
                "accuracy": 0.5
            },
            "temp_refoulement": {
                "name": "Température de refoulement",
                "location": "Sortie compresseur",
                "unit": "°C",
                "normal_range": (40.0, 60.0),
                "warning_range": (60.0, 80.0),
                "critical_range": (80.0, 100.0),
                "accuracy": 0.5
            },
            "temp_condensation": {
                "name": "Température de condensation",
                "location": "Sortie condenseur",
                "unit": "°C",
                "normal_range": (25.0, 45.0),
                "warning_range": (45.0, 55.0),
                "critical_range": (55.0, 65.0),
                "accuracy": 0.5
            },
            "temp_evaporation": {
                "name": "Température d'évaporation",
                "location": "Sortie évaporateur",
                "unit": "°C",
                "normal_range": (-25.0, 0.0),
                "warning_range": (-30.0, -25.0),
                "critical_range": (-35.0, -30.0),
                "accuracy": 0.5
            },
            "temp_liquid": {
                "name": "Température du liquide",
                "location": "Avant détendeur",
                "unit": "°C",
                "normal_range": (20.0, 40.0),
                "warning_range": (15.0, 20.0),
                "critical_range": (10.0, 15.0),
                "accuracy": 0.5
            },
            "temp_ambient": {
                "name": "Température ambiante",
                "location": "Entrée/sortie condenseur",
                "unit": "°C",
                "normal_range": (15.0, 35.0),
                "warning_range": (35.0, 40.0),
                "critical_range": (40.0, 50.0),
                "accuracy": 0.5
            }
        }
        
        # Données typiques selon PDF
        self.typical_data = {
            "temp_evaporation": -10.0,  # t0
            "temp_condensation": 30.0,  # tc
            "superheat_functional": 5.0,  # Surchauffe fonctionnelle
            "superheat_aspiration": 10.0,  # Surchauffe ligne aspiration
            "temp_point_1": 5.0,  # Température aspiration
            "temp_point_3": 48.0,  # Température refoulement
            "subcooling": 5.0,  # Sous-refroidissement
            "enthalpy_h8": 395.69,  # Entrée évaporateur [kJ/kg]
            "enthalpy_h9": 404.45   # Sortie évaporateur [kJ/kg]
        }
        
        # Conditions anormales
        self.abnormal_conditions = {
            "sensor_failure": ["drift", "noise", "stuck", "disconnected"],
            "calibration_error": {"max_deviation": 5.0},
            "pressure_drops": {"max_acceptable": 0.5},
            "operational_issues": [
                "incomplete_evaporation",
                "inefficient_condensation", 
                "misadjusted_expansion_valve",
                "clogged_dehydrator_filter"
            ],
            "refrigerant_issues": [
                "mixed_refrigerants",
                "contamination",
                "water_presence",
                "oil_contamination"
            ]
        }

    def generate_normal_readings(self, machine_id: str) -> Dict[str, SensorReading]:
        """Génère des lectures normales de capteurs"""
        readings = {}
        timestamp = datetime.now()
        
        # Calculs basés sur données typiques du PDF
        t_evap = self.typical_data["temp_evaporation"]
        t_cond = self.typical_data["temp_condensation"]
        
        # Températures calculées
        temp_aspiration = t_evap + self.typical_data["superheat_aspiration"]
        temp_refoulement = self.typical_data["temp_point_3"]
        temp_liquid = t_cond - self.typical_data["subcooling"]
        
        # Pressions calculées (corrélations réalistes)
        pressure_bp = 0.5 * np.exp(0.05 * (t_evap + 20))  # Pression évaporation
        pressure_hp = 2.0 * np.exp(0.04 * (t_cond - 10))  # Pression condensation
        
        # Génération des lectures avec variation réaliste
        sensor_values = {
            "pressure_hp": pressure_hp + np.random.normal(0, 0.2),
            "pressure_bp": pressure_bp + np.random.normal(0, 0.05),
            "pressure_intermediate": pressure_bp + np.random.normal(0, 0.03),
            "pressure_differential": np.random.normal(0.2, 0.1),
            "temp_aspiration": temp_aspiration + np.random.normal(0, 1.0),
            "temp_refoulement": temp_refoulement + np.random.normal(0, 2.0),
            "temp_condensation": t_cond + np.random.normal(0, 1.5),
            "temp_evaporation": t_evap + np.random.normal(0, 1.0),
            "temp_liquid": temp_liquid + np.random.normal(0, 1.0),
            "temp_ambient": 25.0 + np.random.normal(0, 3.0)
        }
        
        # Création des objets SensorReading
        for sensor_id, value in sensor_values.items():
            config = self.sensor_config[sensor_id]
            
            # Validation des plages
            status = self._validate_reading(value, config)
            
            readings[sensor_id] = SensorReading(
                value=round(value, 2),
                timestamp=timestamp,
                sensor_id=sensor_id,
                unit=config["unit"],
                status=status,
                calibration_date=datetime.now()
            )
        
        return readings

    def generate_abnormal_readings(self, machine_id: str, condition_type: str) -> Dict[str, SensorReading]:
        """Génère des lectures anormales selon le type de condition"""
        readings = self.generate_normal_readings(machine_id)
        
        if condition_type == "sensor_failure":
            # Défaillance capteur - valeurs aberrantes
            failed_sensor = random.choice(list(readings.keys()))
            readings[failed_sensor].value = 999.9
            readings[failed_sensor].status = "error"
            
        elif condition_type == "calibration_error":
            # Erreur de calibration - déviation systématique
            for sensor_id, reading in readings.items():
                deviation = np.random.normal(0, 2.0)
                reading.value += deviation
                reading.status = self._validate_reading(reading.value, self.sensor_config[sensor_id])
                
        elif condition_type == "pressure_drop":
            # Chute de pression importante
            readings["pressure_differential"].value = 1.5
            readings["pressure_differential"].status = "critical"
            
        elif condition_type == "incomplete_evaporation":
            # Évaporation incomplète
            readings["temp_evaporation"].value = -5.0
            readings["temp_aspiration"].value = 0.0
            readings["pressure_bp"].value = 3.5
            
        elif condition_type == "inefficient_condensation":
            # Condensation inefficace
            readings["temp_condensation"].value = 55.0
            readings["temp_refoulement"].value = 85.0
            readings["pressure_hp"].value = 18.0
            
        elif condition_type == "misadjusted_expansion_valve":
            # Détendeur mal réglé
            readings["temp_aspiration"].value = 25.0  # Surchauffe excessive
            readings["temp_liquid"].value = 15.0
            
        elif condition_type == "clogged_filter":
            # Filtre déshydrateur obstrué
            readings["pressure_differential"].value = 2.0
            readings["pressure_intermediate"].value = 0.8
            
        # Mise à jour des statuts
        for reading in readings.values():
            if reading.status == "normal":
                reading.status = self._validate_reading(reading.value, self.sensor_config[reading.sensor_id])
        
        return readings

    def _validate_reading(self, value: float, config: Dict) -> str:
        """Valide une lecture de capteur selon les plages configurées"""
        normal_min, normal_max = config["normal_range"]
        warning_min, warning_max = config["warning_range"]
        critical_min, critical_max = config["critical_range"]
        
        if normal_min <= value <= normal_max:
            return "normal"
        elif warning_min <= value <= warning_max:
            return "warning"
        elif critical_min <= value <= critical_max:
            return "critical"
        else:
            return "error"

    def calculate_derived_parameters(self, readings: Dict[str, SensorReading]) -> Dict[str, float]:
        """Calcule les paramètres dérivés selon spécifications PDF"""
        
        # Extraction des valeurs
        temp_aspiration = readings["temp_aspiration"].value
        temp_refoulement = readings["temp_refoulement"].value
        temp_condensation = readings["temp_condensation"].value
        temp_evaporation = readings["temp_evaporation"].value
        temp_liquid = readings["temp_liquid"].value
        pressure_hp = readings["pressure_hp"].value
        pressure_bp = readings["pressure_bp"].value
        
        # Calculs selon PDF
        superheat_functional = temp_aspiration - temp_evaporation
        superheat_aspiration = temp_aspiration - temp_evaporation
        subcooling = temp_condensation - temp_liquid
        
        # Enthalpies approximatives (selon données PDF)
        h8 = 200 + 4.18 * temp_liquid  # Entrée évaporateur
        h9 = 250 + 2.1 * temp_aspiration  # Sortie évaporateur
        h1 = 250 + 2.1 * temp_aspiration  # Aspiration compresseur
        h2 = 280 + 1.8 * temp_refoulement  # Refoulement compresseur
        h3 = 200 + 4.18 * temp_condensation  # Sortie condenseur
        h4 = h3  # Sortie détendeur (détente isenthalpique)
        
        # Indicateurs de performance
        cooling_effect = h1 - h4  # Effet frigorifique
        compression_work = h2 - h1  # Travail de compression
        heat_rejected = h2 - h3  # Chaleur rejetée
        cop = cooling_effect / compression_work if compression_work > 0 else 0
        pressure_ratio = pressure_hp / pressure_bp if pressure_bp > 0 else 0
        
        return {
            "superheat_functional": round(superheat_functional, 2),
            "superheat_aspiration": round(superheat_aspiration, 2),
            "subcooling": round(subcooling, 2),
            "enthalpy_h8": round(h8, 2),
            "enthalpy_h9": round(h9, 2),
            "enthalpy_h1": round(h1, 2),
            "enthalpy_h2": round(h2, 2),
            "enthalpy_h3": round(h3, 2),
            "enthalpy_h4": round(h4, 2),
            "cooling_effect": round(cooling_effect, 2),
            "compression_work": round(compression_work, 2),
            "heat_rejected": round(heat_rejected, 2),
            "cop": round(cop, 3),
            "pressure_ratio": round(pressure_ratio, 2)
        }

    def get_sensor_summary(self) -> Dict:
        """Retourne un résumé des capteurs nécessaires"""
        return {
            "pressure_sensors": {
                "count": 4,
                "types": [
                    "Pression haute (HP) - Après compresseur/condenseur",
                    "Pression basse (BP) - Avant compresseur/évaporateur", 
                    "Pression intermédiaire - Sortie détendeur",
                    "Pression différentielle - Surveillance filtre déshydrateur"
                ]
            },
            "temperature_sensors": {
                "count": 6,
                "types": [
                    "Température d'aspiration - Entrée compresseur",
                    "Température de refoulement - Sortie compresseur",
                    "Température de condensation - Sortie condenseur",
                    "Température d'évaporation - Sortie évaporateur",
                    "Température du liquide - Avant détendeur",
                    "Température ambiante - Entrée/sortie condenseur"
                ]
            },
            "typical_operating_conditions": self.typical_data,
            "abnormal_conditions": self.abnormal_conditions
        }

# Exemple d'utilisation
if __name__ == "__main__":
    sensors = RefrigerationSensors()
    
    print("=== SYSTÈME DE CAPTEURS RÉELS ===")
    print(f"Capteurs configurés: {len(sensors.sensor_config)}")
    
    # Génération de lectures normales
    print("\n=== LECTURES NORMALES ===")
    normal_readings = sensors.generate_normal_readings("MACHINE_001")
    for sensor_id, reading in normal_readings.items():
        print(f"{sensors.sensor_config[sensor_id]['name']}: {reading.value} {reading.unit} ({reading.status})")
    
    # Calcul des paramètres dérivés
    print("\n=== PARAMÈTRES DÉRIVÉS ===")
    derived = sensors.calculate_derived_parameters(normal_readings)
    for param, value in derived.items():
        print(f"{param}: {value}")
    
    # Génération de lectures anormales
    print("\n=== LECTURES ANORMALES (Condensation inefficace) ===")
    abnormal_readings = sensors.generate_abnormal_readings("MACHINE_001", "inefficient_condensation")
    for sensor_id, reading in abnormal_readings.items():
        if reading.status != "normal":
            print(f"{sensors.sensor_config[sensor_id]['name']}: {reading.value} {reading.unit} ({reading.status})")