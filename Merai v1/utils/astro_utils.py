"""
Astronomical utility functions for the Space Detective application.

This module provides functions to calculate and retrieve visible astronomical 
objects, including planets and bright stars, from a given location and time.
"""

import os
from skyfield.api import load, Topos, Star
from skyfield.data import hipparcos
from .wiki_utils import (
    get_object_description, get_object_image_url
)

# --- Constants ---
_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_DATA_DIR = os.path.join(os.path.dirname(_CURRENT_DIR), 'data')
DE421_PATH = os.path.join(_DATA_DIR, "de421.bsp")
HIPP_PATH = os.path.join(_DATA_DIR, "hip_main.dat")

# --- Private Helper Functions ---

def _get_visible_planets(observer, t, planets):
    """
    Calculates the visible planets from the observer's location and time.
    """
    visible_planets = []
    celestial_objects = [
        ('sun', 'Sun'), ('moon', 'Moon'), ('mercury', 'Planet'), ('venus', 'Planet'),
        ('mars', 'Planet'), ('jupiter', 'Planet'), ('saturn', 'Planet'),
        ('uranus', 'Planet'), ('neptune', 'Planet'), ('pluto', 'Planet')
    ]

    for obj_name, obj_type in celestial_objects:
        try:
            body = planets[obj_name]
            alt, az, _ = observer.at(t).observe(body).apparent().altaz()
            if alt.degrees > 0:
                visible_planets.append({
                    'name': obj_name.capitalize(),
                    'type': obj_type,
                    'altitude': round(alt.degrees, 2),
                    'azimuth': round(az.degrees, 2)
                })
        except Exception:
            # Skip objects that can't be processed
            continue
            
    return visible_planets

def _get_visible_stars(observer, t):
    """
    Calculates the visible bright stars from the observer's location and time.
    """
    visible_stars = []
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
                    
                    # The 'hip' value from iterrows() is the index, which is the HIP ID.
                    # It should be an integer, but we validate it to be safe.
                    try:
                        # Convert to string first to handle potential type issues
                        hip_id_int = int(str(hip))
                    except (ValueError, TypeError):
                        continue  # Skip if hip is not a valid integer
                    
                    display_name = str(proper_name).strip() if proper_name and str(proper_name).strip().lower() != 'nan' else None
                    
                    visible_stars.append({
                        'name': display_name,
                        'hip_id': f"HIP {hip_id_int}",
                        'hip_int': hip_id_int,
                        'type': 'Star',
                        'altitude': round(alt.degrees, 2),
                        'azimuth': round(az.degrees, 2)
                    })
            except Exception:
                # Skip stars that can't be processed
                continue
                
    except Exception:
        # Handle cases where star data cannot be loaded or processed
        pass
        
    return visible_stars

# --- Public API ---

def get_visible_objects(lat, lon, user_dt=None):
    """
    Get all visible astronomical objects from a given location and time.
    
    Args:
        lat (float): Latitude in degrees.
        lon (float): Longitude in degrees.
        user_dt (datetime, optional): Specific datetime. Defaults to current time.
        
    Returns:
        list: A list of visible astronomical objects with their properties.
    """
    ts = load.timescale()
    t = ts.from_datetime(user_dt) if user_dt else ts.now()
    
    try:
        planets = load(DE421_PATH)
    except Exception:
        # If planetary data can't be loaded, return an empty list
        return []
        
    observer = planets['earth'] + Topos(latitude_degrees=lat, longitude_degrees=lon)
    
    visible_planets = _get_visible_planets(observer, t, planets)
    visible_stars = _get_visible_stars(observer, t)
    
    return visible_planets + visible_stars

def enhance_visible_objects(visible_objects, constellation_map):
    """
    Enhance astronomical objects with Wikipedia descriptions and constellation info.
    
    Args:
        visible_objects (list): A list of astronomical objects.
        constellation_map (dict): A mapping of HIP IDs to constellation names.
        
    Returns:
        list: A list of enhanced objects with additional information.
    """
    enhanced_objects = []
    
    for obj in visible_objects:
        try:
            image_url = None
            description = None

            if obj['type'] == 'Star':
                # For stars, we prefer using the proper name if available, otherwise the HIP ID.
                lookup_key = obj.get('name') or obj.get('hip_id')
                description = get_object_description(lookup_key)
                image_url = get_object_image_url(lookup_key)
                
                hip_id = obj.get('hip_int')
                if hip_id and hip_id in constellation_map:
                    obj['constellation'] = constellation_map[hip_id]
                else:
                    obj['constellation'] = 'N/A'

            else:  # Planet, Sun, Moon
                description = get_object_description(obj['name'])
                image_url = get_object_image_url(obj['name'])

            obj['description'] = description or "Description not available."
            obj['image_url'] = image_url
            
            enhanced_objects.append(obj)
            
        except Exception:
            # If enhancement fails, ensure basic info is still present.
            obj['description'] = obj.get('description', 'Description not available.')
            obj['image_url'] = obj.get('image_url', None)
            enhanced_objects.append(obj)
            continue
            
    return enhanced_objects
