from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Equipment(db.Model):
    __tablename__ = 'equipment'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # compressor, condenser, evaporator, expansion_valve
    model = db.Column(db.String(100))
    manufacturer = db.Column(db.String(100))
    installation_date = db.Column(db.Date)
    location = db.Column(db.String(200))
    status = db.Column(db.String(20), default='active')  # active, maintenance, inactive
    last_maintenance = db.Column(db.DateTime)
    next_maintenance = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Refrigeration specific attributes
    refrigerant_type = db.Column(db.String(20))  # R-134a, R-404A, etc.
    nominal_capacity = db.Column(db.Float)  # kW
    operating_pressure_low = db.Column(db.Float)  # bar
    operating_pressure_high = db.Column(db.Float)  # bar
    operating_temp_low = db.Column(db.Float)  # °C
    operating_temp_high = db.Column(db.Float)  # °C
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'model': self.model,
            'manufacturer': self.manufacturer,
            'installation_date': self.installation_date.isoformat() if self.installation_date else None,
            'location': self.location,
            'status': self.status,
            'last_maintenance': self.last_maintenance.isoformat() if self.last_maintenance else None,
            'next_maintenance': self.next_maintenance.isoformat() if self.next_maintenance else None,
            'refrigerant_type': self.refrigerant_type,
            'nominal_capacity': self.nominal_capacity,
            'operating_pressure_low': self.operating_pressure_low,
            'operating_pressure_high': self.operating_pressure_high,
            'operating_temp_low': self.operating_temp_low,
            'operating_temp_high': self.operating_temp_high,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Equipment {self.name} ({self.type})>'
