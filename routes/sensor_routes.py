from flask import Blueprint, request, jsonify
from datetime import datetime
from models.sensor_data import SensorData, db
from models.equipment import Equipment
from services.anomaly_detector import AnomalyDetector
from services.thermodynamic_analyzer import ThermodynamicAnalyzer

sensor_bp = Blueprint('sensor', __name__)

@sensor_bp.route('/', methods=['GET'])
def get_sensors():
    """Get all sensor data with optional filtering"""
    equipment_id = request.args.get('equipment_id')
    sensor_type = request.args.get('sensor_type')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    limit = request.args.get('limit', 100, type=int)
    
    query = SensorData.query
    
    if equipment_id:
        query = query.filter_by(equipment_id=equipment_id)
    if sensor_type:
        query = query.filter_by(sensor_type=sensor_type)
    if start_date:
        start_dt = datetime.fromisoformat(start_date)
        query = query.filter(SensorData.timestamp >= start_dt)
    if end_date:
        end_dt = datetime.fromisoformat(end_date)
        query = query.filter(SensorData.timestamp <= end_dt)
    
    sensors = query.order_by(SensorData.timestamp.desc()).limit(limit).all()
    
    return jsonify([sensor.to_dict() for sensor in sensors])

@sensor_bp.route('/', methods=['POST'])
def create_sensor_data():
    """Create new sensor data entry"""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['equipment_id', 'sensor_type', 'sensor_location', 'value', 'unit']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Check if equipment exists
    equipment = Equipment.query.get(data['equipment_id'])
    if not equipment:
        return jsonify({'error': 'Equipment not found'}), 404
    
    try:
        sensor_data = SensorData(
            equipment_id=data['equipment_id'],
            sensor_type=data['sensor_type'],
            sensor_location=data['sensor_location'],
            value=float(data['value']),
            unit=data['unit'],
            timestamp=datetime.fromisoformat(data['timestamp']) if 'timestamp' in data else datetime.utcnow()
        )
        
        db.session.add(sensor_data)
        db.session.commit()
        
        # Trigger anomaly detection
        anomaly_detector = AnomalyDetector()
        anomaly_detector.check_for_anomalies(sensor_data)
        
        # Trigger thermodynamic analysis
        thermo_analyzer = ThermodynamicAnalyzer()
        thermo_analyzer.analyze_cycle(data['equipment_id'])
        
        return jsonify(sensor_data.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@sensor_bp.route('/bulk', methods=['POST'])
def create_bulk_sensor_data():
    """Create multiple sensor data entries"""
    data = request.get_json()
    
    if not isinstance(data, list):
        return jsonify({'error': 'Expected array of sensor data'}), 400
    
    try:
        sensor_entries = []
        for entry in data:
            # Validate required fields
            required_fields = ['equipment_id', 'sensor_type', 'sensor_location', 'value', 'unit']
            for field in required_fields:
                if field not in entry:
                    return jsonify({'error': f'Missing required field: {field}'}), 400
            
            sensor_data = SensorData(
                equipment_id=entry['equipment_id'],
                sensor_type=entry['sensor_type'],
                sensor_location=entry['sensor_location'],
                value=float(entry['value']),
                unit=entry['unit'],
                timestamp=datetime.fromisoformat(entry['timestamp']) if 'timestamp' in entry else datetime.utcnow()
            )
            sensor_entries.append(sensor_data)
        
        db.session.add_all(sensor_entries)
        db.session.commit()
        
        return jsonify({'message': f'Successfully created {len(sensor_entries)} sensor data entries'}), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@sensor_bp.route('/<int:sensor_id>', methods=['GET'])
def get_sensor(sensor_id):
    """Get specific sensor data by ID"""
    sensor = SensorData.query.get_or_404(sensor_id)
    return jsonify(sensor.to_dict())

@sensor_bp.route('/<int:sensor_id>', methods=['DELETE'])
def delete_sensor(sensor_id):
    """Delete sensor data by ID"""
    sensor = SensorData.query.get_or_404(sensor_id)
    
    try:
        db.session.delete(sensor)
        db.session.commit()
        return jsonify({'message': 'Sensor data deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@sensor_bp.route('/latest/<int:equipment_id>', methods=['GET'])
def get_latest_sensors(equipment_id):
    """Get latest sensor readings for an equipment"""
    sensors = SensorData.query.filter_by(equipment_id=equipment_id)\
        .order_by(SensorData.timestamp.desc())\
        .limit(10).all()
    
    return jsonify([sensor.to_dict() for sensor in sensors])

@sensor_bp.route('/statistics/<int:equipment_id>', methods=['GET'])
def get_sensor_statistics(equipment_id):
    """Get sensor statistics for an equipment"""
    from sqlalchemy import func
    
    stats = db.session.query(
        SensorData.sensor_type,
        func.avg(SensorData.value).label('avg_value'),
        func.min(SensorData.value).label('min_value'),
        func.max(SensorData.value).label('max_value'),
        func.count(SensorData.id).label('count')
    ).filter_by(equipment_id=equipment_id)\
     .group_by(SensorData.sensor_type)\
     .all()
    
    result = []
    for stat in stats:
        result.append({
            'sensor_type': stat.sensor_type,
            'avg_value': float(stat.avg_value) if stat.avg_value else 0,
            'min_value': float(stat.min_value) if stat.min_value else 0,
            'max_value': float(stat.max_value) if stat.max_value else 0,
            'count': stat.count
        })
    
    return jsonify(result)
