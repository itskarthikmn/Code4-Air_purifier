from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from datetime import datetime, timedelta
import json
import random
import numpy as np
from typing import Dict, List, Optional
from air_quality_model import AirQualityModel
import aiml
import os

# Purifier Configuration
PURIFIER_CONFIG = {
    "device_ip": os.getenv("PURIFIER_IP", "192.168.1.100"),  # Default IP, change to your purifier's IP
    "device_port": os.getenv("PURIFIER_PORT", "8080"),       # Default port
    "api_key": os.getenv("PURIFIER_API_KEY", ""),           # Your purifier's API key
    "device_id": os.getenv("PURIFIER_ID", ""),              # Your purifier's ID
}

app = FastAPI(title="Smart Air Purifier API")

# Mount static files and templates
app.mount("/static", StaticFiles(directory="."), name="static")
templates = Jinja2Templates(directory=".")

# Initialize AI models
air_quality_model = AirQualityModel()
air_quality_model.load_model()

# Initialize AIML brain
kernel = aiml.Kernel()
kernel.learn("aiml_brain/purifier_rules.aiml")

# Store historical data
historical_data = []
purifier_status = {}

class SensorData(BaseModel):
    pm25: float
    pm10: float
    no2: float
    so2: float
    co: float
    o3: float
    temperature: float
    humidity: float
    wind_speed: float
    traffic_density: float
    timestamp: str

class PurifierControl(BaseModel):
    power_level: float
    mode: str
    fan_speed: int

def generate_recommendations(aqi: float, sensor_data: Dict, power_level: float) -> Dict:
    """Generate AI-powered recommendations based on current conditions"""
    conditions = []
    
    # Air quality based recommendations
    if aqi <= 50:
        conditions.append("Air quality is good")
    elif aqi <= 100:
        conditions.append("Moderate air quality")
    else:
        conditions.append("Poor air quality")
    
    # Temperature based recommendations
    if sensor_data["temperature"] > 30:
        conditions.append("High temperature")
    elif sensor_data["temperature"] < 15:
        conditions.append("Low temperature")
    
    # Traffic based recommendations
    if sensor_data["traffic_density"] > 0.7:
        conditions.append("High traffic")
    
    # Get AIML recommendations
    aiml_input = " ".join(conditions)
    air_quality_rec = kernel.respond(f"AIR {aiml_input}")
    energy_rec = kernel.respond(f"ENERGY {aiml_input}")
    weather_rec = kernel.respond(f"WEATHER {aiml_input}")
    
    return {
        "air_quality": air_quality_rec or "Maintain current air quality levels",
        "energy": energy_rec or f"Current power level: {power_level*100:.1f}%",
        "weather": weather_rec or "No weather-specific recommendations"
    }

@app.get("/")
async def root(request):
    """Serve the dashboard"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/predict")
async def predict_aqi(data: SensorData):
    """Predict AQI and get recommendations"""
    global historical_data
    try:
        # Prepare features for prediction
        features = [
            data.pm25, data.pm10, data.no2, data.so2, data.co, data.o3,
            data.temperature, data.humidity, data.wind_speed, data.traffic_density
        ]
        
        # Get predictions
        aqi_value = air_quality_model.predict(features)
        
        # Calculate power level (0-1) based on AQI
        power_level = min(aqi_value / 200, 1.0)
        
        # Get AQI category
        if aqi_value <= 50:
            category = "GOOD"
        elif aqi_value <= 100:
            category = "MODERATE"
        elif aqi_value <= 150:
            category = "UNHEALTHY"
        elif aqi_value <= 200:
            category = "VERY_UNHEALTHY"
        else:
            category = "HAZARDOUS"
        
        # Generate recommendations
        recommendations = generate_recommendations(
            aqi_value,
            data.dict(),
            power_level
        )
        
        # Store historical data
        historical_data.append({
            "timestamp": data.timestamp,
            "aqi_value": aqi_value,
            "power_level": power_level,
            "sensor_data": data.dict()
        })
        
        # Keep only last 24 hours of data
        cutoff_time = datetime.now() - timedelta(hours=24)
        historical_data = [
            d for d in historical_data
            if datetime.fromisoformat(d["timestamp"]) > cutoff_time
        ]
        
        return {
            "aqi_value": aqi_value,
            "aqi_category": category,
            "power_level": power_level,
            "recommendations": recommendations
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/purifier/{purifier_id}/status")
async def get_purifier_status(purifier_id: str):
    """Get current status of a specific purifier"""
    if purifier_id not in purifier_status:
        purifier_status[purifier_id] = {
            "power_level": 0.5,
            "mode": "auto",
            "fan_speed": 2,
            "last_maintenance": datetime.now().isoformat(),
            "filter_life": random.uniform(0.3, 1.0)
        }
    return purifier_status[purifier_id]

@app.post("/purifier/{purifier_id}/control")
async def control_purifier(purifier_id: str, control: PurifierControl):
    """Update purifier controls"""
    if purifier_id not in purifier_status:
        purifier_status[purifier_id] = {}
    
    purifier_status[purifier_id].update(control.dict())
    return purifier_status[purifier_id]

@app.get("/analytics/daily")
async def get_daily_analytics():
    """Get analytics data for the last 24 hours"""
    return historical_data

@app.get("/analytics/efficiency")
async def get_efficiency_metrics():
    """Calculate efficiency metrics"""
    if not historical_data:
        return {
            "total_energy_consumption": 0,
            "average_aqi": 0,
            "peak_power_usage": 0,
            "estimated_daily_cost": 0
        }
    
    # Calculate metrics
    power_levels = [d["power_level"] for d in historical_data]
    aqi_values = [d["aqi_value"] for d in historical_data]
    
    # Assume each power level unit consumes 100W
    total_energy = sum(power_levels) * 0.1  # kWh
    avg_aqi = sum(aqi_values) / len(aqi_values)
    peak_power = max(power_levels)
    
    # Assume electricity cost of $0.12 per kWh
    daily_cost = total_energy * 0.12
    
    return {
        "total_energy_consumption": total_energy * 1000,  # Convert to Wh
        "average_aqi": avg_aqi,
        "peak_power_usage": peak_power,
        "estimated_daily_cost": daily_cost
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Handle WebSocket connections for real-time updates"""
    await websocket.accept()
    try:
        while True:
            # Receive sensor data
            data = await websocket.receive_text()
            sensor_data = json.loads(data)
            
            # Process data through prediction endpoint
            prediction_data = SensorData(**sensor_data)
            result = await predict_aqi(prediction_data)
            
            # Send back results
            await websocket.send_json(result)
    except Exception as e:
        print(f"WebSocket error: {str(e)}")
    finally:
        await websocket.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
