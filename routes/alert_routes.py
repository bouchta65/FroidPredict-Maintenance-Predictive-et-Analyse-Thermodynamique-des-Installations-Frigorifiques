from flask import Blueprint, request, jsonify
from datetime import datetime
from models.alert import Alert, db
from models.equipment import Equipment

alert_bp = Blueprint('alert', __name__)

@alert_bp.route('/', methods=['GET'])
def get_alerts():
    """Get all alerts with optional filtering"""
    equipment_id = request.args.get('equipment_id')
    alert_type = request.args.get('alert_type')
    severity = request.args.get('severity')
    status = request.args.get('status')
    limit = request.args.get('limit', 100, type=int)
    
    query = Alert.query
    
    if equipment_id:
        query = query.filter_by(equipment_id=equipment_id)
    if alert_type:
        query = query.filter_by(alert_type=alert_type)
    if severity:
        query = query.filter_by(severity=severity)
    if status:
        query = query.filter_by(status=status)
    
    alerts = query.order_by(Alert.created_at.desc()).limit(limit).all()
    
    return jsonify([alert.to_dict() for alert in alerts])

@alert_bp.route('/', methods=['POST'])
def create_alert():
    """Create new alert"""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['equipment_id', 'alert_type', 'severity', 'title']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Check if equipment exists
    equipment = Equipment.query.get(data['equipment_id'])
    if not equipment:
        return jsonify({'error': 'Equipment not found'}), 404
    
    try:
        alert = Alert(
            equipment_id=data['equipment_id'],
            alert_type=data['alert_type'],
            severity=data['severity'],
            title=data['title'],
            description=data.get('description'),
            confidence_score=data.get('confidence_score'),
            anomaly_score=data.get('anomaly_score'),
            affected_parameters=data.get('affected_parameters')
        )
        
        if 'predicted_failure_date' in data:
            alert.predicted_failure_date = datetime.fromisoformat(data['predicted_failure_date'])
        
        db.session.add(alert)
        db.session.commit()
        
        return jsonify(alert.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@alert_bp.route('/<int:alert_id>', methods=['GET'])
def get_alert(alert_id):
    """Get specific alert by ID"""
    alert = Alert.query.get_or_404(alert_id)
    return jsonify(alert.to_dict())

@alert_bp.route('/<int:alert_id>/acknowledge', methods=['POST'])
def acknowledge_alert(alert_id):
    """Acknowledge an alert"""
    alert = Alert.query.get_or_404(alert_id)
    
    try:
        alert.status = 'acknowledged'
        alert.acknowledged_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify(alert.to_dict())
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@alert_bp.route('/<int:alert_id>/resolve', methods=['POST'])
def resolve_alert(alert_id):
    """Resolve an alert"""
    alert = Alert.query.get_or_404(alert_id)
    
    try:
        alert.status = 'resolved'
        alert.resolved_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify(alert.to_dict())
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@alert_bp.route('/<int:alert_id>', methods=['DELETE'])
def delete_alert(alert_id):
    """Delete alert"""
    alert = Alert.query.get_or_404(alert_id)
    
    try:
        db.session.delete(alert)
        db.session.commit()
        return jsonify({'message': 'Alert deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@alert_bp.route('/active', methods=['GET'])
def get_active_alerts():
    """Get all active alerts"""
    alerts = Alert.query.filter_by(status='active').order_by(Alert.created_at.desc()).all()
    return jsonify([alert.to_dict() for alert in alerts])

@alert_bp.route('/statistics', methods=['GET'])
def get_alert_statistics():
    """Get alert statistics"""
    from sqlalchemy import func
    
    stats = db.session.query(
        Alert.severity,
        func.count(Alert.id).label('count')
    ).group_by(Alert.severity).all()
    
    result = {
        'total_alerts': Alert.query.count(),
        'active_alerts': Alert.query.filter_by(status='active').count(),
        'by_severity': {stat.severity: stat.count for stat in stats}
    }
    
    return jsonify(result)
