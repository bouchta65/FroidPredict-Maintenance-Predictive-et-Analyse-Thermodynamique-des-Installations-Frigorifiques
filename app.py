from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os
import threading
import atexit

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///froidpredict.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key')

# Initialize extensions
db = SQLAlchemy(app)
jwt = JWTManager(app)
CORS(app)

# Initialize data processor
data_processor = None

def setup_database():
    """Setup database tables"""
    try:
        # Import models to ensure they are registered
        from models.sensor_data import SensorData
        from models.equipment import Equipment
        from models.alert import Alert
        from models.user import User
        
        db.create_all()
        print("Database tables created successfully")
        
    except Exception as e:
        print(f"Error setting up database: {e}")

def setup_kafka_consumer():
    """Setup Kafka consumer for processing incoming data"""
    global data_processor
    
    try:
        from services.data_processor import DataProcessor
        
        data_processor = DataProcessor(app)
        
        # Start consumer in a separate thread
        def start_consumer():
            data_processor.start()
        
        consumer_thread = threading.Thread(target=start_consumer, daemon=True)
        consumer_thread.start()
        
        print("Kafka consumer started successfully")
        
    except Exception as e:
        print(f"Error setting up Kafka consumer: {e}")

def cleanup():
    """Cleanup resources on shutdown"""
    global data_processor
    
    if data_processor:
        data_processor.stop()
        print("Kafka consumer stopped")

# Register cleanup function
atexit.register(cleanup)

# Import and register routes
try:
    from routes.sensor_routes import sensor_bp
    from routes.equipment_routes import equipment_bp
    from routes.alert_routes import alert_bp
    from routes.auth_routes import auth_bp
    from routes.dashboard_routes import dashboard_bp
    from routes.kafka_routes import kafka_bp
    
    app.register_blueprint(sensor_bp, url_prefix='/api/sensors')
    app.register_blueprint(equipment_bp, url_prefix='/api/equipment')
    app.register_blueprint(alert_bp, url_prefix='/api/alerts')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    app.register_blueprint(kafka_bp, url_prefix='/api/kafka')
    
    print("All routes registered successfully")
    
except ImportError as e:
    print(f"Warning: Could not import some routes: {e}")
    print("The application will still run but some features may not be available")

@app.route('/')
def home():
    return {
        'message': 'FroidPredict API - Maintenance Prédictive des Installations Frigorifiques',
        'version': '1.0.0',
        'status': 'running',
        'features': {
            'sensor_data': True,
            'equipment_management': True,
            'alert_system': True,
            'user_authentication': True,
            'dashboard': True,
            'kafka_integration': True
        }
    }

@app.route('/health')
def health():
    """Health check endpoint"""
    try:
        from services.data_processor import KafkaHealthChecker
        
        health_checker = KafkaHealthChecker()
        kafka_health = health_checker.get_health_status()
        
        return {
            'status': 'healthy',
            'database': 'connected',
            'kafka': kafka_health
        }
    except Exception as e:
        return {
            'status': 'degraded',
            'error': str(e)
        }

@app.route('/api/test')
def test():
    """Test endpoint"""
    return {'message': 'API is working!'}

if __name__ == '__main__':
    with app.app_context():
        # Setup database
        setup_database()
        
        # Setup Kafka consumer
        setup_kafka_consumer()
        
        print("Starting FroidPredict API server...")
        print("Available endpoints:")
        print("  GET  /                     - API information")
        print("  GET  /health              - Health check")
        print("  GET  /api/test            - Test endpoint")
        print("  POST /api/kafka/generate/batch - Generate fake data")
        print("  POST /api/kafka/generate/start - Start continuous data generation")
        print("  POST /api/kafka/generate/stop  - Stop continuous data generation")
        print("  GET  /api/kafka/health    - Kafka health check")
        print("")
        print("Server starting on http://localhost:5000")
        
    app.run(debug=True, host='0.0.0.0', port=5000)