#!/usr/bin/env python3
"""
Standalone script to generate fake data for FroidPredict system
Run this script to continuously generate fake sensor data and alerts
"""

import sys
import os
import time
import argparse
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.fake_data_generator import FakeDataGenerator
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description='Generate fake data for FroidPredict system')
    parser.add_argument('--mode', choices=['batch', 'continuous'], default='batch',
                        help='Data generation mode (default: batch)')
    parser.add_argument('--equipment', type=int, default=5,
                        help='Number of equipment to generate (default: 5)')
    parser.add_argument('--batches', type=int, default=10,
                        help='Number of batches to generate (batch mode only, default: 10)')
    parser.add_argument('--interval', type=int, default=10,
                        help='Interval between data generation in seconds (continuous mode only, default: 10)')
    parser.add_argument('--anomaly-chance', type=float, default=0.1,
                        help='Chance of anomaly in sensor data (0.0-1.0, default: 0.1)')
    
    args = parser.parse_args()
    
    print("🚀 FroidPredict Fake Data Generator")
    print("=" * 50)
    print(f"Mode: {args.mode}")
    print(f"Equipment count: {args.equipment}")
    if args.mode == 'batch':
        print(f"Batches: {args.batches}")
    else:
        print(f"Interval: {args.interval} seconds")
    print(f"Anomaly chance: {args.anomaly_chance * 100}%")
    print("=" * 50)
    
    # Create data generator
    generator = FakeDataGenerator()
    
    try:
        # Generate equipment data
        print("📊 Generating equipment data...")
        equipment_list = generator.generate_equipment_data(args.equipment)
        
        print(f"✅ Generated {len(equipment_list)} equipment:")
        for eq in equipment_list:
            print(f"  - {eq['name']} ({eq['type']}) - {eq['refrigerant_type']}")
        
        print("\n🔄 Starting data generation...")
        
        if args.mode == 'batch':
            # Generate batch data
            print(f"📦 Generating {args.batches} batches of data...")
            generator.generate_batch_data(equipment_list, args.batches)
            print("✅ Batch data generation completed!")
            
        else:
            # Generate continuous data
            print("🔄 Starting continuous data generation...")
            print("Press Ctrl+C to stop")
            
            try:
                generator.generate_continuous_data(equipment_list, args.interval)
            except KeyboardInterrupt:
                print("\n⏹️  Stopping data generation...")
        
    except Exception as e:
        logger.error(f"Error during data generation: {e}")
        sys.exit(1)
    
    finally:
        # Clean up
        generator.close()
        print("🧹 Cleaned up resources")
        print("👋 Goodbye!")

if __name__ == '__main__':
    main()
