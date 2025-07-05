import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from models.sensor_data import SensorData
from models.equipment import Equipment
from models.alert import Alert, db
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import os

class PredictiveModel:
    """Predictive maintenance model for refrigeration equipment"""
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = []
        self.model_path = 'models/predictive_model.pkl'
        self.scaler_path = 'models/predictive_scaler.pkl'
        
    def prepare_features(self, sensor_data):
        """Prepare features for machine learning model"""
        try:
            # Convert sensor data to DataFrame
            df = pd.DataFrame([{
                'timestamp': data.timestamp,
                'equipment_id': data.equipment_id,
                'sensor_type': data.sensor_type,
                'sensor_location': data.sensor_location,
                'value': data.value
            } for data in sensor_data])
            
            # Pivot table to get sensor readings as columns
            pivot_df = df.pivot_table(
                index=['timestamp', 'equipment_id'],
                columns=['sensor_type', 'sensor_location'],
                values='value',
                aggfunc='mean'
            )
            
            # Fill missing values
            pivot_df = pivot_df.fillna(method='ffill').fillna(method='bfill')
            
            # Add time-based features
            pivot_df['hour'] = pivot_df.index.get_level_values('timestamp').hour
            pivot_df['day_of_week'] = pivot_df.index.get_level_values('timestamp').dayofweek
            pivot_df['month'] = pivot_df.index.get_level_values('timestamp').month
            
            # Add rolling statistics
            for col in pivot_df.columns:
                if col not in ['hour', 'day_of_week', 'month']:
                    pivot_df[f'{col}_rolling_mean'] = pivot_df[col].rolling(window=5).mean()
                    pivot_df[f'{col}_rolling_std'] = pivot_df[col].rolling(window=5).std()
            
            # Drop NaN values
            pivot_df = pivot_df.dropna()
            
            return pivot_df
            
        except Exception as e:
            print(f"Error preparing features: {str(e)}")
            return None
    
    def create_failure_labels(self, equipment_id, sensor_data_df):
        """Create failure labels based on alert history"""
        try:
            # Get alert history
            alerts = Alert.query.filter(
                Alert.equipment_id == equipment_id,
                Alert.alert_type.in_(['anomaly', 'prediction'])
            ).all()
            
            if not alerts:
                # No alerts, assume all data is normal
                return np.zeros(len(sensor_data_df))
            
            # Create labels based on alert timestamps
            labels = []
            for timestamp in sensor_data_df.index.get_level_values('timestamp'):
                # Check if there's an alert within 24 hours of this timestamp
                failure_upcoming = False
                for alert in alerts:
                    time_diff = (alert.created_at - timestamp).total_seconds() / 3600
                    if 0 <= time_diff <= 24:  # Alert within next 24 hours
                        failure_upcoming = True
                        break
                
                labels.append(1 if failure_upcoming else 0)
            
            return np.array(labels)
            
        except Exception as e:
            print(f"Error creating failure labels: {str(e)}")
            return np.zeros(len(sensor_data_df))
    
    def train_model(self, equipment_id=None):
        """Train predictive model"""
        try:
            # Get training data
            query = SensorData.query
            if equipment_id:
                query = query.filter_by(equipment_id=equipment_id)
            
            # Get data from last 60 days for training
            start_date = datetime.utcnow() - timedelta(days=60)
            sensor_data = query.filter(SensorData.timestamp >= start_date).all()
            
            if len(sensor_data) < 1000:
                print("Not enough data for training")
                return False
            
            # Prepare features
            features_df = self.prepare_features(sensor_data)
            if features_df is None or features_df.empty:
                print("Failed to prepare features")
                return False
            
            # Create failure labels
            if equipment_id:
                labels = self.create_failure_labels(equipment_id, features_df)
            else:
                # For all equipment, use simplified labeling
                labels = np.random.choice([0, 1], size=len(features_df), p=[0.9, 0.1])
            
            # Prepare data for training
            X = features_df.values
            y = labels
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train model
            self.model = RandomForestRegressor(
                n_estimators=100,
                random_state=42,
                max_depth=10,
                min_samples_split=5
            )
            self.model.fit(X_train_scaled, y_train)
            
            # Evaluate model
            y_pred = self.model.predict(X_test_scaled)
            mse = mean_squared_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            print(f"Model performance - MSE: {mse:.4f}, R2: {r2:.4f}")
            
            # Save model
            self.feature_names = list(features_df.columns)
            os.makedirs('models', exist_ok=True)
            joblib.dump(self.model, self.model_path)
            joblib.dump(self.scaler, self.scaler_path)
            joblib.dump(self.feature_names, 'models/feature_names.pkl')
            
            print("Predictive model trained successfully")
            return True
            
        except Exception as e:
            print(f"Error training model: {str(e)}")
            return False
    
    def load_model(self):
        """Load trained model"""
        try:
            if (os.path.exists(self.model_path) and 
                os.path.exists(self.scaler_path) and 
                os.path.exists('models/feature_names.pkl')):
                
                self.model = joblib.load(self.model_path)
                self.scaler = joblib.load(self.scaler_path)
                self.feature_names = joblib.load('models/feature_names.pkl')
                return True
            return False
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            return False
    
    def predict_failures(self, equipment_id, days_ahead=7):
        """Predict failures for equipment"""
        try:
            # Load model if not already loaded
            if self.model is None:
                if not self.load_model():
                    # Train model if not available
                    if not self.train_model(equipment_id):
                        return None
            
            # Get recent sensor data
            start_date = datetime.utcnow() - timedelta(days=7)
            sensor_data = SensorData.query.filter(
                SensorData.equipment_id == equipment_id,
                SensorData.timestamp >= start_date
            ).all()
            
            if not sensor_data:
                return None
            
            # Prepare features
            features_df = self.prepare_features(sensor_data)
            if features_df is None or features_df.empty:
                return None
            
            # Get latest data point
            latest_features = features_df.iloc[-1:].values
            
            # Make prediction
            latest_scaled = self.scaler.transform(latest_features)
            failure_probability = self.model.predict(latest_scaled)[0]
            
            # Calculate predicted failure date
            if failure_probability > 0.5:
                # Estimate days until failure based on probability
                days_until_failure = int((1 - failure_probability) * days_ahead)
                predicted_failure_date = datetime.utcnow() + timedelta(days=days_until_failure)
            else:
                predicted_failure_date = None
            
            # Get feature importance
            feature_importance = []
            if hasattr(self.model, 'feature_importances_'):
                for i, importance in enumerate(self.model.feature_importances_):
                    if i < len(self.feature_names):
                        feature_importance.append({
                            'feature': self.feature_names[i],
                            'importance': float(importance)
                        })
            
            # Sort by importance
            feature_importance.sort(key=lambda x: x['importance'], reverse=True)
            
            return {
                'equipment_id': equipment_id,
                'failure_probability': float(failure_probability),
                'predicted_failure_date': predicted_failure_date.isoformat() if predicted_failure_date else None,
                'confidence_score': float(abs(failure_probability - 0.5) * 2),
                'risk_level': self._calculate_risk_level(failure_probability),
                'top_risk_factors': feature_importance[:5],
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            print(f"Error predicting failures: {str(e)}")
            return None
    
    def _calculate_risk_level(self, probability):
        """Calculate risk level based on failure probability"""
        if probability > 0.8:
            return 'critical'
        elif probability > 0.6:
            return 'high'
        elif probability > 0.4:
            return 'medium'
        else:
            return 'low'
    
    def create_prediction_alert(self, equipment_id, prediction):
        """Create prediction alert if risk is high"""
        try:
            if prediction['risk_level'] in ['high', 'critical']:
                alert = Alert(
                    equipment_id=equipment_id,
                    alert_type='prediction',
                    severity=prediction['risk_level'],
                    title=f'Failure prediction for equipment {equipment_id}',
                    description=f'Predicted failure probability: {prediction["failure_probability"]:.2f}',
                    predicted_failure_date=datetime.fromisoformat(prediction['predicted_failure_date']) if prediction['predicted_failure_date'] else None,
                    confidence_score=prediction['confidence_score']
                )
                
                db.session.add(alert)
                db.session.commit()
                
                print(f"Prediction alert created for equipment {equipment_id}")
                
        except Exception as e:
            print(f"Error creating prediction alert: {str(e)}")
    
    def get_model_performance(self):
        """Get model performance metrics"""
        try:
            if not os.path.exists('models/model_performance.pkl'):
                return None
            
            performance = joblib.load('models/model_performance.pkl')
            return performance
            
        except Exception as e:
            print(f"Error getting model performance: {str(e)}")
            return None
    
    def retrain_model_periodically(self):
        """Retrain model with new data"""
        try:
            # Check if model needs retraining (e.g., every 7 days)
            if os.path.exists(self.model_path):
                model_age = datetime.utcnow() - datetime.fromtimestamp(os.path.getmtime(self.model_path))
                if model_age.days < 7:
                    return False
            
            # Retrain model
            success = self.train_model()
            if success:
                print("Model retrained successfully")
            
            return success
            
        except Exception as e:
            print(f"Error retraining model: {str(e)}")
            return False
