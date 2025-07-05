#!/usr/bin/env python3
"""
Data simulation script for FroidPredict
"""

import argparse
import sys
import time
from datetime import datetime
from app import app
from utils.data_simulator import DataSimulator
from models.equipment import Equipment

def main():
    parser = argparse.ArgumentParser(description='FroidPredict Data Simulator')
    parser.add_argument('--mode', choices=['realtime', 'historical', 'failure'], 
                       default='realtime', help='Simulation mode')
    parser.add_argument('--equipment-id', type=int, help='Equipment ID to simulate')
    parser.add_argument('--duration', type=int, default=60, 
                       help='Duration in minutes for real-time simulation')
    parser.add_argument('--days', type=int, default=7, 
                       help='Number of days for historical simulation')
    parser.add_argument('--interval', type=int, default=30, 
                       help='Interval in seconds between readings')
    parser.add_argument('--failure-type', choices=['gradual', 'sudden'], 
                       default='gradual', help='Type of failure to simulate')
    
    args = parser.parse_args()
    
    with app.app_context():
        simulator = DataSimulator()
        
        if args.equipment_id:
            equipment = Equipment.query.get(args.equipment_id)
            if not equipment:
                print(f"Equipment with ID {args.equipment_id} not found")
                sys.exit(1)
        else:
            # Get first equipment if no ID specified
            equipment = Equipment.query.first()
            if not equipment:
                print("No equipment found. Please run setup first.")
                sys.exit(1)
        
        print(f"Starting simulation for: {equipment.name}")
        print(f"Mode: {args.mode}")
        print(f"Equipment ID: {equipment.id}")
        
        try:
            if args.mode == 'realtime':
                print(f"Duration: {args.duration} minutes")
                print(f"Interval: {args.interval} seconds")
                simulator.simulate_real_time_data(
                    equipment.id, 
                    args.duration, 
                    args.interval
                )
            
            elif args.mode == 'historical':
                print(f"Historical period: {args.days} days")
                simulator.simulate_historical_data(equipment.id, args.days)
            
            elif args.mode == 'failure':
                print(f"Failure type: {args.failure_type}")
                simulator.simulate_failure_scenario(equipment.id, args.failure_type)
            
            print("Simulation completed successfully!")
            
        except KeyboardInterrupt:
            print("\nSimulation interrupted by user")
        except Exception as e:
            print(f"Error during simulation: {str(e)}")
            sys.exit(1)

if __name__ == '__main__':
    main()
