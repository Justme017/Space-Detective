"""
Sky chart generation functions for the Space Detective application.

This module uses Plotly to create an interactive polar chart representing the 
sky, showing the positions of visible celestial objects.
"""

import plotly.graph_objects as go
import numpy as np
from datetime import datetime

# --- Constants ---

# Defines the visual properties for each type of celestial object on the chart
OBJECT_STYLES = {
    'Star': {'symbol': 'star', 'color': 'white', 'size': 16, 'label': 'Star'},
    'Planet': {'symbol': 'circle', 'color': 'gold', 'size': 22, 'label': 'Planet'},
    'Sun': {'symbol': 'circle', 'color': 'yellow', 'size': 32, 'label': 'Sun'},
    'Moon': {'symbol': 'circle', 'color': 'lightgray', 'size': 28, 'label': 'Moon'},
    'Satellite': {'symbol': 'diamond-open', 'color': 'cyan', 'size': 14, 'label': 'Satellite'},
    'Space Station': {'symbol': 'square-open', 'color': 'lime', 'size': 18, 'label': 'Space Station'},
    'Deep Sky': {'symbol': 'diamond', 'color': 'cyan', 'size': 18, 'label': 'Deep Sky'},
    'Other': {'symbol': 'circle-open', 'color': 'grey', 'size': 10, 'label': 'Other'}
}

# --- Private Helper Functions ---

def _add_object_traces(fig, objects):
    """
    Adds traces for each object type to the Plotly figure.
    """
    objects_by_type = {}
    for obj in objects:
        obj_type = obj.get('type', 'Other')
        objects_by_type.setdefault(obj_type, []).append(obj)

    for obj_type, type_objects in objects_by_type.items():
        style = OBJECT_STYLES.get(obj_type, OBJECT_STYLES['Other'])
        
        # Filter for objects with valid positions
        valid_objects = [o for o in type_objects if o.get('altitude', -1) >= 0]
        if not valid_objects:
            continue

        fig.add_trace(go.Scatterpolar(
            r=[obj['altitude'] for obj in valid_objects],
            theta=[obj['azimuth'] for obj in valid_objects],
            mode='markers+text',
            name=style['label'],
            text=[obj.get('name', 'Unknown') for obj in valid_objects],
            textfont=dict(size=13, color='skyblue', family="Arial Black"),
            textposition="bottom center",
            marker=dict(
                symbol=style['symbol'],
                color=style['color'],
                size=style['size'],
                line=dict(width=1.5, color='black') if obj_type in ['Sun', 'Moon', 'Planet'] else None
            ),
            hoverinfo='text',
            hovertext=[f"{obj.get('name', 'Unknown')}<br>Alt: {obj['altitude']:.1f}°<br>Az: {obj['azimuth']:.1f}°" for obj in valid_objects]
        ))

def _configure_layout(fig, lat, lon, dt_utc, zoom):
    """
    Configures the layout of the sky chart.
    """
    local_time_str = dt_utc.astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
    title_text = f"Sky Chart for Lat: {lat:.2f}, Lon: {lon:.2f}<br>At {local_time_str}"
    
    # Adjust radial axis range based on zoom level
    r_span = 90 / zoom
    r_center = 45
    r_min = max(r_center - r_span / 2, 0)
    r_max = min(r_center + r_span / 2, 90)

    fig.update_layout(
        title=dict(text=title_text, font=dict(size=20, color='gold'), y=0.98, x=0.5, xanchor='center', yanchor='top'),
        showlegend=True,
        legend=dict(font=dict(color='white', size=16), bgcolor='rgba(44, 83, 100, 0.9)', bordercolor='gold', borderwidth=2, x=1.05, y=0.5),
        paper_bgcolor='#0f2027',
        polar=dict(
            bgcolor='#050A0E',
            radialaxis=dict(
                visible=True, range=[r_min, r_max], tickvals=np.arange(0, 91, 15),
                ticktext=[f'{alt}°' for alt in np.arange(0, 91, 15)],
                angle=90, showline=True, showticklabels=True, gridcolor='#303040',
                linecolor='lightgrey', tickfont=dict(color='white', size=14)
            ),
            angularaxis=dict(
                visible=True, direction="clockwise", rotation=90, tickvals=np.arange(0, 360, 45),
                ticktext=['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'],
                showline=True, showticklabels=True, gridcolor='#303040',
                linecolor='lightgrey', tickfont=dict(color='white', size=14)
            )
        ),
        margin=dict(l=40, r=40, t=100, b=40)
    )

# --- Public API ---

def create_sky_chart(objects, observer_lat, observer_lon, dt_utc, zoom=1.0):
    """
    Generates an interactive sky chart of visible objects using Plotly.

    Args:
        objects (list): A list of visible astronomical objects.
        observer_lat (float): The observer's latitude.
        observer_lon (float): The observer's longitude.
        dt_utc (datetime): The observation time in UTC.
        zoom (float): The zoom level for the chart.

    Returns:
        go.Figure or None: A Plotly Figure object, or None if no objects are provided.
    """
    if not objects:
        return None

    try:
        fig = go.Figure()
        _add_object_traces(fig, objects)
        _configure_layout(fig, observer_lat, observer_lon, dt_utc, zoom)
        return fig
    except Exception as e:
        print(f"Error creating Plotly sky chart: {e}")
        return None

# --- Test Block ---

if __name__ == '__main__':
    from datetime import datetime, timezone

    print("Testing Plotly Sky Chart Generation...")
    
    # Comprehensive mock data for testing
    mock_objects = [
        {'name': 'Sun', 'azimuth': 90, 'altitude': 30, 'type': 'Sun'},
        {'name': 'Moon', 'azimuth': 180, 'altitude': 60, 'type': 'Moon'},
        {'name': 'Mars', 'azimuth': 270, 'altitude': 45, 'type': 'Planet'},
        {'name': 'Sirius', 'azimuth': 120, 'altitude': 20, 'type': 'Star'},
        {'name': 'Orion Nebula', 'azimuth': 75, 'altitude': 45, 'type': 'Deep Sky'},
        {'name': 'Hubble Space Telescope', 'azimuth': 210, 'altitude': 50, 'type': 'Satellite'},
        {'name': 'International Space Station', 'azimuth': 330, 'altitude': 55, 'type': 'Space Station'},
        {'name': 'Object Below Horizon', 'azimuth': 150, 'altitude': -10, 'type': 'Star'}
    ]
    
    mock_lat, mock_lon = 34.05, -118.24
    mock_dt = datetime.utcnow().replace(tzinfo=timezone.utc)

    sky_chart_fig = create_sky_chart(mock_objects, mock_lat, mock_lon, mock_dt, zoom=1.5)

    if sky_chart_fig:
        sky_chart_fig.write_html("test_plotly_skychart.html")
        print("Test Plotly sky chart saved to test_plotly_skychart.html")
    else:
        print("Failed to generate test Plotly sky chart.")
