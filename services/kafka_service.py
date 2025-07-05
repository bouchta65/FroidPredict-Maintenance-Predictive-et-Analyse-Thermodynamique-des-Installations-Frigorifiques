import os
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KafkaConfig:
    """Kafka configuration settings"""
    
    def __init__(self):
        self.bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
        self.sensor_data_topic = os.getenv('KAFKA_SENSOR_DATA_TOPIC', 'sensor_data')
        self.alert_topic = os.getenv('KAFKA_ALERT_TOPIC', 'alerts')
        self.maintenance_topic = os.getenv('KAFKA_MAINTENANCE_TOPIC', 'maintenance')
        
        # Consumer group IDs
        self.sensor_consumer_group = os.getenv('KAFKA_SENSOR_CONSUMER_GROUP', 'sensor_processors')
        self.alert_consumer_group = os.getenv('KAFKA_ALERT_CONSUMER_GROUP', 'alert_processors')
        
        # Producer settings
        self.producer_config = {
            'bootstrap_servers': self.bootstrap_servers,
            'value_serializer': lambda v: json.dumps(v, default=str).encode('utf-8'),
            'key_serializer': lambda k: str(k).encode('utf-8') if k else None,
            'acks': 'all',
            'retries': 3,
            'batch_size': 16384,
            'linger_ms': 10,
            'buffer_memory': 33554432
        }
        
        # Consumer settings
        self.consumer_config = {
            'bootstrap_servers': self.bootstrap_servers,
            'value_deserializer': lambda m: json.loads(m.decode('utf-8')),
            'key_deserializer': lambda k: k.decode('utf-8') if k else None,
            'auto_offset_reset': 'earliest',
            'enable_auto_commit': True,
            'auto_commit_interval_ms': 1000,
            'session_timeout_ms': 30000,
            'heartbeat_interval_ms': 10000
        }

class KafkaProducerService:
    """Kafka producer service for sending messages"""
    
    def __init__(self):
        self.config = KafkaConfig()
        self.producer = None
        self._initialize_producer()
    
    def _initialize_producer(self):
        """Initialize Kafka producer"""
        try:
            self.producer = KafkaProducer(**self.config.producer_config)
            logger.info("Kafka producer initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Kafka producer: {e}")
            self.producer = None
    
    def send_sensor_data(self, sensor_data):
        """Send sensor data to Kafka topic"""
        if not self.producer:
            logger.error("Kafka producer not initialized")
            return False
        
        try:
            # Prepare message
            message = {
                'timestamp': datetime.utcnow().isoformat(),
                'equipment_id': sensor_data.get('equipment_id'),
                'sensor_type': sensor_data.get('sensor_type'),
                'sensor_location': sensor_data.get('sensor_location'),
                'value': sensor_data.get('value'),
                'unit': sensor_data.get('unit'),
                'quality': sensor_data.get('quality', 'good')
            }
            
            # Send message
            future = self.producer.send(
                self.config.sensor_data_topic,
                key=str(sensor_data.get('equipment_id')),
                value=message
            )
            
            # Wait for confirmation
            result = future.get(timeout=10)
            logger.info(f"Sensor data sent successfully: {result}")
            return True
            
        except KafkaError as e:
            logger.error(f"Failed to send sensor data: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending sensor data: {e}")
            return False
    
    def send_alert(self, alert_data):
        """Send alert to Kafka topic"""
        if not self.producer:
            logger.error("Kafka producer not initialized")
            return False
        
        try:
            # Prepare message
            message = {
                'timestamp': datetime.utcnow().isoformat(),
                'alert_id': alert_data.get('alert_id'),
                'equipment_id': alert_data.get('equipment_id'),
                'alert_type': alert_data.get('alert_type'),
                'severity': alert_data.get('severity'),
                'title': alert_data.get('title'),
                'description': alert_data.get('description'),
                'confidence_score': alert_data.get('confidence_score'),
                'predicted_failure_date': alert_data.get('predicted_failure_date')
            }
            
            # Send message
            future = self.producer.send(
                self.config.alert_topic,
                key=str(alert_data.get('equipment_id')),
                value=message
            )
            
            # Wait for confirmation
            result = future.get(timeout=10)
            logger.info(f"Alert sent successfully: {result}")
            return True
            
        except KafkaError as e:
            logger.error(f"Failed to send alert: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending alert: {e}")
            return False
    
    def send_maintenance_request(self, maintenance_data):
        """Send maintenance request to Kafka topic"""
        if not self.producer:
            logger.error("Kafka producer not initialized")
            return False
        
        try:
            # Prepare message
            message = {
                'timestamp': datetime.utcnow().isoformat(),
                'equipment_id': maintenance_data.get('equipment_id'),
                'maintenance_type': maintenance_data.get('maintenance_type'),
                'priority': maintenance_data.get('priority'),
                'description': maintenance_data.get('description'),
                'scheduled_date': maintenance_data.get('scheduled_date'),
                'estimated_duration': maintenance_data.get('estimated_duration')
            }
            
            # Send message
            future = self.producer.send(
                self.config.maintenance_topic,
                key=str(maintenance_data.get('equipment_id')),
                value=message
            )
            
            # Wait for confirmation
            result = future.get(timeout=10)
            logger.info(f"Maintenance request sent successfully: {result}")
            return True
            
        except KafkaError as e:
            logger.error(f"Failed to send maintenance request: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending maintenance request: {e}")
            return False
    
    def close(self):
        """Close Kafka producer"""
        if self.producer:
            self.producer.close()
            logger.info("Kafka producer closed")

class KafkaConsumerService:
    """Kafka consumer service for processing messages"""
    
    def __init__(self):
        self.config = KafkaConfig()
        self.consumers = {}
        self.running = False
    
    def create_sensor_consumer(self, callback):
        """Create consumer for sensor data"""
        try:
            consumer = KafkaConsumer(
                self.config.sensor_data_topic,
                group_id=self.config.sensor_consumer_group,
                **self.config.consumer_config
            )
            
            self.consumers['sensor'] = {
                'consumer': consumer,
                'callback': callback
            }
            
            logger.info("Sensor data consumer created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create sensor consumer: {e}")
            return False
    
    def create_alert_consumer(self, callback):
        """Create consumer for alerts"""
        try:
            consumer = KafkaConsumer(
                self.config.alert_topic,
                group_id=self.config.alert_consumer_group,
                **self.config.consumer_config
            )
            
            self.consumers['alert'] = {
                'consumer': consumer,
                'callback': callback
            }
            
            logger.info("Alert consumer created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create alert consumer: {e}")
            return False
    
    def start_consuming(self):
        """Start consuming messages"""
        self.running = True
        logger.info("Starting Kafka consumers...")
        
        import threading
        
        for consumer_type, consumer_info in self.consumers.items():
            thread = threading.Thread(
                target=self._consume_messages,
                args=(consumer_type, consumer_info),
                daemon=True
            )
            thread.start()
            logger.info(f"Started {consumer_type} consumer thread")
    
    def _consume_messages(self, consumer_type, consumer_info):
        """Consume messages from Kafka topic"""
        consumer = consumer_info['consumer']
        callback = consumer_info['callback']
        
        logger.info(f"Starting to consume messages for {consumer_type}")
        
        try:
            while self.running:
                messages = consumer.poll(timeout_ms=1000)
                
                for topic_partition, records in messages.items():
                    for record in records:
                        try:
                            # Process message
                            callback(record.key, record.value)
                            
                        except Exception as e:
                            logger.error(f"Error processing {consumer_type} message: {e}")
                            
        except Exception as e:
            logger.error(f"Error in {consumer_type} consumer loop: {e}")
        finally:
            consumer.close()
            logger.info(f"{consumer_type} consumer stopped")
    
    def stop_consuming(self):
        """Stop consuming messages"""
        self.running = False
        logger.info("Stopping Kafka consumers...")
        
        for consumer_type, consumer_info in self.consumers.items():
            consumer_info['consumer'].close()
        
        self.consumers.clear()
        logger.info("All Kafka consumers stopped")
