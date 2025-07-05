from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class SensorData(db.Model):
    __tablename__ = 'sensor_data'
    
    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=False)
    sensor_type = db.Column(db.String(50), nullable=False)  # temperature, pressure, flow, power
    sensor_location = db.Column(db.String(100), nullable=False)  # compressor_inlet, condenser_outlet, etc.
    value = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    equipment = db.relationship('Equipment', backref=db.backref('sensor_data', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'equipment_id': self.equipment_id,
            'sensor_type': self.sensor_type,
            'sensor_location': self.sensor_location,
            'value': self.value,
            'unit': self.unit,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }
    
    def __repr__(self):
        return f'<SensorData {self.sensor_type}: {self.value} {self.unit}>'
