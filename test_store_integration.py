#!/usr/bin/env python3
"""
Test Real-time Updates with Pinia Store
This script tests the complete real-time update flow
"""

import requests
import time
import json
from datetime import datetime

BASE_URL = "http://localhost:5002"

def test_store_integration():
    """Test that the Pinia store receives real-time updates properly"""
    print("🏪 Testing Pinia Store Integration for Real-time Updates")
    print("=" * 60)
    
    try:
        # Test initial API endpoints
        print("📡 Testing API Endpoints...")
        
        # Test predictions count
        pred_response = requests.get(f"{BASE_URL}/api/predictions/count")
        if pred_response.status_code == 200:
            pred_data = pred_response.json()
            print(f"✅ Predictions API: {pred_data.get('count', 0)} predictions")
        else:
            print(f"❌ Predictions API failed: {pred_response.status_code}")
            return False
        
        # Test alerts count  
        alert_response = requests.get(f"{BASE_URL}/api/alerts/count")
        if alert_response.status_code == 200:
            alert_data = alert_response.json()
            print(f"✅ Alerts API: {alert_data.get('count', 0)} alerts")
        else:
            print(f"❌ Alerts API failed: {alert_response.status_code}")
            return False
        
        # Test dashboard data
        dashboard_response = requests.get(f"{BASE_URL}/api/dashboard_data")
        if dashboard_response.status_code == 200:
            dashboard_data = dashboard_response.json()
            print(f"✅ Dashboard API: {len(dashboard_data.get('predictions', []))} predictions, {len(dashboard_data.get('alerts', []))} alerts")
        else:
            print(f"❌ Dashboard API failed: {dashboard_response.status_code}")
        
        # Test system status
        status_response = requests.get(f"{BASE_URL}/api/system/status")
        if status_response.status_code == 200:
            status_data = status_response.json()
            print(f"✅ System Status API: {status_data.get('system_status', 'unknown')}")
        else:
            print(f"❌ System Status API failed: {status_response.status_code}")
        
        print("\n🤖 Testing Automatic Generation...")
        auto_status_response = requests.get(f"{BASE_URL}/api/auto-prediction/status")
        if auto_status_response.status_code == 200:
            auto_data = auto_status_response.json()
            print(f"✅ Auto Generation: {'Enabled' if auto_data.get('auto_prediction_enabled') else 'Disabled'}")
            print(f"   Total Predictions: {auto_data.get('total_predictions', 0)}")
            print(f"   Total Alerts: {auto_data.get('total_alerts', 0)}")
        else:
            print(f"❌ Auto Generation Status failed: {auto_status_response.status_code}")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("🔌 Cannot connect to Flask server. Make sure it's running on port 5002")
        return False
    except Exception as e:
        print(f"❌ Error testing APIs: {e}")
        return False

def monitor_real_time_updates():
    """Monitor for real-time updates over 2 minutes"""
    print("\n⏱️  Monitoring Real-time Updates for 2 minutes...")
    print("   Frontend should show:")
    print("   - WebSocket connection status")
    print("   - Automatic count updates")
    print("   - Visual feedback (bouncing badges)")
    print("   - Console logs from store")
    
    initial_pred_response = requests.get(f"{BASE_URL}/api/predictions/count")
    initial_alert_response = requests.get(f"{BASE_URL}/api/alerts/count")
    
    if initial_pred_response.status_code == 200 and initial_alert_response.status_code == 200:
        initial_pred_count = initial_pred_response.json().get('count', 0)
        initial_alert_count = initial_alert_response.json().get('count', 0)
        
        print(f"📊 Starting counts: {initial_pred_count} predictions, {initial_alert_count} alerts")
        print("🔄 Monitoring for changes...")
        
        last_pred = initial_pred_count
        last_alert = initial_alert_count
        updates_detected = 0
        
        start_time = time.time()
        while time.time() - start_time < 120:  # 2 minutes
            try:
                pred_response = requests.get(f"{BASE_URL}/api/predictions/count")
                alert_response = requests.get(f"{BASE_URL}/api/alerts/count")
                
                if pred_response.status_code == 200 and alert_response.status_code == 200:
                    current_pred = pred_response.json().get('count', 0)
                    current_alert = alert_response.json().get('count', 0)
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    
                    if current_pred != last_pred or current_alert != last_alert:
                        updates_detected += 1
                        print(f"\n[{timestamp}] 🔥 UPDATE #{updates_detected}")
                        
                        if current_pred != last_pred:
                            change = current_pred - last_pred
                            print(f"   📊 Predictions: {last_pred} → {current_pred} ({change:+d})")
                        
                        if current_alert != last_alert:
                            change = current_alert - last_alert
                            print(f"   🚨 Alerts: {last_alert} → {current_alert} ({change:+d})")
                        
                        last_pred = current_pred
                        last_alert = current_alert
                    else:
                        print(f"[{timestamp}] 📡 P:{current_pred} A:{current_alert}", end='\r')
                
                time.sleep(3)
                
            except Exception as e:
                print(f"\n❌ Error during monitoring: {e}")
        
        print(f"\n\n📋 MONITORING RESULTS:")
        print(f"   🔄 Updates detected: {updates_detected}")
        print(f"   📊 Final predictions: {last_pred} (change: {last_pred - initial_pred_count:+d})")
        print(f"   🚨 Final alerts: {last_alert} (change: {last_alert - initial_alert_count:+d})")
        
        if updates_detected > 0:
            print("✅ SUCCESS: Real-time updates are working!")
        else:
            print("⚠️  No updates detected. Check automatic generation.")

def print_frontend_checklist():
    """Print checklist for frontend testing"""
    print("\n📋 FRONTEND TESTING CHECKLIST:")
    print("=" * 40)
    print("🌐 1. Open http://localhost:3000 in browser")
    print("🔧 2. Open Developer Tools (F12)")
    print("📝 3. Go to Console tab and look for:")
    print("   ✅ '🔗 Store WebSocket connected for real-time updates'")
    print("   ✅ '📊 Store: New prediction received: AUTO_GEN_X Total: XX'")
    print("   ✅ '🚨 Store: New alert received: ... Total active: XX'")
    print("   ✅ '📡 Store: New sensor data: AUTO_GEN_X'")
    print("\n🎯 4. Watch the Sidebar:")
    print("   ✅ Prediction count should increment automatically")
    print("   ✅ Alert count should increment when alerts generated")
    print("   ✅ 'Live' status should show green (WebSocket connected)")
    print("   ✅ Badges should bounce when new data arrives")
    print("   ✅ Last update time should refresh automatically")
    print("\n🌐 5. Check Network tab:")
    print("   ✅ WebSocket connection to localhost:5002")
    print("   ✅ Periodic API calls to /api/predictions/count")
    print("   ✅ Periodic API calls to /api/alerts/count")
    print("\n🎨 6. Visual Indicators:")
    print("   ✅ Green 'Live' indicator = WebSocket connected")
    print("   ✅ Yellow 'Polling' indicator = Fallback mode")
    print("   ✅ Spinning refresh icon = Updates active")
    print("   ✅ Bouncing badges = New data received")

if __name__ == "__main__":
    print("🧪 Real-time Updates Integration Test")
    print("🏪 Testing Pinia Store + WebSocket + Auto Generation")
    print()
    
    # Test API endpoints
    if test_store_integration():
        # Monitor real-time updates
        monitor_real_time_updates()
    
    # Print frontend checklist
    print_frontend_checklist()
    
    print("\n🎯 EXPECTED BEHAVIOR:")
    print("   The sidebar prediction and alert counts should update")
    print("   automatically every 15-45 seconds without clicking refresh!")
    print("   WebSocket provides instant updates, HTTP polling as backup.")
