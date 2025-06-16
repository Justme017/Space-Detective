import plotly.graph_objects as go
import numpy as np
from datetime import datetime
from skyfield.api import utc # Import utc for the test block

def create_sky_chart(objects, observer_lat, observer_lon, dt_utc):
    """
    Generates an interactive sky chart of visible objects using Plotly.

    Args:
        objects (list): A list of dictionaries, where each dictionary represents a celestial object
                        and must contain 'name', 'azimuth' (in degrees), 'altitude' (in degrees),
                        and 'type' (e.g., 'Star', 'Planet', 'Sun', 'Moon').
        observer_lat (float): Observer's latitude.
        observer_lon (float): Observer's longitude.
        dt_utc (datetime): The datetime object (UTC) for which the chart is generated.

    Returns:
        plotly.graph_objects.Figure: A Plotly Figure object for the sky chart, or None if error.
    """
    if not objects:
        return None

    try:
        fig = go.Figure()

        # Define styles for different object types
        styles = {
            'Star': {'symbol': 'asterisk', 'color': 'white', 'size': 7, 'opacity': 0.9, 'label': 'Star'},
            'Planet': {'symbol': 'circle', 'color': 'gold', 'size': 12, 'label': 'Planet'},
            'Sun': {'symbol': 'circle', 'color': 'yellow', 'size': 20, 'label': 'Sun'},
            'Moon': {'symbol': 'circle', 'color': 'lightgray', 'size': 16, 'label': 'Moon'},
            'Deep Sky': {'symbol': 'square', 'color': 'cyan', 'size': 8, 'label': 'Deep Sky'},
            'Other': {'symbol': 'circle-open', 'color': 'grey', 'size': 6, 'label': 'Other'}
        }

        # Group objects by type for potentially different traces / legend entries
        objects_by_type = {}
        for obj in objects:
            obj_type = obj.get('type', 'Other')
            if obj_type not in objects_by_type:
                objects_by_type[obj_type] = []
            objects_by_type[obj_type].append(obj)

        for obj_type, type_objects in objects_by_type.items():
            if not type_objects: continue

            style = styles.get(obj_type, styles['Other'])
            azimuths_deg = []
            altitudes_deg = []
            object_names = []
            hover_texts = []

            for obj in type_objects:
                az = obj.get('azimuth')
                alt = obj.get('altitude')
                if az is None or alt is None or alt < 0: # Skip objects below horizon
                    continue
                
                azimuths_deg.append(az)
                # For Plotly polar, r is distance from center. We want altitude.
                # Plotly's polar chart has theta in degrees by default.
                # r=0 is horizon, r=90 is zenith if we map altitude directly to r.
                altitudes_deg.append(alt)
                object_names.append(obj.get('name', 'Unknown'))
                hover_texts.append(f"{obj.get('name', 'Unknown')}<br>Alt: {alt:.1f}°<br>Az: {az:.1f}°")

            if not azimuths_deg: continue # Skip if no valid objects of this type

            fig.add_trace(go.Scatterpolar(
                r=altitudes_deg,          # Altitude directly as radius
                theta=azimuths_deg,       # Azimuth as theta
                mode='markers+text',      # Show markers and text (names)
                name=style['label'],
                text=object_names,        # Text to display next to markers
                textfont=dict(size=7, color='skyblue', family="Arial"),
                textposition="bottom center",
                marker=dict(
                    symbol=style['symbol'],
                    color=style['color'],
                    size=style['size'],
                    opacity=style.get('opacity', 1.0),
                    line=dict(width=0.5, color='DarkSlateGrey') if obj_type in ['Sun', 'Moon', 'Planet'] else None
                ),
                hoverinfo='text',
                hovertext=hover_texts,
                subplot='polar'
            ))

        local_time_str = dt_utc.astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
        title_text = f"Sky Chart for Lat: {observer_lat:.2f}, Lon: {observer_lon:.2f}<br>At {local_time_str}"

        fig.update_layout(
            title=dict(text=title_text, font=dict(size=14, color='gold'), y=0.98, x=0.5, xanchor='center', yanchor='top'),
            showlegend=True,
            legend=dict(font=dict(color='white'), bgcolor='rgba(44, 83, 100, 0.7)', bordercolor='gold', borderwidth=1, x=1.05, y=0.5),
            paper_bgcolor='#0f2027', # Overall chart background
            polar=dict(
                bgcolor='#050A0E',    # Plot area background (deep space)
                radialaxis=dict(
                    visible=True,
                    range=[0, 90],      # Altitude from 0 (horizon) to 90 (zenith)
                    tickvals=np.arange(0, 91, 15),
                    ticktext=[str(alt) + '°' for alt in np.arange(0, 91, 15)],
                    angle=90,           # Position of radial axis labels (e.g., 90 for right side)
                    showline=True,
                    showticklabels=True,
                    gridcolor='#303040',
                    linecolor='lightgrey',
                    tickfont=dict(color='lightgrey')
                ),
                angularaxis=dict(
                    visible=True,
                    direction="clockwise",
                    rotation=90,        # Makes 0 degrees (North) point upwards
                    tickvals=np.arange(0, 360, 45),
                    ticktext=['N (0°)', 'NE (45°)', 'E (90°)', 'SE (135°)', 'S (180°)', 'SW (225°)', 'W (270°)', 'NW (315°)'],
                    showline=True,
                    showticklabels=True,
                    gridcolor='#303040',
                    linecolor='lightgrey',
                    tickfont=dict(color='lightgrey')
                ),
                hole=0.0 # Optional: if you want a hole in the center like a donut chart
            ),
            margin=dict(l=40, r=40, t=80, b=40) # Adjust margins for title/legend
        )

        return fig

    except Exception as e:
        print(f"Error creating Plotly sky chart: {e}") # For debugging
        return None

if __name__ == '__main__':
    # Example Usage (for testing skychart_utils.py directly)
    print("Testing Plotly Sky Chart Generation...")
    
    # Sample objects (replace with actual data from astro_utils)
    mock_objects = [
        {'name': 'Sun', 'azimuth': 90, 'altitude': 30, 'type': 'Sun'},
        {'name': 'Moon', 'azimuth': 180, 'altitude': 60, 'type': 'Moon'},
        {'name': 'Mars', 'azimuth': 270, 'altitude': 45, 'type': 'Planet'},
        {'name': 'Jupiter', 'azimuth': 0, 'altitude': 75, 'type': 'Planet'},
        {'name': 'Sirius', 'azimuth': 120, 'altitude': 20, 'type': 'Star', 'hip_id': 'HIP32349'},
        {'name': 'Canopus', 'azimuth': 200, 'altitude': 10, 'type': 'Star', 'hip_id': 'HIP30438'},
        {'name': 'Betelgeuse', 'azimuth': 70, 'altitude': 50, 'type': 'Star', 'hip_id': 'HIP27989'},
        {'name': 'Rigel', 'azimuth': 80, 'altitude': 40, 'type': 'Star', 'hip_id': 'HIP24436'},
        {'name': 'Polaris', 'azimuth': 0, 'altitude': 44, 'type': 'Star', 'hip_id': 'HIP11767'}, 
        {'name': 'Orion Nebula', 'azimuth': 75, 'altitude': 45, 'type': 'Deep Sky'}
    ]
    
    mock_lat = 34.0522
    mock_lon = -118.2437
    # For testing, ensure utc is available if not running within Skyfield context
    try:
        from skyfield.api import utc
        mock_dt = datetime.utcnow().replace(tzinfo=utc)
    except ImportError:
        from datetime import timezone
        mock_dt = datetime.utcnow().replace(tzinfo=timezone.utc) # Fallback if skyfield not in test path

    plotly_fig = create_sky_chart(mock_objects, mock_lat, mock_lon, mock_dt)

    if plotly_fig:
        plotly_fig.write_html("test_plotly_skychart.html")
        print("Test Plotly sky chart saved to test_plotly_skychart.html")
        # To display in a browser window immediately (optional):
        # plotly_fig.show()
    else:
        print("Failed to generate test Plotly sky chart.")
