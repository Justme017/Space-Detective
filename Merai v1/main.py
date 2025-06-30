"""
Merai - A Space Detective

A Streamlit web application for exploring visible astronomical objects from any location
and time. This app provides detailed information about planets, stars, and other 
celestial objects, along with an interactive sky chart.

Author: Merai Development Team 
License: MIT
"""

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

# Configuration constants
MAX_DESC_LEN = 120
TILE_HEIGHT = 550
ZOOM_LEVELS = [0.7, 1.0, 1.3, 1.6, 2.0]

# Global data - load once at startup
CONSTELLATION_MAP = load_constellation_data()


class MeraiApp:
    """Main application class for the Merai Space Detective."""
    
    def __init__(self):
        """Initialize the Merai application."""
        self.setup_page_config()
        self.apply_custom_styling()
        self.initialize_session_state()
    
    def setup_page_config(self):
        """Configure Streamlit page settings."""
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
            .stApp {
                background: linear-gradient(120deg, #0f2027 0%, #2c5364 100%);
            }
            .block-container {
                background: rgba(20, 20, 30, 0.85);
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
    
    def initialize_session_state(self):
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
    
    def handle_location_detection(self):
        """Handle automatic location detection."""
        if st.button("🌍 Detect My Location Now", type="primary"):
            with st.spinner("🔍 Detecting your location..."):
                detected_lat, detected_lon, detected_address = get_user_location()
                if detected_lat is not None and detected_lon is not None:
                    st.session_state.latitude = detected_lat
                    st.session_state.longitude = detected_lon
                    st.session_state.address = detected_address
                    st.success(f"✅ Location detected: {detected_address}")
                    st.rerun()
                else:
                    st.session_state.address = "Automatic Detection Failed"
                    st.error("❌ Could not automatically determine location. Please try selecting on the map.")
    
    def handle_map_selection(self):
        """Handle manual location selection on map."""
        st.subheader("🗺️ Click on the map to set your location")
        
        # Create map centered on current location or default
        map_center_lat = st.session_state.get('latitude', 40.7128)  # Default to NYC
        map_center_lon = st.session_state.get('longitude', -74.0060)
        
        m = folium.Map(location=[map_center_lat, map_center_lon], zoom_start=5)
        
        # Add marker if location is set and valid
        if (st.session_state.address not in ["Not set", "Automatic Detection Failed"] and 
            -90 <= st.session_state.latitude <= 90 and 
            -180 <= st.session_state.longitude <= 180):
            folium.Marker(
                [st.session_state.latitude, st.session_state.longitude], 
                popup=st.session_state.address,
                icon=folium.Icon(color='red', icon='star')
            ).add_to(m)
        
        # Display map and handle clicks
        map_data = st_folium(m, height=400, use_container_width=True, key="folium_map_selector")
        
        if map_data and map_data.get("last_clicked"):
            clicked_lat = map_data['last_clicked']['lat']
            clicked_lon = map_data['last_clicked']['lng']
            if (st.session_state.latitude != clicked_lat or 
                st.session_state.longitude != clicked_lon):
                st.session_state.latitude = clicked_lat
                st.session_state.longitude = clicked_lon
                st.session_state.address = f"Map Selected: ({clicked_lat:.2f}, {clicked_lon:.2f})"
                st.rerun()
    
    def render_location_section(self):
        """Render the location selection section."""
        st.header("📍 Location")
        
        location_option = st.radio(
            "Choose location method:",
            ("Detect my location", "Select location on map"),
            key='location_choice',
            horizontal=True
        )
        
        if st.session_state.location_choice == "Detect my location":
            self.handle_location_detection()
        else:
            self.handle_map_selection()
        
        # Show current location if set
        if st.session_state.address not in ["Not set", "Automatic Detection Failed"]:
            st.success(
                f"📍 **Current Location:** {st.session_state.address} "
                f"({st.session_state.latitude:.2f}, {st.session_state.longitude:.2f})"
            )
    
    def render_datetime_section(self):
        """Render the date and time selection section."""
        st.header("🕒 Date and Time")
        
        col1, col2 = st.columns(2)
        with col1:
            st.date_input("📅 Date", key="user_selected_date")
        with col2:
            st.time_input("⏰ Time", key="user_selected_time")
        
        # Create combined datetime
        combined_dt = datetime.combine(
            st.session_state.user_selected_date, 
            st.session_state.user_selected_time
        ).replace(tzinfo=utc)
        
        # Show formatted datetime
        st.info(f"🗓️ Observing time: {combined_dt.strftime('%B %d, %Y at %H:%M UTC')}")
        
        return combined_dt
    
    def enhance_visible_objects(self, visible_objects):
        """
        Enhance astronomical objects with additional information from Wikipedia.
        
        Args:
            visible_objects (list): List of basic astronomical objects
            
        Returns:
            list: Enhanced objects with descriptions and constellation info
        """
        enhanced_objects = []
        
        for obj in visible_objects:
            # Get description for the object
            hip_id = obj.get('hip_id')
            description_lookup_key = hip_id if obj['type'] == 'Star' and hip_id else obj['name']
            description = get_object_description(description_lookup_key)

            # Extract better name from description for stars
            name_from_desc = None
            if obj['type'] == 'Star':
                name_from_desc = extract_name_from_description(description) if description else None
                if name_from_desc:
                    obj['name'] = name_from_desc

            # Add enhanced information
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
    
    def create_object_tile_html(self, name_h1, name_h2, obj_data, constellation, description, image_url):
        """
        Create object tile using minimal HTML to avoid rendering issues.
        
        Args:
            name_h1 (str): Primary name for display
            name_h2 (str): Secondary name (HIP ID for stars)
            obj_data (dict): Object data dictionary
            constellation (str): Constellation name
            description (str): Object description
            image_url (str): URL of object image
        """
        # Get object emoji
        type_emoji = self._get_object_emoji(obj_data['type'])
        
        # Create a simple container
        with st.container():
            # Add basic styling
            st.markdown("""
            <div style="border: 2px solid #ffd700; border-radius: 15px; padding: 15px; margin: 10px 0; background: linear-gradient(135deg, #232526 0%, #414345 100%); box-shadow: 0 4px 15px rgba(0,0,0,0.5);">
            """, unsafe_allow_html=True)
            
            # Image section
            if image_url and image_url.startswith(('http://', 'https://')):
                try:
                    st.image(image_url, width=200)
                except:
                    st.markdown(f"## {type_emoji} {name_h1}")
            else:
                st.markdown(f"## {type_emoji} {name_h1}")
            
            # Title and subtitle
            st.markdown(f"### 🌟 {name_h1}")
            if name_h2:
                st.markdown(f"**{name_h2}**")
            
            # Object details
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**{type_emoji} Type:** {obj_data['type']}")
                st.write(f"**🔺 Altitude:** {obj_data['altitude']}°")
            with col2:
                st.write(f"**🧭 Azimuth:** {obj_data['azimuth']}°")
                st.write(f"**✨ Constellation:** {constellation}")
            
            # Description
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
    
    def _get_object_emoji(self, obj_type):
        """Get appropriate emoji for object type."""
        return {"Star": "⭐", "Planet": "🪐", "Sun": "☀️", "Moon": "🌙"}.get(obj_type, "🌌")
    
    def create_object_tiles(self, objects):
        """
        Create beautiful tiles to display astronomical objects.
        
        Args:
            objects (list): List of enhanced astronomical objects
        """
        if not objects:
            st.info("🌌 No astronomical objects are currently visible from your location.")
            st.markdown("💡 **Tip:** Try adjusting the time or location to see different objects.")
            return
        
        # Sort objects by type and altitude (highest first)
        sorted_objects = sorted(objects, key=lambda x: (x['type'], -x['altitude']))
        
        # Display count
        st.metric("🌟 Visible Objects", len(objects))
        
        # Create tiles in columns
        cols = st.columns(3)
        for idx, obj_data in enumerate(sorted_objects):
            with cols[idx % 3]:
                # Extract display information
                display_name_h1 = (obj_data['name_extracted_from_description_for_tile_h1'] 
                                  if obj_data['name_extracted_from_description_for_tile_h1'] 
                                  else obj_data['name'])
                display_name_h2 = obj_data.get('hip_id', '') if obj_data['type'] == 'Star' else ''
                description = obj_data['fetched_description']
                constellation = obj_data.get('constellation', "N/A")

                # Get image
                image_url = get_object_image_url(obj_data['name'])
                
                # Create tile HTML
                self.create_object_tile_html(
                    display_name_h1, display_name_h2, obj_data, 
                    constellation, description, image_url
                )
    
    def render_sky_chart_section(self, visible_objects, dt):
        """
        Render the interactive sky chart section.
        
        Args:
            visible_objects (list): List of visible astronomical objects
            dt (datetime): Observation datetime
        """
        st.header("🌟 Interactive Sky Chart")
        
        # Zoom controls
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
            chart_lat = st.session_state.get('latitude', 0.0)
            chart_lon = st.session_state.get('longitude', 0.0)
            
            with st.spinner("🌌 Generating sky chart..."):
                try:
                    sky_chart_figure = create_sky_chart(
                        visible_objects, chart_lat, chart_lon, dt, 
                        zoom=st.session_state.sky_zoom
                    )
                    
                    if sky_chart_figure:
                        st.plotly_chart(sky_chart_figure, use_container_width=True, config={'displayModeBar': False})
                        st.info("💡 **Tip:** The sky chart shows the current view from your location. Higher altitude objects are more prominent.")
                    else:
                        st.warning("⚠️ Could not generate the sky chart at this time.")
                        
                except Exception as e:
                    st.error(f"❌ Error generating sky chart: {str(e)}")
        else:
            st.info("ℹ️ No objects visible to display on sky chart.")
    
    def run(self):
        """Run the main application."""
        # Main title and description - centered
        st.markdown(
            """
            <h1 style='text-align: center; color: #ffd700; margin-bottom: 0.5rem;'>
                🔭 Merai - A Space Detective
            </h1>
            <p style='text-align: center; color: #b0b0b0; font-style: italic; font-size: 1.2rem; margin-bottom: 2rem;'>
                🌌 Explore the cosmos from your location and time
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
        
        with st.spinner("🔍 Scanning the cosmos for visible objects..."):
            try:
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
            "🔭 **Merai - A Space Detective** | Built with ❤️ using Streamlit and Skyfield | "
            "Data from NASA JPL, Hipparcos, and Wikipedia"
        )


def main():
    """Entry point for the application."""
    try:
        app = MeraiApp()
        app.run()
    except Exception as e:
        st.error(f"❌ Application error: {str(e)}")
        st.info("Please refresh the page and try again.")


if __name__ == "__main__":
    main()
