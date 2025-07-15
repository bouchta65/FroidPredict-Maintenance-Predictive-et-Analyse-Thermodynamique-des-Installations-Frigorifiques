#!/usr/bin/env python3
"""
Test Real Count Persistence
This script tests if the counts persist correctly and shows the real database counts
"""

import requests
import time
import json
from datetime import datetime

BASE_URL = "http://localhost:5002"

def test_count_persistence():
    """Test that counts persist correctly across page refreshes"""
    print("🔢 Testing Count Persistence and Real Database Counts")
    print("=" * 60)
    
    try:
        # Get current counts
        pred_response = requests.get(f"{BASE_URL}/api/predictions/count")
        alert_response = requests.get(f"{BASE_URL}/api/alerts/count")
        
        if pred_response.status_code == 200 and alert_response.status_code == 200:
            pred_count = pred_response.json().get('count', 0)
            alert_count = alert_response.json().get('count', 0)
            
            print(f"📊 Current Database Counts:")
            print(f"   Predictions: {pred_count}")
            print(f"   Alerts: {alert_count}")
            
            # Test dashboard data (what page refresh loads)
            dashboard_response = requests.get(f"{BASE_URL}/api/dashboard_data")
            if dashboard_response.status_code == 200:
                dashboard_data = dashboard_response.json()
                dashboard_pred_count = len(dashboard_data.get('predictions', []))
                dashboard_alert_count = len(dashboard_data.get('alerts', []))
                dashboard_stats = dashboard_data.get('stats', {})
                
                print(f"\n🌐 Dashboard Data (what page loads):")
                print(f"   Predictions array length: {dashboard_pred_count}")
                print(f"   Alerts array length: {dashboard_alert_count}")
                print(f"   Stats total_predictions: {dashboard_stats.get('total_predictions', 0)}")
                print(f"   Stats total_alerts: {dashboard_stats.get('total_alerts', 0)}")
                
                # Check if stats match database counts
                if dashboard_stats.get('total_predictions') == pred_count:
                    print("   ✅ Prediction stats match database count")
                else:
                    print(f"   ❌ Prediction stats mismatch! Database: {pred_count}, Stats: {dashboard_stats.get('total_predictions')}")
                
                if dashboard_stats.get('total_alerts') == alert_count:
                    print("   ✅ Alert stats match database count")
                else:
                    print(f"   ❌ Alert stats mismatch! Database: {alert_count}, Stats: {dashboard_stats.get('total_alerts')}")
            
            # Explain the issue
            print(f"\n🔍 PROBLEM ANALYSIS:")
            print(f"   The Sidebar should show {pred_count} predictions, not {dashboard_pred_count}")
            print(f"   The Sidebar should show {alert_count} alerts, not {dashboard_alert_count}")
            print(f"   After page refresh, store.predictionCount should be {pred_count}")
            print(f"   After page refresh, store.alertCount should be {alert_count}")
            
            return pred_count, alert_count
            
    except requests.exceptions.ConnectionError:
        print("🔌 Cannot connect to Flask server. Make sure it's running on port 5002")
        return 0, 0
    except Exception as e:
        print(f"❌ Error testing counts: {e}")
        return 0, 0

def wait_for_new_data(initial_pred, initial_alert, timeout=60):
    """Wait for new data to be generated"""
    print(f"\n⏳ Waiting for new data (up to {timeout} seconds)...")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            pred_response = requests.get(f"{BASE_URL}/api/predictions/count")
            alert_response = requests.get(f"{BASE_URL}/api/alerts/count")
            
            if pred_response.status_code == 200 and alert_response.status_code == 200:
                current_pred = pred_response.json().get('count', 0)
                current_alert = alert_response.json().get('count', 0)
                
                if current_pred != initial_pred or current_alert != initial_alert:
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    print(f"[{timestamp}] 🔄 New data detected!")
                    print(f"   Predictions: {initial_pred} → {current_pred} ({current_pred-initial_pred:+d})")
                    print(f"   Alerts: {initial_alert} → {current_alert} ({current_alert-initial_alert:+d})")
                    return current_pred, current_alert
                else:
                    print(f"⏱️  P:{current_pred} A:{current_alert}", end='\r')
            
            time.sleep(2)
            
        except Exception as e:
            print(f"\n❌ Error waiting for data: {e}")
            break
    
    print(f"\n⏰ Timeout reached. No new data generated.")
    return initial_pred, initial_alert

if __name__ == "__main__":
    print("🧪 Count Persistence Test")
    print("Testing real database counts vs frontend display")
    print()
    
    # Test initial state
    initial_pred, initial_alert = test_count_persistence()
    
    if initial_pred > 0 or initial_alert > 0:
        # Wait for new data
        final_pred, final_alert = wait_for_new_data(initial_pred, initial_alert, 60)
        
        # Test again after new data
        print(f"\n🔄 After new data generation:")
        test_count_persistence()
        
        print(f"\n📋 FRONTEND TESTING INSTRUCTIONS:")
        print(f"   1. Open http://localhost:3000")
        print(f"   2. Check sidebar shows: Predictions={final_pred}, Alerts={final_alert}")
        print(f"   3. Press F5 to refresh the page")
        print(f"   4. Sidebar should STILL show: Predictions={final_pred}, Alerts={final_alert}")
        print(f"   5. NOT the array length (which would be 10)")
        print(f"\n✅ If counts persist after refresh = SUCCESS")
        print(f"❌ If counts reset to 10 = PROBLEM")
