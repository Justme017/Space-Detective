import streamlit as st
from datetime import date, datetime
from skyfield.api import utc
from streamlit_folium import st_folium
from astro_utils import get_visible_objects
from wiki_utils import get_object_image_url, get_object_description, extract_name_from_description
from location_utils import get_user_location
from constellation_utils import load_constellation_data
from skychart_utils import create_sky_chart
import folium

# Load constellation data once at the start
CONSTELLATION_MAP = load_constellation_data()

# Streamlit app configuration
st.set_page_config(page_title="Merai - A Space Detective")

# Immersive background and custom styles
st.markdown(
    """
    <style>
    body {
        background: linear-gradient(120deg, #0f2027 0%, #2c5364 100%) !important;
        color: #f1f1f1 !important;
    }
    .stApp {
        background: linear-gradient(120deg, #0f2027 0%, #2c5364 100%) !important;
    }
    .block-container {
        background: rgba(20, 20, 30, 0.85) !important;
        border-radius: 18px;
        padding: 2rem 2rem 1rem 2rem;
        box-shadow: 0 8px 32px #000a;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #ffd700 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("Merai - A Space Detective")

# Location handling
st.header("Location")
if 'location_choice' not in st.session_state:
    st.session_state.location_choice = "Detect my location"
if 'latitude' not in st.session_state:
    st.session_state.latitude = 0.0
if 'longitude' not in st.session_state:
    st.session_state.longitude = 0.0
if 'address' not in st.session_state:
    st.session_state.address = "Not set"

location_option = st.radio(
    "Choose location method:",
    ("Detect my location", "Select location on map"),
    key='location_choice'
)

if st.session_state.location_choice == "Detect my location":
    if st.button("Detect My Location Now"):
        detected_lat, detected_lon, detected_address = get_user_location()
        if detected_lat is not None and detected_lon is not None:
            st.session_state.latitude = detected_lat
            st.session_state.longitude = detected_lon
            st.session_state.address = detected_address
        else:
            st.session_state.address = "Automatic Detection Failed"
            st.error("Could not automatically determine location. Please try selecting on the map.")
elif st.session_state.location_choice == "Select location on map":
    st.subheader("Click on the map to set your location")
    map_center_lat = st.session_state.get('latitude', 0.0)
    map_center_lon = st.session_state.get('longitude', 0.0)
    m = folium.Map(location=[map_center_lat, map_center_lon], zoom_start=5)
    if st.session_state.address not in ["Not set", "Automatic Detection Failed"] and -90 <= st.session_state.latitude <= 90 and -180 <= st.session_state.longitude <= 180:
        folium.Marker([st.session_state.latitude, st.session_state.longitude], popup=st.session_state.address).add_to(m)
    map_data = st_folium(m, height=400, use_container_width=True, key="folium_map_selector")
    if map_data and map_data["last_clicked"]:
        clicked_lat = map_data['last_clicked']['lat']
        clicked_lon = map_data['last_clicked']['lng']
        if st.session_state.latitude != clicked_lat or st.session_state.longitude != clicked_lon:
            st.session_state.latitude = clicked_lat
            st.session_state.longitude = clicked_lon
            st.session_state.address = f"Map Selected: ({clicked_lat:.2f}, {clicked_lon:.2f})"

if st.session_state.address not in ["Not set", "Automatic Detection Failed"]:
    st.success(f"Using location: {st.session_state.address} ({st.session_state.latitude:.2f}, {st.session_state.longitude:.2f})")

# Date and Time handling
st.header("Date and Time")
if 'user_selected_date' not in st.session_state:
    st.session_state.user_selected_date = date.today()
if 'user_selected_time' not in st.session_state:
    st.session_state.user_selected_time = datetime.now().time()

d = st.date_input("Date", key="user_selected_date")
t = st.time_input("Time", key="user_selected_time")
dt = datetime.combine(st.session_state.user_selected_date, st.session_state.user_selected_time).replace(tzinfo=utc)

# Helper function to clean and enhance visible objects
def enhance_visible_objects(visible_objects, constellation_map):
    enhanced_objects = []
    for obj in visible_objects:
        original_astro_name = obj['name']
        hip_id = obj.get('hip_id')
        description_lookup_key = hip_id if obj['type'] == 'Star' and hip_id else original_astro_name
        description = get_object_description(description_lookup_key)

        if obj['type'] == 'Star':
            name_from_desc = extract_name_from_description(description) if description else None
            if name_from_desc:
                obj['name'] = name_from_desc
        else:
            name_from_desc = None

        obj['fetched_description'] = description
        obj['name_extracted_from_description_for_tile_h1'] = name_from_desc

        if obj['type'] == 'Star':
            hip_int_for_lookup = obj.get('hip_int')
            if hip_int_for_lookup and constellation_map:
                obj['constellation'] = constellation_map.get(hip_int_for_lookup, "Unknown")
        else:
            obj['constellation'] = "N/A"

        enhanced_objects.append(obj)
    return enhanced_objects

# Helper function to create tiles for objects
def create_object_tiles(objects):
    cols = st.columns(3)
    MAX_DESC_LEN = 120
    TILE_HEIGHT = 550
    for idx, obj_data in enumerate(objects):
        with cols[idx % 3]:
            display_name_h1 = obj_data['name_extracted_from_description_for_tile_h1'] if obj_data['name_extracted_from_description_for_tile_h1'] else obj_data['name']
            display_name_h2 = obj_data.get('hip_id', '') if obj_data['type'] == 'Star' else ''
            description_for_tile = obj_data['fetched_description']
            constellation_name_for_tile = obj_data.get('constellation', "N/A")

            image_lookup_key = obj_data['name']
            image_url = get_object_image_url(image_lookup_key)

            image_html_part = f"<img src='{image_url}' style='width:100%;height:180px;object-fit:cover;border-top-left-radius:16px;border-top-right-radius:16px;margin-bottom:0;' alt='object image' />" if image_url else "<div style='width:100%;height:180px;display:flex;align-items:center;justify-content:center;background:#333;border-top-left-radius:16px;border-top-right-radius:16px;color:#ff6666;font-size:18px;'>No image found.</div>"
            h1_html_part = f"<h1 style='color:#ffd700;margin:10px 0 0 0;font-size:1.5em;text-align:center;'>{display_name_h1}</h1>"
            h2_html_part = f"<h2 style='color:#fff;margin:0 0 8px 0;font-size:1.1em;text-align:center;letter-spacing:1px;'>{display_name_h2}</h2>" if display_name_h2 else ""
            details_html_part = f"<div style='text-align:center;color:#eee;font-size:0.95em;'><b>Type:</b> {obj_data['type']}<br><b>Altitude:</b> {obj_data['altitude']}°<br><b>Azimuth:</b> {obj_data['azimuth']}°<br><b>Constellation:</b> {constellation_name_for_tile}</div>"

            description_html_part = ""
            if description_for_tile:
                desc_content = description_for_tile[:MAX_DESC_LEN] + "..." if len(description_for_tile) > MAX_DESC_LEN else description_for_tile
                description_html_part = f"<h3 style='color:#bbb;font-size:0.9em;margin:8px 0 0 0;text-align:left;overflow-y:auto;max-height:60px;padding:0 5px;'>{desc_content}</h3>"

            tile_html = f"""
            <div style='height:{TILE_HEIGHT}px; display:flex; flex-direction:column; justify-content:space-between; border:2px solid #ffd700; border-radius:18px; padding:0; margin-bottom:18px; background:linear-gradient(135deg,#232526 0%,#414345 100%); box-shadow:0 4px 24px #000a;'>
                <div> <!-- Top content container -->
                    {image_html_part}
                    <div style='padding: 0 10px;'> <!-- Text content padding -->
                        {h1_html_part}
                        {h2_html_part}
                        {details_html_part}
                        {description_html_part}
                    </div> <!-- Close Text content padding -->
                </div> <!-- Close Top content container -->
                <div style="flex-grow: 1;"></div> <!-- Spacer div to push content up, works with justify-content:space-between -->
            </div>
            """
            st.markdown(tile_html, unsafe_allow_html=True)

            if description_for_tile and len(description_for_tile) > MAX_DESC_LEN:
                with st.expander("Know more"):
                    st.markdown(f"<h4 style='color:#bbb;font-size:1em;margin:0;'>{description_for_tile}</h4>", unsafe_allow_html=True)

# Fetch and display astronomical objects
st.header("Visible Astronomical Objects")
with st.spinner("Fetching visible astronomical objects and details..."):
    # Ensure latitude and longitude are passed to `get_visible_objects`
    visible_objects = get_visible_objects(st.session_state.latitude, st.session_state.longitude, dt)
    if not visible_objects:
        st.warning("No astronomical objects are currently visible from your location.")
        st.stop()
    enhanced_objects = enhance_visible_objects(visible_objects, CONSTELLATION_MAP)
    create_object_tiles(enhanced_objects)

# Sky chart section
st.header("Sky Chart")
zoom_levels = [0.7, 1.0, 1.3, 1.6, 2.0]
if 'sky_zoom' not in st.session_state:
    st.session_state.sky_zoom = 1.0
col1, col2, col3 = st.columns([1, 2, 1])
with col1:
    if st.button("- Zoom Out"):
        idx = zoom_levels.index(st.session_state.sky_zoom) if st.session_state.sky_zoom in zoom_levels else 1
        if idx > 0:
            st.session_state.sky_zoom = zoom_levels[idx-1]
with col3:
    if st.button("+ Zoom In"):
        idx = zoom_levels.index(st.session_state.sky_zoom) if st.session_state.sky_zoom in zoom_levels else 1
        if idx < len(zoom_levels)-1:
            st.session_state.sky_zoom = zoom_levels[idx+1]
if visible_objects:
    chart_lat = st.session_state.get('latitude', 0.0)
    chart_lon = st.session_state.get('longitude', 0.0)
    with st.spinner("Generating Sky Chart..."):
        sky_chart_figure = create_sky_chart(visible_objects, chart_lat, chart_lon, dt, zoom=st.session_state.sky_zoom)
        if sky_chart_figure:
            st.plotly_chart(sky_chart_figure, use_container_width=True)
        else:
            st.warning("Could not generate the sky chart at this time.")
else:
    st.info("No objects visible to display on sky chart.")
