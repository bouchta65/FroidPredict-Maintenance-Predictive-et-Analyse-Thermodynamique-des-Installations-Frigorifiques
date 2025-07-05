import random
import time
from datetime import datetime, timedelta
from models.sensor_data import SensorData, db
from models.equipment import Equipment
from models.alert import Alert
import requests
import numpy as np

class DataSimulator:
    """Simulate sensor data for testing and demonstration"""
    
    def __init__(self):
        self.api_base_url = "http://localhost:5000/api"
        self.equipment_configs = {
            'compressor': {
                'temperature_compressor_inlet': {'min': -10, 'max': 5, 'unit': '°C'},
                'temperature_compressor_outlet': {'min': 60, 'max': 90, 'unit': '°C'},
                'pressure_low_side': {'min': 1.5, 'max': 3.0, 'unit': 'bar'},
                'pressure_high_side': {'min': 12, 'max': 18, 'unit': 'bar'},
                'power_compressor': {'min': 10, 'max': 25, 'unit': 'kW'},
                'vibration_compressor': {'min': 0.5, 'max': 2.0, 'unit': 'mm/s'}
            },
            'condenser': {
                'temperature_condenser_inlet': {'min': 60, 'max': 90, 'unit': '°C'},
                'temperature_condenser_outlet': {'min': 35, 'max': 45, 'unit': '°C'},
                'pressure_condenser': {'min': 12, 'max': 18, 'unit': 'bar'},
                'flow_cooling_water': {'min': 50, 'max': 100, 'unit': 'L/min'},
                'temperature_cooling_water_inlet': {'min': 20, 'max': 30, 'unit': '°C'},
                'temperature_cooling_water_outlet': {'min': 35, 'max': 45, 'unit': '°C'}
            },
            'evaporator': {
                'temperature_evaporator_inlet': {'min': 35, 'max': 45, 'unit': '°C'},
                'temperature_evaporator_outlet': {'min': -10, 'max': 5, 'unit': '°C'},
                'pressure_evaporator': {'min': 1.5, 'max': 3.0, 'unit': 'bar'},
                'flow_chilled_water': {'min': 80, 'max': 120, 'unit': 'L/min'},
                'temperature_chilled_water_inlet': {'min': 12, 'max': 18, 'unit': '°C'},
                'temperature_chilled_water_outlet': {'min': 5, 'max': 8, 'unit': '°C'}
            }
        }
    
    def create_sample_equipment(self):
        """Create sample equipment for testing"""
        try:
            equipment_data = [
                {
                    'name': 'Compressor Unit 1',
                    'type': 'compressor',
                    'model': 'COMP-500',
                    'manufacturer': 'FrigoCorp',
                    'location': 'Plant A - Zone 1',
                    'refrigerant_type': 'R-134a',
                    'nominal_capacity': 500,
                    'operating_pressure_low': 2.5,
                    'operating_pressure_high': 15.0,
                    'operating_temp_low': -5,
                    'operating_temp_high': 80
                },
                {
                    'name': 'Condenser Unit 1',
                    'type': 'condenser',
                    'model': 'COND-300',
                    'manufacturer': 'CoolTech',
                    'location': 'Plant A - Zone 2',
                    'refrigerant_type': 'R-134a',
                    'nominal_capacity': 300,
                    'operating_pressure_low': 12.0,
                    'operating_pressure_high': 18.0,
                    'operating_temp_low': 30,
                    'operating_temp_high': 50
                },
                {
                    'name': 'Evaporator Unit 1',
                    'type': 'evaporator',
                    'model': 'EVAP-400',
                    'manufacturer': 'ChillMax',
                    'location': 'Plant A - Zone 3',
                    'refrigerant_type': 'R-134a',
                    'nominal_capacity': 400,
                    'operating_pressure_low': 1.5,
                    'operating_pressure_high': 3.0,
                    'operating_temp_low': -10,
                    'operating_temp_high': 50
                }
            ]
            
            created_equipment = []
            for eq_data in equipment_data:
                equipment = Equipment(**eq_data)
                db.session.add(equipment)
                db.session.commit()
                created_equipment.append(equipment)
                print(f"Created equipment: {equipment.name}")
            
            return created_equipment
            
        except Exception as e:
            print(f"Error creating sample equipment: {str(e)}")
            db.session.rollback()
            return []
    
    def generate_sensor_reading(self, equipment_type, sensor_config, anomaly_factor=1.0):
        """Generate a single sensor reading"""
        try:
            base_value = random.uniform(sensor_config['min'], sensor_config['max'])
            
            # Add some noise
            noise = random.uniform(-0.1, 0.1) * base_value
            
            # Apply anomaly factor
            if anomaly_factor > 1.0:
                # Introduce anomaly
                anomaly_value = base_value * anomaly_factor
                # Ensure it's still within reasonable bounds
                max_anomaly = sensor_config['max'] * 1.5
                value = min(anomaly_value, max_anomaly)
            else:
                value = base_value + noise
            
            return round(value, 2)
            
        except Exception as e:
            print(f"Error generating sensor reading: {str(e)}")
            return 0.0
    
    def simulate_real_time_data(self, equipment_id, duration_minutes=60, interval_seconds=30):
        """Simulate real-time sensor data"""
        try:
            equipment = Equipment.query.get(equipment_id)
            if not equipment:
                print(f"Equipment {equipment_id} not found")
                return
            
            if equipment.type not in self.equipment_configs:
                print(f"No configuration for equipment type: {equipment.type}")
                return
            
            config = self.equipment_configs[equipment.type]
            end_time = datetime.utcnow() + timedelta(minutes=duration_minutes)
            
            print(f"Starting real-time simulation for {equipment.name}")
            print(f"Duration: {duration_minutes} minutes, Interval: {interval_seconds} seconds")
            
            while datetime.utcnow() < end_time:
                # Randomly introduce anomalies (5% chance)
                anomaly_factor = random.uniform(1.2, 1.8) if random.random() < 0.05 else 1.0
                
                sensor_readings = []
                for sensor_location, sensor_config in config.items():
                    sensor_type = sensor_location.split('_')[0]  # Extract sensor type
                    
                    value = self.generate_sensor_reading(
                        equipment.type,
                        sensor_config,
                        anomaly_factor
                    )
                    
                    sensor_data = SensorData(
                        equipment_id=equipment_id,
                        sensor_type=sensor_type,
                        sensor_location=sensor_location,
                        value=value,
                        unit=sensor_config['unit'],
                        timestamp=datetime.utcnow()
                    )
                    
                    sensor_readings.append(sensor_data)
                
                # Batch insert
                db.session.add_all(sensor_readings)
                db.session.commit()
                
                print(f"Generated {len(sensor_readings)} sensor readings for {equipment.name}")
                time.sleep(interval_seconds)
            
            print(f"Simulation completed for {equipment.name}")
            
        except Exception as e:
            print(f"Error simulating real-time data: {str(e)}")
            db.session.rollback()
    
    def simulate_historical_data(self, equipment_id, days=30):
        """Simulate historical sensor data"""
        try:
            equipment = Equipment.query.get(equipment_id)
            if not equipment:
                print(f"Equipment {equipment_id} not found")
                return
            
            if equipment.type not in self.equipment_configs:
                print(f"No configuration for equipment type: {equipment.type}")
                return
            
            config = self.equipment_configs[equipment.type]
            start_date = datetime.utcnow() - timedelta(days=days)
            
            print(f"Generating historical data for {equipment.name}")
            print(f"Period: {days} days")
            
            # Generate data every 5 minutes
            current_time = start_date
            end_time = datetime.utcnow()
            
            batch_size = 100
            sensor_readings = []
            
            while current_time < end_time:
                # Introduce anomalies occasionally
                anomaly_factor = 1.0
                if random.random() < 0.02:  # 2% chance
                    anomaly_factor = random.uniform(1.2, 1.5)
                
                for sensor_location, sensor_config in config.items():
                    sensor_type = sensor_location.split('_')[0]
                    
                    value = self.generate_sensor_reading(
                        equipment.type,
                        sensor_config,
                        anomaly_factor
                    )
                    
                    sensor_data = SensorData(
                        equipment_id=equipment_id,
                        sensor_type=sensor_type,
                        sensor_location=sensor_location,
                        value=value,
                        unit=sensor_config['unit'],
                        timestamp=current_time
                    )
                    
                    sensor_readings.append(sensor_data)
                
                # Batch insert
                if len(sensor_readings) >= batch_size:
                    db.session.add_all(sensor_readings)
                    db.session.commit()
                    print(f"Inserted {len(sensor_readings)} records")
                    sensor_readings = []
                
                current_time += timedelta(minutes=5)
            
            # Insert remaining records
            if sensor_readings:
                db.session.add_all(sensor_readings)
                db.session.commit()
                print(f"Inserted final {len(sensor_readings)} records")
            
            print(f"Historical data generation completed for {equipment.name}")
            
        except Exception as e:
            print(f"Error simulating historical data: {str(e)}")
            db.session.rollback()
    
    def simulate_failure_scenario(self, equipment_id, failure_type='gradual'):
        """Simulate a failure scenario"""
        try:
            equipment = Equipment.query.get(equipment_id)
            if not equipment:
                print(f"Equipment {equipment_id} not found")
                return
            
            print(f"Simulating {failure_type} failure for {equipment.name}")
            
            if failure_type == 'gradual':
                # Gradual degradation over 24 hours
                for hour in range(24):
                    degradation_factor = 1.0 + (hour * 0.05)  # 5% degradation per hour
                    
                    self._generate_degraded_readings(equipment_id, degradation_factor)
                    time.sleep(1)  # 1 second per hour for demo
                    
            elif failure_type == 'sudden':
                # Sudden failure after 2 hours
                for hour in range(2):
                    self._generate_normal_readings(equipment_id)
                    time.sleep(1)
                
                # Sudden failure
                self._generate_failure_readings(equipment_id)
                
            print(f"Failure simulation completed for {equipment.name}")
            
        except Exception as e:
            print(f"Error simulating failure scenario: {str(e)}")
    
    def _generate_degraded_readings(self, equipment_id, degradation_factor):
        """Generate degraded sensor readings"""
        equipment = Equipment.query.get(equipment_id)
        config = self.equipment_configs[equipment.type]
        
        sensor_readings = []
        for sensor_location, sensor_config in config.items():
            sensor_type = sensor_location.split('_')[0]
            
            value = self.generate_sensor_reading(
                equipment.type,
                sensor_config,
                degradation_factor
            )
            
            sensor_data = SensorData(
                equipment_id=equipment_id,
                sensor_type=sensor_type,
                sensor_location=sensor_location,
                value=value,
                unit=sensor_config['unit'],
                timestamp=datetime.utcnow()
            )
            
            sensor_readings.append(sensor_data)
        
        db.session.add_all(sensor_readings)
        db.session.commit()
    
    def _generate_normal_readings(self, equipment_id):
        """Generate normal sensor readings"""
        self._generate_degraded_readings(equipment_id, 1.0)
    
    def _generate_failure_readings(self, equipment_id):
        """Generate failure sensor readings"""
        self._generate_degraded_readings(equipment_id, 2.0)
    
    def run_continuous_simulation(self, equipment_ids, interval_minutes=5):
        """Run continuous simulation for multiple equipment"""
        try:
            print(f"Starting continuous simulation for equipment: {equipment_ids}")
            print(f"Interval: {interval_minutes} minutes")
            
            while True:
                for equipment_id in equipment_ids:
                    self._generate_normal_readings(equipment_id)
                    
                    # Randomly introduce anomalies
                    if random.random() < 0.1:  # 10% chance
                        print(f"Introducing anomaly for equipment {equipment_id}")
                        self._generate_degraded_readings(equipment_id, random.uniform(1.3, 1.8))
                
                time.sleep(interval_minutes * 60)
                
        except KeyboardInterrupt:
            print("Simulation stopped by user")
        except Exception as e:
            print(f"Error in continuous simulation: {str(e)}")
    
    def generate_sample_alerts(self):
        """Generate sample alerts for testing"""
        try:
            equipment_list = Equipment.query.all()
            
            for equipment in equipment_list:
                # Generate random alerts
                for _ in range(random.randint(1, 3)):
                    alert_types = ['anomaly', 'prediction', 'maintenance']
                    severities = ['low', 'medium', 'high', 'critical']
                    
                    alert = Alert(
                        equipment_id=equipment.id,
                        alert_type=random.choice(alert_types),
                        severity=random.choice(severities),
                        title=f'Sample alert for {equipment.name}',
                        description=f'This is a sample alert for testing purposes.',
                        created_at=datetime.utcnow() - timedelta(days=random.randint(0, 7)),
                        confidence_score=random.uniform(0.5, 0.95),
                        anomaly_score=random.uniform(-0.8, 0.2)
                    )
                    
                    db.session.add(alert)
            
            db.session.commit()
            print("Sample alerts generated successfully")
            
        except Exception as e:
            print(f"Error generating sample alerts: {str(e)}")
            db.session.rollback()
