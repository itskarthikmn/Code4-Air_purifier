import requests
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

def fetch_analytics():
    """Fetch 24-hour analytics data from the API"""
    response = requests.get("http://127.0.0.1:8000/analytics/daily")
    return response.json()

def create_analytics_dashboard(data):
    """Create an interactive analytics dashboard"""
    # Convert data to pandas DataFrame
    df = pd.DataFrame(data)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Add AQI trace
    fig.add_trace(
        go.Scatter(
            x=df['timestamp'],
            y=df['aqi_value'],
            name="Air Quality Index",
            line=dict(color="#1f77b4", width=2)
        ),
        secondary_y=False
    )
    
    # Add Power Level trace
    fig.add_trace(
        go.Scatter(
            x=df['timestamp'],
            y=[p * 100 for p in df['power_level']],  # Convert to percentage
            name="Purifier Power Level (%)",
            line=dict(color="#d62728", width=2, dash='dash')
        ),
        secondary_y=True
    )
    
    # Add shapes for time periods
    fig.add_vrect(
        x0=df['timestamp'].iloc[7],  # 7 AM
        x1=df['timestamp'].iloc[10],  # 10 AM
        fillcolor="yellow",
        opacity=0.2,
        layer="below",
        line_width=0,
        annotation_text="Morning Peak",
        annotation_position="top left"
    )
    
    fig.add_vrect(
        x0=df['timestamp'].iloc[16],  # 4 PM
        x1=df['timestamp'].iloc[19],  # 7 PM
        fillcolor="yellow",
        opacity=0.2,
        layer="below",
        line_width=0,
        annotation_text="Evening Peak",
        annotation_position="top left"
    )
    
    # Update layout
    fig.update_layout(
        title="24-Hour Air Quality and Purifier Performance Analysis",
        xaxis_title="Time",
        yaxis_title="Air Quality Index",
        yaxis2_title="Power Level (%)",
        hovermode='x unified',
        showlegend=True,
        template="plotly_white"
    )
    
    # Calculate key statistics
    stats = {
        "Average AQI": df['aqi_value'].mean(),
        "Max AQI": df['aqi_value'].max(),
        "Min AQI": df['aqi_value'].min(),
        "Average Power": df['power_level'].mean() * 100,
        "Peak Hours Power": df.loc[
            (df['timestamp'].dt.hour.isin(range(7, 11))) |
            (df['timestamp'].dt.hour.isin(range(16, 20))),
            'power_level'
        ].mean() * 100
    }
    
    return fig, stats

def main():
    # Fetch data
    print("Fetching analytics data...")
    data = fetch_analytics()
    
    # Create dashboard
    fig, stats = create_analytics_dashboard(data)
    
    # Print statistics
    print("\nKey Statistics:")
    print("-" * 50)
    print(f"Average AQI: {stats['Average AQI']:.1f}")
    print(f"Maximum AQI: {stats['Max AQI']:.1f}")
    print(f"Minimum AQI: {stats['Min AQI']:.1f}")
    print(f"Average Power Level: {stats['Average Power']:.1f}%")
    print(f"Average Power During Peak Hours: {stats['Peak Hours Power']:.1f}%")
    
    # Save the plot as HTML
    output_file = "analytics_dashboard.html"
    fig.write_html(output_file)
    print(f"\nAnalytics dashboard saved to {output_file}")
    print("Open this file in your web browser to view the interactive visualization")

if __name__ == "__main__":
    main()
