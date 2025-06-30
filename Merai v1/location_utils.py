"""
Location utility functions for the Merai Space Detective application.

Simple, reliable location detection using browser geolocation (preferred).
"""

from streamlit_js_eval import streamlit_js_eval

def get_user_location():
    """
    Detect user's location using browser geolocation (preferred).
    Returns:
        tuple: (latitude, longitude, address)
    """
    location = streamlit_js_eval(
        js_expressions="navigator.geolocation.getCurrentPosition((pos)=>{return [pos.coords.latitude,pos.coords.longitude]})",
        key="get_user_location"
    )
    if location is None:
        return None, None, None
    if isinstance(location, list) and len(location) == 2:
        lat, lon = location
        return lat, lon, "Browser Geolocation"
    # Fallback: Default location (should only be used by main app if user denies or unavailable after waiting)
    return None, None, None


