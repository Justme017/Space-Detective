"""
Location utility functions for the Merai Space Detective application.

This module provides functions to detect user location and handle datetime operations.
"""

import geocoder
import requests
from skyfield.api import utc
from datetime import datetime
import streamlit as st

def get_user_location():
    """
    Detect user's location using multiple methods with fallbacks.
    
    Returns:
        tuple: (latitude, longitude, address) if successful, (None, None, None) if failed
    """
    
    # Try multiple location detection methods in order of reliability
    methods = [
        _get_location_ip_geolocation,
        _get_location_ipapi,
        _get_location_ipinfo,
        _get_location_geocoder_ip,
        _get_location_geocoder_here,
        _get_location_default
    ]
    
    for method in methods:
        try:
            lat, lon, address = method()
            if lat is not None and lon is not None:
                # Validate coordinates are reasonable
                if -90 <= lat <= 90 and -180 <= lon <= 180:
                    return lat, lon, address
        except Exception as e:
            # Log error but continue to next method
            continue
    
    return None, None, None

def _get_location_ip_geolocation():
    """Try ip-geolocation.io service for more accurate location detection."""
    try:
        response = requests.get('https://api.ip-geolocation.io/ipgeo', timeout=5)
        if response.status_code == 200:
            data = response.json()
            if 'latitude' in data and 'longitude' in data:
                lat = float(data['latitude'])
                lon = float(data['longitude'])
                city = data.get('city', '')
                state = data.get('state_prov', '')
                country = data.get('country_name', '')
                
                # Create detailed address
                address_parts = [part for part in [city, state, country] if part]
                address = ', '.join(address_parts) if address_parts else "IP Geolocation"
                return lat, lon, address
    except:
        pass
    return None, None, None

def _get_location_ipapi():
    """Try ipapi.co service for location detection."""
    try:
        response = requests.get('https://ipapi.co/json/', timeout=5)
        if response.status_code == 200:
            data = response.json()
            if 'latitude' in data and 'longitude' in data:
                lat = float(data['latitude'])
                lon = float(data['longitude'])
                city = data.get('city', '')
                country = data.get('country_name', '')
                address = f"{city}, {country}" if city and country else "Detected location"
                return lat, lon, address
    except:
        pass
    return None, None, None

def _get_location_ipinfo():
    """Try ipinfo.io service for location detection."""
    try:
        response = requests.get('https://ipinfo.io/json', timeout=5)
        if response.status_code == 200:
            data = response.json()
            if 'loc' in data:
                # ipinfo.io returns location as "lat,lon" string
                lat_str, lon_str = data['loc'].split(',')
                lat = float(lat_str.strip())
                lon = float(lon_str.strip())
                
                city = data.get('city', '')
                region = data.get('region', '')
                country = data.get('country', '')
                
                # Create address from available data
                address_parts = [part for part in [city, region, country] if part]
                address = ', '.join(address_parts) if address_parts else "IPInfo location"
                return lat, lon, address
    except:
        pass
    return None, None, None

def _get_location_geocoder_ip():
    """Try geocoder with IP method."""
    try:
        g = geocoder.ip('me')
        if g.ok and g.latlng:
            lat, lon = g.latlng
            address = f"{g.city}, {g.country}" if g.city and g.country else "IP-based location"
            return lat, lon, address
    except:
        pass
    return None, None, None

def _get_location_geocoder_here():
    """Try geocoder with HERE service."""
    try:
        g = geocoder.here('me')
        if g.ok and g.latlng:
            lat, lon = g.latlng
            address = g.address if g.address else "HERE-based location"
            return lat, lon, address
    except:
        pass
    return None, None, None

def _get_location_default():
    """Provide a default location as last resort."""
    # Use a major city as default (New York City)
    return 40.7128, -74.0060, "New York, NY (Default)"

def get_user_datetime():
    """
    Get current datetime with UTC timezone.
    
    Returns:
        datetime: Current datetime with UTC timezone
    """
    return datetime.now().replace(tzinfo=utc)
