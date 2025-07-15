#!/usr/bin/env python3
"""
Test Prediction Data Duplication Fix
This script tests that predictions and alerts are not duplicated
"""

import requests
import time
from datetime import datetime

BASE_URL = "http://localhost:5002"

def test_duplicate_prevention():
    """Test that the frontend prevents data duplication"""
    print("🧪 Testing Duplicate Prevention System")
    print("=" * 50)
    
    try:
        # Test dashboard data first
        print("📊 Testing Dashboard Data...")
        response = requests.get(f"{BASE_URL}/api/dashboard_data")
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                predictions = data.get('predictions', [])
                alerts = data.get('alerts', [])
                stats = data.get('stats', {})
                
                print(f"✅ Dashboard API working:")
                print(f"   📊 UI Predictions: {len(predictions)} items")
                print(f"   🚨 UI Alerts: {len(alerts)} items")
                print(f"   📊 DB Total Predictions: {stats.get('total_predictions', 0)}")
                print(f"   🚨 DB Total Alerts: {stats.get('total_alerts', 0)}")
                
                # Check for duplicates in UI data
                pred_ids = [p.get('_id') or p.get('machine_id') for p in predictions]
                alert_ids = [a.get('_id') or f"{a.get('machine_id')}_{a.get('timestamp')}" for a in alerts]
                
                pred_unique = len(set(pred_ids))
                alert_unique = len(set(alert_ids))
                
                print(f"\n🔍 Checking for duplicates:")
                print(f"   📊 Predictions: {len(predictions)} total, {pred_unique} unique {'✅' if len(predictions) == pred_unique else '❌ DUPLICATES!'}")
                print(f"   🚨 Alerts: {len(alerts)} total, {alert_unique} unique {'✅' if len(alerts) == alert_unique else '❌ DUPLICATES!'}")
                
                return len(predictions) == pred_unique and len(alerts) == alert_unique
            else:
                print(f"❌ Dashboard API error: {data}")
                return False
        else:
            print(f"❌ Dashboard API failed: {response.status_code}")
            return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def monitor_new_data_handling():
    """Monitor how new data is handled to check for duplication"""
    print("\n⏱️  Monitoring New Data Handling for 90 seconds...")
    print("This tests WebSocket vs API data synchronization")
    
    try:
        # Get initial state
        response = requests.get(f"{BASE_URL}/api/dashboard_data")
        if response.status_code == 200:
            initial_data = response.json()
            if initial_data.get('status') == 'success':
                initial_predictions = initial_data.get('predictions', [])
                initial_alerts = initial_data.get('alerts', [])
                
                print(f"📊 Starting with {len(initial_predictions)} predictions, {len(initial_alerts)} alerts in UI")
                
                # Track changes
                start_time = time.time()
                last_pred_count = len(initial_predictions)
                last_alert_count = len(initial_alerts)
                duplicates_detected = 0
                
                while time.time() - start_time < 90:  # 90 seconds
                    try:
                        response = requests.get(f"{BASE_URL}/api/dashboard_data")
                        if response.status_code == 200:
                            data = response.json()
                            if data.get('status') == 'success':
                                predictions = data.get('predictions', [])
                                alerts = data.get('alerts', [])
                                timestamp = datetime.now().strftime("%H:%M:%S")
                                
                                # Check for duplicates
                                pred_ids = [p.get('_id') or p.get('machine_id') for p in predictions]
                                alert_ids = [a.get('_id') or f"{a.get('machine_id')}_{a.get('timestamp')}" for a in alerts]
                                
                                pred_unique = len(set(pred_ids))
                                alert_unique = len(set(alert_ids))
                                
                                has_duplicates = len(predictions) != pred_unique or len(alerts) != alert_unique
                                
                                if has_duplicates:
                                    duplicates_detected += 1
                                    print(f"\n[{timestamp}] ❌ DUPLICATES DETECTED #{duplicates_detected}")
                                    if len(predictions) != pred_unique:
                                        print(f"   📊 Prediction duplicates: {len(predictions)} total, {pred_unique} unique")
                                    if len(alerts) != alert_unique:
                                        print(f"   🚨 Alert duplicates: {len(alerts)} total, {alert_unique} unique")
                                
                                # Check for changes
                                if len(predictions) != last_pred_count or len(alerts) != last_alert_count:
                                    print(f"\n[{timestamp}] 📊 UI Data Changed:")
                                    print(f"   Predictions: {last_pred_count} → {len(predictions)}")
                                    print(f"   Alerts: {last_alert_count} → {len(alerts)}")
                                    
                                    last_pred_count = len(predictions)
                                    last_alert_count = len(alerts)
                                else:
                                    print(f"[{timestamp}] 📡 P:{len(predictions)} A:{len(alerts)} {'✅' if not has_duplicates else '❌'}", end='\r')
                        
                        time.sleep(3)
                        
                    except Exception as e:
                        print(f"\n❌ Error during monitoring: {e}")
                
                print(f"\n\n📋 DUPLICATE MONITORING RESULTS:")
                print(f"   ❌ Duplicates detected: {duplicates_detected} times")
                
                if duplicates_detected == 0:
                    print("✅ SUCCESS: No duplicates detected during monitoring!")
                    return True
                else:
                    print("❌ FAILURE: Duplicates were detected!")
                    return False
                    
        else:
            print(f"❌ Cannot get initial state: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error during monitoring: {e}")
        return False

def print_frontend_duplicate_test():
    """Print frontend duplicate testing guide"""
    print("\n📋 FRONTEND DUPLICATE TESTING GUIDE")
    print("=" * 50)
    print("🌐 1. Open http://localhost:3000 in browser")
    print("🔧 2. Open Developer Tools (F12) → Console tab")
    print("\n📝 3. Look for Duplicate Prevention Logs:")
    print("   ✅ '📊 Store: New prediction received: ... (duplicate skipped)'")
    print("   ✅ '🚨 Store: New alert received: ... (duplicate skipped)'")
    print("   ✅ '🧹 Removed X duplicate predictions'")
    print("   ✅ '🧹 Removed X duplicate alerts'")
    print("   ✅ '🔄 Periodic count sync and cleanup completed'")
    print("\n🎯 4. Test Different Pages:")
    print("   📊 Dashboard: Check prediction list for duplicates")
    print("   📊 Predictions Page: Scroll through list, look for repeated items")
    print("   🚨 Alerts Page: Check alert list for duplicates")
    print("\n⏱️  5. Test Real-time Updates:")
    print("   ✅ New items should appear without duplicating existing ones")
    print("   ✅ Page refresh should not create duplicates")
    print("   ✅ Switching between pages should show consistent data")
    print("\n🔍 6. Manual Duplicate Check:")
    print("   📊 Look for same machine_id appearing multiple times")
    print("   🚨 Look for same alert message with same timestamp")
    print("   ⚡ Check if WebSocket and API data conflict")

if __name__ == "__main__":
    print("🧪 PREDICTION DATA DUPLICATION TEST")
    print("🎯 Testing duplicate prevention in frontend store")
    print()
    
    # Test initial duplicate prevention
    if test_duplicate_prevention():
        print("\n🚀 Initial duplicate test passed! Monitoring new data...")
        # Monitor new data handling
        monitor_new_data_handling()
    else:
        print("\n❌ Initial duplicate test failed!")
    
    # Print frontend testing guide
    print_frontend_duplicate_test()
    
    print("\n🎯 EXPECTED RESULTS:")
    print("   ✅ No duplicate predictions in UI lists")
    print("   ✅ No duplicate alerts in UI lists")
    print("   ✅ WebSocket and API data should merge cleanly")
    print("   ✅ Page refresh should not create duplicates")
    print("   ✅ Store should automatically clean duplicates")
