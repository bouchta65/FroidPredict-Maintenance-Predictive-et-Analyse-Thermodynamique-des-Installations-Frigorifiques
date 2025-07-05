from flask import Blueprint, request, jsonify
from services.kafka_service import KafkaProducerService
from services.fake_data_generator import FakeDataGenerator
from services.data_processor import KafkaHealthChecker
import threading
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

kafka_bp = Blueprint('kafka', __name__)

# Global variables for data generation
data_generator = None
generation_thread = None
is_generating = False

@kafka_bp.route('/health', methods=['GET'])
def kafka_health():
    """Check Kafka health status"""
    try:
        health_checker = KafkaHealthChecker()
        health_status = health_checker.get_health_status()
        
        return jsonify(health_status), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@kafka_bp.route('/send/sensor', methods=['POST'])
def send_sensor_data():
    """Send sensor data to Kafka"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['equipment_id', 'sensor_type', 'sensor_location', 'value', 'unit']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Send to Kafka
        producer = KafkaProducerService()
        success = producer.send_sensor_data(data)
        producer.close()
        
        if success:
            return jsonify({'message': 'Sensor data sent successfully'}), 200
        else:
            return jsonify({'error': 'Failed to send sensor data'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@kafka_bp.route('/send/alert', methods=['POST'])
def send_alert():
    """Send alert to Kafka"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['equipment_id', 'alert_type', 'severity', 'title']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Send to Kafka
        producer = KafkaProducerService()
        success = producer.send_alert(data)
        producer.close()
        
        if success:
            return jsonify({'message': 'Alert sent successfully'}), 200
        else:
            return jsonify({'error': 'Failed to send alert'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@kafka_bp.route('/send/maintenance', methods=['POST'])
def send_maintenance_request():
    """Send maintenance request to Kafka"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['equipment_id', 'maintenance_type', 'priority']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Send to Kafka
        producer = KafkaProducerService()
        success = producer.send_maintenance_request(data)
        producer.close()
        
        if success:
            return jsonify({'message': 'Maintenance request sent successfully'}), 200
        else:
            return jsonify({'error': 'Failed to send maintenance request'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@kafka_bp.route('/generate/equipment', methods=['POST'])
def generate_fake_equipment():
    """Generate fake equipment data"""
    try:
        data = request.get_json() or {}
        num_equipment = data.get('num_equipment', 5)
        
        generator = FakeDataGenerator()
        equipment_list = generator.generate_equipment_data(num_equipment)
        generator.close()
        
        return jsonify({
            'message': f'Generated {len(equipment_list)} equipment',
            'equipment': equipment_list
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@kafka_bp.route('/generate/sensor-data', methods=['POST'])
def generate_fake_sensor_data():
    """Generate fake sensor data"""
    try:
        data = request.get_json() or {}
        equipment_id = data.get('equipment_id', 1)
        equipment_type = data.get('equipment_type', 'compressor')
        anomaly_chance = data.get('anomaly_chance', 0.1)
        
        generator = FakeDataGenerator()
        sensor_data = generator.generate_sensor_data(equipment_id, equipment_type, anomaly_chance)
        
        # Send to Kafka
        for sensor in sensor_data:
            generator.kafka_producer.send_sensor_data(sensor)
        
        generator.close()
        
        return jsonify({
            'message': f'Generated and sent {len(sensor_data)} sensor readings',
            'sensor_data': sensor_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@kafka_bp.route('/generate/batch', methods=['POST'])
def generate_batch_data():
    """Generate batch fake data"""
    try:
        data = request.get_json() or {}
        num_equipment = data.get('num_equipment', 5)
        num_batches = data.get('num_batches', 10)
        
        generator = FakeDataGenerator()
        
        # Generate equipment first
        equipment_list = generator.generate_equipment_data(num_equipment)
        
        # Generate batch data
        generator.generate_batch_data(equipment_list, num_batches)
        generator.close()
        
        return jsonify({
            'message': f'Generated {num_batches} batches of data for {num_equipment} equipment',
            'equipment_count': len(equipment_list),
            'batches': num_batches
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@kafka_bp.route('/generate/start', methods=['POST'])
def start_continuous_generation():
    """Start continuous fake data generation"""
    global data_generator, generation_thread, is_generating
    
    try:
        if is_generating:
            return jsonify({'message': 'Data generation already running'}), 200
        
        data = request.get_json() or {}
        num_equipment = data.get('num_equipment', 5)
        interval_seconds = data.get('interval_seconds', 10)
        
        # Create data generator
        data_generator = FakeDataGenerator()
        equipment_list = data_generator.generate_equipment_data(num_equipment)
        
        # Start generation in a separate thread
        def generate_data():
            global is_generating
            is_generating = True
            try:
                data_generator.generate_continuous_data(equipment_list, interval_seconds)
            except Exception as e:
                logger.error(f"Error in continuous data generation: {e}")
            finally:
                is_generating = False
        
        generation_thread = threading.Thread(target=generate_data, daemon=True)
        generation_thread.start()
        
        return jsonify({
            'message': 'Started continuous data generation',
            'equipment_count': len(equipment_list),
            'interval_seconds': interval_seconds
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@kafka_bp.route('/generate/stop', methods=['POST'])
def stop_continuous_generation():
    """Stop continuous fake data generation"""
    global data_generator, generation_thread, is_generating
    
    try:
        if not is_generating:
            return jsonify({'message': 'No data generation running'}), 200
        
        # Stop generation
        is_generating = False
        
        if data_generator:
            data_generator.close()
            data_generator = None
        
        return jsonify({'message': 'Stopped continuous data generation'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@kafka_bp.route('/generate/status', methods=['GET'])
def generation_status():
    """Get data generation status"""
    try:
        return jsonify({
            'is_generating': is_generating,
            'has_generator': data_generator is not None,
            'thread_alive': generation_thread.is_alive() if generation_thread else False
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@kafka_bp.route('/topics', methods=['GET'])
def get_kafka_topics():
    """Get Kafka topics information"""
    try:
        from services.kafka_service import KafkaConfig
        
        config = KafkaConfig()
        
        topics = {
            'sensor_data_topic': config.sensor_data_topic,
            'alert_topic': config.alert_topic,
            'maintenance_topic': config.maintenance_topic,
            'bootstrap_servers': config.bootstrap_servers
        }
        
        return jsonify(topics), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@kafka_bp.route('/config', methods=['GET'])
def get_kafka_config():
    """Get Kafka configuration"""
    try:
        from services.kafka_service import KafkaConfig
        
        config = KafkaConfig()
        
        config_info = {
            'bootstrap_servers': config.bootstrap_servers,
            'topics': {
                'sensor_data': config.sensor_data_topic,
                'alerts': config.alert_topic,
                'maintenance': config.maintenance_topic
            },
            'consumer_groups': {
                'sensor_processors': config.sensor_consumer_group,
                'alert_processors': config.alert_consumer_group
            }
        }
        
        return jsonify(config_info), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
