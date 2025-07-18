#!/usr/bin/env python3
"""
Quick test script to verify the reports API functionality
"""
import requests
import json

BASE_URL = "http://localhost:5002"

def test_api_endpoint(endpoint, method='GET', data=None):
    """Test an API endpoint"""
    url = f"{BASE_URL}{endpoint}"
    try:
        if method == 'GET':
            response = requests.get(url, timeout=10)
        elif method == 'POST':
            response = requests.post(url, json=data, timeout=30)
        
        print(f"\n🌐 Testing {method} {endpoint}")
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            if 'application/json' in response.headers.get('content-type', ''):
                content = response.json()
                print(f"JSON Response (first 500 chars): {str(content)[:500]}...")
            else:
                print(f"Response Size: {len(response.content)} bytes")
                print(f"Content Type: {response.headers.get('content-type')}")
        else:
            print(f"Error Response: {response.text[:500]}")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ Error testing {endpoint}: {e}")
        return False

def main():
    print("🧪 Testing Reports API functionality")
    print("=" * 50)
    
    # Test basic data endpoints
    test_api_endpoint('/api/alerts')
    test_api_endpoint('/api/predictions')
    
    # Test reports generation
    report_data = {
        'format': 'excel',
        'dateRange': {
            'start': '2024-07-11T00:00',
            'end': '2024-07-18T23:59'
        },
        'includeBreakdown': True,
        'includeTrends': True
    }
    
    print("\n" + "=" * 50)
    print("🧪 Testing Reports Generation")
    print("=" * 50)
    
    test_api_endpoint('/api/reports/alerts', 'POST', report_data)
    test_api_endpoint('/api/reports/predictions', 'POST', report_data)
    
    # Test system report
    system_data = {
        'type': 'summary',
        'dateRange': report_data['dateRange'],
        'includePerformance': True,
        'includeHealth': True
    }
    
    test_api_endpoint('/api/reports/system', 'POST', system_data)

if __name__ == "__main__":
    main()
