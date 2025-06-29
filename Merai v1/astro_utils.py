"""
Astronomical utility functions for the Merai Space Detective application.

This module provides functions to calculate and retrieve visible astronomical objects
including planets and bright stars from a given location and time using Skyfield.
"""

import os
from skyfield.api import load, Topos, Star
from skyfield.data import hipparcos

# Get the directory where astro_utils.py is located
_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Construct absolute paths to the data files
DE421_PATH = os.path.join(_CURRENT_DIR, "de421.bsp")
HIPP_PATH = os.path.join(_CURRENT_DIR, "hip_main.dat")

def get_visible_objects(lat, lon, user_dt=None):
    """
    Get all visible astronomical objects from a given location and time.
    
    Args:
        lat (float): Latitude in degrees
        lon (float): Longitude in degrees
        user_dt (datetime, optional): Specific datetime, defaults to current time
        
    Returns:
        list: List of visible astronomical objects with their properties
    """
    ts = load.timescale()
    t = ts.from_datetime(user_dt) if user_dt else ts.now()
    planets = load(DE421_PATH)
    earth = planets['earth']
    observer = earth + Topos(latitude_degrees=lat, longitude_degrees=lon)
    visible = []

    # List of celestial objects to check for visibility
    celestial_objects = [
        ('sun', 'Sun'),
        ('moon', 'Moon'),
        ('mercury', 'Planet'),
        ('venus', 'Planet'),
        ('mars', 'Planet'),
        ('jupiter', 'Planet'),
        ('saturn', 'Planet'),
        ('uranus', 'Planet'),
        ('neptune', 'Planet'),
        ('pluto', 'Planet')
    ]

    # Check each celestial object for visibility
    for obj_name, obj_type in celestial_objects:
        try:
            body = planets[obj_name]
            alt, az, _ = observer.at(t).observe(body).apparent().altaz()
            if alt.degrees > 0:
                pretty_name = obj_name.capitalize()
                visible.append({
                    'name': pretty_name,
                    'type': obj_type,
                    'altitude': round(alt.degrees, 2),
                    'azimuth': round(az.degrees, 2)
                })
        except Exception:
            # Skip objects that can't be processed
            continue

    # For bright stars from Hipparcos catalog
    try:
        with open(HIPP_PATH, 'rb') as f:
            stars = hipparcos.load_dataframe(f)
        bright_stars = stars[stars['magnitude'] < 2.0]
        
        for hip, star_row in bright_stars.iterrows():
            try:
                star = Star(ra_hours=star_row['ra_hours'], dec_degrees=star_row['dec_degrees'])
                alt, az, _ = observer.at(t).observe(star).apparent().altaz()
                if alt.degrees > 0:
                    proper_name = star_row.get('proper')
                    
                    # Fix the hip conversion issue with better error handling
                    hip_id_int = 0
                    try:
                        if isinstance(hip, (int, float)):
                            hip_id_int = int(hip)
                        elif isinstance(hip, str):
                            hip_id_int = int(float(hip))
                        else:
                            hip_id_int = int(str(hip))
                    except (ValueError, TypeError):
                        hip_id_int = 0  # Fallback value
                    
                    hip_id_str = f"HIP {hip_id_int}"
                    
                    # Determine the primary display name
                    if proper_name and str(proper_name).strip() and str(proper_name).strip().lower() != 'nan':
                        display_name_h1 = str(proper_name).strip()
                    else:
                        display_name_h1 = hip_id_str
                    
                    visible.append({
                        'name': display_name_h1,  # Primary name for H1 (Common name or HIP ID)
                        'hip_id': hip_id_str,     # Always the HIP ID, for H2
                        'hip_int': hip_id_int,    # Add integer HIP ID for constellation lookup
                        'type': 'Star',
                        'altitude': round(alt.degrees, 2),
                        'azimuth': round(az.degrees, 2)
                    })
            except Exception:
                # Skip stars that can't be processed
                continue
                
    except Exception:
        # Handle stars processing errors gracefully
        pass
    
    return visible
