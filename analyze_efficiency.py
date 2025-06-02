import requests
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

def fetch_data():
    """Fetch 24-hour analytics data"""
    response = requests.get("http://127.0.0.1:8000/analytics/daily")
    return response.json()

def calculate_efficiency_metrics(df):
    """Calculate energy efficiency metrics"""
    # Calculate AQI improvement per unit power
    df['efficiency_ratio'] = df['aqi_value'] / (df['power_level'] * 100)
    
    # Calculate energy consumption (simplified model)
    # Assuming 50W at 100% power
    MAX_POWER_WATTS = 50
    df['energy_consumption'] = df['power_level'] * MAX_POWER_WATTS
    
    # Calculate cost (assuming $0.12 per kWh)
    COST_PER_KWH = 0.12
    df['hourly_cost'] = (df['energy_consumption'] * COST_PER_KWH) / 1000
    
    return {
        'total_energy': df['energy_consumption'].sum(),
        'total_cost': df['hourly_cost'].sum(),
        'avg_efficiency': df['efficiency_ratio'].mean(),
        'peak_efficiency': df.loc[df['efficiency_ratio'].idxmax()],
        'lowest_efficiency': df.loc[df['efficiency_ratio'].idxmin()]
    }

def create_efficiency_dashboard(df, metrics):
    """Create an interactive efficiency dashboard"""
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            "Power Usage vs. Air Quality",
            "Efficiency Ratio Over Time",
            "Hourly Energy Consumption",
            "Cost Analysis"
        )
    )
    
    # Power vs AQI scatter plot
    fig.add_trace(
        go.Scatter(
            x=df['power_level'] * 100,
            y=df['aqi_value'],
            mode='markers',
            name='AQI vs Power',
            marker=dict(
                size=8,
                color=df['efficiency_ratio'],
                colorscale='Viridis',
                showscale=True
            )
        ),
        row=1, col=1
    )
    
    # Efficiency ratio over time
    fig.add_trace(
        go.Scatter(
            x=df['timestamp'],
            y=df['efficiency_ratio'],
            name='Efficiency Ratio',
            line=dict(color='#2ecc71')
        ),
        row=1, col=2
    )
    
    # Energy consumption bar chart
    fig.add_trace(
        go.Bar(
            x=df['timestamp'],
            y=df['energy_consumption'],
            name='Energy (Wh)',
            marker_color='#3498db'
        ),
        row=2, col=1
    )
    
    # Cost analysis
    fig.add_trace(
        go.Scatter(
            x=df['timestamp'],
            y=df['hourly_cost'],
            name='Cost ($)',
            fill='tozeroy',
            line=dict(color='#e74c3c')
        ),
        row=2, col=2
    )
    
    # Update layout
    fig.update_layout(
        height=800,
        title_text="Smart Air Purifier Efficiency Analysis",
        showlegend=True,
        template="plotly_white"
    )
    
    # Update axes labels
    fig.update_xaxes(title_text="Power Level (%)", row=1, col=1)
    fig.update_yaxes(title_text="AQI Value", row=1, col=1)
    
    fig.update_xaxes(title_text="Time", row=1, col=2)
    fig.update_yaxes(title_text="Efficiency Ratio", row=1, col=2)
    
    fig.update_xaxes(title_text="Time", row=2, col=1)
    fig.update_yaxes(title_text="Energy (Wh)", row=2, col=1)
    
    fig.update_xaxes(title_text="Time", row=2, col=2)
    fig.update_yaxes(title_text="Cost ($)", row=2, col=2)
    
    return fig

def main():
    print("Analyzing energy efficiency...")
    
    # Fetch and process data
    data = fetch_data()
    df = pd.DataFrame(data)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Calculate metrics
    metrics = calculate_efficiency_metrics(df)
    
    # Print efficiency report
    print("\nEfficiency Report")
    print("=" * 50)
    print(f"Total Energy Consumption: {metrics['total_energy']:.2f} Wh")
    print(f"Total Operating Cost: ${metrics['total_cost']:.2f}")
    print(f"Average Efficiency Ratio: {metrics['avg_efficiency']:.2f}")
    
    print("\nPeak Efficiency:")
    peak = metrics['peak_efficiency']
    print(f"Time: {peak['timestamp']}")
    print(f"AQI: {peak['aqi_value']:.1f}")
    print(f"Power Level: {peak['power_level']*100:.1f}%")
    print(f"Efficiency Ratio: {peak['efficiency_ratio']:.2f}")
    
    print("\nLowest Efficiency:")
    lowest = metrics['lowest_efficiency']
    print(f"Time: {lowest['timestamp']}")
    print(f"AQI: {lowest['aqi_value']:.1f}")
    print(f"Power Level: {lowest['power_level']*100:.1f}%")
    print(f"Efficiency Ratio: {lowest['efficiency_ratio']:.2f}")
    
    # Create and save dashboard
    fig = create_efficiency_dashboard(df, metrics)
    output_file = "efficiency_dashboard.html"
    fig.write_html(output_file)
    print(f"\nEfficiency dashboard saved to {output_file}")

if __name__ == "__main__":
    main()
