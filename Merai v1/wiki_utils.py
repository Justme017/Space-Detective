"""
Wikipedia utility functions for the Merai Space Detective application.

This module provides functions to fetch object descriptions and images from Wikipedia
to enhance the display of astronomical objects with additional information.
"""

import requests
import html
import re
from bs4 import BeautifulSoup

def get_object_image_url(name):
    """
    Fetch object image URL from Wikipedia API with improved handling.
    
    Args:
        name (str): Name of the astronomical object
        
    Returns:
        str or None: Image URL if available, None otherwise
    """
    # Define fallback image URLs for common astronomical objects
    fallback_images = {
        'Moon': 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/e1/FullMoon2010.jpg/256px-FullMoon2010.jpg',
        'Sun': 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/b4/The_Sun_by_the_Atmospheric_Imaging_Assembly_of_NASA%27s_Solar_Dynamics_Observatory_-_20100819.jpg/256px-The_Sun_by_the_Atmospheric_Imaging_Assembly_of_NASA%27s_Solar_Dynamics_Observatory_-_20100819.jpg',
        'Mercury': 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/4a/Mercury_in_true_color.jpg/256px-Mercury_in_true_color.jpg',
        'Venus': 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/08/Venus_from_Mariner_10.jpg/256px-Venus_from_Mariner_10.jpg',
        'Mars': 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/02/OSIRIS_Mars_true_color.jpg/256px-OSIRIS_Mars_true_color.jpg',
        'Jupiter': 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/2b/Jupiter_and_its_shrunken_Great_Red_Spot.jpg/256px-Jupiter_and_its_shrunken_Great_Red_Spot.jpg',
        'Saturn': 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c1/Saturn_from_Cassini_Orbiter_%282004-10-06%29.jpg/256px-Saturn_from_Cassini_Orbiter_%282004-10-06%29.jpg',
        'Uranus': 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/48/Uranus_as_seen_by_NASA%27s_Voyager_2_%28remastered%29.png/256px-Uranus_as_seen_by_NASA%27s_Voyager_2_%28remastered%29.png',
        'Neptune': 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/63/Neptune_-_Voyager_2_%2829347980845%29_flatten_crop.jpg/256px-Neptune_-_Voyager_2_%2829347980845%29_flatten_crop.jpg',
        'Pluto': 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/ef/Pluto_in_True_Color_-_High-Res.jpg/256px-Pluto_in_True_Color_-_High-Res.jpg'
    }
    
    # First, try to get image from Wikipedia API
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{name}"
    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            if 'thumbnail' in data and 'source' in data['thumbnail']:
                # Get higher resolution image if available
                img_url = data['thumbnail']['source']
                # Try to get a larger version by modifying the URL
                if '/thumb/' in img_url and img_url.endswith('px-'):
                    # Replace with higher resolution
                    img_url = img_url.replace('/thumb/', '/').split('/')
                    if len(img_url) > 1:
                        # Remove the size specification to get original size
                        original_filename = img_url[-1].split('-')[-1]
                        img_url[-2] = original_filename
                        img_url = '/'.join(img_url[:-1])
                        return img_url
                return data['thumbnail']['source']
    except Exception:
        pass
    
    # If Wikipedia API fails, try fallback images
    if name in fallback_images:
        return fallback_images[name]
    
    # For stars, try to get a generic star image
    if name.startswith('HIP ') or 'star' in name.lower():
        return 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c4/Sirius_A_and_B_Hubble_photo.jpg/256px-Sirius_A_and_B_Hubble_photo.jpg'
    
    return None

def get_object_description(name):
    """
    Fetch object description from Wikipedia API.
    
    Args:
        name (str): Name of the astronomical object
        
    Returns:
        str: Cleaned description text or default message if not available
    """
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{name}"
    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            if 'extract' in data:
                raw_description = html.unescape(data['extract'])
                # Use BeautifulSoup to clean HTML
                soup = BeautifulSoup(raw_description, "html.parser")
                cleaned_description = soup.get_text(strip=True)
                return cleaned_description
    except Exception:
        pass
    return "Description not available."

def extract_name_from_description(description: str) -> str | None:
    """
    Extract a potential common name from the beginning of a description.
    
    Stops at the first occurrence of ' is ' or ',', with a fallback to
    the first capitalized word if delimiters are not found.
    
    Args:
        description (str): Description text to extract name from
        
    Returns:
        str or None: Extracted name if found, None otherwise
    """
    if not description:
        return None

    idx_is = description.find(" is ")
    idx_comma = description.find(",")

    end_idx = -1

    # Determine the earliest valid delimiter position
    if idx_is != -1 and idx_comma != -1:
        end_idx = min(idx_is, idx_comma)
    elif idx_is != -1:
        end_idx = idx_is
    elif idx_comma != -1:
        end_idx = idx_comma
    
    # If a delimiter was found, try to extract name using it
    if end_idx != -1:
        potential_name_by_delimiter = description[:end_idx].strip()
        # Validate: not empty, starts with an uppercase letter, and not excessively long
        if (potential_name_by_delimiter and 
            potential_name_by_delimiter[0].isupper() and 
            len(potential_name_by_delimiter) < 70):
            return potential_name_by_delimiter

    # Fallback to original logic: first capitalized word (min 3 characters)
    # This is used if delimiters are not found, or if the extraction above was unsuitable.
    match = re.match(r"([A-Z][a-zA-Z0-9\\-]{2,})", description)
    if match:
        return match.group(1)
            
    return None
