"""
Location utility functions for the Merai Space Detective application.

Simple, reliable location detection using only the most accurate method.
"""

def get_user_location():
from streamlit_js_eval import streamlit_js_eval

def get_user_location():
    """
    Detect user's location using browser geolocation (preferred) or fallback.
    Returns:
        tuple: (latitude, longitude, address)
    """
    # Try browser geolocation first
    location = streamlit_js_eval(
        js_expressions="navigator.geolocation.getCurrentPosition((pos)=>{return [pos.coords.latitude,pos.coords.longitude]})",
        key="get_user_location"
    )
    if location and isinstance(location, list) and len(location) == 2:
        lat, lon = location
        return lat, lon, "Browser Geolocation"
    # Fallback: Default location (New York City)
    return 40.7128, -74.0060, "New York, NY (Default)"

def get_user_datetime():
    """
    Get current datetime with UTC timezone.
    
    Returns:
        datetime: Current datetime with UTC timezone
    """
    return datetime.now().replace(tzinfo=utc)
