#!/usr/bin/env python3
"""
Test script for the new Reports functionality
"""
import requests
import json
from datetime import datetime, timedelta

def test_reports_api():
    """Test the reports API endpoints"""
    base_url = "http://localhost:5002"
    
    print("🧪 Testing Reports API Endpoints")
    print("=" * 50)
    
    # Test data for requests
    test_date_range = {
        "start": (datetime.now() - timedelta(days=7)).isoformat(),
        "end": datetime.now().isoformat()
    }
    
    # Test alerts report
    print("\n📊 Testing Alerts Report...")
    try:
        response = requests.post(f"{base_url}/api/reports/alerts", 
                               json={
                                   "format": "pdf",
                                   "dateRange": test_date_range,
                                   "includeBreakdown": True,
                                   "includeTrends": True
                               },
                               timeout=30)
        
        if response.status_code == 200:
            print("✅ Alerts PDF report generated successfully")
            print(f"   Response size: {len(response.content)} bytes")
        else:
            print(f"❌ Alerts report failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing alerts report: {e}")
    
    # Test predictions report
    print("\n📈 Testing Predictions Report...")
    try:
        response = requests.post(f"{base_url}/api/reports/predictions", 
                               json={
                                   "format": "excel",
                                   "dateRange": test_date_range,
                                   "includeAccuracy": True,
                                   "includeTrends": True
                               },
                               timeout=30)
        
        if response.status_code == 200:
            print("✅ Predictions Excel report generated successfully")
            print(f"   Response size: {len(response.content)} bytes")
        else:
            print(f"❌ Predictions report failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing predictions report: {e}")
    
    # Test diagrams report
    print("\n🎨 Testing Diagrams Report...")
    try:
        response = requests.post(f"{base_url}/api/reports/diagrams", 
                               json={
                                   "type": "complete",
                                   "dateRange": test_date_range,
                                   "includeAnalysis": True
                               },
                               timeout=30)
        
        if response.status_code == 200:
            print("✅ Diagrams complete report generated successfully")
            print(f"   Response size: {len(response.content)} bytes")
        else:
            print(f"❌ Diagrams report failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing diagrams report: {e}")
    
    # Test system report
    print("\n⚙️ Testing System Report...")
    try:
        response = requests.post(f"{base_url}/api/reports/system", 
                               json={
                                   "type": "comprehensive",
                                   "dateRange": test_date_range,
                                   "includePerformance": True,
                                   "includeHealth": True
                               },
                               timeout=30)
        
        if response.status_code == 200:
            print("✅ System comprehensive report generated successfully")
            print(f"   Response size: {len(response.content)} bytes")
        else:
            print(f"❌ System report failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing system report: {e}")
    
    # Test custom report
    print("\n🔧 Testing Custom Report...")
    try:
        response = requests.post(f"{base_url}/api/reports/custom", 
                               json={
                                   "dateRange": test_date_range,
                                   "sections": {
                                       "includeAlerts": True,
                                       "includePredictions": True,
                                       "includeDiagrams": False,
                                       "includePerformance": True
                                   }
                               },
                               timeout=30)
        
        if response.status_code == 200:
            print("✅ Custom report generated successfully")
            print(f"   Response size: {len(response.content)} bytes")
        else:
            print(f"❌ Custom report failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing custom report: {e}")
    
    # Test scheduled report
    print("\n⏰ Testing Scheduled Report...")
    try:
        response = requests.post(f"{base_url}/api/reports/schedule", 
                               json={
                                   "frequency": "weekly",
                                   "reportType": "alerts",
                                   "dateRange": test_date_range
                               },
                               timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Scheduled report created successfully")
            print(f"   Schedule ID: {data.get('scheduleId', 'N/A')}")
        else:
            print(f"❌ Scheduled report failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing scheduled report: {e}")
    
    print("\n" + "=" * 50)
    print("✨ Reports API testing completed!")
    print("\n📋 To test the full UI:")
    print("   1. Start the Flask server: python app.py")
    print("   2. Start the frontend dev server: npm run dev")
    print("   3. Open http://localhost:3000/reports")
    print("   4. Test report generation and downloads")

def test_frontend_integration():
    """Test that the frontend can access the reports page"""
    print("\n🌐 Testing Frontend Integration...")
    
    # Check if frontend dev server is running
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend dev server is running")
            print("📱 Reports page should be available at: http://localhost:3000/reports")
        else:
            print("❌ Frontend dev server returned error")
    except Exception as e:
        print("❌ Frontend dev server is not running")
        print("   Start it with: npm run dev")

if __name__ == "__main__":
    print("🚀 FroidPredict Reports Testing Suite")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    test_reports_api()
    test_frontend_integration()
    
    print(f"\n⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
