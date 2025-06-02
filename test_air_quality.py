import requests
import json
import time
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"

def test_air_quality_scenario(scenario_name, data):
    """Test system response to different air quality scenarios"""
    print(f"\nTesting {scenario_name} Scenario:")
    print("-" * 50)
    
    # Add timestamp to data
    data["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        # Get purifier response
        response = requests.post(f"{BASE_URL}/predict", json=data)
        result = response.json()
        
        print(f"AQI Value: {result.get('aqi_value', 'N/A')}")
        print(f"Category: {result.get('aqi_category', 'N/A')}")
        print(f"Power Level: {result.get('power_level', 'N/A') * 100}%")
        print(f"Recommendation: {result.get('recommendations', {}).get('air_quality', 'N/A')}")
        print(f"Energy Status: {result.get('recommendations', {}).get('energy', 'N/A')}")
        
    except Exception as e:
        print(f"Error: {str(e)}")

# Test Scenarios
scenarios = {
    "Good Air Quality": {
        "pm25": 10.0,
        "pm10": 20.0,
        "no2": 15.0,
        "so2": 10.0,
        "co": 0.5,
        "o3": 20.0,
        "temperature": 22.0,
        "humidity": 50.0,
        "wind_speed": 5.0,
        "traffic_density": 0.2
    },
    "Moderate Pollution": {
        "pm25": 35.0,
        "pm10": 75.0,
        "no2": 45.0,
        "so2": 30.0,
        "co": 1.2,
        "o3": 45.0,
        "temperature": 25.0,
        "humidity": 60.0,
        "wind_speed": 3.0,
        "traffic_density": 0.5
    },
    "Heavy Pollution": {
        "pm25": 150.0,
        "pm10": 250.0,
        "no2": 120.0,
        "so2": 75.0,
        "co": 4.5,
        "o3": 90.0,
        "temperature": 30.0,
        "humidity": 70.0,
        "wind_speed": 1.5,
        "traffic_density": 0.8
    },
    "Critical Pollution": {
        "pm25": 300.0,
        "pm10": 450.0,
        "no2": 200.0,
        "so2": 150.0,
        "co": 9.0,
        "o3": 180.0,
        "temperature": 35.0,
        "humidity": 80.0,
        "wind_speed": 1.0,
        "traffic_density": 0.9
    }
}

if __name__ == "__main__":
    print("Starting Air Quality Scenario Tests")
    print("=" * 50)
    
    for scenario_name, scenario_data in scenarios.items():
        test_air_quality_scenario(scenario_name, scenario_data)
        time.sleep(2)  # Wait between tests
        
    print("\nAll scenarios tested!")
    print("=" * 50)
