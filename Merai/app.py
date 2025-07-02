# app.py

from flask import Flask, render_template, request, session
from utils.location_utils import get_user_location, get_user_datetime
from utils.astro_utils import get_visible_objects, enhance_visible_objects
from utils.constellation_utils import load_constellation_data
from utils.skychart_utils import create_sky_chart
from utils.app_utils import format_datetime_utc, crop_description, get_image_for, ZOOM_LEVELS
from skyfield.api import utc
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Replace with a secure random key

@app.route('/', methods=['GET', 'POST'])
def index():
    # Initialize defaults
    session.setdefault('location_detected', False)
    session.setdefault('sky_zoom', 1.0)

    # Handle POST from the “See the Sky” button
    if request.method == 'POST':
        # Location
        lat = request.form.get('latitude')
        lon = request.form.get('longitude')
        addr = request.form.get('address')
        if lat and lon:
            session['latitude']          = float(lat)
            session['longitude']         = float(lon)
            session['address']           = addr
            session['location_detected'] = True

        # Date/time
        session['user_date'] = request.form.get('user_date')
        session['user_time'] = request.form.get('user_time')

        # Zoom controls
        zoom_action = request.form.get('zoom')
        idx = ZOOM_LEVELS.index(session['sky_zoom'])
        if zoom_action == 'in' and idx < len(ZOOM_LEVELS) - 1:
            session['sky_zoom'] = ZOOM_LEVELS[idx + 1]
        elif zoom_action == 'out' and idx > 0:
            session['sky_zoom'] = ZOOM_LEVELS[idx - 1]

    # If still no location, try IP-based lookup
    if not session['location_detected']:
        lat, lon, addr = get_user_location()
        if lat is not None:
            session['latitude']          = lat
            session['longitude']         = lon
            session['address']           = addr
            session['location_detected'] = True

    # Build the datetime with UTC tz
    if session.get('user_date') and session.get('user_time'):
        naive_dt = datetime.fromisoformat(f"{session['user_date']}T{session['user_time']}")
        dt = naive_dt.replace(tzinfo=utc)
    else:
        dt = get_user_datetime()

    # Form defaults
    dt_date = dt.date().isoformat()
    dt_time = dt.time().strftime("%H:%M:%S")

    # Fetch objects and chart
    objects, chart_html = [], None
    if session['location_detected']:
        cmap = load_constellation_data()
        raw = get_visible_objects(session['latitude'], session['longitude'], dt)
        objects = enhance_visible_objects(raw, cmap) if raw else []
        fig = create_sky_chart(
            objects,
            session['latitude'],
            session['longitude'],
            dt,
            zoom=session['sky_zoom']
        )
        if fig:
            chart_html = fig.to_html(full_html=False, include_plotlyjs='cdn')

    return render_template(
        'index.html',
        address      = session.get('address'),
        dt_date      = dt_date,
        dt_time      = dt_time,
        objects      = objects,
        chart_html   = chart_html,
        sky_zoom     = session['sky_zoom'],
        zoom_levels  = ZOOM_LEVELS,
        crop_desc    = crop_description,
        get_image    = get_image_for,
        show_results = (request.method == 'POST')
    )

if __name__ == '__main__':
    app.run(debug=True)
