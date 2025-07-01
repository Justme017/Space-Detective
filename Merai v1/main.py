"""
Merai - A Space Detective v2.0.0

Author: Merai Development Team 
License: MIT
Version: 2.0.0 - Live App Release
"""

import streamlit as st
from datetime import date, datetime
from skyfield.api import utc
from streamlit_folium import st_folium
from streamlit_javascript import st_javascript
import folium

# Import custom modules (these contain the astronomy calculations)
from astro_utils import get_visible_objects
from wiki_utils import get_object_image_url, get_object_description, extract_name_from_description
from constellation_utils import load_constellation_data
from skychart_utils import create_sky_chart

# Configuration constants - these control the app behavior
MAX_DESC_LEN = 120  # Maximum description length to display
ZOOM_LEVELS = [0.7, 1.0, 1.3, 1.6, 2.0]  # Available zoom levels for sky chart

# Load constellation data once at startup (this is more efficient)
CONSTELLATION_MAP = load_constellation_data()


class MeraiApp:
    """Main application class for the Merai Space Detective."""
    
    def __init__(self):
        """Initialize the application with page settings and styling."""
        self.setup_page_config()
        self.apply_custom_styling()
        self.initialize_session_state()
    
    def setup_page_config(self):
        """Configure basic Streamlit page settings."""
        st.set_page_config(
            page_title="Merai - A Space Detective",
            page_icon="🔭",
            layout="wide",
            initial_sidebar_state="collapsed"
        )
    
    def apply_custom_styling(self):
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
            
            /* Container for manual coordinate entry */
            .manual-entry-container {
                background: rgba(20, 30, 40, 0.8);
                padding: 1.5rem;
                border-radius: 15px;
                border: 1px solid #2c5364;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
    
    def initialize_session_state(self):
        """Initialize all session state variables with default values."""
        # Session state keeps track of user selections between app reruns
        defaults = {
            'latitude': 0.0,
            'longitude': 0.0,
            'address': "Not set",
            'user_selected_date': date.today(),
            'user_selected_time': datetime.now().time(),
            'sky_zoom': 1.0,
            'location_detected': False
        }
        
        # Only set values that haven't been set yet
        for key, default_value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = default_value
    
    def _apply_coordinates(self, lat, lon, source="Manual"):
        """Apply coordinates to session state."""
        st.session_state.latitude = float(lat)
        st.session_state.longitude = float(lon)
        st.session_state.address = f"{source} ({lat:.6f}, {lon:.6f})"
        st.session_state.location_detected = True
        st.success(f"🎯 {source} coordinates applied!")
        st.rerun()

    def render_gps_section(self):
        """Render GPS detection with Vercel window and manual input."""
        
        st.markdown(
            """
            <div style="display: flex; gap: 0; align-items: stretch;">
                <!-- GPS Section -->
                <div style="flex: 1.1; background: rgba(20, 20, 30, 0.85); border-radius: 15px; padding: 1.1rem 1rem; margin-right: 5px;">
                    <h3 style="color: #ffd700;">🛰️ GPS Location Detection</h3>
                    <p style="color: #f1f1f1;"><strong>🌐 Vercel GPS Service:</strong></p>
                    <div style="border-radius: 15px; overflow: hidden; height: 300px;">
                        <iframe src="https://geolocation-page.vercel.app" width="100%" height="100%" style="border:none;"></iframe>
                    </div>
                </div>

                <!-- Manual Entry Section -->
                <div style="flex: 1; background: rgba(20, 20, 30, 0.85); border-radius: 15px; padding: 1.1rem 1rem; margin-left: 5px;">
                    <h3 style="color: #ffd700;">📍 Coordinate Entry</h3>
                    <!-- Streamlit widgets will be rendered below this HTML block -->
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # We need to recreate the layout with columns to place the widgets, 
        # but the visible styling will come from the HTML above.
        col1, col2 = st.columns([1.1, 1], gap="small")

        with col1:
            # This column is a placeholder for layout alignment.
            # The content is already defined in the HTML above.
            # We just need to make sure the space is occupied.
            st.markdown('<div style="height: 340px;"></div>', unsafe_allow_html=True)


        with col2:
            # The manual entry widgets are placed in the second column,
            # which aligns with the styled div in the HTML.
            manual_lat = st.number_input(
                "Latitude",
                min_value=-90.0,
                max_value=90.0,
                value=st.session_state.get('latitude', 0.0),
                step=0.000001,
                format="%.6f",
                key="manual_lat",
                label_visibility="collapsed"
            )
            
            manual_lon = st.number_input(
                "Longitude", 
                min_value=-180.0,
                max_value=180.0,
                value=st.session_state.get('longitude', 0.0),
                step=0.000001,
                format="%.6f",
                key="manual_lon",
                label_visibility="collapsed"
            )
            
            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
            if st.button("🚀 Apply Coordinates", type="primary"):
                if manual_lat != 0.0 or manual_lon != 0.0:
                    self._apply_coordinates(manual_lat, manual_lon, "Manual Entry")
                else:
                    st.warning("⚠️ Enter valid coordinates")

    def handle_location_detection(self):
        """
        Handle automatic location detection using only GPS service.
        
        This method provides GPS-based location detection:
        1. Browser GPS through Vercel-hosted service (PRIMARY - most accurate)
        2. Extended wait time for GPS response
        3. Manual map selection if GPS fails or is denied
        4. No IP-based fallback - only precise GPS or user selection
        """
        if not st.session_state.location_detected:
            if st.button("🌍 Detect My Location", type="primary"):
                with st.spinner("🔍 Getting your precise GPS location..."):
                    # Primary attempt: GPS location via Vercel
                    st.info("�️ Requesting GPS location from your device...")
                    st.info("💡 Please allow location access when prompted for best accuracy")
                    
                    location_data = self._get_gps_location()
                    
                    if location_data and "latitude" in location_data and "longitude" in location_data:
                        # SUCCESS! GPS location detected
                        st.success("🎯 Excellent! GPS location detected with high accuracy!")
                        self._set_location_from_gps(location_data)
                        
                    elif location_data and "error" in location_data:
                        # GPS explicitly failed (user denied, not supported, etc.)
                        error_msg = location_data.get("error", "Unknown GPS error")
                        st.warning(f"🌍 GPS Error: {error_msg}")
                        
                        # Show user-friendly message and offer alternatives
                        if "denied" in error_msg.lower() or "permission" in error_msg.lower():
                            st.info("💡 **To enable GPS:** Refresh the page and click 'Allow' when prompted")
                            st.info("📍 **Alternative:** Use the map selection below to manually choose your location")
                            
                            # Give user choice: try again or use manual selection
                            if st.button("🔄 Try GPS Again"):
                                st.rerun()
                            st.info("👇 **Or scroll down to use the interactive map for manual location selection**")
                        else:
                            # For other GPS errors, encourage manual selection
                            st.info("📍 **Please use the interactive map below to manually select your location**")
                            if st.button("� Try GPS Again"):
                                st.rerun()
                        
                    else:
                        # No response from GPS service (timeout or service issue)
                        st.warning("🌍 GPS service taking longer than expected...")
                        st.info("🔧 This might be due to:")
                        st.info("   • Slow internet connection")
                        st.info("   • Browser security settings")
                        st.info("   • Service temporarily unavailable")
                        
                        # Give user options: try again or use manual selection
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("🔄 Try GPS Again"):
                                st.rerun()
                        with col2:
                            st.info("� **Use the map below to select your location manually**")
        else:
            # Location already detected, show it and offer refresh option
            st.success(f"✅ Location detected: {st.session_state.address}")
            if st.button("🔄 Refresh Location"):
                st.session_state.location_detected = False
                st.rerun()
    
    def _get_gps_location(self):
        """
        Get GPS location using Vercel-hosted service with extended timeout.
        
        This method prioritizes GPS accuracy by:
        - Using longer timeout (45 seconds instead of 25)
        - Better error handling and user feedback
        - More detailed logging for debugging
        """
        # Increment counter for unique component keys
        st.session_state.location_request_count = st.session_state.get('location_request_count', 0) + 1
        
        # Use JavaScript to get location from Vercel service with extended patience
        location_data = st_javascript("""
            function() {
                return new Promise((resolve) => {
                    let resolved = false;
                    let messageCount = 0;
                    
                    console.log('🛰️ Starting HIGH-PRIORITY GPS location request via Vercel...');
                    
                    // Create invisible iframe to load Vercel geolocation service
                    const iframe = document.createElement('iframe');
                    iframe.src = 'https://geolocation-page.vercel.app';
                    iframe.style.display = 'none';
                    iframe.style.width = '1px';
                    iframe.style.height = '1px';
                    
                    // Listen for location data from the iframe
                    const messageHandler = (event) => {
                        messageCount++;
                        console.log(`📨 GPS Message ${messageCount} from:`, event.origin);
                        console.log('📍 GPS Data received:', event.data);
                        
                        if (event.origin === 'https://geolocation-page.vercel.app' && !resolved) {
                            console.log('✅ VALID GPS message from Vercel service!');
                            resolved = true;
                            window.removeEventListener('message', messageHandler);
                            
                            // Clean up iframe
                            if (document.body.contains(iframe)) {
                                document.body.removeChild(iframe);
                            }
                            
                            resolve(event.data);
                        } else if (!resolved) {
                            console.log('⚠️ GPS message from unknown origin:', event.origin);
                        }
                    };
                    
                    // Set up message listener and add iframe to page
                    window.addEventListener('message', messageHandler);
                    document.body.appendChild(iframe);
                    console.log('📱 GPS iframe loaded, waiting for location response...');
                    
                    // EXTENDED timeout - give GPS more time to work (45 seconds)
                    setTimeout(() => {
                        if (!resolved) {
                            console.log(`⏰ GPS timeout after 45 seconds. Messages received: ${messageCount}`);
                            resolved = true;
                            window.removeEventListener('message', messageHandler);
                            
                            if (document.body.contains(iframe)) {
                                document.body.removeChild(iframe);
                            }
                            
                            resolve({
                                error: 'GPS location timeout - service may be slow or unavailable',
                                debug: {
                                    messagesReceived: messageCount,
                                    timeoutAfter: '45 seconds',
                                    service: 'Vercel GPS'
                                }
                            });
                        }
                    }, 45000); // Extended to 45 seconds
                });
            }
            """, key=f"gps_priority_request_{st.session_state.location_request_count}")
        
        return location_data
    
    def _set_location_from_gps(self, location_data):
        """Set location from GPS data and update session state."""
        st.success("🎯 GPS Location Successfully Detected!")
        st.session_state.latitude = float(location_data["latitude"])
        st.session_state.longitude = float(location_data["longitude"])
        accuracy = location_data.get('accuracy', 'unknown')
        st.session_state.address = f"GPS Location ({location_data['latitude']:.4f}, {location_data['longitude']:.4f}) ±{accuracy}m"
        st.session_state.location_detected = True
        st.balloons()  # Celebrate success!
        st.rerun()
      
    def handle_map_selection(self):
        """Handle manual location selection using an interactive map."""
        st.subheader("🗺️ Click on the map to set your location")
        
        # Create map centered on current location or default (Hamburg)
        map_center_lat = st.session_state.get('latitude', 53.462601)
        map_center_lon = st.session_state.get('longitude', 9.969690)
        
        # Create the map using Folium
        m = folium.Map(location=[map_center_lat, map_center_lon], zoom_start=5)
        
        # Add marker if location is already set and valid
        if (st.session_state.address not in ["Not set", "Automatic Detection Failed"] and 
            -90 <= st.session_state.latitude <= 90 and 
            -180 <= st.session_state.longitude <= 180):
            folium.Marker(
                [st.session_state.latitude, st.session_state.longitude], 
                popup=st.session_state.address,
                icon=folium.Icon(color='red', icon='star')
            ).add_to(m)
        
        # Display map and handle clicks
        map_data = st_folium(m, height=400, use_container_width=True, key="map_selector")
        
        # Check if user clicked on the map
        if map_data and map_data.get("last_clicked"):
            clicked_lat = map_data['last_clicked']['lat']
            clicked_lon = map_data['last_clicked']['lng']
            
            # Update location if user clicked on a different spot
            if (st.session_state.latitude != clicked_lat or 
                st.session_state.longitude != clicked_lon):
                self._apply_coordinates(clicked_lat, clicked_lon, "Map Selected")
    
    def render_location_section(self):
        """Render the location selection section of the app."""
        st.header("📍 Location")
        
        # Let user choose between automatic detection or manual selection
        location_option = st.radio(
            "Choose how to set your location:",
            ("GPS and Manual Entry", "Select on map"),
            key='location_choice',
            horizontal=True,
            help="GPS detection is more accurate but requires permission. Map selection always works."
        )
        
        # Handle the selected option
        if st.session_state.location_choice == "GPS and Manual Entry":
            self.render_gps_section()
        else:
            self.handle_map_selection()
        
        # Show current location information if available
        if st.session_state.location_detected:
            if "GPS Location" in st.session_state.address or "Manual Entry" in st.session_state.address or "Map Selected" in st.session_state.address:
                st.success("🎯 **Location Set**")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("📍 Latitude", f"{st.session_state.latitude:.6f}")
                with col2:
                    st.metric("📍 Longitude", f"{st.session_state.longitude:.6f}")
                st.success(f"🎯 {st.session_state.address}")
            else:
                # Manual or other location selection
                st.success(
                    f"📍 **Current Location:** {st.session_state.address} "
                    f"({st.session_state.latitude:.4f}, {st.session_state.longitude:.4f})"
                )
    
    def render_datetime_section(self):
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
    
    def enhance_visible_objects(self, visible_objects):
        """
        Enhance astronomical objects with additional information from Wikipedia.
        
        This function takes the basic astronomical data and adds:
        - Detailed descriptions from Wikipedia
        - Constellation information for stars
        - Better names extracted from descriptions
        
        Args:
            visible_objects (list): List of basic astronomical objects
            
        Returns:
            list: Enhanced objects with additional information
        """
        enhanced_objects = []
        
        for obj in visible_objects:
            # Get Wikipedia description for the object
            hip_id = obj.get('hip_id')
            # For stars, use HIP ID if available, otherwise use name
            description_lookup_key = hip_id if obj['type'] == 'Star' and hip_id else obj['name']
            description = get_object_description(description_lookup_key)

            # Try to extract a better name from the description for stars
            name_from_desc = None
            if obj['type'] == 'Star' and description:
                name_from_desc = extract_name_from_description(description)
                if name_from_desc:
                    obj['name'] = name_from_desc

            # Add the enhanced information to the object
            obj['fetched_description'] = description
            obj['name_extracted_from_description_for_tile_h1'] = name_from_desc

            # Add constellation information for stars
            if obj['type'] == 'Star':
                hip_int_for_lookup = obj.get('hip_int')
                if hip_int_for_lookup and CONSTELLATION_MAP:
                    obj['constellation'] = CONSTELLATION_MAP.get(hip_int_for_lookup, "Unknown")
                else:
                    obj['constellation'] = "Unknown"
            else:
                obj['constellation'] = "N/A"

            enhanced_objects.append(obj)
        
        return enhanced_objects
    
    def get_object_emoji(self, obj_type):
        """Get the appropriate emoji for each type of astronomical object."""
        emoji_map = {
            "Star": "⭐", 
            "Planet": "🪐", 
            "Sun": "☀️", 
            "Moon": "🌙"
        }
        return emoji_map.get(obj_type, "🌌")
    
    def create_object_tile(self, obj_data):
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
        type_emoji = self.get_object_emoji(obj_data['type'])
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
    
    def create_object_tiles(self, objects):
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
                self.create_object_tile(obj_data)
    
    def render_sky_chart_section(self, visible_objects, dt):
        """
        Render the interactive sky chart section.
        
        Args:
            visible_objects (list): List of visible astronomical objects
            dt (datetime): Observation datetime
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
    
    def run(self):
        """Run the main application."""
        # App title and description
        st.markdown(
            """
            <h1 style='text-align: center; color: #ffd700; margin-bottom: 0.5rem;'>
                🔭 Merai - A Space Detective
            </h1>
            <p style='text-align: center; color: #b0b0b0; font-style: italic; font-size: 1.2rem; margin-bottom: 0.5rem;'>
                🌌 Explore the cosmos from your location and time
            </p>
            <p style='text-align: center; color: #808080; font-size: 0.9rem; margin-bottom: 2rem;'>
                v2.0.0 - Live App Release 🚀
            </p>
            """,
            unsafe_allow_html=True
        )
        st.markdown("---")
        
        # Render main sections
        self.render_location_section()
        dt = self.render_datetime_section()
        
        # Validate location before proceeding
        if st.session_state.address in ["Not set", "Automatic Detection Failed"]:
            st.warning("📍 Please set your location to see visible astronomical objects.")
            st.stop()
        
        # Fetch and display astronomical objects
        st.header("🌌 Visible Astronomical Objects")
        st.markdown("*Objects visible from your location at the selected time*")
        
        with st.spinner("🔍 Scanning the cosmos for visible objects..."):
            try:
                # Get visible objects using astronomical calculations
                visible_objects = get_visible_objects(
                    st.session_state.latitude, 
                    st.session_state.longitude, 
                    dt
                )
                
                if not visible_objects:
                    st.warning("🌑 No astronomical objects are currently visible from your location.")
                    st.info("💡 Try adjusting the time or location to see different objects.")
                    st.stop()
                
                # Enhance objects with Wikipedia information
                enhanced_objects = self.enhance_visible_objects(visible_objects)
                
                # Display object tiles
                self.create_object_tiles(enhanced_objects)
                
            except Exception as e:
                st.error(f"❌ Error fetching astronomical data: {str(e)}")
                st.info("Please check your internet connection and try again.")
                st.stop()
        
        # Render sky chart
        self.render_sky_chart_section(visible_objects, dt)
        
        # Footer
        st.markdown("---")
        st.markdown(
            """
            <div style='text-align: center; color: #888; font-size: 0.9rem;'>
                🔭 <strong>Merai - A Space Detective</strong> | 
                Built with ❤️ using Streamlit and Skyfield | 
                Data from NASA JPL, Hipparcos, and Wikipedia<br>
                <em>Educational tool for learning astronomy and web development</em>
            </div>
            """,
            unsafe_allow_html=True
        )


def main():
    """
    Entry point for the application.
    
    This function creates and runs the Merai app, with error handling
    to provide a good user experience even if something goes wrong.
    """
    try:
        app = MeraiApp()
        app.run()
    except Exception as e:
        st.error(f"❌ Application error: {str(e)}")
        st.info("Please refresh the page and try again.")


if __name__ == "__main__":
    main()
