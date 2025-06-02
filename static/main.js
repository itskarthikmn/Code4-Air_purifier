// WebSocket connection
let ws = null;
let powerGauge = null;
let analyticsChart = null;

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    initializeWebSocket();
    initializePowerGauge();
    initializeAnalyticsChart();
    startDataSimulation();
});

function initializeWebSocket() {
    ws = new WebSocket('ws://localhost:8000/ws');
    
    ws.onopen = function() {
        console.log('WebSocket connected');
        sendSensorData();  // Start sending data
    };
    
    ws.onmessage = function(event) {
        const data = JSON.parse(event.data);
        updateDashboard(data);
    };
    
    ws.onclose = function() {
        console.log('WebSocket disconnected');
        setTimeout(initializeWebSocket, 5000);  // Reconnect after 5 seconds
    };
}

function initializePowerGauge() {
    const gaugeData = {
        type: "indicator",
        mode: "gauge+number",
        value: 0,
        title: { text: "Power Level" },
        gauge: {
            axis: { range: [0, 100] },
            bar: { color: "#3498db" },
            bgcolor: "white",
            borderwidth: 2,
            bordercolor: "#ccc",
            steps: [
                { range: [0, 30], color: "#2ecc71" },
                { range: [30, 70], color: "#f1c40f" },
                { range: [70, 100], color: "#e74c3c" }
            ]
        }
    };
    
    Plotly.newPlot('power-gauge', [gaugeData], {
        width: 200,
        height: 200,
        margin: { t: 25, b: 25, l: 25, r: 25 }
    });
    
    powerGauge = document.getElementById('power-gauge');
}

function initializeAnalyticsChart() {
    fetch('/analytics/daily')
        .then(response => response.json())
        .then(data => {
            const timestamps = data.map(d => d.timestamp);
            const aqiValues = data.map(d => d.aqi_value);
            const powerLevels = data.map(d => d.power_level * 100);
            
            const trace1 = {
                x: timestamps,
                y: aqiValues,
                name: 'AQI',
                type: 'scatter',
                line: { color: '#3498db' }
            };
            
            const trace2 = {
                x: timestamps,
                y: powerLevels,
                name: 'Power Level (%)',
                type: 'scatter',
                line: { color: '#e74c3c' }
            };
            
            const layout = {
                showlegend: true,
                legend: { orientation: 'h' },
                margin: { t: 10, l: 40, r: 40, b: 40 },
                xaxis: { title: 'Time' },
                yaxis: { title: 'Value' }
            };
            
            Plotly.newPlot('analytics-chart', [trace1, trace2], layout);
            analyticsChart = document.getElementById('analytics-chart');
        });
}

function updateDashboard(data) {
    // Update AQI
    document.getElementById('aqi-value').textContent = Math.round(data.aqi_value);
    document.getElementById('aqi-category').textContent = data.aqi_category;
    updateAqiIndicator(data.aqi_value);
    
    // Update power level
    const powerLevel = Math.round(data.power_level * 100);
    document.getElementById('power-level').textContent = `${powerLevel}%`;
    Plotly.update('power-gauge', { 'value': [powerLevel] });
    
    // Update recommendations
    document.getElementById('air-quality-rec').innerHTML = 
        `<i class='bx bx-bulb text-primary'></i> ${data.recommendations.air_quality}`;
    document.getElementById('energy-rec').innerHTML = 
        `<i class='bx bx-energy text-success'></i> ${data.recommendations.energy}`;
    document.getElementById('weather-rec').innerHTML = 
        `<i class='bx bx-cloud text-info'></i> ${data.recommendations.weather}`;
    
    // Update environmental conditions if available
    if (data.sensor_data) {
        document.getElementById('temperature').textContent = 
            `${data.sensor_data.temperature.toFixed(1)}°C`;
        document.getElementById('humidity').textContent = 
            `${data.sensor_data.humidity.toFixed(1)}%`;
        document.getElementById('wind-speed').textContent = 
            `${data.sensor_data.wind_speed.toFixed(1)} m/s`;
        document.getElementById('traffic-density').textContent = 
            getTrafficLevel(data.sensor_data.traffic_density);
    }
}

function updateAqiIndicator(aqi) {
    const indicator = document.getElementById('aqi-indicator');
    indicator.className = 'status-indicator';
    
    if (aqi <= 50) {
        indicator.classList.add('good');
    } else if (aqi <= 100) {
        indicator.classList.add('moderate');
    } else if (aqi <= 150) {
        indicator.classList.add('unhealthy');
    } else if (aqi <= 200) {
        indicator.classList.add('very-unhealthy');
    } else {
        indicator.classList.add('hazardous');
    }
}

function getTrafficLevel(density) {
    if (density <= 0.3) return 'Low';
    if (density <= 0.7) return 'Moderate';
    return 'High';
}

function sendSensorData() {
    if (ws && ws.readyState === WebSocket.OPEN) {
        // Simulate sensor data
        const data = {
            pm25: Math.random() * 100,
            pm10: Math.random() * 150,
            no2: Math.random() * 100,
            so2: Math.random() * 50,
            co: Math.random() * 10,
            o3: Math.random() * 100,
            temperature: 20 + Math.random() * 15,
            humidity: 30 + Math.random() * 50,
            wind_speed: Math.random() * 10,
            traffic_density: Math.random(),
            timestamp: new Date().toISOString()
        };
        
        ws.send(JSON.stringify(data));
    }
}

function startDataSimulation() {
    // Send sensor data every 5 seconds
    setInterval(sendSensorData, 5000);
}

// Handle window resize for charts
window.addEventListener('resize', function() {
    if (powerGauge) {
        Plotly.Plots.resize(powerGauge);
    }
    if (analyticsChart) {
        Plotly.Plots.resize(analyticsChart);
    }
});
