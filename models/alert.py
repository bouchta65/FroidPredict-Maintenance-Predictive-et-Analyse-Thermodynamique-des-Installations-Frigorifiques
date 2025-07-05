from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Alert(db.Model):
    __tablename__ = 'alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=False)
    alert_type = db.Column(db.String(50), nullable=False)  # anomaly, prediction, maintenance
    severity = db.Column(db.String(20), nullable=False)  # low, medium, high, critical
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='active')  # active, acknowledged, resolved
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    acknowledged_at = db.Column(db.DateTime)
    resolved_at = db.Column(db.DateTime)
    
    # Prediction specific fields
    predicted_failure_date = db.Column(db.DateTime)
    confidence_score = db.Column(db.Float)  # 0-1 confidence in prediction
    
    # Anomaly specific fields
    anomaly_score = db.Column(db.Float)
    affected_parameters = db.Column(db.JSON)  # List of affected sensor parameters
    
    # Relationships
    equipment = db.relationship('Equipment', backref=db.backref('alerts', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'equipment_id': self.equipment_id,
            'alert_type': self.alert_type,
            'severity': self.severity,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'acknowledged_at': self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'predicted_failure_date': self.predicted_failure_date.isoformat() if self.predicted_failure_date else None,
            'confidence_score': self.confidence_score,
            'anomaly_score': self.anomaly_score,
            'affected_parameters': self.affected_parameters
        }
    
    def __repr__(self):
        return f'<Alert {self.title} ({self.severity})>'
