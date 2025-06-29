import plotly.graph_objects as go
import numpy as np
from datetime import datetime
from skyfield.api import Star, load, Topos
from skyfield.projections import build_stereographic_projection
from skyfield.framelib import ecliptic_frame

def create_sky_chart(objects, t, lat, lon, zoom=1.0):
    """
    Generates an interactive sky chart of visible objects using Plotly.
    Returns a Plotly Figure object.
    """
    if not objects:
        # Return an empty figure with a message if no objects are visible
        fig = go.Figure()
        fig.update_layout(
            paper_bgcolor='#0f2027',
            plot_bgcolor='#050A0E',
            annotations=[
                dict(
                    text="No celestial objects are currently visible.",
                    showarrow=False,
                    font=dict(color="white", size=16)
                )
            ]
        )
        return fig

    try:
        ts = load.timescale()
        # Ensure t is a Skyfield Time object
        if isinstance(t, datetime):
            t = ts.from_datetime(t)
        elif not hasattr(t, 'tt'):
            # Fallback for unexpected formats
            t = ts.now()

        # Correctly initialize the observer
        eph = load('de421.bsp')
        earth = eph['earth']
        observer = earth + Topos(latitude_degrees=lat, longitude_degrees=lon)

        # The projection needs a time-specific observer position
        projection = build_stereographic_projection(observer.at(t))

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
            
            # Get positions for each object type
            positions = []
            # This part requires that star objects have ra_hours and dec_degrees
            for obj in type_objects:
                if obj_type == 'Star':
                    # Stars need their coordinates from the catalog data
                    if 'ra_hours' in obj and 'dec_degrees' in obj:
                        star = Star(ra_hours=obj['ra_hours'], dec_degrees=obj['dec_degrees'])
                        positions.append(observer.at(t).observe(star).apparent())
                else:
                    # For Sun, Moon, and Planets, observe them directly by name
                    try:
                        body = eph[obj['name'].lower()]
                        positions.append(observer.at(t).observe(body).apparent())
                    except (KeyError, AttributeError):
                        # Skip if the object name is not in the ephemeris (e.g., 'Pluto')
                        continue

            if not positions:
                continue

            # Project all positions at once
            # Note: altaz() returns altitude, azimuth, distance. We need alt and az.
            alts = [pos.altaz()[0].degrees for pos in positions]
            azs = [pos.altaz()[1].degrees for pos in positions]
            
            # Get other data for the trace
            object_names = [obj.get('name', 'Unknown') for obj in type_objects]
            hover_texts = [f"{name}<br>Alt: {alt:.1f}°<br>Az: {az:.1f}°" 
                           for name, alt, az in zip(object_names, alts, azs)]

            # Filter out objects below the horizon
            visible_indices = [i for i, alt in enumerate(alts) if alt >= 0]
            if not visible_indices:
                continue

            fig.add_trace(go.Scatterpolar(
                r=[alts[i] for i in visible_indices],
                theta=[azs[i] for i in visible_indices],
                mode='markers+text',
                name=style['label'],
                text=[object_names[i] for i in visible_indices],
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
                hovertext=[hover_texts[i] for i in visible_indices],
                subplot='polar'
            ))

        # Convert Skyfield Time to a Python datetime object for formatting.
        local_dt = t.utc_datetime()
        # Ensure local_dt is a scalar datetime, not an array
        if isinstance(local_dt, np.ndarray):
            local_dt = local_dt.item()
        local_time_str = local_dt.strftime("%Y-%m-%d %H:%M:%S UTC")

        title_text = f"Sky Chart for {local_time_str}"
        # Calculate zoomed range, centered on the zenith (90 degrees).
        # A zoom of 1.0 shows the full sky from 0 to 90 degrees.
        # A zoom > 1.0 zooms in, showing a smaller altitude range from a value > 0 up to 90.
        # A zoom < 1.0 is clamped to 1.0 to prevent zooming out beyond the full view.
        zoom_level = max(1.0, zoom)
        r_max = 90
        r_min = r_max - (90 / zoom_level)

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
        # Return an empty figure with an error message
        fig = go.Figure()
        fig.update_layout(
            paper_bgcolor='#0f2027',
            plot_bgcolor='#050A0E',
            annotations=[
                dict(
                    text=f"Error: Could not generate sky chart.",
                    showarrow=False,
                    font=dict(color="red", size=16)
                )
            ]
        )
        return fig

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

    sky_chart_fig = create_sky_chart(mock_objects, mock_dt, mock_lat, mock_lon)

    if sky_chart_fig:
        # Save as HTML file
        sky_chart_fig.write_html("test_plotly_skychart.html", include_plotlyjs='cdn')
        print("Test Plotly sky chart saved to test_plotly_skychart.html")
        # To display immediately (optional, requires internet for Plotly JS):
        # sky_chart_fig.show()
    else:
        print("Failed to generate test Plotly sky chart.")
