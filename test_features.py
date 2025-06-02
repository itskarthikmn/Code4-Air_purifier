import requests
import json
from datetime import datetime
import time

BASE_URL = "http://127.0.0.1:8000"

def test_predict_endpoint():
    """Test the AQI prediction endpoint"""
    print("\n1. Testing AQI Prediction Endpoint...")
    
    data = {
        "pm25": 35.5,
        "pm10": 75.2,
        "no2": 45.0,
        "so2": 20.0,
        "co": 1.2,
        "o3": 35.0,
        "temperature": 25.5,
        "humidity": 65.0,
        "wind_speed": 3.5,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    response = requests.post(f"{BASE_URL}/predict", json=data)
    print(f"Status Code: {response.status_code}")
    print("Response:", json.dumps(response.json(), indent=2))

def test_purifier_status():
    """Test getting purifier status"""
    print("\n2. Testing Purifier Status Endpoint...")
    
    response = requests.get(f"{BASE_URL}/purifier/lamp001/status")
    print(f"Status Code: {response.status_code}")
    print("Response:", json.dumps(response.json(), indent=2))

def test_purifier_control():
    """Test purifier control endpoint"""
    print("\n3. Testing Purifier Control Endpoint...")
    
    power_level = 0.75  # 75% power
    response = requests.post(f"{BASE_URL}/purifier/lamp001/control", params={"power_level": power_level})
    print(f"Status Code: {response.status_code}")
    print("Response:", json.dumps(response.json(), indent=2))

def test_analytics():
    """Test analytics endpoint"""
    print("\n4. Testing Analytics Endpoint...")
    
    response = requests.get(f"{BASE_URL}/analytics/daily")
    print(f"Status Code: {response.status_code}")
    print(f"Number of data points: {len(response.json())}")
    print("Sample data point:", json.dumps(response.json()[0], indent=2))

if __name__ == "__main__":
    print("Starting Feature Tests...")
    print("=" * 50)
    
    try:
        test_predict_endpoint()
        test_purifier_status()
        test_purifier_control()
        test_analytics()
        
        print("\nAll tests completed successfully!")
        print("=" * 50)
    except Exception as e:
        print(f"\nError during testing: {str(e)}")
