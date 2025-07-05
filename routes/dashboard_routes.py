from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from models.sensor_data import SensorData, db
from models.equipment import Equipment
from models.alert import Alert
from services.thermodynamic_analyzer import ThermodynamicAnalyzer
from services.predictive_model import PredictiveModel
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/overview', methods=['GET'])
def get_overview():
    """Get dashboard overview statistics"""
    try:
        # Get counts
        total_equipment = Equipment.query.count()
        active_equipment = Equipment.query.filter_by(status='active').count()
        total_alerts = Alert.query.filter_by(status='active').count()
        critical_alerts = Alert.query.filter_by(status='active', severity='critical').count()
        
        # Get recent sensor data
        recent_data = SensorData.query.order_by(SensorData.timestamp.desc()).limit(10).all()
        
        # Get equipment by type
        equipment_types = db.session.query(
            Equipment.type,
            db.func.count(Equipment.id).label('count')
        ).group_by(Equipment.type).all()
        
        return jsonify({
            'total_equipment': total_equipment,
            'active_equipment': active_equipment,
            'total_alerts': total_alerts,
            'critical_alerts': critical_alerts,
            'recent_data': [data.to_dict() for data in recent_data],
            'equipment_by_type': {eq_type.type: eq_type.count for eq_type in equipment_types}
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/thermodynamic/<int:equipment_id>', methods=['GET'])
def get_thermodynamic_analysis(equipment_id):
    """Get thermodynamic analysis for equipment"""
    try:
        analyzer = ThermodynamicAnalyzer()
        analysis = analyzer.analyze_cycle(equipment_id)
        
        if not analysis:
            return jsonify({'error': 'No data available for analysis'}), 404
        
        return jsonify(analysis)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/mollier/<int:equipment_id>', methods=['GET'])
def get_mollier_diagram(equipment_id):
    """Generate Mollier diagram for equipment"""
    try:
        analyzer = ThermodynamicAnalyzer()
        diagram_data = analyzer.generate_mollier_diagram(equipment_id)
        
        if not diagram_data:
            return jsonify({'error': 'No data available for diagram'}), 404
        
        return jsonify(diagram_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/performance/<int:equipment_id>', methods=['GET'])
def get_performance_metrics(equipment_id):
    """Get performance metrics for equipment"""
    try:
        # Get time range from query parameters
        days = request.args.get('days', 7, type=int)
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get sensor data
        sensor_data = SensorData.query.filter(
            SensorData.equipment_id == equipment_id,
            SensorData.timestamp >= start_date
        ).order_by(SensorData.timestamp).all()
        
        if not sensor_data:
            return jsonify({'error': 'No data available'}), 404
        
        # Process data for visualization
        df = pd.DataFrame([{
            'timestamp': data.timestamp,
            'sensor_type': data.sensor_type,
            'sensor_location': data.sensor_location,
            'value': data.value,
            'unit': data.unit
        } for data in sensor_data])
        
        # Group by sensor type for plotting
        charts = {}
        for sensor_type in df['sensor_type'].unique():
            sensor_df = df[df['sensor_type'] == sensor_type]
            
            fig = px.line(
                sensor_df,
                x='timestamp',
                y='value',
                color='sensor_location',
                title=f'{sensor_type.title()} Over Time'
            )
            
            charts[sensor_type] = fig.to_dict()
        
        # Calculate performance metrics
        analyzer = ThermodynamicAnalyzer()
        metrics = analyzer.calculate_performance_metrics(equipment_id, days)
        
        return jsonify({
            'charts': charts,
            'metrics': metrics,
            'data_points': len(sensor_data)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/predictions/<int:equipment_id>', methods=['GET'])
def get_predictions(equipment_id):
    """Get failure predictions for equipment"""
    try:
        model = PredictiveModel()
        predictions = model.predict_failures(equipment_id)
        
        return jsonify(predictions)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/alerts/timeline', methods=['GET'])
def get_alerts_timeline():
    """Get alerts timeline"""
    try:
        # Get time range from query parameters
        days = request.args.get('days', 30, type=int)
        start_date = datetime.utcnow() - timedelta(days=days)
        
        alerts = Alert.query.filter(
            Alert.created_at >= start_date
        ).order_by(Alert.created_at).all()
        
        # Group alerts by date
        df = pd.DataFrame([{
            'date': alert.created_at.date(),
            'severity': alert.severity,
            'count': 1
        } for alert in alerts])
        
        if not df.empty:
            timeline = df.groupby(['date', 'severity']).count().reset_index()
            timeline['date'] = timeline['date'].astype(str)
            
            fig = px.bar(
                timeline,
                x='date',
                y='count',
                color='severity',
                title='Alerts Timeline'
            )
            
            return jsonify({
                'chart': fig.to_dict(),
                'total_alerts': len(alerts)
            })
        else:
            return jsonify({
                'chart': None,
                'total_alerts': 0
            })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/efficiency/<int:equipment_id>', methods=['GET'])
def get_efficiency_trends(equipment_id):
    """Get efficiency trends for equipment"""
    try:
        # Get time range from query parameters
        days = request.args.get('days', 30, type=int)
        start_date = datetime.utcnow() - timedelta(days=days)
        
        analyzer = ThermodynamicAnalyzer()
        efficiency_data = analyzer.calculate_efficiency_trends(equipment_id, start_date)
        
        return jsonify(efficiency_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
