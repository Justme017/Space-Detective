import streamlit as st
st.set_page_config(page_title="Merai - A Space Detective") # Changed page_title
from datetime import date, datetime
from skyfield.api import utc
import pandas as pd
import folium # Added for interactive map
from streamlit_folium import st_folium # Added for interactive map
from astro_utils import get_visible_objects
from wiki_utils import get_object_image_url, get_object_description, extract_name_from_description
from location_utils import get_user_location
from constellation_utils import load_constellation_data # Import new utility
from skychart_utils import create_sky_chart # Import the new sky chart utility

# Load constellation data once at the start
CONSTELLATION_MAP = load_constellation_data()

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

st.title("Merai - A Space Detective") # Changed title

# Location
st.header("Location")

# Initialize session state for location choice and coordinates if not already present
if 'location_choice' not in st.session_state:
    st.session_state.location_choice = "Detect my location" # Default choice
if 'latitude' not in st.session_state: # Ensure these are initialized for map centering
    st.session_state.latitude = 0.0 # Default latitude
if 'longitude' not in st.session_state:
    st.session_state.longitude = 0.0 # Default longitude
if 'address' not in st.session_state:
    st.session_state.address = "Not set"

# Let user choose location method
location_option = st.radio(
    "Choose location method:",
    ("Detect my location", "Select location on map"), # Changed options
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
    # Use current session state lat/lon for map center, or a default if not set
    map_center_lat = st.session_state.get('latitude', 0.0)
    map_center_lon = st.session_state.get('longitude', 0.0)
    
    m = folium.Map(location=[map_center_lat, map_center_lon], zoom_start=5) # Adjusted zoom
    
    # Add a marker for the current session state location if it's valid
    if st.session_state.address not in ["Not set", "Automatic Detection Failed", "Default Location (Detection Failed)"] and -90 <= st.session_state.latitude <= 90 and -180 <= st.session_state.longitude <= 180 :
        folium.Marker([st.session_state.latitude, st.session_state.longitude], popup=st.session_state.address).add_to(m)

    map_data = st_folium(m, height=400, use_container_width=True, key="folium_map_selector")

    if map_data and map_data["last_clicked"]:
        clicked_lat = map_data['last_clicked']['lat']
        clicked_lon = map_data['last_clicked']['lng']
        # Update session state only if the clicked location is different to avoid unnecessary reruns on map load/pan
        if st.session_state.latitude != clicked_lat or st.session_state.longitude != clicked_lon:
            st.session_state.latitude = clicked_lat
            st.session_state.longitude = clicked_lon
            st.session_state.address = f"Map Selected: ({clicked_lat:.2f}, {clicked_lon:.2f})"

# Display the current location status
if st.session_state.address not in ["Not set", "Automatic Detection Failed", "Default Location (Detection Failed)"]:
    st.success(f"Using location: {st.session_state.address} ({st.session_state.latitude:.2f}, {st.session_state.longitude:.2f})")
elif st.session_state.address == "Automatic Detection Failed":
    st.warning("Automatic detection failed. Please select your location on the map or try detecting again.")
else: # "Not set" or "Default Location (Detection Failed)"
    st.info("Please detect your location or select it on the map.")

# Date and Time
st.header("Date and Time")

# Initialize session state for date and time if not already present
if 'user_selected_date' not in st.session_state:
    st.session_state.user_selected_date = date.today()
if 'user_selected_time' not in st.session_state:
    st.session_state.user_selected_time = datetime.now().time()

# The widgets will read from and write to st.session_state using their keys.
# The values assigned to d and t will be the current values from session_state.
d = st.date_input("Date", key="user_selected_date")
t = st.time_input("Time", key="user_selected_time")

# Construct dt from the session state, which reflects the latest user input
dt = datetime.combine(st.session_state.user_selected_date, st.session_state.user_selected_time).replace(tzinfo=utc)

# Fetch Data
st.header("Visible Astronomical Objects")
with st.spinner("Fetching visible astronomical objects and details..."): # Updated spinner message
    # Use latitude and longitude from session state
    visible_objects = get_visible_objects(st.session_state.latitude, st.session_state.longitude, dt)
    if not visible_objects:
        st.warning("No astronomical objects are currently visible from your location.")
        st.stop()

    # Enhance objects with descriptions and refined names for DataFrame and Tiles
    for obj in visible_objects:
        original_astro_name = obj['name'] # Name from astro_utils (proper name or HIP ID)
        hip_id = obj.get('hip_id')

        description_lookup_key = hip_id if obj['type'] == 'Star' and hip_id else original_astro_name
        description = get_object_description(description_lookup_key)
        name_from_desc = extract_name_from_description(description) if description else None

        # Update obj['name'] for DataFrame display: Wikipedia name > Hipparcos proper name > HIP ID
        if name_from_desc:
            obj['name'] = name_from_desc
        # else obj['name'] remains what astro_utils set it to (proper_name or HIP ID)
        
        # Store details for tile generation to avoid re-fetching
        obj['fetched_description'] = description
        obj['name_extracted_from_description_for_tile_h1'] = name_from_desc
        
        # Add constellation for DataFrame if it's a star
        obj['constellation'] = "N/A"
        if obj['type'] == 'Star':
            hip_int_for_lookup = obj.get('hip_int')
            if hip_int_for_lookup and CONSTELLATION_MAP:
                obj['constellation'] = CONSTELLATION_MAP.get(hip_int_for_lookup, "Unknown")

# Create DataFrame for display
df_columns = ['Name', 'HIP ID', 'Type', 'Altitude', 'Azimuth', 'Constellation'] # Ensured all are capitalized

df_display_data = []
for obj in visible_objects:
    row_data = {
        'Name': obj.get('name', 'N/A'), # Changed key to 'Name'
        'HIP ID': obj.get('hip_id', 'N/A'),
        'Type': obj.get('type', 'N/A'), # Changed key to 'Type'
        'Altitude': obj.get('altitude', 'N/A'),
        'Azimuth': obj.get('azimuth', 'N/A'),
        'Constellation': obj.get('constellation', 'N/A') # Corrected obj.get key to lowercase 'constellation'
    }
    df_display_data.append(row_data)

df = pd.DataFrame(df_display_data)
st.dataframe(df[df_columns]) # Ensure column order

# Add Sky Chart Section
st.header("Sky Chart")
if visible_objects: # Ensure there are objects to plot
    # Use latitude, longitude, and dt from session state or current values
    chart_lat = st.session_state.get('latitude', 0.0)
    chart_lon = st.session_state.get('longitude', 0.0)
    # dt is already defined and in UTC

    with st.spinner("Generating Sky Chart..."):
        sky_chart_image = create_sky_chart(visible_objects, chart_lat, chart_lon, dt)
        if sky_chart_image:
            st.image(sky_chart_image, caption=f"Sky chart for {st.session_state.address} at {dt.strftime('%Y-%m-%d %H:%M:%S UTC')}", use_container_width=True)
        else:
            st.warning("Could not generate the sky chart at this time.")
else:
    st.info("No objects visible to display on sky chart.")


# Details as uniform dark-mode friendly tiles with fixed height and content truncation
st.header("Learn More About Each Object")
cols = st.columns(3)
MAX_DESC_LEN = 120  # characters
TILE_HEIGHT = 550   # px, (already adjusted for constellation line)
for idx, obj_data in enumerate(visible_objects): 
    with cols[idx % 3]:
        display_name_h1 = obj_data['name_extracted_from_description_for_tile_h1'] if obj_data['name_extracted_from_description_for_tile_h1'] else "NULL"
        display_name_h2 = obj_data.get('hip_id', '') 
        description_for_tile = obj_data['fetched_description']
        constellation_name_for_tile = obj_data.get('constellation', "N/A")

        if display_name_h1 == display_name_h2 and display_name_h1 != "NULL":
            display_name_h2 = ''

        # Prioritize using the resolved common name for image lookup.
        # obj_data['name'] should hold the best available name (Wikipedia name > Hipparcos proper name > HIP ID)
        image_lookup_key = obj_data['name'] 
        
        # As a fallback, if the resolved name happens to be a HIP ID and we want to ensure
        # we are not using it if a more specific display_name_h1 (from description) is available
        # and different, we could add more logic. But for now, obj_data['name'] is the most refined.
        # If obj_data['name'] is "Alnilam", use "Alnilam".
        # If obj_data['name'] is "HIP 26311" (because no common name was found), use "HIP 26311".

        image_url = get_object_image_url(image_lookup_key)

        # Prepare HTML parts for embedding in the main f-string
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
        """ # Closing triple quote for tile_html
        st.markdown(tile_html, unsafe_allow_html=True)

        if description_for_tile and len(description_for_tile) > MAX_DESC_LEN:
            with st.expander("Know more"):
                st.markdown(f"<h4 style='color:#bbb;font-size:1em;margin:0;'>{description_for_tile}</h4>", unsafe_allow_html=True)
