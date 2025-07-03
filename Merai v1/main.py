"""
Merai - A Space Detective v2.1.0

Author: Merai Development Team
License: MIT
Version: 2.1.0 - Refactored Release
"""

import streamlit as st

from astro_utils import get_visible_objects, enhance_visible_objects
from constellation_utils import load_constellation_data
from satellites_utils import get_visible_satellites
from skychart_utils import create_sky_chart
from app_utils import (
    apply_custom_styling,
    render_location_section,
    render_datetime_section,
    create_object_tiles,
    render_sky_chart_section,
)

# --- Page Setup and Initialization ---
st.set_page_config(
    page_title="Merai - A Space Detective",
    page_icon="🔭",
    layout="wide",
    initial_sidebar_state="collapsed"
)

apply_custom_styling()

# Initialize session state variables if they don't exist
defaults = {
    'latitude': 0.0, 'longitude': 0.0, 'address': "Not set",
    'sky_zoom': 1.0, 'location_detected': False
}
for key, value in defaults.items():
    st.session_state.setdefault(key, value)

# --- Application Header ---
st.markdown("<h1 style='text-align: center;'>🔭 Merai - A Space Detective</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-style: italic;'>Explore the cosmos from your location</p>", unsafe_allow_html=True)
st.markdown("---")

# --- Core Application Sections ---
render_location_section()
dt = render_datetime_section()

# Stop if location is not set
if not st.session_state.get('location_detected', False):
    st.warning("📍 Please set your location to discover the sky.")
    st.stop()

# --- Data Fetching and Processing ---
st.header("🌌 Visible Astronomical Objects & Satellites")
with st.spinner("Scanning the cosmos..."):
    try:
        # Fetch planets and stars
        constellation_map = load_constellation_data()
        visible_astro_objects = get_visible_objects(
            st.session_state.latitude,
            st.session_state.longitude,
            dt
        )
        
        enhanced_objects = enhance_visible_objects(visible_astro_objects, constellation_map) if visible_astro_objects else []

        # Fetch satellites
        visible_satellites = get_visible_satellites(
            st.session_state.latitude,
            st.session_state.longitude,
            dt
        )
        
        # Combine all objects
        all_visible_objects = enhanced_objects + visible_satellites

    except Exception as e:
        st.error(f"Failed to fetch astronomical data: {e}")
        st.stop()

# --- Display Results ---
create_object_tiles(all_visible_objects)
render_sky_chart_section(all_visible_objects, dt, create_sky_chart)

# --- Footer ---
st.markdown("---")
st.markdown("<div style='text-align: center; color: #888;'>Built with ❤️ using Aladin, Streamlit & Skyfield</div>", unsafe_allow_html=True)
