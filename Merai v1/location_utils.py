"""
Location utility functions for the Merai Space Detective application.

Simple, reliable location detection using only the most accurate method.
"""

import requests
from skyfield.api import utc
from datetime import datetime

def get_user_location():
    """
    Detect user's location using the most reliable method.
    
    Returns:
        tuple: (latitude, longitude, address)
    """
    # Try the most reliable IP-based location service
    try:
        response = requests.get('https://ipapi.co/json/', timeout=8)
        if response.status_code == 200:
            data = response.json()
            if 'latitude' in data and 'longitude' in data:
                lat = float(data['latitude'])
                lon = float(data['longitude'])
                
                # Validate coordinates
                if -90 <= lat <= 90 and -180 <= lon <= 180:
                    # Build address string
                    city = data.get('city', '')
                    region = data.get('region', '')
                    country = data.get('country_name', '')
                    
                    address_parts = []
                    if city:
                        address_parts.append(city)
                    if region and region != city:
                        address_parts.append(region)
                    if country:
                        address_parts.append(country)
                    
                    address = ', '.join(address_parts) if address_parts else "Detected Location"
                    return lat, lon, address
    except:
        pass
    
    # Default fallback location (New York City)
    return 40.7128, -74.0060, "New York, NY (Default)"

def get_user_datetime():
    """
    Get current datetime with UTC timezone.
    
    Returns:
        datetime: Current datetime with UTC timezone
    """
    return datetime.now().replace(tzinfo=utc)
