"""
Location utility functions for the Merai Space Detective application.

This module provides functions to detect user location and handle datetime operations.
"""

import requests
from skyfield.api import utc
from datetime import datetime

def get_user_location():
    """
    Detect user's location using IP-based geolocation service (ipapi.co).
    
    This function makes an HTTP request to a free geolocation API service
    that returns location information based on your IP address.
    
    How it works:
    1. Makes a request to ipapi.co/json/ (a free IP geolocation service)
    2. Parses the JSON response to extract latitude, longitude, and address
    3. Combines city, region, and country into a readable address string
    4. Returns the location data or None if the service is unavailable
    
    Returns:
        tuple: (latitude, longitude, address) if successful
               (None, None, None) if location detection fails
        
    Example:
        lat, lon, addr = get_user_location()
        if lat is not None:
            print(f"You are at {lat}, {lon} - {addr}")
        else:
            print("Could not detect location")
    """
    try:
        # Make HTTP request to geolocation service with 8 second timeout
        response = requests.get('https://ipapi.co/json/', timeout=8)
        
        # Check if the request was successful (status code 200 = OK)
        if response.status_code == 200:
            # Parse the JSON response
            data = response.json()
            
            # Extract location data if available
            if 'latitude' in data and 'longitude' in data:
                lat = float(data['latitude'])
                lon = float(data['longitude'])
                
                # Build a readable address from available components
                city = data.get('city', '')
                region = data.get('region', '')
                country = data.get('country_name', '')
                
                # Combine non-empty address parts
                address_parts = [part for part in [city, region, country] if part]
                address = ', '.join(address_parts) if address_parts else "IP-based Location"
                
                return lat, lon, address
                
    except Exception:
        # If anything goes wrong (network error, invalid response, etc.),
        # silently return None values instead of crashing the app
        pass
    
    # Return None values if location detection failed
    return None, None, None

def get_user_datetime():
    """
    Get current datetime with UTC timezone.
    
    Returns:
        datetime: Current datetime with UTC timezone
    """
    return datetime.now().replace(tzinfo=utc)
