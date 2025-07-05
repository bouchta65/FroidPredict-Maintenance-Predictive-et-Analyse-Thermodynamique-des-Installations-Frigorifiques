from flask import Blueprint, request, jsonify
from datetime import datetime
from models.equipment import Equipment, db

equipment_bp = Blueprint('equipment', __name__)

@equipment_bp.route('/', methods=['GET'])
def get_equipment():
    """Get all equipment with optional filtering"""
    equipment_type = request.args.get('type')
    status = request.args.get('status')
    
    query = Equipment.query
    
    if equipment_type:
        query = query.filter_by(type=equipment_type)
    if status:
        query = query.filter_by(status=status)
    
    equipment = query.order_by(Equipment.created_at.desc()).all()
    
    return jsonify([eq.to_dict() for eq in equipment])

@equipment_bp.route('/', methods=['POST'])
def create_equipment():
    """Create new equipment"""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['name', 'type']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    try:
        equipment = Equipment(
            name=data['name'],
            type=data['type'],
            model=data.get('model'),
            manufacturer=data.get('manufacturer'),
            location=data.get('location'),
            refrigerant_type=data.get('refrigerant_type'),
            nominal_capacity=data.get('nominal_capacity'),
            operating_pressure_low=data.get('operating_pressure_low'),
            operating_pressure_high=data.get('operating_pressure_high'),
            operating_temp_low=data.get('operating_temp_low'),
            operating_temp_high=data.get('operating_temp_high')
        )
        
        if 'installation_date' in data:
            equipment.installation_date = datetime.fromisoformat(data['installation_date']).date()
        
        db.session.add(equipment)
        db.session.commit()
        
        return jsonify(equipment.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@equipment_bp.route('/<int:equipment_id>', methods=['GET'])
def get_equipment_by_id(equipment_id):
    """Get specific equipment by ID"""
    equipment = Equipment.query.get_or_404(equipment_id)
    return jsonify(equipment.to_dict())

@equipment_bp.route('/<int:equipment_id>', methods=['PUT'])
def update_equipment(equipment_id):
    """Update equipment"""
    equipment = Equipment.query.get_or_404(equipment_id)
    data = request.get_json()
    
    try:
        # Update fields
        for field in ['name', 'type', 'model', 'manufacturer', 'location', 'status', 
                     'refrigerant_type', 'nominal_capacity', 'operating_pressure_low',
                     'operating_pressure_high', 'operating_temp_low', 'operating_temp_high']:
            if field in data:
                setattr(equipment, field, data[field])
        
        if 'installation_date' in data:
            equipment.installation_date = datetime.fromisoformat(data['installation_date']).date()
        
        equipment.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify(equipment.to_dict())
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@equipment_bp.route('/<int:equipment_id>', methods=['DELETE'])
def delete_equipment(equipment_id):
    """Delete equipment"""
    equipment = Equipment.query.get_or_404(equipment_id)
    
    try:
        db.session.delete(equipment)
        db.session.commit()
        return jsonify({'message': 'Equipment deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@equipment_bp.route('/<int:equipment_id>/maintenance', methods=['POST'])
def schedule_maintenance(equipment_id):
    """Schedule maintenance for equipment"""
    equipment = Equipment.query.get_or_404(equipment_id)
    data = request.get_json()
    
    try:
        if 'next_maintenance' in data:
            equipment.next_maintenance = datetime.fromisoformat(data['next_maintenance'])
        
        if 'last_maintenance' in data:
            equipment.last_maintenance = datetime.fromisoformat(data['last_maintenance'])
        
        equipment.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify(equipment.to_dict())
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
