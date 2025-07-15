#!/usr/bin/env python3
"""
Test All Counter Systems
Verify that all counting mechanisms work correctly
"""

import requests
import time
from datetime import datetime

BASE_URL = "http://localhost:5002"

def test_backend_apis():
    """Test all backend API endpoints for counts"""
    print("🔧 Testing Backend API Endpoints")
    print("=" * 50)
    
    try:
        # Test dashboard_data endpoint (should have real DB counts now)
        print("📊 Testing /api/dashboard_data...")
        response = requests.get(f"{BASE_URL}/api/dashboard_data")
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                stats = data.get('stats', {})
                print(f"✅ Dashboard API:")
                print(f"   📊 UI Predictions: {len(data.get('predictions', []))}")
                print(f"   🚨 UI Alerts: {len(data.get('alerts', []))}")
                print(f"   📊 Total Predictions (DB): {stats.get('total_predictions', 0)}")
                print(f"   🚨 Total Alerts (DB): {stats.get('total_alerts', 0)}")
                print(f"   🔌 MongoDB Connected: {stats.get('mongodb_connected', False)}")
                
                dashboard_pred_count = stats.get('total_predictions', 0)
                dashboard_alert_count = stats.get('total_alerts', 0)
            else:
                print(f"❌ Dashboard API error: {data}")
                return False
        else:
            print(f"❌ Dashboard API failed: {response.status_code}")
            return False
        
        # Test individual count endpoints
        print("\n📊 Testing /api/predictions/count...")
        pred_response = requests.get(f"{BASE_URL}/api/predictions/count")
        if pred_response.status_code == 200:
            pred_data = pred_response.json()
            if pred_data.get('status') == 'success':
                pred_count = pred_data.get('count', 0)
                print(f"✅ Predictions Count API: {pred_count}")
            else:
                print(f"❌ Predictions Count API error: {pred_data}")
                return False
        else:
            print(f"❌ Predictions Count API failed: {pred_response.status_code}")
            return False
        
        print("\n🚨 Testing /api/alerts/count...")
        alert_response = requests.get(f"{BASE_URL}/api/alerts/count")
        if alert_response.status_code == 200:
            alert_data = alert_response.json()
            if alert_data.get('status') == 'success':
                alert_count = alert_data.get('count', 0)
                print(f"✅ Alerts Count API: {alert_count}")
            else:
                print(f"❌ Alerts Count API error: {alert_data}")
                return False
        else:
            print(f"❌ Alerts Count API failed: {alert_response.status_code}")
            return False
        
        # Check consistency
        print(f"\n🔍 Checking Consistency:")
        pred_match = dashboard_pred_count == pred_count
        alert_match = dashboard_alert_count == alert_count
        
        print(f"   📊 Predictions: Dashboard={dashboard_pred_count}, Count API={pred_count} {'✅' if pred_match else '❌'}")
        print(f"   🚨 Alerts: Dashboard={dashboard_alert_count}, Count API={alert_count} {'✅' if alert_match else '❌'}")
        
        if pred_match and alert_match:
            print("✅ All backend APIs are consistent!")
            return True
        else:
            print("❌ Backend APIs are inconsistent!")
            return False
        
    except requests.exceptions.ConnectionError:
        print("🔌 Cannot connect to Flask server. Make sure it's running on port 5002")
        return False
    except Exception as e:
        print(f"❌ Error testing backend APIs: {e}")
        return False

def monitor_real_time_updates():
    """Monitor real-time updates for 1 minute"""
    print("\n⏱️  Monitoring Real-time Updates for 1 minute...")
    print("Watch frontend for automatic counter updates!")
    
    try:
        # Get initial counts
        dashboard_response = requests.get(f"{BASE_URL}/api/dashboard_data")
        if dashboard_response.status_code == 200:
            initial_data = dashboard_response.json()
            if initial_data.get('status') == 'success':
                initial_stats = initial_data.get('stats', {})
                initial_pred = initial_stats.get('total_predictions', 0)
                initial_alert = initial_stats.get('total_alerts', 0)
                
                print(f"📊 Starting counts: {initial_pred} predictions, {initial_alert} alerts")
                print("🔄 Monitoring for changes...")
                
                updates_detected = 0
                start_time = time.time()
                last_pred = initial_pred
                last_alert = initial_alert
                
                while time.time() - start_time < 60:  # 1 minute
                    try:
                        response = requests.get(f"{BASE_URL}/api/dashboard_data")
                        if response.status_code == 200:
                            data = response.json()
                            if data.get('status') == 'success':
                                stats = data.get('stats', {})
                                current_pred = stats.get('total_predictions', 0)
                                current_alert = stats.get('total_alerts', 0)
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
                print(f"   📊 Final predictions: {last_pred} (change: {last_pred - initial_pred:+d})")
                print(f"   🚨 Final alerts: {last_alert} (change: {last_alert - initial_alert:+d})")
                
                if updates_detected > 0:
                    print("✅ SUCCESS: Real-time updates are working!")
                else:
                    print("⚠️  No updates detected during monitoring period.")
                    
        else:
            print(f"❌ Cannot get initial counts: {dashboard_response.status_code}")
            
    except Exception as e:
        print(f"❌ Error during monitoring: {e}")

def print_frontend_checklist():
    """Print detailed frontend testing checklist"""
    print("\n📋 FRONTEND TESTING CHECKLIST")
    print("=" * 50)
    print("🌐 1. Open http://localhost:3000 in browser")
    print("🔧 2. Open Developer Tools (F12) → Console tab")
    print("\n📝 3. Look for Store Initialization Logs:")
    print("   ✅ '🏪 Initializing store with real database counts...'")
    print("   ✅ '📊 Dashboard loaded - Predictions: XXXX, Alerts: XXX'")
    print("   ✅ '🔗 Store WebSocket connected for real-time updates'")
    print("\n🎯 4. Check ALL Pages for Correct Counts:")
    print("   📊 Dashboard: Total Predictions should show DB count (not 10)")
    print("   📊 Predictions Page: Total Predictions should match Dashboard")
    print("   🚨 Alerts Page: Total Alerts should match Dashboard")
    print("   📈 Diagrams Page: Should show same counts")
    print("   🧪 Test Dashboard: Should show same counts")
    print("\n⏱️  5. Watch Real-time Updates:")
    print("   ✅ Sidebar counters should update automatically")
    print("   ✅ Page counters should update without refresh")
    print("   ✅ All views should show consistent numbers")
    print("   ✅ 'Live' indicator should be green")
    print("\n🔍 6. Test Page Refresh:")
    print("   ✅ Refresh any page - counts should persist (not reset to 10)")
    print("   ✅ Navigate between pages - counts should remain consistent")
    print("   ✅ Open new tab - counts should be same as other tabs")

if __name__ == "__main__":
    print("🧪 COMPREHENSIVE COUNTER SYSTEM TEST")
    print("🎯 Testing all counting mechanisms for consistency")
    print()
    
    # Test backend APIs
    if test_backend_apis():
        print("\n🚀 Backend tests passed! Now testing real-time updates...")
        # Monitor real-time updates
        monitor_real_time_updates()
    else:
        print("\n❌ Backend tests failed! Fix backend issues first.")
    
    # Print frontend checklist
    print_frontend_checklist()
    
    print("\n🎯 EXPECTED RESULTS:")
    print("   ✅ All counter displays should show real database counts")
    print("   ✅ Page refresh should not reset counts to 10")
    print("   ✅ All pages should show identical counter values")
    print("   ✅ Real-time updates should work across all pages")
    print("   ✅ WebSocket and HTTP polling should both work")
