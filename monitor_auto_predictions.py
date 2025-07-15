#!/usr/bin/env python3
"""
Real-time Monitor for Automatic Predictions
Watch the automatic prediction generation in real-time
"""

import requests
import time
import json
from datetime import datetime

BASE_URL = "http://localhost:5002"

def monitor_predictions():
    """Monitor prediction count in real-time"""
    print("🤖 Monitoring Automatic Prediction Generation")
    print("=" * 60)
    
    previous_count = 0
    previous_alerts = 0
    start_time = datetime.now()
    
    try:
        while True:
            try:
                # Get current counts
                pred_response = requests.get(f"{BASE_URL}/api/predictions/count", timeout=5)
                alert_response = requests.get(f"{BASE_URL}/api/alerts/count", timeout=5)
                
                if pred_response.status_code == 200 and alert_response.status_code == 200:
                    pred_data = pred_response.json()
                    alert_data = alert_response.json()
                    
                    current_predictions = pred_data.get('count', 0)
                    current_alerts = alert_data.get('count', 0)
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    
                    # Check for new predictions
                    new_predictions = current_predictions - previous_count
                    new_alerts = current_alerts - previous_alerts
                    
                    if new_predictions > 0 or new_alerts > 0:
                        status = "🔥 NEW DATA!"
                        if new_predictions > 0:
                            print(f"[{timestamp}] 📊 +{new_predictions} prediction(s) | Total: {current_predictions}")
                        if new_alerts > 0:
                            print(f"[{timestamp}] 🚨 +{new_alerts} alert(s) | Total: {current_alerts}")
                    else:
                        print(f"[{timestamp}] 📡 Monitoring... | Predictions: {current_predictions} | Alerts: {current_alerts}")
                    
                    previous_count = current_predictions
                    previous_alerts = current_alerts
                    
                else:
                    print(f"[{timestamp}] ❌ API Error - Status: {pred_response.status_code}")
                
            except requests.exceptions.ConnectionError:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔌 Server not responding")
            except Exception as e:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ Error: {e}")
            
            time.sleep(3)  # Check every 3 seconds
            
    except KeyboardInterrupt:
        runtime = datetime.now() - start_time
        print(f"\n🏁 Monitoring stopped after {runtime}")
        print(f"📊 Final count: {previous_count} predictions, {previous_alerts} alerts")

def test_auto_generation_status():
    """Test the auto-generation status endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/auto-prediction/status")
        if response.status_code == 200:
            data = response.json()
            print("🤖 Auto-Generation Status:")
            print(f"   Enabled: {data.get('auto_prediction_enabled', 'Unknown')}")
            print(f"   Total Predictions: {data.get('total_predictions', 0)}")
            print(f"   Total Alerts: {data.get('total_alerts', 0)}")
        else:
            print(f"❌ Status check failed: {response.status_code}")
    except Exception as e:
        print(f"⚠️ Status check error: {e}")

if __name__ == "__main__":
    print("🚀 Starting Real-time Prediction Monitor")
    print("📡 Make sure Flask server is running on localhost:5002")
    print("⏹️  Press Ctrl+C to stop monitoring")
    print()
    
    # Check status first
    test_auto_generation_status()
    print()
    
    # Start monitoring
    monitor_predictions()
