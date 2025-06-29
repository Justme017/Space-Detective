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
    Fetch object image URL from Wikipedia API.
    
    Args:
        name (str): Name of the astronomical object
        
    Returns:
        str or None: Image URL if available, None otherwise
    """
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{name}"
    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            if 'thumbnail' in data and 'source' in data['thumbnail']:
                return data['thumbnail']['source']
    except Exception:
        pass
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
