import plotly.graph_objects as go
import numpy as np
from datetime import datetime

def create_sky_chart(objects, observer_lat, observer_lon, dt_utc, zoom=1.0):
    """
    Generates an interactive sky chart of visible objects using Plotly.
    Returns a Plotly Figure object.
    """
    if not objects:
        return None

    try:
        fig = go.Figure()
        # Define styles for different object types
        styles = {
            'Star': {'symbol': 'star', 'color': 'white', 'size': 16, 'opacity': 1, 'label': 'Star'},
            'Planet': {'symbol': 'circle', 'color': 'gold', 'size': 22, 'label': 'Planet'},
            'Sun': {'symbol': 'circle', 'color': 'yellow', 'size': 32, 'label': 'Sun'},
            'Moon': {'symbol': 'circle', 'color': 'lightgray', 'size': 28, 'label': 'Moon'},
            'Deep Sky': {'symbol': 'diamond', 'color': 'cyan', 'size': 18, 'label': 'Deep Sky'},
            'Other': {'symbol': 'circle-open', 'color': 'grey', 'size': 10, 'label': 'Other'}
        }
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
                if az is None or alt is None or alt < 0:
                    continue
                azimuths_deg.append(az)
                altitudes_deg.append(alt)
                object_names.append(obj.get('name', 'Unknown'))
                hover_texts.append(f"{obj.get('name', 'Unknown')}<br>Alt: {alt:.1f}°<br>Az: {az:.1f}°")
            if not azimuths_deg: continue
            fig.add_trace(go.Scatterpolar(
                r=altitudes_deg,
                theta=azimuths_deg,
                mode='markers+text',
                name=style['label'],
                text=object_names,
                textfont=dict(size=13, color='skyblue', family="Arial Black"),
                textposition="bottom center",
                marker=dict(
                    symbol=style['symbol'],
                    color=style['color'],
                    size=style['size'],
                    opacity=style.get('opacity', 1.0),
                    line=dict(width=1.5, color='black') if obj_type in ['Sun', 'Moon', 'Planet'] else None
                ),
                hoverinfo='text',
                hovertext=hover_texts,
                subplot='polar'
            ))
        local_time_str = dt_utc.astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
        title_text = f"Sky Chart for Lat: {observer_lat:.2f}, Lon: {observer_lon:.2f}<br>At {local_time_str}"
        # Calculate zoomed range
        min_r, max_r = 0, 90
        r_center = 45
        r_span = (max_r - min_r) / zoom
        r_min = max(r_center - r_span/2, 0)
        r_max = min(r_center + r_span/2, 90)
        fig.update_layout(
            title=dict(text=title_text, font=dict(size=20, color='gold'), y=0.98, x=0.5, xanchor='center', yanchor='top'),
            showlegend=True,
            legend=dict(font=dict(color='white', size=16), bgcolor='rgba(44, 83, 100, 0.9)', bordercolor='gold', borderwidth=2, x=1.05, y=0.5),
            paper_bgcolor='#0f2027',
            polar=dict(
                bgcolor='#050A0E',
                radialaxis=dict(
                    visible=True,
                    range=[r_min, r_max],
                    tickvals=np.arange(0, 91, 15),
                    ticktext=[str(alt) + '°' for alt in np.arange(0, 91, 15)],
                    angle=90,
                    showline=True,
                    showticklabels=True,
                    gridcolor='#303040',
                    linecolor='lightgrey',
                    tickfont=dict(color='white', size=14)
                ),
                angularaxis=dict(
                    visible=True,
                    direction="clockwise",
                    rotation=90,
                    tickvals=np.arange(0, 360, 45),
                    ticktext=['N (0°)', 'NE (45°)', 'E (90°)', 'SE (135°)', 'S (180°)', 'SW (225°)', 'W (270°)', 'NW (315°)'],
                    showline=True,
                    showticklabels=True,
                    gridcolor='#303040',
                    linecolor='lightgrey',
                    tickfont=dict(color='white', size=14)
                ),
                hole=0.0
            ),
            margin=dict(l=40, r=40, t=100, b=40)
        )
        return fig
    except Exception as e:
        print(f"Error creating Plotly sky chart: {e}")
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

    sky_chart_fig = create_sky_chart(mock_objects, mock_lat, mock_lon, mock_dt)

    if sky_chart_fig:
        # Save as HTML file
        sky_chart_fig.write_html("test_plotly_skychart.html", include_plotlyjs='cdn')
        print("Test Plotly sky chart saved to test_plotly_skychart.html")
        # To display immediately (optional, requires internet for Plotly JS):
        # sky_chart_fig.show()
    else:
        print("Failed to generate test Plotly sky chart.")
