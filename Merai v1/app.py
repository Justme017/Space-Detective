from flask import Flask, render_template, request
from datetime import datetime, date
from skyfield.api import utc
import folium
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from astro_utils import get_visible_objects
from wiki_utils import get_object_image_url, get_object_description, extract_name_from_description
from location_utils import get_user_location
from constellation_utils import load_constellation_data
from skychart_utils import create_sky_chart

app = Flask(__name__)
app.config['SECRET_KEY'] = 'replace-with-a-secure-key'
CONSTELLATION_MAP = load_constellation_data()
ZOOM_LEVELS = [0.7, 1.0, 1.3, 1.6, 2.0]

# Port of your Streamlit helper

def enhance_visible_objects(visible_objects, constellation_map):
    enhanced = []
    for obj in visible_objects:
        desc_key = obj['hip_id'] if obj['type']=='Star' and obj.get('hip_id') else obj['name']
        description = get_object_description(desc_key)
        # Extract proper name
        if obj['type']=='Star':
            nice_name = extract_name_from_description(description) if description else None
            if nice_name:
                obj['name'] = nice_name
            hip_int = obj.get('hip_int')
            obj['constellation'] = constellation_map.get(hip_int, 'Unknown') if hip_int else 'Unknown'
        else:
            obj['constellation'] = 'N/A'
            nice_name = None
        obj['fetched_description'] = description
        obj['name_extracted_from_description_for_tile_h1'] = nice_name
        # Always fetch image URL from Wikipedia for every object
        obj['image_url'] = get_object_image_url(obj['name'])
        enhanced.append(obj)
    return enhanced

@app.route('/', methods=['GET','POST'])
def index():
    # Defaults
    lat = lon = None
    zoom = 1.0
    action = 'view'
    today = date.today().isoformat()
    now_time = datetime.now().strftime('%H:%M')
    date_str = today
    time_str = now_time

    # Parse POST
    if request.method=='POST':
        lat = request.form.get('latitude', type=float)
        lon = request.form.get('longitude', type=float)
        date_str = request.form.get('date') or datetime.utcnow().date().isoformat()
        time_str = request.form.get('time') or datetime.utcnow().time().strftime('%H:%M')
        zoom = float(request.form.get('zoom', zoom))
        action = request.form.get('action', 'view')
        # Zoom logic
        if action in ('zoom_in','zoom_out'):
            try:
                idx = ZOOM_LEVELS.index(zoom)
            except ValueError:
                idx = 1
            if action=='zoom_in' and idx < len(ZOOM_LEVELS)-1:
                zoom = ZOOM_LEVELS[idx+1]
            if action=='zoom_out' and idx > 0:
                zoom = ZOOM_LEVELS[idx-1]
    # Fallback to IP geo
    if lat is None or lon is None:
        lat, lon, _ = get_user_location()
    # Build datetime
    dt = datetime.fromisoformat(f"{date_str}T{time_str}").replace(tzinfo=utc)

    # Fetch & enhance
    visible = get_visible_objects(lat, lon, dt)
    enhanced = enhance_visible_objects(visible, CONSTELLATION_MAP)
    # Sky chart
    fig = create_sky_chart(visible, lat, lon, dt, zoom=zoom)
    chart_html = fig.to_html(full_html=False, include_plotlyjs='cdn') if fig else ''
    # Folium map
    fmap = folium.Map(location=[lat, lon], zoom_start=5)
    fmap.add_child(folium.LatLngPopup())
    map_name = fmap.get_name()
    map_html = fmap._repr_html_()

    return render_template('results.html',
                           latitude=lat, longitude=lon,
                           date=date_str, time=time_str,
                           zoom=zoom,
                           map_html=map_html,
                           map_name=map_name,
                           objects=enhanced,
                           chart_html=chart_html)

if __name__=='__main__':
    app.run(debug=True)