import random
import time
from datetime import datetime, timedelta
from faker import Faker
import json
import logging
from services.kafka_service import KafkaProducerService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

fake = Faker()

class FakeDataGenerator:
    """Generate fake sensor data for refrigeration systems"""
    
    def __init__(self):
        self.kafka_producer = KafkaProducerService()
        self.equipment_types = ['compressor', 'condenser', 'evaporator', 'expansion_valve']
        self.sensor_types = ['temperature', 'pressure', 'flow', 'power', 'vibration', 'current']
        self.refrigerants = ['R-134a', 'R-404A', 'R-410A', 'R-507A', 'R-22']
        
        # Equipment configurations
        self.equipment_configs = {
            'compressor': {
                'temperature': {'min': -10, 'max': 80, 'unit': '°C'},
                'pressure': {'min': 2, 'max': 25, 'unit': 'bar'},
                'power': {'min': 5, 'max': 500, 'unit': 'kW'},
                'vibration': {'min': 0, 'max': 10, 'unit': 'mm/s'},
                'current': {'min': 10, 'max': 200, 'unit': 'A'}
            },
            'condenser': {
                'temperature': {'min': 30, 'max': 60, 'unit': '°C'},
                'pressure': {'min': 8, 'max': 25, 'unit': 'bar'},
                'flow': {'min': 100, 'max': 2000, 'unit': 'L/min'}
            },
            'evaporator': {
                'temperature': {'min': -25, 'max': 10, 'unit': '°C'},
                'pressure': {'min': 1, 'max': 8, 'unit': 'bar'},
                'flow': {'min': 50, 'max': 1000, 'unit': 'L/min'}
            },
            'expansion_valve': {
                'temperature': {'min': -20, 'max': 40, 'unit': '°C'},
                'pressure': {'min': 1, 'max': 20, 'unit': 'bar'},
                'flow': {'min': 10, 'max': 500, 'unit': 'L/min'}
            }
        }
        
        # Sensor locations for each equipment type
        self.sensor_locations = {
            'compressor': ['inlet', 'outlet', 'discharge', 'suction'],
            'condenser': ['inlet', 'outlet', 'fan_motor', 'coil'],
            'evaporator': ['inlet', 'outlet', 'fan_motor', 'coil'],
            'expansion_valve': ['upstream', 'downstream', 'body']
        }
        
        # Anomaly patterns
        self.anomaly_patterns = {
            'gradual_drift': lambda base_value: base_value * (1 + random.uniform(-0.1, 0.1)),
            'sudden_spike': lambda base_value: base_value * random.uniform(1.2, 2.0),
            'sudden_drop': lambda base_value: base_value * random.uniform(0.3, 0.8),
            'oscillation': lambda base_value: base_value * (1 + 0.2 * random.sin(time.time())),
            'noise': lambda base_value: base_value + random.normalvariate(0, base_value * 0.05)
        }
    
    def generate_equipment_data(self, num_equipment=5):
        """Generate fake equipment data"""
        equipment_data = []
        
        for i in range(1, num_equipment + 1):
            equipment_type = random.choice(self.equipment_types)
            
            equipment = {
                'id': i,
                'name': f"{equipment_type.title()} {i}",
                'type': equipment_type,
                'model': fake.bothify(text='??-####'),
                'manufacturer': fake.company(),
                'installation_date': fake.date_between(start_date='-5y', end_date='today'),
                'location': fake.city(),
                'status': random.choice(['active', 'maintenance', 'inactive']),
                'refrigerant_type': random.choice(self.refrigerants),
                'nominal_capacity': round(random.uniform(10, 500), 2),
                'operating_pressure_low': round(random.uniform(1, 8), 2),
                'operating_pressure_high': round(random.uniform(10, 25), 2),
                'operating_temp_low': round(random.uniform(-25, 5), 2),
                'operating_temp_high': round(random.uniform(40, 80), 2)
            }
            
            equipment_data.append(equipment)
        
        return equipment_data
    
    def generate_sensor_data(self, equipment_id, equipment_type, anomaly_chance=0.1):
        """Generate fake sensor data for equipment"""
        sensor_data = []
        
        if equipment_type not in self.equipment_configs:
            return sensor_data
        
        config = self.equipment_configs[equipment_type]
        locations = self.sensor_locations[equipment_type]
        
        for sensor_type, params in config.items():
            for location in locations:
                # Generate base value
                base_value = random.uniform(params['min'], params['max'])
                
                # Apply anomaly if chance hits
                if random.random() < anomaly_chance:
                    anomaly_type = random.choice(list(self.anomaly_patterns.keys()))
                    value = self.anomaly_patterns[anomaly_type](base_value)
                    quality = 'anomaly'
                else:
                    # Add normal variation
                    value = base_value + random.normalvariate(0, base_value * 0.02)
                    quality = 'good'
                
                # Ensure value is within reasonable bounds
                value = max(params['min'] * 0.8, min(params['max'] * 1.2, value))
                
                sensor_reading = {
                    'equipment_id': equipment_id,
                    'sensor_type': sensor_type,
                    'sensor_location': location,
                    'value': round(value, 2),
                    'unit': params['unit'],
                    'quality': quality,
                    'timestamp': datetime.utcnow().isoformat()
                }
                
                sensor_data.append(sensor_reading)
        
        return sensor_data
    
    def generate_alert_data(self, equipment_id, sensor_data):
        """Generate fake alert data based on sensor anomalies"""
        alerts = []
        
        # Check for anomalies in sensor data
        anomaly_sensors = [s for s in sensor_data if s['quality'] == 'anomaly']
        
        if anomaly_sensors:
            for sensor in anomaly_sensors:
                # Generate alert based on sensor type and value
                alert_type = self._determine_alert_type(sensor)
                severity = self._determine_severity(sensor)
                
                alert = {
                    'equipment_id': equipment_id,
                    'alert_type': alert_type,
                    'severity': severity,
                    'title': self._generate_alert_title(sensor, alert_type),
                    'description': self._generate_alert_description(sensor, alert_type),
                    'confidence_score': round(random.uniform(0.7, 0.95), 3),
                    'anomaly_score': round(random.uniform(0.6, 1.0), 3),
                    'affected_parameters': [f"{sensor['sensor_type']}_{sensor['sensor_location']}"],
                    'predicted_failure_date': (datetime.utcnow() + timedelta(days=random.randint(1, 30))).isoformat()
                }
                
                alerts.append(alert)
        
        return alerts
    
    def _determine_alert_type(self, sensor):
        """Determine alert type based on sensor data"""
        if sensor['sensor_type'] == 'temperature':
            return 'thermal_anomaly'
        elif sensor['sensor_type'] == 'pressure':
            return 'pressure_anomaly'
        elif sensor['sensor_type'] == 'vibration':
            return 'mechanical_anomaly'
        elif sensor['sensor_type'] == 'power':
            return 'electrical_anomaly'
        else:
            return 'anomaly'
    
    def _determine_severity(self, sensor):
        """Determine severity based on sensor anomaly"""
        if sensor['quality'] == 'anomaly':
            # Base severity on how far from normal the value is
            if sensor['sensor_type'] == 'temperature' and abs(sensor['value']) > 70:
                return 'critical'
            elif sensor['sensor_type'] == 'pressure' and sensor['value'] > 20:
                return 'high'
            elif sensor['sensor_type'] == 'vibration' and sensor['value'] > 8:
                return 'high'
            else:
                return random.choice(['medium', 'high'])
        return 'low'
    
    def _generate_alert_title(self, sensor, alert_type):
        """Generate alert title"""
        return f"{alert_type.replace('_', ' ').title()} - {sensor['sensor_type'].title()} {sensor['sensor_location'].title()}"
    
    def _generate_alert_description(self, sensor, alert_type):
        """Generate alert description"""
        return f"Anomalous {sensor['sensor_type']} reading of {sensor['value']} {sensor['unit']} detected at {sensor['sensor_location']} location. Immediate attention required."
    
    def generate_continuous_data(self, equipment_list, interval_seconds=10):
        """Generate continuous fake data and send to Kafka"""
        logger.info(f"Starting continuous data generation for {len(equipment_list)} equipment")
        
        while True:
            try:
                for equipment in equipment_list:
                    # Generate sensor data
                    sensor_data = self.generate_sensor_data(
                        equipment['id'],
                        equipment['type'],
                        anomaly_chance=0.05  # 5% chance of anomaly
                    )
                    
                    # Send sensor data to Kafka
                    for sensor in sensor_data:
                        self.kafka_producer.send_sensor_data(sensor)
                    
                    # Generate and send alerts if anomalies detected
                    alerts = self.generate_alert_data(equipment['id'], sensor_data)
                    for alert in alerts:
                        self.kafka_producer.send_alert(alert)
                    
                    logger.info(f"Generated {len(sensor_data)} sensor readings and {len(alerts)} alerts for equipment {equipment['id']}")
                
                # Wait before next iteration
                time.sleep(interval_seconds)
                
            except KeyboardInterrupt:
                logger.info("Stopping continuous data generation...")
                break
            except Exception as e:
                logger.error(f"Error in continuous data generation: {e}")
                time.sleep(interval_seconds)
    
    def generate_batch_data(self, equipment_list, num_batches=10):
        """Generate batch fake data and send to Kafka"""
        logger.info(f"Starting batch data generation: {num_batches} batches for {len(equipment_list)} equipment")
        
        for batch in range(num_batches):
            try:
                for equipment in equipment_list:
                    # Generate sensor data
                    sensor_data = self.generate_sensor_data(
                        equipment['id'],
                        equipment['type'],
                        anomaly_chance=0.1  # 10% chance of anomaly
                    )
                    
                    # Send sensor data to Kafka
                    for sensor in sensor_data:
                        self.kafka_producer.send_sensor_data(sensor)
                    
                    # Generate and send alerts if anomalies detected
                    alerts = self.generate_alert_data(equipment['id'], sensor_data)
                    for alert in alerts:
                        self.kafka_producer.send_alert(alert)
                
                logger.info(f"Completed batch {batch + 1}/{num_batches}")
                time.sleep(2)  # Short delay between batches
                
            except Exception as e:
                logger.error(f"Error in batch {batch + 1}: {e}")
        
        logger.info("Batch data generation completed")
    
    def close(self):
        """Close Kafka producer"""
        self.kafka_producer.close()

if __name__ == "__main__":
    # Example usage
    generator = FakeDataGenerator()
    
    # Generate equipment data
    equipment_list = generator.generate_equipment_data(5)
    
    print("Generated Equipment:")
    for eq in equipment_list:
        print(f"- {eq['name']} ({eq['type']})")
    
    # Generate batch data
    generator.generate_batch_data(equipment_list, num_batches=5)
    
    # Close resources
    generator.close()
    print("Data generation completed!")
