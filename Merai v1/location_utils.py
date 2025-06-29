"""
Location utility functions for the Merai Space Detective application.

This module provides functions to detect user location and handle datetime operations.
"""

import geocoder
from skyfield.api import utc
from datetime import datetime

def get_user_location():
    """
    Detect user's location using IP-based geolocation.
    
    Returns:
        tuple: (latitude, longitude, address) if successful, (None, None, None) if failed
    """
    g = geocoder.ip('me')
    if g.ok:
        lat, lon = g.latlng
        address = g.city + ", " + g.country if g.city and g.country else "Unknown location"
        return lat, lon, address
    else:
        return None, None, None

def get_user_datetime():
    """
    Get current datetime with UTC timezone.
    
    Returns:
        datetime: Current datetime with UTC timezone
    """
    return datetime.now().replace(tzinfo=utc)
