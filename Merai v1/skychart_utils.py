import matplotlib.pyplot as plt
import numpy as np
import io
from datetime import datetime

def create_sky_chart(objects, observer_lat, observer_lon, dt_utc):
    """
    Generates a sky chart of visible objects.

    Args:
        objects (list): A list of dictionaries, where each dictionary represents a celestial object
                        and must contain 'name', 'azimuth' (in degrees), 'altitude' (in degrees),
                        and 'type' (e.g., 'Star', 'Planet', 'Sun', 'Moon').
        observer_lat (float): Observer's latitude.
        observer_lon (float): Observer's longitude.
        dt_utc (datetime): The datetime object (UTC) for which the chart is generated.

    Returns:
        io.BytesIO: A BytesIO object containing the PNG image of the sky chart, or None if error.
    """
    if not objects:
        return None

    try:
        fig = plt.figure(figsize=(10, 10), facecolor='#0f2027') # Match app background
        ax = fig.add_subplot(111, projection='polar')
        ax.set_facecolor('#050A0E') # Darker background for the plot area (deep space)

        # Configure the polar plot
        ax.set_theta_zero_location("N")  # North at the top
        ax.set_theta_direction(-1)       # Clockwise (East to the right)
        ax.set_rlim(0, 90)               # Radius represents 90 - altitude (zenith at center)
        ax.set_rticks(np.arange(0, 91, 15)) # Ticks from 90 (zenith) to 0 (horizon)
        ax.set_rlabel_position(0)
        
        # Invert r-axis so 90 is at the center (zenith) and 0 is at the edge (horizon)
        ax.set_ylim(90, 0)
        
        alt_labels = [str(90 - int(r)) + '°' for r in ax.get_yticks()]
        ax.set_yticklabels(alt_labels)

        # More subtle grid lines
        ax.grid(True, color='#303040', linestyle=':', linewidth=0.4, alpha=0.6) 
        ax.tick_params(axis='x', colors='lightgrey') # Azimuth ticks
        ax.tick_params(axis='y', colors='lightgrey') # Altitude ticks (radial)
        plt.setp(ax.spines.values(), color='lightgrey', alpha=0.7) # Make spines slightly less prominent

        # Define markers and colors
        markers = {
            'Star': {'marker': '*', 'color': 'white', 'size': 20, 'alpha': 0.85, 'label': 'Star'},
            'Planet': {'marker': 'o', 'color': 'gold', 'size': 50, 'label': 'Planet'},
            'Sun': {'marker': 'o', 'color': 'yellow', 'size': 100, 'label': 'Sun'},
            'Moon': {'marker': 'o', 'color': 'lightgray', 'size': 80, 'label': 'Moon'},
            'Deep Sky': {'marker': 's', 'color': 'cyan', 'size': 30, 'label': 'Deep Sky'}
        }
        default_marker = {'marker': '.', 'color': 'grey', 'size': 10, 'alpha': 0.7, 'label': 'Other'}

        plotted_labels = set() 

        for obj in objects:
            name = obj.get('name', 'Unknown')
            azimuth_deg = obj.get('azimuth')
            altitude_deg = obj.get('altitude')
            obj_type = obj.get('type', 'Other')

            if azimuth_deg is None or altitude_deg is None or altitude_deg < 0: 
                continue

            azimuth_rad = np.deg2rad(azimuth_deg)
            r = 90 - altitude_deg 

            style = markers.get(obj_type, default_marker)
            
            current_label = style['label']
            if current_label not in plotted_labels:
                ax.scatter(azimuth_rad, r, s=style['size'], color=style['color'], 
                           marker=style['marker'], alpha=style.get('alpha', 1.0), label=current_label,
                           edgecolors='black' if obj_type in ['Sun', 'Moon', 'Planet'] else 'none') 
                plotted_labels.add(current_label)
            else:
                 ax.scatter(azimuth_rad, r, s=style['size'], color=style['color'], 
                           marker=style['marker'], alpha=style.get('alpha', 1.0),
                           edgecolors='black' if obj_type in ['Sun', 'Moon', 'Planet'] else 'none')

            # Annotate prominent objects
            if obj_type in ['Sun', 'Moon', 'Planet'] or (obj_type == 'Star' and altitude_deg > 10): 
                ax.text(azimuth_rad, r + 3, name, color='skyblue', fontsize=7, ha='center', va='bottom', alpha=0.85)
        
        # Add cardinal direction labels
        for angle, label in [(0, 'N'), (np.pi/2, 'E'), (np.pi, 'S'), (3*np.pi/2, 'W')]:
            ax.text(angle, ax.get_rmax() + 7, label, ha='center', va='center', color='lightgrey', fontsize=12, fontweight='bold')

        # Legend
        if plotted_labels:
            legend = ax.legend(loc='lower left', bbox_to_anchor=(1.05, 0), facecolor='#2c5364', edgecolor='gold', labelcolor='white', fontsize=9)
            for text in legend.get_texts():
                text.set_color('white')

        # Title
        local_time_str = dt_utc.astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
        title = f"Sky Chart for Lat: {observer_lat:.2f}, Lon: {observer_lon:.2f}\nAt {local_time_str}"
        ax.set_title(title, va='bottom', color='gold', fontsize=14, pad=25)

        # Save to BytesIO
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', facecolor=fig.get_facecolor(), dpi=150)
        plt.close(fig) 
        buf.seek(0)
        return buf

    except Exception as e:
        print(f"Error creating sky chart: {e}") 
        return None

if __name__ == '__main__':
    # Example Usage (for testing skychart_utils.py directly)
    print("Testing Matplotlib Sky Chart Generation...")
    
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

    sky_chart_image = create_sky_chart(mock_objects, mock_lat, mock_lon, mock_dt)

    if sky_chart_image:
        with open("test_matplotlib_skychart.png", "wb") as f:
            f.write(sky_chart_image.getvalue())
        print("Test Matplotlib sky chart saved to test_matplotlib_skychart.png")
        # To display immediately (optional):
        # from PIL import Image
        # Image.open(sky_chart_image).show()
    else:
        print("Failed to generate test Matplotlib sky chart.")
