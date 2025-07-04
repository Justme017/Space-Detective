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
_DATA_DIR = os.path.join(os.path.dirname(_CURRENT_DIR), 'data')
DE421_PATH = os.path.join(_DATA_DIR, "de421.bsp")

# Local TLE files
STATIONS_FILE = os.path.join(_DATA_DIR, "stations.tle")
BRIGHTEST_FILE = os.path.join(_DATA_DIR, "brightest.tle")

# --- Pre-load data to speed up subsequent calls ---
def _preload_data():
    """
    Loads planetary and satellite data from local files.
    This runs once when the module is imported.
    """
    print("Loading planetary and satellite data from local files...")
    try:
        planets = load(DE421_PATH)
        
        if not os.path.exists(STATIONS_FILE) or not os.path.exists(BRIGHTEST_FILE):
            st.error("Satellite data files (stations.tle, brightest.tle) not found. Please run the `download_tle_data.py` script first.")
            return None, []

        stations = load.tle_file(STATIONS_FILE)
        brightest_sats = load.tle_file(BRIGHTEST_FILE)
        
        # Combine and remove duplicates
        all_sats = {sat.model.satnum: sat for sat in stations + brightest_sats}
        satellites = list(all_sats.values())
        
        print("Data loading complete.")
        return planets, satellites
    except Exception as e:
        print(f"Fatal error during data loading: {e}")
        st.error(f"An error occurred while loading satellite data: {e}")
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
