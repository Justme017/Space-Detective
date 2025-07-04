"""
Astronomical utility functions for the Space Detective application.

This module provides functions to calculate and retrieve visible astronomical 
objects, including planets and bright stars, from a given location and time.
"""

import os
import pandas as pd
from skyfield.api import load, Topos, Star
from .wiki_utils import (
    get_object_description, get_object_image_url
)

# --- Constants ---
_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_DATA_DIR = os.path.join(os.path.dirname(_CURRENT_DIR), 'data')
DE421_PATH = os.path.join(_DATA_DIR, "de421.bsp")
HYG_CATALOG_PATH = os.path.join(_DATA_DIR, "hygdata_v41.csv")
HIP_NAMES_PATH = os.path.join(_DATA_DIR, "hip_common_names.csv")

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
    Calculates the visible bright stars from the observer's location and time,
    incorporating common names.
    """
    visible_stars = []
    try:
        # Step 1 & 2: Load the star catalog and the common names file.
        stars_df = pd.read_csv(HYG_CATALOG_PATH)
        hip_names_df = pd.read_csv(HIP_NAMES_PATH)

        # Step 3: Merge the two dataframes to get common names alongside star data.
        # We ensure the 'hip' columns are of the same type to merge correctly.
        stars_df['hip'] = pd.to_numeric(stars_df['hip'], errors='coerce').astype('Int64')
        hip_names_df['hip_id'] = pd.to_numeric(hip_names_df['hip_id'], errors='coerce').astype('Int64')
        stars_df = pd.merge(stars_df, hip_names_df, left_on='hip', right_on='hip_id', how='left')

        # Step 4: Filter for bright stars and valid HIP numbers.
        bright_stars = stars_df[(stars_df['mag'] < 4.5) & (stars_df['hip'].notna())].copy()
        bright_stars['hip'] = bright_stars['hip'].astype(int)

        for _, star_row in bright_stars.iterrows():
            try:
                # Create a Skyfield Star object to calculate its position.
                star = Star(ra_hours=star_row['ra'], dec_degrees=star_row['dec'])
                alt, az, _ = observer.at(t).observe(star).apparent().altaz()

                # Check if the star is above the horizon.
                if alt.degrees > 0:
                    hip_id = star_row['hip']
                    common_name = star_row.get('common_name')
                    
                    # Step 5: Format the display name.
                    display_name = f"{common_name} (HIP {hip_id})" if pd.notna(common_name) else f"HIP {hip_id}"

                    visible_stars.append({
                        'name': display_name,
                        'common_name': common_name if pd.notna(common_name) else None,
                        'hip_id': f"HIP {hip_id}",
                        'hip_int': hip_id,
                        'type': 'Star',
                        'altitude': round(alt.degrees, 2),
                        'azimuth': round(az.degrees, 2)
                    })
            except Exception:
                # Skip any single star that causes an error.
                continue
                
    except Exception as e:
        # If the whole process fails, log the error.
        print(f"Error loading or processing star data: {e}")
        
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
    """
    enhanced_objects = []
    
    for obj in visible_objects:
        try:
            image_url = None
            description = None

            if obj['type'] == 'Star':
                # For stars, we prefer using the common name for lookups if available.
                lookup_key = obj.get('common_name') or obj.get('hip_id')
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
