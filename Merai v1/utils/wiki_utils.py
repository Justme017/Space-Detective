"""
Wikipedia utility functions for the Space Detective application.

This module provides functions to fetch object descriptions and images from 
Wikipedia to enhance the display of astronomical objects.
"""

import requests
import html
import re
from bs4 import BeautifulSoup

# --- Constants ---

WIKIPEDIA_API_URL = "https://en.wikipedia.org/api/rest_v1/page/summary/{name}"

# Fallback images for common celestial objects
FALLBACK_IMAGES = {
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

# --- Private Helper Functions ---

def _fetch_from_wikipedia_api(name):
    """
    Fetches data from the Wikipedia summary API.
    """
    try:
        resp = requests.get(WIKIPEDIA_API_URL.format(name=name), timeout=5)
        resp.raise_for_status()  # Raise an exception for bad status codes
        return resp.json()
    except requests.RequestException:
        return None

# --- Public API ---

def get_object_image_url(name):
    """
    Fetch an object's image URL from Wikipedia, with fallbacks.

    Args:
        name (str): The name of the astronomical object.

    Returns:
        str or None: The image URL if found, otherwise None.
    """
    data = _fetch_from_wikipedia_api(name)
    if data and 'thumbnail' in data and 'source' in data['thumbnail']:
        return data['thumbnail']['source']

    # Fallback to predefined images if API fails or has no image
    if name in FALLBACK_IMAGES:
        return FALLBACK_IMAGES[name]

    # If Wikipedia fails, construct a targeted search query for a better source
    try:
        # A more specific query for astronomical images
        search_query = name.replace(" ", "+") + "+star"
        # Using a service that might have better astronomical images.
        # This is still a demonstration as a dedicated API would be better.
        return f"https://source.unsplash.com/400x400/?{search_query}"
    except Exception:
        # If all else fails, return None so the UI can handle it gracefully
        return None


def get_object_description(name):
    """
    Fetch a cleaned object description from the Wikipedia API.

    Args:
        name (str): The name of the astronomical object.

    Returns:
        str: The cleaned description or a default message.
    """
    data = _fetch_from_wikipedia_api(name)
    if data and 'extract' in data:
        raw_description = html.unescape(data['extract'])
        soup = BeautifulSoup(raw_description, "html.parser")
        return soup.get_text(strip=True)
        
    return "Description not available."

def extract_name_from_description(description: str) -> str | None:
    """
    Extract a common name from a description, prioritizing structured patterns.

    Args:
        description (str): The description text.

    Returns:
        str or None: The extracted name if found, otherwise None.
    """
    if not description:
        return None

    # Try to find name before " is " or ","
    match = re.match(r"(.*?)(?: is |,)", description)
    if match:
        potential_name = match.group(1).strip()
        if potential_name and potential_name[0].isupper() and len(potential_name) < 70:
            return potential_name

    # Fallback to the first capitalized word (if suitable)
    match = re.match(r"([A-Z][a-zA-Z0-9\\-]{2,})", description)
    if match:
        return match.group(1)
            
    return None
