"""
Satellite utility functions for the Space Detective application.

This module provides functions to calculate and retrieve visible satellites,
including the International Space Station (ISS) and other bright objects,
from a given location and time.
"""

from skyfield.api import load, Topos
import os
import streamlit as st

# --- Constants ---
_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DE421_PATH = os.path.join(_CURRENT_DIR, "de421.bsp")

# URLs for TLE data from CelesTrak
STATIONS_URL = "https://celestrak.org/NORAD/elements/gp.php?GROUP=stations&FORMAT=tle"
BRIGHTEST_URL = "https://celestrak.org/NORAD/elements/gp.php?GROUP=visual&FORMAT=tle"

# --- Pre-load data to speed up subsequent calls ---
@st.cache_data(show_spinner=False)
def _preload_data():
    """
    Loads and caches planetary and satellite data.
    Using st.cache_data ensures this runs only once.
    """
    print("Pre-loading planetary and satellite data...")
    try:
        planets = load(DE421_PATH)
        stations = load.tle_file(STATIONS_URL, reload=False)
        brightest_sats = load.tle_file(BRIGHTEST_URL, reload=False)
        
        # Combine and remove duplicates
        all_sats = {sat.model.satnum: sat for sat in stations + brightest_sats}
        satellites = list(all_sats.values())
        
        print("Data pre-loading complete.")
        return planets, satellites
    except Exception as e:
        print(f"Fatal error during data pre-loading: {e}")
        # Return empty objects on failure
        return None, []

PLANETS, SATELLITES = _preload_data()
EARTH = PLANETS['earth'] if PLANETS else None

# --- Public API ---

def get_visible_satellites(lat, lon, user_dt):
    """
    Get all visible satellites from a given location and time.

    Args:
        lat (float): Latitude in degrees.
        lon (float): Longitude in degrees.
        user_dt (datetime): Specific datetime object (UTC).

    Returns:
        list: A list of visible satellites with their properties.
    """
    if not SATELLITES or not EARTH:
        st.error("Satellite or planetary data could not be loaded. Satellite tracking is unavailable.")
        return []

    ts = load.timescale()
    t = ts.from_datetime(user_dt)

    observer = EARTH + Topos(latitude_degrees=lat, longitude_degrees=lon)

    visible_sats = []

    for sat in SATELLITES:
        try:
            difference = sat - observer
            topocentric = difference.at(t)
            alt, az, _ = topocentric.altaz()

            # Check if the satellite is above the horizon
            if alt.degrees > 10:  # Use a 10-degree minimum altitude for better visibility
                # Check if the satellite is illuminated by the sun
                if sat.at(t).is_sunlit(EARTH):
                    visible_sats.append({
                        'name': str(sat.name).strip(),
                        'type': 'Satellite' if 'ISS' not in str(sat.name).upper() else 'Space Station',
                        'altitude': round(alt.degrees, 2),
                        'azimuth': round(az.degrees, 2),
                        'norad_id': sat.model.satnum
                    })
        except Exception:
            # Some satellites may have expired TLEs or other issues
            continue
            
    # Sort by highest altitude
    visible_sats.sort(key=lambda x: x['altitude'], reverse=True)

    return visible_sats
