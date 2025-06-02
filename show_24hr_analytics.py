import requests
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

def fetch_analytics():
    """Fetch 24-hour analytics data"""
    response = requests.get("http://127.0.0.1:8000/analytics/daily")
    return response.json()

def create_24hr_dashboard(data):
    """Create an interactive 24-hour analytics dashboard"""
    df = pd.DataFrame(data)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Create figure with secondary y-axis
    fig = make_subplots(
        rows=3, cols=1,
        subplot_titles=(
            "Air Quality Index vs Purifier Power",
            "Hourly Performance Metrics",
            "Cumulative Energy Usage"
        ),
        vertical_spacing=0.12,
        specs=[[{"secondary_y": True}],
               [{"secondary_y": True}],
               [{"secondary_y": True}]]
    )
    
    # Plot 1: AQI and Power Level
    fig.add_trace(
        go.Scatter(
            x=df['timestamp'],
            y=df['aqi_value'],
            name="AQI",
            line=dict(color="#1f77b4", width=2)
        ),
        row=1, col=1,
        secondary_y=False
    )
    
    fig.add_trace(
        go.Scatter(
            x=df['timestamp'],
            y=[p * 100 for p in df['power_level']],
            name="Power Level (%)",
            line=dict(color="#d62728", width=2, dash='dash')
        ),
        row=1, col=1,
        secondary_y=True
    )
    
    # Plot 2: Hourly Performance
    efficiency_ratio = df['aqi_value'] / (df['power_level'] * 100)
    fig.add_trace(
        go.Bar(
            x=df['timestamp'],
            y=efficiency_ratio,
            name="Efficiency Ratio",
            marker_color="#2ecc71"
        ),
        row=2, col=1,
        secondary_y=False
    )
    
    # Plot 3: Cumulative Energy Usage
    energy_consumption = df['power_level'].cumsum() * 50  # Assuming 50W max power
    cost = energy_consumption * 0.12 / 1000  # $0.12 per kWh
    
    fig.add_trace(
        go.Scatter(
            x=df['timestamp'],
            y=energy_consumption,
            name="Energy (Wh)",
            fill='tozeroy',
            line=dict(color="#3498db")
        ),
        row=3, col=1,
        secondary_y=False
    )
    
    fig.add_trace(
        go.Scatter(
            x=df['timestamp'],
            y=cost,
            name="Cost ($)",
            line=dict(color="#e74c3c")
        ),
        row=3, col=1,
        secondary_y=True
    )
    
    # Add peak traffic period highlights
    morning_peak_start = df['timestamp'].iloc[7]  # 7 AM
    morning_peak_end = df['timestamp'].iloc[10]   # 10 AM
    evening_peak_start = df['timestamp'].iloc[16] # 4 PM
    evening_peak_end = df['timestamp'].iloc[19]   # 7 PM
    
    for row in [1, 2, 3]:
        fig.add_vrect(
            x0=morning_peak_start,
            x1=morning_peak_end,
            fillcolor="yellow",
            opacity=0.2,
            layer="below",
            line_width=0,
            row=row, col=1
        )
        
        fig.add_vrect(
            x0=evening_peak_start,
            x1=evening_peak_end,
            fillcolor="yellow",
            opacity=0.2,
            layer="below",
            line_width=0,
            row=row, col=1
        )
    
    # Update layout
    fig.update_layout(
        height=1000,
        title_text="24-Hour Smart Air Purifier Analytics Dashboard",
        showlegend=True,
        template="plotly_white"
    )
    
    # Update y-axes titles
    fig.update_yaxes(title_text="AQI Value", row=1, col=1, secondary_y=False)
    fig.update_yaxes(title_text="Power Level (%)", row=1, col=1, secondary_y=True)
    fig.update_yaxes(title_text="Efficiency Ratio", row=2, col=1, secondary_y=False)
    fig.update_yaxes(title_text="Energy (Wh)", row=3, col=1, secondary_y=False)
    fig.update_yaxes(title_text="Cost ($)", row=3, col=1, secondary_y=True)
    
    return fig

def print_summary_stats(df):
    """Print summary statistics"""
    print("\n24-Hour Performance Summary")
    print("=" * 50)
    
    # Calculate metrics
    avg_aqi = df['aqi_value'].mean()
    max_aqi = df['aqi_value'].max()
    min_aqi = df['aqi_value'].min()
    avg_power = df['power_level'].mean() * 100
    total_energy = df['power_level'].sum() * 50  # 50W max power
    total_cost = total_energy * 0.12 / 1000  # $0.12 per kWh
    
    # Air Quality Stats
    print("\nAir Quality Metrics:")
    print(f"Average AQI: {avg_aqi:.1f}")
    print(f"Maximum AQI: {max_aqi:.1f}")
    print(f"Minimum AQI: {min_aqi:.1f}")
    
    # Power Usage Stats
    print("\nPower Usage Metrics:")
    print(f"Average Power Level: {avg_power:.1f}%")
    print(f"Total Energy Consumption: {total_energy:.2f} Wh")
    print(f"Total Operating Cost: ${total_cost:.3f}")
    
    # Peak Hours Analysis
    peak_hours_df = df[
        (df['timestamp'].dt.hour.isin(range(7, 11))) |
        (df['timestamp'].dt.hour.isin(range(16, 20)))
    ]
    
    print("\nPeak Hours Performance:")
    print(f"Average AQI: {peak_hours_df['aqi_value'].mean():.1f}")
    print(f"Average Power Level: {peak_hours_df['power_level'].mean() * 100:.1f}%")
    
    # Efficiency Analysis
    efficiency_ratio = df['aqi_value'] / (df['power_level'] * 100)
    print("\nEfficiency Metrics:")
    print(f"Average Efficiency Ratio: {efficiency_ratio.mean():.2f}")
    print(f"Best Efficiency: {efficiency_ratio.max():.2f}")
    print(f"Worst Efficiency: {efficiency_ratio.min():.2f}")

def main():
    # Fetch data
    print("Fetching 24-hour analytics data...")
    data = fetch_analytics()
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Print summary statistics
    print_summary_stats(df)
    
    # Create and save dashboard
    fig = create_24hr_dashboard(data)
    output_file = "24hr_analytics_dashboard.html"
    fig.write_html(output_file)
    print(f"\nInteractive dashboard saved to {output_file}")

if __name__ == "__main__":
    main()
