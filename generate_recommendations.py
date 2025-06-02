import requests
import pandas as pd
import aiml
from datetime import datetime

def fetch_data():
    """Fetch 24-hour analytics data"""
    response = requests.get("http://127.0.0.1:8000/analytics/daily")
    return response.json()

def analyze_patterns(df):
    """Analyze usage patterns and identify optimization opportunities"""
    patterns = {
        'peak_usage_hours': df[df['power_level'] > df['power_level'].mean()].index.tolist(),
        'low_efficiency_periods': df[df['efficiency_ratio'] < df['efficiency_ratio'].mean()].index.tolist(),
        'high_aqi_periods': df[df['aqi_value'] > 100].index.tolist()
    }
    return patterns

def get_aiml_recommendations(kernel, metrics):
    """Get AI-powered recommendations based on performance metrics"""
    recommendations = []
    
    # Get energy efficiency recommendation
    if metrics['avg_power'] > 0.7:
        energy_status = "HIGH_USAGE"
    elif metrics['avg_power'] > 0.4:
        energy_status = "MODERATE_USAGE"
    else:
        energy_status = "EFFICIENT_USAGE"
    
    recommendations.append(kernel.respond(f"ENERGY_EFFICIENCY {energy_status}"))
    
    # Get air quality recommendation
    if metrics['avg_aqi'] > 150:
        aqi_status = "HAZARDOUS"
    elif metrics['avg_aqi'] > 100:
        aqi_status = "UNHEALTHY"
    elif metrics['avg_aqi'] > 50:
        aqi_status = "MODERATE"
    else:
        aqi_status = "GOOD"
    
    recommendations.append(kernel.respond(f"AIR_QUALITY {aqi_status}"))
    
    return recommendations

def calculate_potential_savings(df):
    """Calculate potential energy and cost savings"""
    # Assume we can reduce power by 10% during low AQI periods
    low_aqi_periods = df[df['aqi_value'] <= 50]
    potential_power_reduction = 0.1  # 10% reduction
    
    current_energy = (df['power_level'] * 50).sum()  # 50W max power
    potential_energy = current_energy - (low_aqi_periods['power_level'] * 50 * potential_power_reduction).sum()
    
    savings = {
        'energy_savings': current_energy - potential_energy,
        'cost_savings': (current_energy - potential_energy) * 0.12 / 1000,  # $0.12 per kWh
        'optimization_periods': len(low_aqi_periods)
    }
    return savings

def main():
    print("Generating Smart Air Purifier Recommendations")
    print("=" * 50)
    
    # Initialize AIML kernel
    kernel = aiml.Kernel()
    kernel.learn("aiml_brain/purifier_rules.aiml")
    
    # Fetch and process data
    data = fetch_data()
    df = pd.DataFrame(data)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Calculate efficiency ratio
    df['efficiency_ratio'] = df['aqi_value'] / (df['power_level'] * 100)
    
    # Calculate metrics
    metrics = {
        'avg_power': df['power_level'].mean(),
        'avg_aqi': df['aqi_value'].mean(),
        'peak_power_time': df.loc[df['power_level'].idxmax(), 'timestamp'],
        'lowest_efficiency_time': df.loc[df['efficiency_ratio'].idxmin(), 'timestamp']
    }
    
    # Get patterns
    patterns = analyze_patterns(df)
    
    # Get AIML recommendations
    recommendations = get_aiml_recommendations(kernel, metrics)
    
    # Calculate potential savings
    savings = calculate_potential_savings(df)
    
    # Print recommendations report
    print("\n1. Current Performance Analysis:")
    print("-" * 50)
    print(f"Average Power Usage: {metrics['avg_power']*100:.1f}%")
    print(f"Average Air Quality Index: {metrics['avg_aqi']:.1f}")
    print(f"Peak Power Usage: {df['power_level'].max()*100:.1f}% at {metrics['peak_power_time']}")
    print(f"Lowest Efficiency: at {metrics['lowest_efficiency_time']}")
    
    print("\n2. AI Recommendations:")
    print("-" * 50)
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec}")
    
    print("\n3. Optimization Opportunities:")
    print("-" * 50)
    print(f"• Identified {savings['optimization_periods']} periods for power optimization")
    print(f"• Potential Daily Energy Savings: {savings['energy_savings']:.2f} Wh")
    print(f"• Potential Monthly Cost Savings: ${savings['cost_savings']*30:.2f}")
    
    print("\n4. Smart Features Recommendations:")
    print("-" * 50)
    print("• Enable adaptive power mode during off-peak hours")
    print("• Implement predictive air quality monitoring")
    print("• Use weather forecast data for proactive adjustments")
    print("• Enable night mode for quieter operation during sleeping hours")
    
    print("\n5. Maintenance Recommendations:")
    print("-" * 50)
    print("• Schedule filter cleaning during low AQI periods")
    print("• Monitor filter efficiency during peak pollution hours")
    print("• Calibrate sensors monthly for optimal performance")
    print("• Update AI models with local air quality patterns")

if __name__ == "__main__":
    main()
