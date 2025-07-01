"""
Application utilities for the Space Detective Streamlit app.

This module contains helper functions for rendering UI components, handling 
user input, and managing application state.
"""

import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime
from skyfield.api import utc
from streamlit_folium import st_folium
import folium
from streamlit_javascript import st_javascript
from wiki_utils import get_object_image_url

# --- Constants ---
MAX_DESC_LEN = 120
ZOOM_LEVELS = [0.7, 1.0, 1.3, 1.6, 2.0]

# --- Styling ---

def apply_custom_styling():
    """Applies custom CSS for a space-themed UI."""
    st.markdown("""
        <style>
            .stApp {
                background: linear-gradient(120deg, #0f2027 0%, #2c5364 100%);
            }
            .block-container {
                background: rgba(20, 20, 30, 0.85);
                border-radius: 18px;
                padding: 2rem;
            }
            h1, h2, h3 {
                color: #ffd700 !important;
            }
            .stMetric {
                background: rgba(255, 215, 0, 0.1);
                padding: 1rem;
                border-radius: 8px;
            }
        </style>
    """, unsafe_allow_html=True)

# --- Location Handling ---

def _get_gps_location():
    """Fetches GPS location using a Vercel-hosted service."""
    # Unique key to re-trigger JavaScript on subsequent calls
    key = f"gps_request_{st.session_state.get('location_request_count', 0) + 1}"
    st.session_state.location_request_count = st.session_state.get('location_request_count', 0) + 1
    
    return st_javascript("""
        new Promise(resolve => {
            const iframe = document.createElement('iframe');
            iframe.src = 'https://geolocation-page.vercel.app';
            iframe.style.display = 'none';
            
            const timeout = setTimeout(() => {
                window.removeEventListener('message', handler);
                document.body.removeChild(iframe);
                resolve({error: 'GPS timeout'});
            }, 15000);

            const handler = event => {
                if (event.origin === 'https://geolocation-page.vercel.app') {
                    clearTimeout(timeout);
                    window.removeEventListener('message', handler);
                    document.body.removeChild(iframe);
                    resolve(event.data);
                }
            };

            window.addEventListener('message', handler);
            document.body.appendChild(iframe);
        });
    """, key=key)

def _apply_coordinates(lat, lon, source="Manual"):
    """Saves selected coordinates to the session state and reruns the app."""
    st.session_state.latitude = float(lat)
    st.session_state.longitude = float(lon)
    st.session_state.address = f"{source} ({lat:.4f}, {lon:.4f})"
    st.session_state.location_detected = True
    st.success(f"🎯 Location set via {source}!")
    st.rerun()

def render_location_section():
    """Renders the entire location selection UI."""
    st.markdown("<h1 style='text-align: center;'>📍 Set Your Observation Point</h1>", unsafe_allow_html=True)

    if st.session_state.get('location_detected', False):
        _render_detected_location_view()
    else:
        _render_location_selection_view()

def _render_detected_location_view():
    """Displays the currently set location and a button to change it."""
    st.success(f"✅ Location Locked: {st.session_state.address}")
    col1, col2 = st.columns(2)
    col1.metric("Latitude", f"{st.session_state.latitude:.4f}°")
    col2.metric("Longitude", f"{st.session_state.longitude:.4f}°")
    
    if st.button("🔄 Change Location"):
        st.session_state.location_detected = False
        st.rerun()

def _render_location_selection_view():
    """Renders the UI for selecting a location method (GPS or Map)."""
    st.info("Choose a method to set your location.")
    method = st.radio("Location Method", ("🛰️ GPS", "🗺️ Map"), horizontal=True)

    if method == "🛰️ GPS":
        _render_gps_section()
    else:
        _render_map_section()

def _render_gps_section():
    """Renders the UI for GPS and manual coordinate entry."""
    st.markdown("### 🛰️ GPS & Manual Entry")
    if st.button("Get GPS Location"):
        with st.spinner("Requesting GPS coordinates..."):
            location_data = _get_gps_location()
            if location_data and 'latitude' in location_data:
                _apply_coordinates(location_data['latitude'], location_data['longitude'], "GPS")
            else:
                st.error("Could not retrieve GPS location. Please use manual entry or the map.")
                st.info("If GPS fails, you can grant location permissions manually by visiting the link below, then try again:")
                st.code("https://geolocation-page.vercel.app/")

    with st.form("manual_coords_form"):
        lat = st.number_input("Latitude", -90.0, 90.0, format="%.6f")
        lon = st.number_input("Longitude", -180.0, 180.0, format="%.6f")
        if st.form_submit_button("Apply Manual Coordinates"):
            if lat != 0.0 or lon != 0.0:
                _apply_coordinates(lat, lon, "Manual Entry")
            else:
                st.warning("Please enter non-zero coordinates.")

def _render_map_section():
    """Renders an interactive map for location selection."""
    st.markdown("### 🗺️ Map Selection")
    map_center = [st.session_state.get('latitude', 51.5), st.session_state.get('longitude', -0.12)]
    m = folium.Map(location=map_center, zoom_start=4)
    
    map_data = st_folium(m, height=400, use_container_width=True)
    
    if map_data and map_data.get("last_clicked"):
        lat, lon = map_data['last_clicked']['lat'], map_data['last_clicked']['lng']
        if st.session_state.get('latitude') != lat or st.session_state.get('longitude') != lon:
            _apply_coordinates(lat, lon, "Map Selection")

# --- Date & Time Handling ---

def render_datetime_section():
    """Renders the date and time selection UI."""
    st.header("🕒 Select Date and Time")
    col1, col2 = st.columns(2)
    date = col1.date_input("Date", key="user_date")
    time = col2.time_input("Time", key="user_time")
    
    combined_dt = datetime.combine(date, time).replace(tzinfo=utc)
    st.info(f"Observing Time (UTC): {combined_dt.strftime('%Y-%m-%d %H:%M:%S')}")
    return combined_dt

# --- Object Display ---

def get_object_emoji(obj_type):
    """Returns an emoji for a given celestial object type."""
    return {"Star": "⭐", "Planet": "🪐", "Sun": "☀️", "Moon": "🌙"}.get(obj_type, "🌌")

def create_object_tile(obj, container):
    """Creates a display tile for a single celestial object."""
    name = obj.get('name') or obj.get('hip_id', 'Unknown')
    emoji = get_object_emoji(obj['type'])
    
    with container:
        st.markdown(f"<div style='border: 1px solid #ffd700; border-radius: 10px; padding: 1rem; margin-bottom: 1rem;'>", unsafe_allow_html=True)
        st.markdown(f"<h5>{emoji} {name}</h5>", unsafe_allow_html=True)

        img_url = get_object_image_url(name)
        if img_url:
            st.image(img_url, use_container_width=True)

        st.write(f"**Type:** {obj['type']}")
        st.write(f"**Altitude:** {obj['altitude']:.2f}°")
        st.write(f"**Azimuth:** {obj['azimuth']:.2f}°")
        if obj.get('constellation') != "N/A":
            st.write(f"**Constellation:** {obj.get('constellation', 'Unknown')}")

        desc = obj.get('fetched_description', '')
        if desc and desc != "Description not available.":
            if len(desc) > MAX_DESC_LEN:
                with st.expander("Read Description"):
                    st.write(desc)
            else:
                st.write(f"**Desc:** {desc}")
        st.markdown("</div>", unsafe_allow_html=True)

def create_object_tiles(objects):
    """Creates a grid of display tiles for all visible objects."""
    if not objects:
        st.info("No astronomical objects are currently visible. Try changing the time or location.")
        return

    st.metric("Visible Objects", len(objects))
    sorted_objects = sorted(objects, key=lambda x: (-x['altitude']))
    
    cols = st.columns(3)
    for i, obj in enumerate(sorted_objects):
        create_object_tile(obj, cols[i % 3])

# --- Sky Chart ---

def render_sky_chart_section(visible_objects, dt, create_sky_chart_func):
    """Renders the interactive sky chart and its controls."""
    st.header("🌟 Interactive Sky Chart")

    # Zoom controls
    zoom_idx = ZOOM_LEVELS.index(st.session_state.get('sky_zoom', 1.0))
    col1, col2, col3 = st.columns([1, 1, 1])
    if col1.button("Zoom Out", disabled=(zoom_idx == 0)):
        st.session_state.sky_zoom = ZOOM_LEVELS[zoom_idx - 1]
        st.rerun()
    col2.metric("Zoom", f"{st.session_state.get('sky_zoom', 1.0)}x")
    if col3.button("Zoom In", disabled=(zoom_idx == len(ZOOM_LEVELS) - 1)):
        st.session_state.sky_zoom = ZOOM_LEVELS[zoom_idx + 1]
        st.rerun()

    if visible_objects:
        with st.spinner("Generating sky chart..."):
            chart = create_sky_chart_func(
                visible_objects, 
                st.session_state.latitude, 
                st.session_state.longitude, 
                dt, 
                zoom=st.session_state.get('sky_zoom', 1.0)
            )
            if chart:
                st.plotly_chart(chart, use_container_width=True, config={'displayModeBar': False})
            else:
                st.warning("Could not generate the sky chart.")
    else:
        st.info("No objects to display on the sky chart.")

    # Aladin Lite embed
    st.markdown("### 🔭 Online Sky Atlas (Aladin Lite)")
    components.html(
        '<iframe src="https://aladin.u-strasbg.fr/AladinLite/" width="100%" height="500" style="border:none;"></iframe>',
        height=510
    )
