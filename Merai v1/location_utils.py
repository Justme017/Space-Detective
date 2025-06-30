"""
Location utility functions for the Merai Space Detective application.

Simple, reliable location detection using IP-based geolocation (ipapi.co).
"""

import requests

def get_user_location():
    """
    Detect user's location using ipapi.co (IP-based geolocation).
    Returns:
        tuple: (latitude, longitude, address) or (None, None, None) if not available
    """
    try:
        response = requests.get('https://ipapi.co/json/', timeout=8)
        if response.status_code == 200:
            data = response.json()
            if 'latitude' in data and 'longitude' in data:
                lat = float(data['latitude'])
                lon = float(data['longitude'])
                city = data.get('city', '')
                region = data.get('region', '')
                country = data.get('country_name', '')
                address_parts = [part for part in [city, region, country] if part]
                address = ', '.join(address_parts) if address_parts else "IP-based Location"
                return lat, lon, address
    except Exception:
        pass
    return None, None, None


