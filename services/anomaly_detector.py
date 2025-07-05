import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from models.sensor_data import SensorData
from models.equipment import Equipment
from models.alert import Alert, db
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib
import os

class AnomalyDetector:
    """Anomaly detection service for refrigeration equipment"""
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.model_path = 'models/anomaly_detector.pkl'
        self.scaler_path = 'models/scaler.pkl'
        
    def train_model(self, equipment_id=None):
        """Train anomaly detection model"""
        try:
            # Get training data
            query = SensorData.query
            if equipment_id:
                query = query.filter_by(equipment_id=equipment_id)
            
            # Get data from last 30 days for training
            start_date = datetime.utcnow() - timedelta(days=30)
            sensor_data = query.filter(SensorData.timestamp >= start_date).all()
            
            if len(sensor_data) < 100:
                print("Not enough data for training")
                return False
            
            # Prepare features
            features = []
            for data in sensor_data:
                features.append([
                    data.value,
                    data.equipment_id,
                    hash(data.sensor_type) % 1000,
                    hash(data.sensor_location) % 1000
                ])
            
            X = np.array(features)
            X_scaled = self.scaler.fit_transform(X)
            
            # Train isolation forest
            self.model = IsolationForest(
                contamination=0.1,
                random_state=42,
                n_estimators=100
            )
            self.model.fit(X_scaled)
            
            # Save model
            os.makedirs('models', exist_ok=True)
            joblib.dump(self.model, self.model_path)
            joblib.dump(self.scaler, self.scaler_path)
            
            print("Anomaly detection model trained successfully")
            return True
            
        except Exception as e:
            print(f"Error training model: {str(e)}")
            return False
    
    def load_model(self):
        """Load trained model"""
        try:
            if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
                self.model = joblib.load(self.model_path)
                self.scaler = joblib.load(self.scaler_path)
                return True
            return False
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            return False
    
    def detect_anomaly(self, sensor_data):
        """Detect anomaly in sensor data"""
        try:
            # Load model if not already loaded
            if self.model is None:
                if not self.load_model():
                    # Train model if not available
                    if not self.train_model(sensor_data.equipment_id):
                        return None
            
            # Prepare features
            features = np.array([[
                sensor_data.value,
                sensor_data.equipment_id,
                hash(sensor_data.sensor_type) % 1000,
                hash(sensor_data.sensor_location) % 1000
            ]])
            
            features_scaled = self.scaler.transform(features)
            
            # Predict anomaly
            prediction = self.model.predict(features_scaled)[0]
            anomaly_score = self.model.decision_function(features_scaled)[0]
            
            # -1 indicates anomaly, 1 indicates normal
            is_anomaly = prediction == -1
            
            return {
                'is_anomaly': is_anomaly,
                'anomaly_score': float(anomaly_score),
                'severity': self._calculate_severity(anomaly_score)
            }
            
        except Exception as e:
            print(f"Error detecting anomaly: {str(e)}")
            return None
    
    def _calculate_severity(self, anomaly_score):
        """Calculate severity based on anomaly score"""
        if anomaly_score < -0.5:
            return 'critical'
        elif anomaly_score < -0.3:
            return 'high'
        elif anomaly_score < -0.1:
            return 'medium'
        else:
            return 'low'
    
    def check_for_anomalies(self, sensor_data):
        """Check for anomalies and create alerts if needed"""
        try:
            result = self.detect_anomaly(sensor_data)
            
            if result and result['is_anomaly']:
                # Create alert
                alert = Alert(
                    equipment_id=sensor_data.equipment_id,
                    alert_type='anomaly',
                    severity=result['severity'],
                    title=f'Anomaly detected in {sensor_data.sensor_type}',
                    description=f'Anomalous reading detected for {sensor_data.sensor_type} '
                               f'at {sensor_data.sensor_location}. Value: {sensor_data.value} {sensor_data.unit}',
                    anomaly_score=result['anomaly_score'],
                    affected_parameters=[{
                        'sensor_type': sensor_data.sensor_type,
                        'sensor_location': sensor_data.sensor_location,
                        'value': sensor_data.value,
                        'unit': sensor_data.unit
                    }]
                )
                
                db.session.add(alert)
                db.session.commit()
                
                print(f"Anomaly alert created for equipment {sensor_data.equipment_id}")
                
        except Exception as e:
            print(f"Error checking for anomalies: {str(e)}")
    
    def get_anomaly_history(self, equipment_id, days=30):
        """Get anomaly history for equipment"""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            alerts = Alert.query.filter(
                Alert.equipment_id == equipment_id,
                Alert.alert_type == 'anomaly',
                Alert.created_at >= start_date
            ).order_by(Alert.created_at.desc()).all()
            
            return [alert.to_dict() for alert in alerts]
            
        except Exception as e:
            print(f"Error getting anomaly history: {str(e)}")
            return []
