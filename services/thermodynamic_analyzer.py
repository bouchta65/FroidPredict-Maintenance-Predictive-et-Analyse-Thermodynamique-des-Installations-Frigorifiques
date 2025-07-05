import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from models.sensor_data import SensorData
from models.equipment import Equipment
import plotly.graph_objects as go

class ThermodynamicAnalyzer:
    """Thermodynamic analysis service for refrigeration cycles"""
    
    def __init__(self):
        self.R_values = {
            'R-134a': {'R': 0.08149, 'Tc': 101.06, 'Pc': 40.59},
            'R-404A': {'R': 0.09779, 'Tc': 72.1, 'Pc': 37.35},
            'R-410A': {'R': 0.1173, 'Tc': 71.34, 'Pc': 49.00},
            'R-22': {'R': 0.09615, 'Tc': 96.15, 'Pc': 49.90}
        }
    
    def analyze_cycle(self, equipment_id):
        """Analyze refrigeration cycle for equipment"""
        try:
            # Get latest sensor data
            equipment = Equipment.query.get(equipment_id)
            if not equipment:
                return None
            
            # Get recent sensor data (last hour)
            start_time = datetime.utcnow() - timedelta(hours=1)
            sensor_data = SensorData.query.filter(
                SensorData.equipment_id == equipment_id,
                SensorData.timestamp >= start_time
            ).all()
            
            if not sensor_data:
                return None
            
            # Organize data by sensor type and location
            data_dict = {}
            for data in sensor_data:
                key = f"{data.sensor_type}_{data.sensor_location}"
                if key not in data_dict:
                    data_dict[key] = []
                data_dict[key].append(data.value)
            
            # Calculate averages
            avg_data = {key: np.mean(values) for key, values in data_dict.items()}
            
            # Extract key points
            cycle_points = self._extract_cycle_points(avg_data)
            
            if not cycle_points:
                return None
            
            # Calculate cycle parameters
            analysis = {
                'equipment_id': equipment_id,
                'equipment_name': equipment.name,
                'refrigerant': equipment.refrigerant_type or 'R-134a',
                'timestamp': datetime.utcnow().isoformat(),
                'cycle_points': cycle_points,
                'performance_metrics': self._calculate_performance_metrics(cycle_points, equipment.refrigerant_type or 'R-134a'),
                'efficiency_analysis': self._analyze_efficiency(cycle_points),
                'recommendations': self._generate_recommendations(cycle_points)
            }
            
            return analysis
            
        except Exception as e:
            print(f"Error analyzing cycle: {str(e)}")
            return None
    
    def _extract_cycle_points(self, data):
        """Extract key cycle points from sensor data"""
        try:
            points = {}
            
            # Extract temperatures
            if 'temperature_compressor_inlet' in data:
                points['T1'] = data['temperature_compressor_inlet']
            if 'temperature_compressor_outlet' in data:
                points['T2'] = data['temperature_compressor_outlet']
            if 'temperature_condenser_outlet' in data:
                points['T3'] = data['temperature_condenser_outlet']
            if 'temperature_evaporator_inlet' in data:
                points['T4'] = data['temperature_evaporator_inlet']
            
            # Extract pressures
            if 'pressure_high_side' in data:
                points['P_high'] = data['pressure_high_side']
            if 'pressure_low_side' in data:
                points['P_low'] = data['pressure_low_side']
            
            # Extract power
            if 'power_compressor' in data:
                points['W_comp'] = data['power_compressor']
            
            # Extract flow rates
            if 'flow_refrigerant' in data:
                points['m_dot'] = data['flow_refrigerant']
            
            return points if len(points) >= 4 else None
            
        except Exception as e:
            print(f"Error extracting cycle points: {str(e)}")
            return None
    
    def _calculate_performance_metrics(self, points, refrigerant):
        """Calculate performance metrics"""
        try:
            metrics = {}
            
            # Calculate COP (Coefficient of Performance)
            if 'T1' in points and 'T2' in points and 'T3' in points and 'T4' in points:
                T_evap = points['T1'] + 273.15  # Convert to Kelvin
                T_cond = points['T2'] + 273.15
                
                # Ideal COP (Carnot)
                cop_carnot = T_evap / (T_cond - T_evap)
                metrics['cop_carnot'] = cop_carnot
                
                # Actual COP (if power available)
                if 'W_comp' in points and 'm_dot' in points:
                    # Simplified calculation
                    Q_evap = points['m_dot'] * 250  # Simplified enthalpy difference
                    cop_actual = Q_evap / points['W_comp']
                    metrics['cop_actual'] = cop_actual
                    metrics['cop_efficiency'] = cop_actual / cop_carnot
            
            # Calculate pressure ratio
            if 'P_high' in points and 'P_low' in points:
                metrics['pressure_ratio'] = points['P_high'] / points['P_low']
            
            # Calculate temperature difference
            if 'T2' in points and 'T1' in points:
                metrics['compression_temp_rise'] = points['T2'] - points['T1']
            
            # Calculate subcooling
            if 'T3' in points and 'P_high' in points:
                # Simplified subcooling calculation
                T_sat_cond = self._calculate_saturation_temp(points['P_high'], refrigerant)
                if T_sat_cond:
                    metrics['subcooling'] = T_sat_cond - points['T3']
            
            # Calculate superheat
            if 'T1' in points and 'P_low' in points:
                # Simplified superheat calculation
                T_sat_evap = self._calculate_saturation_temp(points['P_low'], refrigerant)
                if T_sat_evap:
                    metrics['superheat'] = points['T1'] - T_sat_evap
            
            return metrics
            
        except Exception as e:
            print(f"Error calculating performance metrics: {str(e)}")
            return {}
    
    def _calculate_saturation_temp(self, pressure, refrigerant):
        """Calculate saturation temperature (simplified)"""
        try:
            if refrigerant not in self.R_values:
                return None
            
            # Simplified Antoine equation approximation
            # This is a very simplified calculation - in practice, you'd use proper refrigerant properties
            if refrigerant == 'R-134a':
                # Simplified correlation for R-134a
                return 50 * np.log(pressure) - 200
            
            return None
            
        except Exception as e:
            print(f"Error calculating saturation temperature: {str(e)}")
            return None
    
    def _analyze_efficiency(self, points):
        """Analyze system efficiency"""
        try:
            analysis = {}
            
            # Temperature efficiency
            if 'T1' in points and 'T2' in points and 'T3' in points and 'T4' in points:
                # Check for proper temperature progression
                if points['T2'] > points['T1'] and points['T3'] > points['T4']:
                    analysis['temperature_progression'] = 'normal'
                else:
                    analysis['temperature_progression'] = 'abnormal'
            
            # Pressure efficiency
            if 'P_high' in points and 'P_low' in points:
                pressure_ratio = points['P_high'] / points['P_low']
                if 2 < pressure_ratio < 10:
                    analysis['pressure_ratio_status'] = 'normal'
                elif pressure_ratio >= 10:
                    analysis['pressure_ratio_status'] = 'high'
                else:
                    analysis['pressure_ratio_status'] = 'low'
            
            return analysis
            
        except Exception as e:
            print(f"Error analyzing efficiency: {str(e)}")
            return {}
    
    def _generate_recommendations(self, points):
        """Generate maintenance recommendations"""
        try:
            recommendations = []
            
            # Check pressure ratio
            if 'P_high' in points and 'P_low' in points:
                pressure_ratio = points['P_high'] / points['P_low']
                if pressure_ratio > 8:
                    recommendations.append({
                        'type': 'maintenance',
                        'priority': 'high',
                        'message': 'High pressure ratio detected. Check for condenser fouling or refrigerant overcharge.'
                    })
            
            # Check temperature differences
            if 'T2' in points and 'T1' in points:
                temp_rise = points['T2'] - points['T1']
                if temp_rise > 60:
                    recommendations.append({
                        'type': 'maintenance',
                        'priority': 'medium',
                        'message': 'High compression temperature rise. Check compressor efficiency.'
                    })
            
            # Check subcooling
            if 'subcooling' in points and points['subcooling'] < 5:
                recommendations.append({
                    'type': 'maintenance',
                    'priority': 'medium',
                    'message': 'Low subcooling detected. Check refrigerant charge level.'
                })
            
            return recommendations
            
        except Exception as e:
            print(f"Error generating recommendations: {str(e)}")
            return []
    
    def generate_mollier_diagram(self, equipment_id):
        """Generate Mollier diagram data"""
        try:
            analysis = self.analyze_cycle(equipment_id)
            if not analysis:
                return None
            
            points = analysis['cycle_points']
            
            # Create simplified Mollier diagram data
            # In practice, you'd use proper refrigerant property libraries
            diagram_data = {
                'cycle_points': [],
                'isotherms': [],
                'isobars': [],
                'title': f'Mollier Diagram - {analysis["equipment_name"]}'
            }
            
            # Add cycle points
            if 'T1' in points and 'P_low' in points:
                diagram_data['cycle_points'].append({
                    'name': 'Point 1 (Evaporator Outlet)',
                    'x': self._calculate_enthalpy(points['T1'], points['P_low']),
                    'y': self._calculate_entropy(points['T1'], points['P_low']),
                    'temp': points['T1'],
                    'pressure': points['P_low']
                })
            
            return diagram_data
            
        except Exception as e:
            print(f"Error generating Mollier diagram: {str(e)}")
            return None
    
    def _calculate_enthalpy(self, temp, pressure):
        """Calculate enthalpy (simplified)"""
        # This is a very simplified calculation
        # In practice, you'd use proper refrigerant property libraries
        return temp * 4.18 + pressure * 0.1
    
    def _calculate_entropy(self, temp, pressure):
        """Calculate entropy (simplified)"""
        # This is a very simplified calculation
        # In practice, you'd use proper refrigerant property libraries
        return 4.18 * np.log((temp + 273.15) / 273.15) - 0.287 * np.log(pressure / 101.325)
    
    def calculate_performance_metrics(self, equipment_id, days=7):
        """Calculate performance metrics over time"""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            sensor_data = SensorData.query.filter(
                SensorData.equipment_id == equipment_id,
                SensorData.timestamp >= start_date
            ).order_by(SensorData.timestamp).all()
            
            if not sensor_data:
                return {}
            
            # Group data by time periods
            df = pd.DataFrame([{
                'timestamp': data.timestamp,
                'sensor_type': data.sensor_type,
                'value': data.value
            } for data in sensor_data])
            
            # Calculate daily averages
            daily_metrics = {}
            for sensor_type in df['sensor_type'].unique():
                sensor_df = df[df['sensor_type'] == sensor_type]
                daily_avg = sensor_df.groupby(sensor_df['timestamp'].dt.date)['value'].mean()
                daily_metrics[sensor_type] = daily_avg.to_dict()
            
            return daily_metrics
            
        except Exception as e:
            print(f"Error calculating performance metrics: {str(e)}")
            return {}
    
    def calculate_efficiency_trends(self, equipment_id, start_date):
        """Calculate efficiency trends over time"""
        try:
            sensor_data = SensorData.query.filter(
                SensorData.equipment_id == equipment_id,
                SensorData.timestamp >= start_date
            ).order_by(SensorData.timestamp).all()
            
            if not sensor_data:
                return {}
            
            # Calculate daily efficiency metrics
            efficiency_trends = {
                'dates': [],
                'cop_values': [],
                'power_consumption': [],
                'temperature_efficiency': []
            }
            
            # Group by day and calculate metrics
            df = pd.DataFrame([{
                'date': data.timestamp.date(),
                'sensor_type': data.sensor_type,
                'sensor_location': data.sensor_location,
                'value': data.value
            } for data in sensor_data])
            
            for date in df['date'].unique():
                daily_data = df[df['date'] == date]
                
                # Calculate daily metrics (simplified)
                efficiency_trends['dates'].append(date.isoformat())
                efficiency_trends['cop_values'].append(np.random.uniform(2.5, 4.0))  # Placeholder
                efficiency_trends['power_consumption'].append(np.random.uniform(10, 25))  # Placeholder
                efficiency_trends['temperature_efficiency'].append(np.random.uniform(0.7, 0.9))  # Placeholder
            
            return efficiency_trends
            
        except Exception as e:
            print(f"Error calculating efficiency trends: {str(e)}")
            return {}
