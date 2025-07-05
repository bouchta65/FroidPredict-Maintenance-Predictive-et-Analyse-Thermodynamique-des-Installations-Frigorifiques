import logging
import json
from datetime import datetime
from services.kafka_service import KafkaConsumerService
from models.sensor_data import SensorData, db
from models.equipment import Equipment
from models.alert import Alert

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataProcessor:
    """Process incoming Kafka messages and store in database"""
    
    def __init__(self, app):
        self.app = app
        self.kafka_consumer = KafkaConsumerService()
        self.setup_consumers()
    
    def setup_consumers(self):
        """Setup Kafka consumers"""
        # Setup sensor data consumer
        self.kafka_consumer.create_sensor_consumer(self.process_sensor_data)
        
        # Setup alert consumer
        self.kafka_consumer.create_alert_consumer(self.process_alert_data)
    
    def process_sensor_data(self, key, value):
        """Process sensor data from Kafka"""
        try:
            logger.info(f"Processing sensor data: {key}")
            
            with self.app.app_context():
                # Check if equipment exists
                equipment = Equipment.query.get(value['equipment_id'])
                if not equipment:
                    logger.warning(f"Equipment {value['equipment_id']} not found, skipping sensor data")
                    return
                
                # Create sensor data entry
                sensor_data = SensorData(
                    equipment_id=value['equipment_id'],
                    sensor_type=value['sensor_type'],
                    sensor_location=value['sensor_location'],
                    value=float(value['value']),
                    unit=value['unit'],
                    timestamp=datetime.fromisoformat(value['timestamp'])
                )
                
                db.session.add(sensor_data)
                db.session.commit()
                
                logger.info(f"Stored sensor data: {sensor_data.id}")
                
                # Trigger additional processing if needed
                self.analyze_sensor_data(sensor_data)
                
        except Exception as e:
            logger.error(f"Error processing sensor data: {e}")
            if 'db' in locals():
                db.session.rollback()
    
    def process_alert_data(self, key, value):
        """Process alert data from Kafka"""
        try:
            logger.info(f"Processing alert data: {key}")
            
            with self.app.app_context():
                # Check if equipment exists
                equipment = Equipment.query.get(value['equipment_id'])
                if not equipment:
                    logger.warning(f"Equipment {value['equipment_id']} not found, skipping alert")
                    return
                
                # Create alert entry
                alert = Alert(
                    equipment_id=value['equipment_id'],
                    alert_type=value['alert_type'],
                    severity=value['severity'],
                    title=value['title'],
                    description=value['description'],
                    confidence_score=value.get('confidence_score'),
                    anomaly_score=value.get('anomaly_score'),
                    affected_parameters=value.get('affected_parameters'),
                    predicted_failure_date=datetime.fromisoformat(value['predicted_failure_date']) if value.get('predicted_failure_date') else None
                )
                
                db.session.add(alert)
                db.session.commit()
                
                logger.info(f"Stored alert: {alert.id}")
                
                # Trigger additional processing if needed
                self.handle_critical_alert(alert)
                
        except Exception as e:
            logger.error(f"Error processing alert data: {e}")
            if 'db' in locals():
                db.session.rollback()
    
    def analyze_sensor_data(self, sensor_data):
        """Analyze sensor data for patterns"""
        try:
            # Here you can add more sophisticated analysis
            # For example, check for trending patterns, compare with historical data, etc.
            
            # Simple threshold checking
            if sensor_data.sensor_type == 'temperature' and sensor_data.value > 80:
                logger.warning(f"High temperature detected: {sensor_data.value}°C")
            
            if sensor_data.sensor_type == 'pressure' and sensor_data.value > 25:
                logger.warning(f"High pressure detected: {sensor_data.value} bar")
            
            if sensor_data.sensor_type == 'vibration' and sensor_data.value > 10:
                logger.warning(f"High vibration detected: {sensor_data.value} mm/s")
            
        except Exception as e:
            logger.error(f"Error analyzing sensor data: {e}")
    
    def handle_critical_alert(self, alert):
        """Handle critical alerts"""
        try:
            if alert.severity == 'critical':
                logger.critical(f"CRITICAL ALERT: {alert.title} - Equipment {alert.equipment_id}")
                
                # Here you can add notification logic
                # For example, send email, SMS, or push notifications
                
                # You can also trigger automatic maintenance requests
                self.trigger_maintenance_request(alert)
                
        except Exception as e:
            logger.error(f"Error handling critical alert: {e}")
    
    def trigger_maintenance_request(self, alert):
        """Trigger maintenance request for critical alerts"""
        try:
            from services.kafka_service import KafkaProducerService
            
            producer = KafkaProducerService()
            
            maintenance_request = {
                'equipment_id': alert.equipment_id,
                'maintenance_type': 'emergency',
                'priority': 'high',
                'description': f"Emergency maintenance required due to critical alert: {alert.title}",
                'scheduled_date': (datetime.utcnow()).isoformat(),
                'estimated_duration': 4  # hours
            }
            
            producer.send_maintenance_request(maintenance_request)
            logger.info(f"Triggered maintenance request for equipment {alert.equipment_id}")
            
        except Exception as e:
            logger.error(f"Error triggering maintenance request: {e}")
    
    def start(self):
        """Start processing messages"""
        logger.info("Starting data processor...")
        self.kafka_consumer.start_consuming()
    
    def stop(self):
        """Stop processing messages"""
        logger.info("Stopping data processor...")
        self.kafka_consumer.stop_consuming()

class KafkaHealthChecker:
    """Check Kafka connection health"""
    
    def __init__(self):
        self.kafka_producer = None
        self.kafka_consumer = None
    
    def check_producer_health(self):
        """Check if Kafka producer is healthy"""
        try:
            from services.kafka_service import KafkaProducerService
            
            producer = KafkaProducerService()
            
            # Try to send a test message
            test_message = {
                'test': True,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # This will raise an exception if Kafka is not available
            result = producer.send_sensor_data(test_message)
            producer.close()
            
            return result
            
        except Exception as e:
            logger.error(f"Kafka producer health check failed: {e}")
            return False
    
    def check_consumer_health(self):
        """Check if Kafka consumer is healthy"""
        try:
            from services.kafka_service import KafkaConsumerService
            
            consumer_service = KafkaConsumerService()
            
            # Try to create a consumer
            def dummy_callback(key, value):
                pass
            
            result = consumer_service.create_sensor_consumer(dummy_callback)
            consumer_service.stop_consuming()
            
            return result
            
        except Exception as e:
            logger.error(f"Kafka consumer health check failed: {e}")
            return False
    
    def get_health_status(self):
        """Get overall Kafka health status"""
        producer_healthy = self.check_producer_health()
        consumer_healthy = self.check_consumer_health()
        
        return {
            'kafka_producer': producer_healthy,
            'kafka_consumer': consumer_healthy,
            'overall_healthy': producer_healthy and consumer_healthy,
            'timestamp': datetime.utcnow().isoformat()
        }
