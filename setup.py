#!/usr/bin/env python3
"""
Setup script for FroidPredict application
"""

import os
import sys
from datetime import datetime
from app import app, db
from models.equipment import Equipment
from models.user import User
from models.sensor_data import SensorData
from models.alert import Alert
from utils.data_simulator import DataSimulator

def create_tables():
    """Create database tables"""
    print("Creating database tables...")
    with app.app_context():
        db.create_all()
        print("✓ Database tables created successfully")

def create_admin_user():
    """Create admin user"""
    print("Creating admin user...")
    with app.app_context():
        # Check if admin user already exists
        admin_user = User.query.filter_by(username='admin').first()
        if admin_user:
            print("✓ Admin user already exists")
            return
        
        # Create admin user
        admin = User(
            username='admin',
            email='admin@froidpredict.com',
            first_name='Admin',
            last_name='User',
            role='admin'
        )
        admin.set_password('admin123')
        
        db.session.add(admin)
        db.session.commit()
        print("✓ Admin user created (username: admin, password: admin123)")

def create_sample_data():
    """Create sample equipment and data"""
    print("Creating sample data...")
    with app.app_context():
        # Check if sample data already exists
        if Equipment.query.count() > 0:
            print("✓ Sample data already exists")
            return
        
        # Create sample equipment
        simulator = DataSimulator()
        equipment_list = simulator.create_sample_equipment()
        
        if equipment_list:
            print(f"✓ Created {len(equipment_list)} sample equipment")
            
            # Generate historical data for each equipment
            for equipment in equipment_list:
                print(f"Generating historical data for {equipment.name}...")
                simulator.simulate_historical_data(equipment.id, days=7)
            
            # Generate sample alerts
            simulator.generate_sample_alerts()
            print("✓ Sample alerts generated")
        else:
            print("✗ Failed to create sample equipment")

def setup_environment():
    """Setup environment variables"""
    print("Setting up environment...")
    
    env_file = '.env'
    if os.path.exists(env_file):
        print("✓ Environment file already exists")
        return
    
    env_content = """DATABASE_URL=sqlite:///froidpredict.db
SECRET_KEY=dev-secret-key-change-in-production
JWT_SECRET_KEY=jwt-secret-key-change-in-production
FLASK_ENV=development
DEBUG=True
"""
    
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    print("✓ Environment file created")

def install_dependencies():
    """Install Python dependencies"""
    print("Installing dependencies...")
    
    try:
        import subprocess
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ Dependencies installed successfully")
        else:
            print("✗ Failed to install dependencies")
            print(result.stderr)
            
    except Exception as e:
        print(f"✗ Error installing dependencies: {str(e)}")

def run_setup():
    """Run complete setup"""
    print("="*50)
    print("FroidPredict Setup Script")
    print("="*50)
    
    try:
        # Setup environment
        setup_environment()
        
        # Install dependencies
        install_dependencies()
        
        # Create database tables
        create_tables()
        
        # Create admin user
        create_admin_user()
        
        # Create sample data
        create_sample_data()
        
        print("\n" + "="*50)
        print("✓ Setup completed successfully!")
        print("="*50)
        print("\nTo start the application:")
        print("1. Run: python app.py")
        print("2. Open: http://localhost:5000")
        print("3. Frontend: http://localhost:5000/../frontend/index.html")
        print("\nAdmin credentials:")
        print("Username: admin")
        print("Password: admin123")
        print("\nAPI Documentation:")
        print("Base URL: http://localhost:5000/api")
        print("Endpoints:")
        print("  - GET /api/equipment/")
        print("  - GET /api/sensors/")
        print("  - GET /api/alerts/")
        print("  - GET /api/dashboard/overview")
        print("="*50)
        
    except Exception as e:
        print(f"\n✗ Setup failed: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    run_setup()
