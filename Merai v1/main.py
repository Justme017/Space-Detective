"""
Merai - A Space Detective v2.0.0

Author: Merai Development Team 
License: MIT
Version: 2.0.0 - Live App Release
"""

import streamlit as st
from datetime import date, datetime

# Import custom modules
from astro_utils import get_visible_objects, enhance_visible_objects
from constellation_utils import load_constellation_data
from skychart_utils import create_sky_chart
from app_utils import (
    apply_custom_styling,
    render_location_section,
    render_datetime_section,
    create_object_tiles,
    render_sky_chart_section,
)

# Configuration constants
MAX_DESC_LEN = 120
ZOOM_LEVELS = [0.7, 1.0, 1.3, 1.6, 2.0]

# Load constellation data once
CONSTELLATION_MAP = load_constellation_data()


class MeraiApp:
    """Main application class for the Merai Space Detective."""
    
    def __init__(self):
        """Initialize the application with page settings and styling."""
        self.setup_page_config()
        apply_custom_styling()
        self.initialize_session_state()
    
    def setup_page_config(self):
        """Configure basic Streamlit page settings."""
        st.set_page_config(
            page_title="Merai - A Space Detective",
            page_icon="🔭",
            layout="wide",
            initial_sidebar_state="collapsed"
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
            'sky_zoom': 1.0,
            'location_detected': False
        }
        
        for key, default_value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = default_value

    def run(self):
        """Run the main application flow."""
        # Render location section and check if location is set
        render_location_section()

        if st.session_state.location_detected:
            st.markdown("---")
            
            # Render datetime section and get combined datetime
            dt = render_datetime_section()
            
            st.markdown("---")
            
            # Get visible objects
            visible_objects = get_visible_objects(
                st.session_state.latitude,
                st.session_state.longitude,
                dt
            )
            
            # Enhance objects with more data
            enhanced_objects = enhance_visible_objects(visible_objects, CONSTELLATION_MAP)
            
            # Display objects in tiles
            create_object_tiles(enhanced_objects)
            
            st.markdown("---")
            
            # Render the sky chart
            render_sky_chart_section(enhanced_objects, dt, create_sky_chart)

if __name__ == "__main__":
    app = MeraiApp()
    app.run()
