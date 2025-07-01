"""
Astronomical utility functions for the Merai Space Detective application.

This module provides functions to calculate and retrieve visible astronomical objects
including planets and bright stars from a given location and time using Skyfield.
"""

import os
from skyfield.api import load, Topos, Star
from skyfield.data import hipparcos
from wiki_utils import get_object_description, extract_name_from_description

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

def enhance_visible_objects(visible_objects, constellation_map):
    """
    Enhance astronomical objects with additional information from Wikipedia.
    
    This function takes the basic astronomical data and adds:
    - Detailed descriptions from Wikipedia
    - Constellation information for stars
    - Better names extracted from descriptions
    
    Args:
        visible_objects (list): List of basic astronomical objects
        constellation_map (dict): Mapping of HIP IDs to constellation names
        
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
            if hip_int_for_lookup and constellation_map:
                obj['constellation'] = constellation_map.get(hip_int_for_lookup, "Unknown")
            else:
                obj['constellation'] = "Unknown"
        else:
            obj['constellation'] = "N/A"

        enhanced_objects.append(obj)
    
    return enhanced_objects
