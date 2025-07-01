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

from astro_utils import get_visible_objects
from wiki_utils import get_object_image_url, get_object_description, extract_name_from_description
from constellation_utils import load_constellation_data
from skychart_utils import create_sky_chart

MAX_DESC_LEN = 120  
ZOOM_LEVELS = [0.7, 1.0, 1.3, 1.6, 2.0]  

CONSTELLATION_MAP = load_constellation_data()


class MeraiApp:
    
    def __init__(self):
        self.setup_page_config()
        self.apply_custom_styling()
        self.initialize_session_state()
    
    def setup_page_config(self):
        st.set_page_config(
            page_title="Merai - A Space Detective",
            page_icon="🔭",
            layout="wide",
            initial_sidebar_state="collapsed"
        )
    
    def apply_custom_styling(self):
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
        defaults = {
            'latitude': 0.0,
            'longitude': 0.0,
            'address': "Not set",
            'user_selected_date': date.today(),
            'user_selected_time': datetime.now().time(),
            'sky_zoom': 1.0,
            'location_detected': False
        }
        
        for key, default_value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = default_value
    
    def _apply_coordinates(self, lat, lon, source="Manual"):
        st.session_state.latitude = float(lat)
        st.session_state.longitude = float(lon)
        st.session_state.address = f"{source} ({lat:.6f}, {lon:.6f})"
        st.session_state.location_detected = True
        st.success(f"🎯 {source} coordinates applied!")
        st.rerun()

    def render_gps_section(self):
        import streamlit.components.v1 as components
        
        st.markdown("### 🛰️ GPS Location & Manual Entry")
        col1, col2 = st.columns([1.1, 1], gap="medium")

        with col1:
            st.markdown("**🌐 GPS Service:**")
            components.iframe(
                "https://geolocation-page.vercel.app",
                width=800,
                height=300,
                scrolling=True
            )

        with col2:
            st.markdown("**📍 Coordinate Entry:**")
            
            manual_lat = st.number_input(
                "Latitude",
                min_value=-90.0,
                max_value=90.0,
                value=st.session_state.get('latitude', 0.0),
                step=0.000001,
                format="%.6f",
                key="manual_lat"
            )
            
            manual_lon = st.number_input(
                "Longitude", 
                min_value=-180.0,
                max_value=180.0,
                value=st.session_state.get('longitude', 0.0),
                step=0.000001,
                format="%.6f",
                key="manual_lon"
            )
            
            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
            if st.button("🚀 Apply Coordinates", type="primary"):
                if manual_lat != 0.0 or manual_lon != 0.0:
                    self._apply_coordinates(manual_lat, manual_lon, "Manual Entry")
                else:
                    st.warning("⚠️ Enter valid coordinates")

    def handle_location_detection(self):
        
        if not st.session_state.location_detected:
            if st.button("🌍 Detect My Location", type="primary"):
                with st.spinner("🔍 Getting your precise GPS location..."):
                    st.info("�️ Requesting GPS location from your device...")
                    st.info("💡 Please allow location access when prompted for best accuracy")
                    
                    location_data = self._get_gps_location()
                    
                    if location_data and "latitude" in location_data and "longitude" in location_data:
                        st.success("🎯 Excellent! GPS location detected with high accuracy!")
                        self._set_location_from_gps(location_data)
                        
                    elif location_data and "error" in location_data:
                        error_msg = location_data.get("error", "Unknown GPS error")
                        st.warning(f"🌍 GPS Error: {error_msg}")
                        
                        if "denied" in error_msg.lower() or "permission" in error_msg.lower():
                            st.info("💡 **To enable GPS:** Refresh the page and click 'Allow' when prompted")
                            st.info("📍 **Alternative:** Use the map selection below to manually choose your location")
                            
                            if st.button("🔄 Try GPS Again"):
                                st.rerun()
                            st.info("👇 **Or scroll down to use the interactive map for manual location selection**")
                        else:
                            st.info("📍 **Please use the interactive map below to manually select your location**")
                            if st.button("� Try GPS Again"):
                                st.rerun()
                        
                    else:
                        st.warning("🌍 GPS service taking longer than expected...")
                        st.info("🔧 This might be due to:")
                        st.info("   • Slow internet connection")
                        st.info("   • Browser security settings")
                        st.info("   • Service temporarily unavailable")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("🔄 Try GPS Again"):
                                st.rerun()
                        with col2:
                            st.info("� **Use the map below to select your location manually**")
        else:
            st.success(f"✅ Location detected: {st.session_state.address}")
            if st.button("🔄 Refresh Location"):
                st.session_state.location_detected = False
                st.rerun()
    
    def _get_gps_location(self):
        
        st.session_state.location_request_count = st.session_state.get('location_request_count', 0) + 1
        
        location_data = st_javascript("""
            function() {
                return new Promise((resolve) => {
                    let resolved = false;
                    let messageCount = 0;
                    
                    console.log('🛰️ Starting HIGH-PRIORITY GPS location request via Vercel...');
                    
                    const iframe = document.createElement('iframe');
                    iframe.src = 'https://geolocation-page.vercel.app';
                    iframe.style.display = 'none';
                    iframe.style.width = '1px';
                    iframe.style.height = '1px';
                    
                    const messageHandler = (event) => {
                        messageCount++;
                        console.log(`📨 GPS Message ${messageCount} from:`, event.origin);
                        console.log('📍 GPS Data received:', event.data);
                        
                        if (event.origin === 'https://geolocation-page.vercel.app' && !resolved) {
                            console.log('✅ VALID GPS message from Vercel service!');
                            resolved = true;
                            window.removeEventListener('message', messageHandler);
                            
                            if (document.body.contains(iframe)) {
                                document.body.removeChild(iframe);
                            }
                            
                            resolve(event.data);
                        } else if (!resolved) {
                            console.log('⚠️ GPS message from unknown origin:', event.origin);
                        }
                    };
                    
                    window.addEventListener('message', messageHandler);
                    document.body.appendChild(iframe);
                    console.log('📱 GPS iframe loaded, waiting for location response...');
                    
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
        st.success("🎯 GPS Location Successfully Detected!")
        st.session_state.latitude = float(location_data["latitude"])
        st.session_state.longitude = float(location_data["longitude"])
        accuracy = location_data.get('accuracy', 'unknown')
        st.session_state.address = f"GPS Location ({location_data['latitude']:.4f}, {location_data['longitude']:.4f}) ±{accuracy}m"
        st.session_state.location_detected = True
        st.balloons()
        st.rerun()
      
    def handle_map_selection(self):
        st.subheader("🗺️ Click on the map to set your location")
        
        map_center_lat = st.session_state.get('latitude', 53.462601)
        map_center_lon = st.session_state.get('longitude', 9.969690)
        
        m = folium.Map(location=[map_center_lat, map_center_lon], zoom_start=5)
        
        if (st.session_state.address not in ["Not set", "Automatic Detection Failed"] and 
            -90 <= st.session_state.latitude <= 90 and 
            -180 <= st.session_state.longitude <= 180):
            folium.Marker(
                [st.session_state.latitude, st.session_state.longitude], 
                popup=st.session_state.address,
                icon=folium.Icon(color='red', icon='star')
            ).add_to(m)
        
        map_data = st_folium(m, height=400, use_container_width=True, key="map_selector")
        
        if map_data and map_data.get("last_clicked"):
            clicked_lat = map_data['last_clicked']['lat']
            clicked_lon = map_data['last_clicked']['lng']
            
            if (st.session_state.latitude != clicked_lat or 
                st.session_state.longitude != clicked_lon):
                self._apply_coordinates(clicked_lat, clicked_lon, "Map Selected")
    
    def render_location_section(self):
        st.header("📍 Location")
        
        location_option = st.radio(
            "Choose how to set your location:",
            ("GPS and Manual Entry", "Select on map"),
            key='location_choice',
            horizontal=True,
            help="GPS detection is more accurate but requires permission. Map selection always works."
        )
        
        if st.session_state.location_choice == "GPS and Manual Entry":
            self.render_gps_section()
        else:
            self.handle_map_selection()
        
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
                st.success(
                    f"📍 **Current Location:** {st.session_state.address} "
                    f"({st.session_state.latitude:.4f}, {st.session_state.longitude:.4f})"
                )
    
    def render_datetime_section(self):
        st.header("🕒 Date and Time")
        
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
        
        combined_dt = datetime.combine(
            st.session_state.user_selected_date, 
            st.session_state.user_selected_time
        ).replace(tzinfo=utc)
        
        st.info(f"🗓️ Observing time: {combined_dt.strftime('%B %d, %Y at %H:%M UTC')}")
        
        return combined_dt
    
    def enhance_visible_objects(self, visible_objects):
        enhanced_objects = []
        
        for obj in visible_objects:
            hip_id = obj.get('hip_id')
            description_lookup_key = hip_id if obj['type'] == 'Star' and hip_id else obj['name']
            description = get_object_description(description_lookup_key)

            name_from_desc = None
            if obj['type'] == 'Star' and description:
                name_from_desc = extract_name_from_description(description)
                obj['name_from_description'] = name_from_desc

            obj['fetched_description'] = description

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
        emoji_map = {
            "Star": "⭐", 
            "Planet": "🪐", 
            "Sun": "☀️", 
            "Moon": "🌙"
        }
        return emoji_map.get(obj_type, "🌌")
    
    def create_object_tile(self, obj_data):
        display_name = obj_data.get('name') or obj_data.get('name_from_description') or obj_data.get('hip_id', 'Unnamed Star')
        secondary_name = obj_data.get('hip_id', '') if obj_data['type'] == 'Star' and display_name != obj_data.get('hip_id') else ''
        description = obj_data.get('fetched_description') # Use .get for safety
        constellation = obj_data.get('constellation', "N/A")
        
        type_emoji = self.get_object_emoji(obj_data['type'])
        image_url = get_object_image_url(display_name)
        
        with st.container():
            st.markdown("""
            <div style="border: 2px solid #ffd700; border-radius: 15px; padding: 15px; margin: 10px 0; 
                        background: linear-gradient(135deg, #232526 0%, #414345 100%); 
                        box-shadow: 0 4px 15px rgba(0,0,0,0.5);">
            """, unsafe_allow_html=True)
            
            st.markdown(f"### {type_emoji} {display_name}")
            if secondary_name:
                st.markdown(f"**{secondary_name}**")

            col1, col2 = st.columns([1, 2])

            with col1:
                if image_url and image_url.startswith(('http://', 'https://')):
                    st.image(image_url, caption=display_name, use_container_width=True)
                else:
                    st.markdown(f"<div style='text-align: center; font-size: 5rem;'>{type_emoji}</div>", 
                              unsafe_allow_html=True)

            with col2:
                st.write(f"**🌙 Type:** {obj_data['type']}")
                st.write(f"**🔺 Altitude:** {obj_data['altitude']:.2f}°")
                st.write(f"**🧭 Azimuth:** {obj_data['azimuth']:.2f}°")
                st.write(f"**✨ Constellation:** {constellation}")
            
            if description and description != "Description not available.":
                if len(description) > MAX_DESC_LEN:
                    desc_content = description[:MAX_DESC_LEN] + "..."
                    st.write(f"**📖 Description:** {desc_content}")
                    with st.expander("📖 Read full description"):
                        st.write(description)
                else:
                    st.write(f"**📖 Description:** {description}")
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    def create_object_tiles(self, objects):
        if not objects:
            st.info("🌌 No astronomical objects are currently visible from your location.")
            st.markdown("💡 **Tip:** Try adjusting the time or location to see different objects.")
            return
        
        sorted_objects = sorted(objects, key=lambda x: (x['type'], -x['altitude']))
        
        st.metric("🌟 Visible Objects", len(objects))
        
        cols = st.columns(3)
        for idx, obj_data in enumerate(sorted_objects):
            with cols[idx % 3]:
                self.create_object_tile(obj_data)
    
    def render_sky_chart_section(self, visible_objects, dt):
        st.header("🌟 Interactive Sky Chart")
        
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

            st.markdown("---")
            st.subheader("🛰️ Online Sky Atlas")
            st.markdown("*Explore the night sky with the interactive Aladin Lite viewer below*")

            import streamlit.components.v1 as components
            components.html(
                '<iframe src="https://aladin.u-strasbg.fr/AladinLite/" width="100%" height="600" style="border:none;"></iframe>',
                height=600
            )
        else:
            st.info("ℹ️ No objects visible to display on sky chart.")
    
    def run(self):
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
        
        self.render_location_section()
        dt = self.render_datetime_section()
        
        if st.session_state.address in ["Not set", "Automatic Detection Failed"]:
            st.warning("📍 Please set your location to see visible astronomical objects.")
            st.stop()
        
        st.header("🌌 Visible Astronomical Objects")
        st.markdown("*Objects visible from your location at the selected time*")
        
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
                
                enhanced_objects = self.enhance_visible_objects(visible_objects)
                
                self.create_object_tiles(enhanced_objects)
                
            except Exception as e:
                st.error(f"❌ Error fetching astronomical data: {str(e)}")
                st.info("Please check your internet connection and try again.")
                st.stop()
        
        self.render_sky_chart_section(visible_objects, dt)
        
        st.markdown("---")
        st.markdown(
            """
            <div style='text-align: center; color: #888; font-size: 0.9rem;'>
                🔭 <strong>Merai - A Space Detective</strong> | 
                Built with ❤️ using Streamlit and Skyfield | 
                Data from NASA JPL, Hipparcos, and Wikipedia<br>
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
