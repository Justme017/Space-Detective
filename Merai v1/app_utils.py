
import streamlit as st
from datetime import date, datetime
from skyfield.api import utc
from streamlit_folium import st_folium
import folium
from streamlit_javascript import st_javascript

# Import custom modules (these contain the astronomy calculations)
from wiki_utils import get_object_image_url

# Configuration constants - these control the app behavior
MAX_DESC_LEN = 120  # Maximum description length to display
ZOOM_LEVELS = [0.7, 1.0, 1.3, 1.6, 2.0]  # Available zoom levels for sky chart

def apply_custom_styling():
    """Apply immersive space-themed styling to the app."""
    st.markdown(
        """
        <style>
                    /* Main app background with space gradient */
        .stApp {
            background: linear-gradient(120deg, #0f2027 0%, #2c5364 100%);
        }
        
                   /* Content container with dark space theme */
        .block-container {
            background: rgba(20, 20, 30, 0.85);
            border-radius: 18px;
            padding: 2rem 2rem 1rem 2rem;
            box-shadow: 0 8px 32px rgba(0,0,0,0.6);
        }
        
                 /* Make headers golden like stars */
        h1, h2, h3, h4, h5, h6 {
            color: #ffd700 !important;
        }
        
                 /* Style radio buttons for better visibility */
        .stRadio > div {
            color: #f1f1f1;
        }
        
                 /* Style metric containers */
        .stMetric {
            background: rgba(255, 215, 0, 0.1);
            padding: 1rem;
            border-radius: 8px;
            border: 1px solid rgba(255, 215, 0, 0.3);
        }
        </style>
        """,
        unsafe_allow_html=True
    )

def _get_gps_location():
    """Get GPS location using Vercel service."""
    st.session_state.location_request_count = st.session_state.get('location_request_count', 0) + 1
    
    location_data = st_javascript("""
        function() {
            return new Promise((resolve) => {
                let resolved = false;
                
                const iframe = document.createElement('iframe');
                iframe.src = 'https://geolocation-page.vercel.app';
                iframe.style.display = 'none';
                iframe.style.width = '1px';
                iframe.style.height = '1px';
                
                const messageHandler = (event) => {
                    if (event.origin === 'https://geolocation-page.vercel.app' && !resolved) {
                        resolved = true;
                        window.removeEventListener('message', messageHandler);
                        if (document.body.contains(iframe)) {
                            document.body.removeChild(iframe);
                        }
                        resolve(event.data);
                    }
                };
                
                window.addEventListener('message', messageHandler);
                document.body.appendChild(iframe);
                
                setTimeout(() => {
                    if (!resolved) {
                        resolved = true;
                        window.removeEventListener('message', messageHandler);
                        if (document.body.contains(iframe)) {
                            document.body.removeChild(iframe);
                        }
                        resolve({error: 'GPS timeout'});
                    }
                }, 30000);
            });
        }
        """, key=f"gps_request_{st.session_state.location_request_count}")
    
    return location_data

def _apply_coordinates(lat, lon, source="Manual"):
    """Apply coordinates to session state."""
    st.session_state.latitude = float(lat)
    st.session_state.longitude = float(lon)
    st.session_state.address = f"{source} ({lat:.6f}, {lon:.6f})"
    st.session_state.location_detected = True
    st.success(f"🎯 {source} coordinates applied!")
    st.rerun()

def render_gps_section():
    """Render GPS detection with Vercel window and manual input."""
    st.markdown("### 🛰️ GPS Location Detection")
    
    # Vercel Window and Manual Entry Side by Side
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("**🌐 Vercel GPS Service:**")
        import streamlit.components.v1 as components
        components.iframe(
            "https://geolocation-page.vercel.app",
            width=400,
            height=300,
            scrolling=True
        )
    
    with col2:
        st.markdown("**📍 Coordinate Entry:**")
        
        manual_lat = st.number_input(
            "Latitude",
            min_value=-90.0,
            max_value=90.0,
            value=0.000000,
            step=0.000001,
            format="%.6f",
            key="manual_lat"
        )
        
        manual_lon = st.number_input(
            "Longitude", 
            min_value=-180.0,
            max_value=180.0,
            value=0.000000,
            step=0.000001,
            format="%.6f",
            key="manual_lon"
        )
        
        col_auto, col_apply = st.columns(2)
        with col_auto:
            if st.button("📋 Auto-Fill", type="secondary"):
                st.info("💡 Copy coordinates from Vercel window above")
        
        with col_apply:
            if st.button("🚀 Apply Coordinates", type="primary"):
                if manual_lat != 0.0 or manual_lon != 0.0:
                    _apply_coordinates(manual_lat, manual_lon, "GPS Entry")
                else:
                    st.warning("⚠️ Enter valid coordinates")

def render_map_section():
    """Render interactive map for location selection."""
    st.markdown("### 🗺️ Map Location Selection")
    st.markdown("Click anywhere on the map to set your location:")
    
    # Create map
    map_center_lat = st.session_state.get('latitude', 53.462601)
    map_center_lon = st.session_state.get('longitude', 9.969690)
    
    m = folium.Map(location=[map_center_lat, map_center_lon], zoom_start=5)
    
    # Add marker if location is set
    if st.session_state.location_detected:
        folium.Marker(
            [st.session_state.latitude, st.session_state.longitude], 
            popup=st.session_state.address,
            icon=folium.Icon(color='red', icon='star')
        ).add_to(m)
    
    # Display map
    map_data = st_folium(m, height=400, use_container_width=True, key="location_map")
    
    # Handle map clicks
    if map_data and map_data.get("last_clicked"):
        clicked_lat = map_data['last_clicked']['lat']
        clicked_lon = map_data['last_clicked']['lng']
        
        if (st.session_state.latitude != clicked_lat or 
            st.session_state.longitude != clicked_lon):
            _apply_coordinates(clicked_lat, clicked_lon, "Map Selected")

def render_location_section():
    """Render the main location selection section."""
    # Header
    st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <h1 style="color: #ffd700; font-size: 3rem; margin-bottom: 0.5rem;">📍 Set Your Location</h1>
            <p style="color: #b0b0b0; font-size: 1.2rem;">
                Choose your observation point to discover the cosmos above you
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Show current location if detected
    if st.session_state.location_detected:
        # Success card
        if "GPS" in st.session_state.address:
            card_color = "#4CAF50"
            card_title = "🛰️ GPS LOCATION DETECTED"
        else:
            card_color = "#FFC107"
            card_title = "🗺️ LOCATION SELECTED"
        
        st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                border: 2px solid {card_color};
                border-radius: 15px;
                padding: 1.5rem;
                margin-bottom: 2rem;
                text-align: center;
                box-shadow: 0 8px 32px rgba(76, 175, 80, 0.3);
            ">
                <h3 style="color: {card_color}; margin-bottom: 1rem;">{card_title}</h3>
            </div>
        """, unsafe_allow_html=True)
        
        # Show coordinates
        col1, col2 = st.columns(2)
        with col1:
            st.metric("🌍 Latitude", f"{st.session_state.latitude:.6f}°")
        with col2:
            st.metric("🌍 Longitude", f"{st.session_state.longitude:.6f}°")
        
        st.success(f"✅ Current Location: {st.session_state.address}")
        
        # Change location button
        if st.button("🔄 Change Location", type="secondary"):
            st.session_state.location_detected = False
            st.rerun()
    
    else:
        # Location not set
        st.markdown("""
            <div style="
                background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
                border: 2px solid #FF5722;
                border-radius: 15px;
                padding: 1.5rem;
                margin-bottom: 2rem;
                text-align: center;
                box-shadow: 0 8px 32px rgba(255, 87, 34, 0.3);
            ">
                <h3 style="color: #FF5722; margin-bottom: 0.5rem;">⚠️ Location Required</h3>
                <p style="color: #333; margin-bottom: 0;">Please set your location to see astronomical objects</p>
            </div>
        """, unsafe_allow_html=True)
    
    # Location method selection
    st.markdown("### 🎯 Choose Location Method")
    
    location_method = st.radio(
        "",
        ("🛰️ GPS Detection", "🗺️ Map Selection"),
        horizontal=True,
        help="GPS provides highest accuracy, Map selection always works"
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Render selected method
    if location_method == "🛰️ GPS Detection":
        render_gps_section()
    else:
        render_map_section()

def render_datetime_section():
    """Render the date and time selection section."""
    st.header("🕒 Date and Time")
    
    # Create two columns for date and time inputs
    col1, col2 = st.columns(2)
    with col1:
        st.date_input(
            "📅 Date", 
            key="user_selected_date",
            help="Select the date you want to observe the sky"
        )
    with col2:
        st.time_input(
            "⏰ Time", 
            key="user_selected_time",
            help="Select the time you want to observe the sky (in your local time)"
        )
    
    # Combine date and time into a single datetime object
    combined_dt = datetime.combine(
        st.session_state.user_selected_date, 
        st.session_state.user_selected_time
    ).replace(tzinfo=utc)
    
    # Show the formatted datetime to the user
    st.info(f"🗓️ Observing time: {combined_dt.strftime('%B %d, %Y at %H:%M UTC')}")
    
    return combined_dt

def get_object_emoji(obj_type):
    """Get the appropriate emoji for each type of astronomical object."""
    emoji_map = {
        "Star": "⭐", 
        "Planet": "🪐", 
        "Sun": "☀️", 
        "Moon": "🌙"
    }
    return emoji_map.get(obj_type, "🌌")

def create_object_tile(obj_data):
    """
    Create a beautiful tile to display information about an astronomical object.
    
    Args:
        obj_data (dict): Dictionary containing all object information
    """
    # Get display information
    display_name = (obj_data['name_extracted_from_description_for_tile_h1'] 
                   if obj_data['name_extracted_from_description_for_tile_h1'] 
                   else obj_data['name'])
    secondary_name = obj_data.get('hip_id', '') if obj_data['type'] == 'Star' else ''
    description = obj_data['fetched_description']
    constellation = obj_data.get('constellation', "N/A")
    
    # Get emoji and image
    type_emoji = get_object_emoji(obj_data['type'])
    image_url = get_object_image_url(obj_data['name'])
    
    # Create tile with custom styling
    with st.container():
        st.markdown("""
        <div style="border: 2px solid #ffd700; border-radius: 15px; padding: 15px; margin: 10px 0; 
                    background: linear-gradient(135deg, #232526 0%, #414345 100%); 
                    box-shadow: 0 4px 15px rgba(0,0,0,0.5);">
        """, unsafe_allow_html=True)
        
        # Object name and type
        st.markdown(f"### {type_emoji} {display_name}")
        if secondary_name:
            st.markdown(f"**{secondary_name}**")

        # Create two columns for image and info
        col1, col2 = st.columns([1, 2])

        with col1:
            # Show image if available, otherwise show emoji
            if image_url and image_url.startswith(('http://', 'https://')):
                st.image(image_url, caption=display_name, use_container_width=True)
            else:
                st.markdown(f"<div style='text-align: center; font-size: 5rem;'>{type_emoji}</div>", 
                          unsafe_allow_html=True)

        with col2:
            # Show astronomical information
            st.write(f"**🌙 Type:** {obj_data['type']}")
            st.write(f"**🔺 Altitude:** {obj_data['altitude']:.2f}°")
            st.write(f"**🧭 Azimuth:** {obj_data['azimuth']:.2f}°")
            st.write(f"**✨ Constellation:** {constellation}")
        
        # Show description (truncated if too long)
        if description and description != "Description not available.":
            desc_content = (description[:MAX_DESC_LEN] + "..." 
                           if len(description) > MAX_DESC_LEN 
                           else description)
            st.write(f"**📖 Description:** {desc_content}")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Expandable full description
        if description and description != "Description not available." and len(description) > MAX_DESC_LEN:
            with st.expander("📖 Read full description"):
                st.write(description)

def create_object_tiles(objects):
    """
    Create tiles for all visible astronomical objects.
    
    Args:
        objects (list): List of enhanced astronomical objects
    """
    if not objects:
        st.info("🌌 No astronomical objects are currently visible from your location.")
        st.markdown("💡 **Tip:** Try adjusting the time or location to see different objects.")
        return
    
    # Sort objects by type and altitude (highest first for better visibility)
    sorted_objects = sorted(objects, key=lambda x: (x['type'], -x['altitude']))
    
    # Show count of visible objects
    st.metric("🌟 Visible Objects", len(objects))
    
    # Create tiles in 3 columns
    cols = st.columns(3)
    for idx, obj_data in enumerate(sorted_objects):
        with cols[idx % 3]:
            create_object_tile(obj_data)

def render_sky_chart_section(visible_objects, dt, create_sky_chart):
    """
    Render the interactive sky chart section.
    
    Args:
        visible_objects (list): List of visible astronomical objects
        dt (datetime): Observation datetime
        create_sky_chart (function): Function to generate the sky chart
    """
    st.header("🌟 Interactive Sky Chart")
    
    # Create zoom controls
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.button("🔍 Zoom Out", disabled=st.session_state.sky_zoom <= min(ZOOM_LEVELS)):
            idx = ZOOM_LEVELS.index(st.session_state.sky_zoom) if st.session_state.sky_zoom in ZOOM_LEVELS else 1
            if idx > 0:
                st.session_state.sky_zoom = ZOOM_LEVELS[idx-1]
                st.rerun()
    
    with col2:
        st.metric("🔍 Zoom Level", f"{st.session_state.sky_zoom}x")
    
    with col3:
        if st.button("🔍 Zoom In", disabled=st.session_state.sky_zoom >= max(ZOOM_LEVELS)):
            idx = ZOOM_LEVELS.index(st.session_state.sky_zoom) if st.session_state.sky_zoom in ZOOM_LEVELS else 1
            if idx < len(ZOOM_LEVELS)-1:
                st.session_state.sky_zoom = ZOOM_LEVELS[idx+1]
                st.rerun()
    
    # Generate and display sky chart
    if visible_objects:
        with st.spinner("🌌 Generating sky chart..."):
            try:
                sky_chart_figure = create_sky_chart(
                    visible_objects, 
                    st.session_state.latitude, 
                    st.session_state.longitude, 
                    dt, 
                    zoom=st.session_state.sky_zoom
                )
                
                if sky_chart_figure:
                    st.plotly_chart(sky_chart_figure, use_container_width=True, 
                                  config={'displayModeBar': False})
                    st.info("💡 **Tip:** The sky chart shows the current view from your location. "
                           "Higher altitude objects are more prominent in the sky.")
                else:
                    st.warning("⚠️ Could not generate the sky chart at this time.")
                    
            except Exception as e:
                st.error(f"❌ Error generating sky chart: {str(e)}")

        # Add online sky atlas
        st.markdown("---")
        st.subheader("🛰️ Online Sky Atlas")
        st.markdown("*Explore the night sky with the interactive Aladin Lite viewer below*")

        # Embed Aladin Lite sky atlas
        import streamlit.components.v1 as components
        components.html(
            '<iframe src="https://aladin.u-strasbg.fr/AladinLite/" width="100%" height="600" style="border:none;"></iframe>',
            height=600
        )
    else:
        st.info("ℹ️ No objects visible to display on sky chart.")
