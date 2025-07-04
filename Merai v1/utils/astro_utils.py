"""
Astronomical utility functions for the Space Detective application.

This module provides functions to calculate and retrieve visible astronomical 
objects, including planets and bright stars, from a given location and time.
"""

import os
from skyfield.api import load, Topos, Star
from skyfield.data import hipparcos
from .wiki_utils import (
    get_object_description, get_object_image_url, extract_name_from_description
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
                lookup_key = obj.get('name') or obj.get('hip_id')
                description = get_object_description(lookup_key)

                if not obj.get('name') and description:
                    name_from_desc = extract_name_from_description(description)
                    if name_from_desc:
                        obj['name'] = name_from_desc
                
                image_url = get_object_image_url(obj.get('name') or lookup_key)
            else:
                description = get_object_description(obj['name'])
                image_url = get_object_image_url(obj['name'])

            obj['fetched_description'] = description
            obj['image_url'] = image_url

            # If description is still empty, provide a default message
            if not obj.get('fetched_description'):
                obj['fetched_description'] = "No description available for this object."

            # Add constellation information for stars
            if obj['type'] == 'Star':
                hip_int = obj.get('hip_int')
                obj['constellation'] = constellation_map.get(hip_int, "Unknown") if hip_int and constellation_map else "Unknown"
            else:
                obj['constellation'] = "N/A"

            enhanced_objects.append(obj)
        except Exception as e:
            # Log the error and continue with the next object
            # In a real application, you would use a proper logger
            print(f"Error enhancing object {obj.get('name', obj.get('hip_id'))}: {e}")
            # Optionally, you could append the object without enhancement
            # obj['fetched_description'] = "Error fetching details."
            # obj['constellation'] = "Unknown"
            # enhanced_objects.append(obj)
            continue
    
    return enhanced_objects
