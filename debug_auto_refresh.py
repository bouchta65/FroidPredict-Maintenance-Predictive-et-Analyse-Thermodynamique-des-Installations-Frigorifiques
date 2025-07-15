#!/usr/bin/env python3
"""
Debug Auto-Refresh System
This script helps debug the automatic refresh functionality
"""

import requests
import time
import json
from datetime import datetime

BASE_URL = "http://localhost:5002"

def test_automatic_refresh():
    """Test that the system is generating predictions automatically"""
    print("🔍 Testing Automatic Refresh System")
    print("=" * 50)
    
    # Initial counts
    try:
        pred_response = requests.get(f"{BASE_URL}/api/predictions/count")
        alert_response = requests.get(f"{BASE_URL}/api/alerts/count")
        
        if pred_response.status_code == 200:
            initial_predictions = pred_response.json().get('count', 0)
            print(f"📊 Initial predictions count: {initial_predictions}")
        else:
            print(f"❌ Cannot connect to predictions API: {pred_response.status_code}")
            return
            
        if alert_response.status_code == 200:
            initial_alerts = alert_response.json().get('count', 0)
            print(f"🚨 Initial alerts count: {initial_alerts}")
        else:
            print(f"❌ Cannot connect to alerts API: {alert_response.status_code}")
            return
            
    except requests.exceptions.ConnectionError:
        print("🔌 Cannot connect to Flask server. Make sure it's running on port 5002")
        return
    
    print("\n⏱️  Monitoring for 60 seconds...")
    print("   (Flask generates predictions every 15-45 seconds)")
    print("   (Frontend refreshes every 10 seconds)")
    print("   (WebSocket should provide instant updates)")
    
    # Monitor for changes
    start_time = time.time()
    last_pred_count = initial_predictions
    last_alert_count = initial_alerts
    
    while time.time() - start_time < 60:  # Monitor for 60 seconds
        try:
            # Check counts
            pred_response = requests.get(f"{BASE_URL}/api/predictions/count")
            alert_response = requests.get(f"{BASE_URL}/api/alerts/count")
            
            if pred_response.status_code == 200 and alert_response.status_code == 200:
                current_pred = pred_response.json().get('count', 0)
                current_alert = alert_response.json().get('count', 0)
                timestamp = datetime.now().strftime("%H:%M:%S")
                
                # Check for changes
                pred_changed = current_pred != last_pred_count
                alert_changed = current_alert != last_alert_count
                
                if pred_changed or alert_changed:
                    print(f"\n[{timestamp}] 🔥 CHANGE DETECTED!")
                    
                    if pred_changed:
                        change = current_pred - last_pred_count
                        print(f"   📊 Predictions: {last_pred_count} → {current_pred} ({change:+d})")
                    
                    if alert_changed:
                        change = current_alert - last_alert_count
                        print(f"   🚨 Alerts: {last_alert_count} → {current_alert} ({change:+d})")
                    
                    last_pred_count = current_pred
                    last_alert_count = current_alert
                else:
                    print(f"[{timestamp}] 📡 Monitoring... P:{current_pred} A:{current_alert}", end='\r')
            
            time.sleep(2)  # Check every 2 seconds
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
    
    # Final results
    final_pred = last_pred_count
    final_alert = last_alert_count
    
    print(f"\n\n📋 FINAL RESULTS:")
    print(f"   📊 Predictions: {initial_predictions} → {final_pred} (Total change: {final_pred - initial_predictions:+d})")
    print(f"   🚨 Alerts: {initial_alerts} → {final_alert} (Total change: {final_alert - initial_alerts:+d})")
    
    if final_pred > initial_predictions or final_alert > initial_alerts:
        print("✅ SUCCESS: Automatic generation is working!")
    else:
        print("⚠️  No new data detected. Check that Flask automatic generation is running.")
    
    print("\n💡 FRONTEND DEBUGGING TIPS:")
    print("   1. Open browser dev tools (F12)")
    print("   2. Go to Console tab")
    print("   3. Look for these messages:")
    print("      - '🔗 WebSocket connected for real-time updates'")
    print("      - '📊 New prediction received: AUTO_GEN_X'")
    print("      - '🚨 New alert received: ...'")
    print("      - '🔄 Auto-sync: Predictions updated from X to Y'")
    print("   4. Check Network tab for regular API calls to:")
    print("      - /api/predictions/count")
    print("      - /api/alerts/count")
    print("      - /api/system/status")

if __name__ == "__main__":
    test_automatic_refresh()
