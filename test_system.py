import requests
import json
import websockets
import asyncio
import time
from datetime import datetime
import plotly.graph_objects as go

class SmartAirPurifierTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.ws_url = "ws://localhost:8000/ws"
        self.headers = {"Content-Type": "application/json"}
        
    def test_aqi_prediction(self):
        """Test AQI prediction endpoint"""
        print("\n1. Testing AQI Prediction Endpoint")
        print("----------------------------------")
        
        test_data = {
            "pm25": 25.0,
            "pm10": 45.0,
            "no2": 30.0,
            "so2": 20.0,
            "co": 5.0,
            "o3": 35.0,
            "temperature": 25.0,
            "humidity": 60.0,
            "wind_speed": 3.0,
            "traffic_density": 0.4,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/predict",
                headers=self.headers,
                json=test_data
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✓ AQI Prediction successful")
                print(f"  - AQI Value: {result['aqi_value']:.1f}")
                print(f"  - Category: {result['aqi_category']}")
                print(f"  - Power Level: {result['power_level']*100:.1f}%")
                print("\nRecommendations:")
                print(f"  - Air Quality: {result['recommendations']['air_quality']}")
                print(f"  - Energy: {result['recommendations']['energy']}")
                if 'weather' in result['recommendations']:
                    print(f"  - Weather: {result['recommendations']['weather']}")
            else:
                print(f"✗ Error: {response.status_code}")
                print(response.text)
        except Exception as e:
            print(f"✗ Error: {str(e)}")
    
    def test_purifier_control(self):
        """Test purifier control endpoints"""
        print("\n2. Testing Purifier Control")
        print("--------------------------")
        
        purifier_id = "test_purifier_1"
        
        # Test status endpoint
        try:
            response = requests.get(f"{self.base_url}/purifier/{purifier_id}/status")
            if response.status_code == 200:
                print("✓ Status check successful")
                print(f"  Current status: {json.dumps(response.json(), indent=2)}")
            else:
                print(f"✗ Status check failed: {response.status_code}")
        except Exception as e:
            print(f"✗ Error checking status: {str(e)}")
        
        # Test control endpoint
        control_data = {
            "power_level": 0.7,
            "mode": "auto",
            "fan_speed": 3
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/purifier/{purifier_id}/control",
                headers=self.headers,
                json=control_data
            )
            
            if response.status_code == 200:
                print("✓ Control update successful")
                print(f"  Updated status: {json.dumps(response.json(), indent=2)}")
            else:
                print(f"✗ Control update failed: {response.status_code}")
        except Exception as e:
            print(f"✗ Error updating control: {str(e)}")
    
    def test_analytics(self):
        """Test analytics endpoints"""
        print("\n3. Testing Analytics")
        print("------------------")
        
        # Test daily analytics
        try:
            response = requests.get(f"{self.base_url}/analytics/daily")
            if response.status_code == 200:
                data = response.json()
                print("✓ Daily analytics retrieved successfully")
                print(f"  Number of data points: {len(data)}")
                
                # Create a simple visualization
                timestamps = [entry['timestamp'] for entry in data]
                aqi_values = [entry['aqi_value'] for entry in data]
                power_levels = [entry['power_level'] * 100 for entry in data]
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=timestamps, y=aqi_values, name='AQI'))
                fig.add_trace(go.Scatter(x=timestamps, y=power_levels, name='Power %'))
                fig.update_layout(title='24-Hour Performance')
                fig.write_html("analytics_test.html")
                print("  Analytics visualization saved to 'analytics_test.html'")
            else:
                print(f"✗ Failed to get daily analytics: {response.status_code}")
        except Exception as e:
            print(f"✗ Error retrieving analytics: {str(e)}")
        
        # Test efficiency metrics
        try:
            response = requests.get(f"{self.base_url}/analytics/efficiency")
            if response.status_code == 200:
                metrics = response.json()
                print("\nEfficiency Metrics:")
                print(f"  - Total Energy: {metrics['total_energy_consumption']:.2f} Wh")
                print(f"  - Average AQI: {metrics['average_aqi']:.1f}")
                print(f"  - Peak Power: {metrics['peak_power_usage']*100:.1f}%")
                print(f"  - Daily Cost: ${metrics['estimated_daily_cost']:.3f}")
            else:
                print(f"✗ Failed to get efficiency metrics: {response.status_code}")
        except Exception as e:
            print(f"✗ Error retrieving efficiency metrics: {str(e)}")
    
    async def test_websocket(self):
        """Test WebSocket connection"""
        print("\n4. Testing WebSocket Connection")
        print("-----------------------------")
        
        try:
            async with websockets.connect(self.ws_url) as websocket:
                print("✓ WebSocket connected successfully")
                
                # Send test data
                test_data = {
                    "pm25": 30.0,
                    "pm10": 50.0,
                    "no2": 35.0,
                    "so2": 25.0,
                    "co": 6.0,
                    "o3": 40.0,
                    "temperature": 26.0,
                    "humidity": 65.0,
                    "wind_speed": 4.0,
                    "traffic_density": 0.5,
                    "timestamp": datetime.now().isoformat()
                }
                
                await websocket.send(json.dumps(test_data))
                print("  Sent test data")
                
                # Wait for response
                response = await websocket.recv()
                result = json.loads(response)
                print("  Received real-time update:")
                print(f"  - AQI: {result['aqi_value']:.1f}")
                print(f"  - Power Level: {result['power_level']*100:.1f}%")
                print(f"  - Recommendations updated: {len(result['recommendations'])}")
        except Exception as e:
            print(f"✗ WebSocket test failed: {str(e)}")
    
    def run_all_tests(self):
        """Run all tests"""
        print("\nSmart Air Purifier System Test")
        print("=============================")
        print(f"Testing against: {self.base_url}")
        print(f"Time: {datetime.now().isoformat()}")
        print("\nRunning all tests...")
        
        self.test_aqi_prediction()
        self.test_purifier_control()
        self.test_analytics()
        
        # Run WebSocket test
        asyncio.get_event_loop().run_until_complete(self.test_websocket())
        
        print("\nTest Suite Completed!")

if __name__ == "__main__":
    tester = SmartAirPurifierTester()
    tester.run_all_tests()
