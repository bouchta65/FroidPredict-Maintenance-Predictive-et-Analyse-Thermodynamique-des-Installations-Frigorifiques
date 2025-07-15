#!/usr/bin/env python3
"""
Test script for real-time API endpoints
Run this to verify that the new API endpoints are working correctly
"""

import requests
import time
import json

BASE_URL = "http://localhost:5000"

def test_endpoint(endpoint, description):
    """Test a specific API endpoint"""
    try:
        response = requests.get(f"{BASE_URL}{endpoint}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {description}")
            print(f"   URL: {endpoint}")
            print(f"   Response: {json.dumps(data, indent=2)}")
        else:
            print(f"❌ {description} - Status: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print(f"🔌 {description} - Server not running")
    except Exception as e:
        print(f"⚠️ {description} - Error: {e}")
    print()

def main():
    """Test all real-time API endpoints"""
    print("🚀 Testing Real-time API Endpoints")
    print("=" * 50)
    
    # Test predictions count
    test_endpoint("/api/predictions/count", "Predictions Count API")
    
    # Test alerts count
    test_endpoint("/api/alerts/count", "Alerts Count API")
    
    # Test system status
    test_endpoint("/api/system/status", "System Status API")
    
    # Test original endpoints for comparison
    test_endpoint("/api/system_status", "Original System Status API")
    
    print("🔄 Testing real-time updates (5 seconds)")
    for i in range(5):
        try:
            response = requests.get(f"{BASE_URL}/api/predictions/count")
            if response.status_code == 200:
                data = response.json()
                timestamp = data.get('timestamp', 'N/A')
                count = data.get('count', 0)
                print(f"   [{i+1}/5] Predictions: {count} at {timestamp}")
            time.sleep(1)
        except:
            print(f"   [{i+1}/5] Connection failed")
    
    print("\n✨ Test completed!")

if __name__ == "__main__":
    main()
