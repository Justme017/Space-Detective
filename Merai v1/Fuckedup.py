import streamlit as st
from datetime import date, datetime
from skyfield.api import utc
from streamlit_folium import st_folium
import folium

# Import custom modules
from astro_utils import get_visible_objects
from wiki_utils import get_object_image_url, get_object_description, extract_name_from_description
from location_utils import get_user_location
from constellation_utils import load_constellation_data
from skychart_utils import create_sky_chart

# Constants
MAX_DESC_LEN = 120
TILE_HEIGHT = 550
ZOOM_LEVELS = [0.7, 1.0, 1.3, 1.6, 2.0]

# Load constellation data once at startup
CONSTELLATION_MAP = load_constellation_data()

# Streamlit app configuration
st.set_page_config(
    page_title="Merai - A Space Detective",
    page_icon="🔭",
    layout="wide"
)

# Apply custom CSS styling
def apply_custom_styling():
    """Apply immersive space-themed styling to the app."""
    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(120deg, #0f2027 0%, #2c5364 100%) !important;
        }
        .block-container {
            background: rgba(20, 20, 30, 0.85) !important;
            border-radius: 18px;
            padding: 2rem 2rem 1rem 2rem;
            box-shadow: 0 8px 32px rgba(0,0,0,0.6);
        }
        h1, h2, h3, h4, h5, h6 {
            color: #ffd700 !important;
        }
        .stRadio > div {
            color: #f1f1f1;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# Initialize session state
def initialize_session_state():
    """Initialize all session state variables with default values."""
    defaults = {
        'location_choice': "Detect my location",
        'latitude': 0.0,
        'longitude': 0.0,
        'address': "Not set",
        'user_selected_date': date.today(),
        'user_selected_time': datetime.now().time(),
        'sky_zoom': 1.0
    }
    
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

def handle_location_detection():
    """Handle automatic location detection."""
    if st.button("🌍 Detect My Location Now"):
        with st.spinner("Detecting your location..."):
            detected_lat, detected_lon, detected_address = get_user_location()
            if detected_lat is not None and detected_lon is not None:
                st.session_state.latitude = detected_lat
                st.session_state.longitude = detected_lon
                st.session_state.address = detected_address
                st.success(f"✅ Location detected: {detected_address}")
            else:
                st.session_state.address = "Automatic Detection Failed"
                st.error("❌ Could not automatically determine location. Please try selecting on the map.")

def handle_map_selection():
    """Handle manual location selection on map."""
    st.subheader("🗺️ Click on the map to set your location")
    
    # Create map centered on current location or default
    map_center_lat = st.session_state.get('latitude', 0.0)
    map_center_lon = st.session_state.get('longitude', 0.0)
    m = folium.Map(location=[map_center_lat, map_center_lon], zoom_start=5)
    
    # Add marker if location is set
    if (st.session_state.address not in ["Not set", "Automatic Detection Failed"] and 
        -90 <= st.session_state.latitude <= 90 and 
        -180 <= st.session_state.longitude <= 180):
        folium.Marker(
            [st.session_state.latitude, st.session_state.longitude], 
            popup=st.session_state.address
        ).add_to(m)
    
    # Display map and handle clicks
    map_data = st_folium(m, height=400, use_container_width=True, key="folium_map_selector")
    if map_data and map_data["last_clicked"]:
        clicked_lat = map_data['last_clicked']['lat']
        clicked_lon = map_data['last_clicked']['lng']
        if (st.session_state.latitude != clicked_lat or 
            st.session_state.longitude != clicked_lon):
            st.session_state.latitude = clicked_lat
            st.session_state.longitude = clicked_lon
            st.session_state.address = f"Map Selected: ({clicked_lat:.2f}, {clicked_lon:.2f})"

def render_location_section():
    """Render the location selection section."""
    st.header("📍 Location")
    
    location_option = st.radio(
        "Choose location method:",
        ("Detect my location", "Select location on map"),
        key='location_choice'
    )
    
    if st.session_state.location_choice == "Detect my location":
        handle_location_detection()
    else:
        handle_map_selection()
    
    # Show current location if set
    if st.session_state.address not in ["Not set", "Automatic Detection Failed"]:
        st.success(
            f"📍 Using location: {st.session_state.address} "
            f"({st.session_state.latitude:.2f}, {st.session_state.longitude:.2f})"
        )

def render_datetime_section():
    """Render the date and time selection section."""
    st.header("🕒 Date and Time")
    
    col1, col2 = st.columns(2)
    with col1:
        d = st.date_input("📅 Date", key="user_selected_date")
    with col2:
        t = st.time_input("⏰ Time", key="user_selected_time")
    
    return datetime.combine(
        st.session_state.user_selected_date, 
        st.session_state.user_selected_time
    ).replace(tzinfo=utc)

# Helper function to clean and enhance visible objects
def enhance_visible_objects(visible_objects, constellation_map):
    """Enhance astronomical objects with additional information."""
    enhanced_objects = []
    for obj in visible_objects:
        # Get description for the object
        hip_id = obj.get('hip_id')
        description_lookup_key = hip_id if obj['type'] == 'Star' and hip_id else obj['name']
        description = get_object_description(description_lookup_key)

        # Extract better name from description for stars
        if obj['type'] == 'Star':
            name_from_desc = extract_name_from_description(description) if description else None
            if name_from_desc:
                obj['name'] = name_from_desc
        else:
            name_from_desc = None

        # Add enhanced information
        obj['fetched_description'] = description
        obj['name_extracted_from_description_for_tile_h1'] = name_from_desc

        # Add constellation information for stars
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
    """Create beautiful tiles to display astronomical objects."""
    if not objects:
        st.info("🌌 No astronomical objects are currently visible from your location.")
        return
    
    cols = st.columns(3)
    for idx, obj_data in enumerate(objects):
        with cols[idx % 3]:
            # Extract display information
            display_name_h1 = (obj_data['name_extracted_from_description_for_tile_h1'] 
                              if obj_data['name_extracted_from_description_for_tile_h1'] 
                              else obj_data['name'])
            display_name_h2 = obj_data.get('hip_id', '') if obj_data['type'] == 'Star' else ''
            description = obj_data['fetched_description']
            constellation = obj_data.get('constellation', "N/A")

            # Get image and create tile using Streamlit components for better reliability
            image_url = get_object_image_url(obj_data['name'])
            create_streamlit_object_tile(
                display_name_h1, display_name_h2, obj_data, 
                constellation, description, image_url
            )

def create_streamlit_object_tile(name_h1, name_h2, obj_data, constellation, description, image_url):
    """Create object tile using Streamlit components for better image handling."""
    # Create container with custom styling
    with st.container():
        # Add styling
        st.markdown(f"""
        <div style="border: 2px solid #ffd700; border-radius: 15px; padding: 15px; margin: 10px 0; 
                    background: linear-gradient(135deg, #232526 0%, #414345 100%); 
                    box-shadow: 0 4px 15px rgba(0,0,0,0.5); min-height: {TILE_HEIGHT}px;">
        """, unsafe_allow_html=True)
        
        # Image section using Streamlit's image component (more reliable)
        if image_url and image_url.startswith(('http://', 'https://')):
            try:
                st.image(image_url, width=250, caption=f"📸 {name_h1}")
            except Exception as e:
                st.markdown("🌌 **Image not available**")
                st.write(f"Debug: {str(e)[:50]}...")  # Debug info
        else:
            st.markdown("🌌 **No image found**")
        
        # Object type emoji
        type_emoji = {"Star": "⭐", "Planet": "🪐", "Sun": "☀️", "Moon": "🌙"}.get(obj_data['type'], "🌌")
        
        # Title and subtitle
        st.markdown(f"### {type_emoji} {name_h1}")
        if name_h2:
            st.markdown(f"**{name_h2}**")
        
        # Object details in columns
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Type:** {obj_data['type']}")
            st.write(f"**Altitude:** {obj_data['altitude']}°")
        with col2:
            st.write(f"**Azimuth:** {obj_data['azimuth']}°")
            st.write(f"**Constellation:** {constellation}")
        
        # Description
        if description and description != "Description not available.":
            desc_content = (description[:MAX_DESC_LEN] + "..." 
                           if len(description) > MAX_DESC_LEN 
                           else description)
            st.write(f"**Description:** {desc_content}")
            
            # Expandable full description
            if len(description) > MAX_DESC_LEN:
                with st.expander("📖 Read full description"):
                    st.write(description)
        
        st.markdown("</div>", unsafe_allow_html=True)

def render_sky_chart_section(visible_objects, dt):
    """Render the interactive sky chart section."""
    st.header("🌟 Sky Chart")
    
    # Zoom controls
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.button("🔍- Zoom Out"):
            idx = ZOOM_LEVELS.index(st.session_state.sky_zoom) if st.session_state.sky_zoom in ZOOM_LEVELS else 1
            if idx > 0:
                st.session_state.sky_zoom = ZOOM_LEVELS[idx-1]
    
    with col2:
        st.metric("🔍 Zoom Level", f"{st.session_state.sky_zoom}x")
    
    with col3:
        if st.button("🔍+ Zoom In"):
            idx = ZOOM_LEVELS.index(st.session_state.sky_zoom) if st.session_state.sky_zoom in ZOOM_LEVELS else 1
            if idx < len(ZOOM_LEVELS)-1:
                st.session_state.sky_zoom = ZOOM_LEVELS[idx+1]
    
    # Generate and display sky chart
    if visible_objects:
        chart_lat = st.session_state.get('latitude', 0.0)
        chart_lon = st.session_state.get('longitude', 0.0)
        
        with st.spinner("🌌 Generating Sky Chart..."):
            sky_chart_figure = create_sky_chart(
                visible_objects, dt, chart_lat, chart_lon, 
                zoom=st.session_state.sky_zoom
            )
            
            if sky_chart_figure:
                st.plotly_chart(sky_chart_figure, use_container_width=True)
            else:
                st.warning("⚠️ Could not generate the sky chart at this time.")
    else:
        st.info("ℹ️ No objects visible to display on sky chart.")

def main():
    """Main application function."""
    # Apply styling and initialize
    apply_custom_styling()
    initialize_session_state()
    
    # Main title
    st.title("🔭 Merai - A Space Detective")
    st.markdown("*Explore the cosmos from your location and time*")
    
    # Render sections
    render_location_section()
    dt = render_datetime_section()
    
    # Fetch and display astronomical objects
    st.header("🌌 Visible Astronomical Objects")
    
    with st.spinner("🔍 Scanning the cosmos for visible objects..."):
        visible_objects = get_visible_objects(
            st.session_state.latitude, 
            st.session_state.longitude, 
            dt
        )
        
        if not visible_objects:
            st.warning("🌑 No astronomical objects are currently visible from your location.")
            st.info("💡 Try adjusting the time or location to see different objects.")
            st.stop()
        
        # Enhance objects with additional information
        enhanced_objects = enhance_visible_objects(visible_objects, CONSTELLATION_MAP)
        
        # Display object tiles
        create_object_tiles(enhanced_objects)
    
    # Render sky chart
    render_sky_chart_section(visible_objects, dt)

# Run the application
if __name__ == "__main__":
    main()
