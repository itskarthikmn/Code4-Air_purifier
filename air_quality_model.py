import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import joblib
import os
from datetime import datetime
from typing import Dict, List, Tuple

class AirQualityModel:
    def __init__(self):
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.model_path = 'air_quality_model.joblib'
        self.scaler_path = 'scaler.joblib'
        
        # Initialize with sample data if model doesn't exist
        if not os.path.exists(self.model_path):
            self._initialize_with_sample_data()
    
    def _initialize_with_sample_data(self):
        """Initialize model with sample data for demonstration"""
        print("Initializing model with sample data...")
        
        # Generate sample data
        np.random.seed(42)
        n_samples = 1000
        
        # Generate features with realistic ranges
        features = np.zeros((n_samples, 10))
        
        # PM2.5 (0-500 μg/m³)
        features[:, 0] = np.random.uniform(0, 500, n_samples)
        
        # PM10 (0-600 μg/m³)
        features[:, 1] = np.random.uniform(0, 600, n_samples)
        
        # NO2 (0-200 ppb)
        features[:, 2] = np.random.uniform(0, 200, n_samples)
        
        # SO2 (0-100 ppb)
        features[:, 3] = np.random.uniform(0, 100, n_samples)
        
        # CO (0-50 ppm)
        features[:, 4] = np.random.uniform(0, 50, n_samples)
        
        # O3 (0-200 ppb)
        features[:, 5] = np.random.uniform(0, 200, n_samples)
        
        # Temperature (0-50°C)
        features[:, 6] = np.random.uniform(0, 50, n_samples)
        
        # Humidity (0-100%)
        features[:, 7] = np.random.uniform(0, 100, n_samples)
        
        # Wind Speed (0-20 m/s)
        features[:, 8] = np.random.uniform(0, 20, n_samples)
        
        # Traffic Density (0-1)
        features[:, 9] = np.random.uniform(0, 1, n_samples)
        
        # Generate AQI values based on feature combinations
        aqi_values = np.zeros(n_samples)
        
        for i in range(n_samples):
            # Calculate base AQI from main pollutants
            pm25_aqi = features[i, 0] * 0.8
            pm10_aqi = features[i, 1] * 0.6
            no2_aqi = features[i, 2] * 1.2
            so2_aqi = features[i, 3] * 1.5
            co_aqi = features[i, 4] * 3
            o3_aqi = features[i, 5] * 1.1
            
            # Take maximum AQI from pollutants
            base_aqi = max(pm25_aqi, pm10_aqi, no2_aqi, so2_aqi, co_aqi, o3_aqi)
            
            # Add environmental effects
            temp_effect = abs(features[i, 6] - 25) * 0.5  # Deviation from 25°C
            humidity_effect = features[i, 7] * 0.2
            wind_effect = -features[i, 8] * 2  # Wind reduces AQI
            traffic_effect = features[i, 9] * 50
            
            # Combine all effects
            aqi_values[i] = max(0, min(500, base_aqi + temp_effect + humidity_effect + wind_effect + traffic_effect))
        
        # Fit scaler
        self.scaler.fit(features)
        scaled_features = self.scaler.transform(features)
        
        # Train model
        self.model.fit(scaled_features, aqi_values)
        
        # Save model and scaler
        self.save_model()
    
    def predict(self, features):
        """Predict AQI value from sensor data"""
        if isinstance(features, (list, tuple)):
            features = np.array(features).reshape(1, -1)
        elif isinstance(features, dict):
            features = np.array([
                features['pm25'],
                features['pm10'],
                features['no2'],
                features['so2'],
                features['co'],
                features['o3'],
                features['temperature'],
                features['humidity'],
                features['wind_speed'],
                features['traffic_density']
            ]).reshape(1, -1)
        
        # Scale features
        scaled_features = self.scaler.transform(features)
        
        # Make prediction
        aqi_prediction = self.model.predict(scaled_features)[0]
        
        # Ensure prediction is within valid range
        return max(0, min(500, aqi_prediction))
    
    def save_model(self):
        """Save model and scaler to disk"""
        try:
            joblib.dump(self.model, self.model_path)
            joblib.dump(self.scaler, self.scaler_path)
            return True
        except Exception as e:
            print(f"Error saving model: {str(e)}")
            return False
    
    def load_model(self):
        """Load model and scaler from disk"""
        try:
            if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
                self.model = joblib.load(self.model_path)
                self.scaler = joblib.load(self.scaler_path)
                return True
            return False
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            return False

class PurifierOptimizer:
    def __init__(self):
        self.power_thresholds = {
            'GOOD': 0.3,      # 30% power when air quality is good
            'MODERATE': 0.5,  # 50% power for moderate air quality
            'UNHEALTHY': 0.7, # 70% power for unhealthy air
            'VERY_UNHEALTHY': 0.9,  # 90% power for very unhealthy air
            'HAZARDOUS': 1.0  # 100% power for hazardous conditions
        }
        
    def get_aqi_category(self, aqi_value: float) -> str:
        """Get AQI category based on value"""
        if aqi_value <= 50:
            return 'GOOD'
        elif aqi_value <= 100:
            return 'MODERATE'
        elif aqi_value <= 150:
            return 'UNHEALTHY'
        elif aqi_value <= 200:
            return 'VERY_UNHEALTHY'
        else:
            return 'HAZARDOUS'
    
    def calculate_power_level(self, aqi_value: float, conditions: Dict) -> float:
        """Calculate optimal power level based on AQI and conditions"""
        base_power = self.power_thresholds[self.get_aqi_category(aqi_value)]
        
        # Adjust for environmental conditions
        if conditions['humidity'] > 70:  # High humidity
            base_power *= 1.2
        if conditions['temperature'] > 30:  # High temperature
            base_power *= 1.1
        if conditions['traffic_density'] > 0.7:  # High traffic
            base_power *= 1.15
            
        # Night time reduction (if available)
        hour = datetime.now().hour
        if 22 <= hour or hour <= 5:  # Night time
            base_power *= 0.8
            
        return min(1.0, base_power)  # Cap at 100% power
    
    def calculate_energy_cost(self, power_level: float, duration_hours: float, 
                            rate_per_kwh: float = 0.12) -> float:
        """Calculate energy cost for given power level and duration"""
        # Assume max power consumption is 50W (0.05 kW)
        power_consumption = 0.05 * power_level * duration_hours
        return power_consumption * rate_per_kwh
    
    def optimize_schedule(self, daily_aqi_pattern: List[float], 
                         peak_hours: List[tuple]) -> List[float]:
        """Optimize purifier schedule for 24 hours"""
        schedule = []
        for hour, aqi in enumerate(daily_aqi_pattern):
            power = self.power_thresholds[self.get_aqi_category(aqi)]
            
            # Reduce power during non-peak hours if air quality is good
            if aqi <= 50 and not any(start <= hour <= end for start, end in peak_hours):
                power *= 0.8
                
            schedule.append(min(1.0, power))
            
        return schedule
