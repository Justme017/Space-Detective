"""
Wikipedia utility functions for the Space Detective application.

This module provides functions to fetch object descriptions and images from 
Wikipedia to enhance the display of astronomical objects.
"""

import requests
import html
import re
from bs4 import BeautifulSoup

# --- Constants --- / --- API ---

WIKIPEDIA_API_URL = "https://en.wikipedia.org/api/rest_v1/page/summary/{name}"

# Fallback images for common celestial objects and bright stars
FALLBACK_IMAGES = {
    # Planets and celestial bodies
    'Moon': 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/e1/FullMoon2010.jpg/256px-FullMoon2010.jpg',
    'Sun': 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/b4/The_Sun_by_the_Atmospheric_Imaging_Assembly_of_NASA%27s_Solar_Dynamics_Observatory_-_20100819.jpg/256px-The_Sun_by_the_Atmospheric_Imaging_Assembly_of_NASA%27s_Solar_Dynamics_Observatory_-_20100819.jpg',
    'Mercury': 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/4a/Mercury_in_true_color.jpg/256px-Mercury_in_true_color.jpg',
    'Venus': 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/08/Venus_from_Mariner_10.jpg/256px-Venus_from_Mariner_10.jpg',
    'Mars': 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/02/OSIRIS_Mars_true_color.jpg/256px-OSIRIS_Mars_true_color.jpg',
    'Jupiter': 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/2b/Jupiter_and_its_shrunken_Great_Red_Spot.jpg/256px-Jupiter_and_its_shrunken_Great_Red_Spot.jpg',
    'Saturn': 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c1/Saturn_from_Cassini_Orbiter_%282004-10-06%29.jpg/256px-Saturn_from_Cassini_Orbiter_%282004-10-06%29.jpg',
    'Uranus': 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/48/Uranus_as_seen_by_NASA%27s_Voyager_2_%28remastered%29.png/256px-Uranus_as_seen_by_NASA%27s_Voyager_2_%28remastered%29.png',
    'Neptune': 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/63/Neptune_-_Voyager_2_%2829347980845%29_flatten_crop.jpg/256px-Neptune_-_Voyager_2_%2829347980845%29_flatten_crop.jpg',
    'Pluto': 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/ef/Pluto_in_True_Color_-_High-Res.jpg/256px-Pluto_in_True_Color_-_High-Res.jpg',
    
    # Bright stars with reliable astronomical images
    'Mimosa': 'https://nineplanets.org/wp-content/uploads/2020/01/optical-image-of-the-star-mimosa-or-beta-crucis-celestial-image-co.jpg',
    'Sirius': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=400&fit=crop&crop=center',
    'Canopus': 'https://freestarcharts.com/images/Articles/Stars/Canopus/Canopus_Espenak.jpg',
    'Arcturus': 'https://en.wikipedia.org/wiki/Arcturus#/media/File:Arcturus_(optical).png',
    'Vega': 'https://images.unsplash.com/photo-1502134249126-9f3755a50d78?w=400&h=400&fit=crop&crop=center',
    'Capella': 'https://theplanets.org/123/2022/03/The-Capella-Star.jpgr',
    'Rigel': 'https://theplanets.org/123/2022/03/The-Rigel-Star-System.png',
    'Procyon': 'https://assets.science.nasa.gov/dynamicimage/assets/science/astro/universe/internal_resources/408/red_dwarf-1.jpeg?w=1280&h=1255&fit=clip&crop=faces%2Cfocalpoint',
    'Betelgeuse': 'https://images.unsplash.com/photo-1464802686167-b939a6910659?w=400&h=400&fit=crop&crop=center',
    'Achernar': 'https://images.unsplash.com/photo-1502134249126-9f3755a50d78?w=400&h=400&fit=crop&crop=center',
    'Hadar': 'https://www.star-facts.com/wp-content/uploads/2022/06/South-Star-Polaris-Australis.webp?w=400&h=400&fit=crop&crop=center',
    'Altair': 'https://www.star-facts.com/wp-content/uploads/2019/09/Altair-Alpha-Aquilae.webp',
    'Aldebaran': 'https://www.star-facts.com/wp-content/uploads/2022/06/South-Star-Polaris-Australis.webp?w=400&h=400&fit=crop&crop=center',
    'Antares': 'https://www.star-facts.com/wp-content/uploads/2022/06/South-Star-Polaris-Australis.webp?w=400&h=400&fit=crop&crop=center',
    'Spica': 'https://imgs.search.brave.com/VOo1HpORc_leSuzyOP0IsU1e6XI5MHxzjnY_QL-M1I8/rs:fit:500:0:1:0/g:ce/aHR0cHM6Ly93d3cu/c3Rhci1mYWN0cy5j/b20vd3AtY29udGVu/dC91cGxvYWRzLzIw/MTkvMTAvU3BpY2Et/QWxwaGEtVmlyZ2lu/aXMud2VicA',
    'Pollux': 'https://imgs.search.brave.com/dUZTOfAAt2Gz_ZVAE25zcKsVaHxeaBI6b-2GyaKSH-8/rs:fit:860:0:0:0/g:ce/aHR0cHM6Ly90NC5m/dGNkbi5uZXQvanBn/LzA4LzM3LzYxLzE5/LzM2MF9GXzgzNzYx/MTk4OV80SUFkUHBo/aFE3T2xRamo4Rlhp/WmZlTlNmbzVsU0hT/Si5qcGc',
    'Fomalhaut': 'https://www.nasa.gov/wp-content/uploads/2023/05/stsci-01gwwhep4rves5p1vr29z2dbsz.png',
    'Deneb': 'https://www.star-facts.com/wp-content/uploads/2022/11/Deneb-Algedi.webp?w=400&h=400&fit=crop&crop=center',
    'Regulus': 'https://www.constellation-guide.com/wp-content/uploads/2015/04/Regulus.webp?w=400&h=400&fit=crop&crop=center',
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

def _try_inthesky_image(name, hip_id=None):
    """
    Attempt to get an image from in-the-sky.org for a star.
    
    Args:
        name (str): Star name
        hip_id (int): HIP catalog number if available
        
    Returns:
        str or None: Image URL if found, None otherwise
    """
    # FUTURE CASE, PARSING IN-THE-SKY.ORG
    # For now, this is a placeholder. We would need to:
    # 1. Determine if in-the-sky.org has a public API
    # 2. Find the URL pattern for HIP star images
    # 3. Implement the logic to construct URLs
    
    # Example of what this might look like if we find a pattern:
    # if hip_id:
    #     return f"https://in-the-sky.org/starimage.php?hip={hip_id}&style=medium"
    
    return None

# --- Public API --- API REMOVED

def get_object_image_url(name):
    """
    Fetch an object's image URL from Wikipedia, with fallbacks.

    Args:
        name (str): The name of the astronomical object.

    Returns:
        str or None: The image URL if found, otherwise None.
    """
    # Special case: Always use hardcoded image for Mimosa
    if name == 'Mimosa':
        return FALLBACK_IMAGES['Mimosa']
    
    # First try Wikipedia
    data = _fetch_from_wikipedia_api(name)
    if data and 'thumbnail' in data and 'source' in data['thumbnail']:
        return data['thumbnail']['source']

    # Then check our curated fallback images
    if name in FALLBACK_IMAGES:
        return FALLBACK_IMAGES[name]
    
    # Could try in-the-sky.org dynamic lookup here if we find the pattern
    # inthesky_url = _try_inthesky_image(name)
    # if inthesky_url:
    #     return inthesky_url

    # Final fallback to generic star image
    return "https://images.unsplash.com/photo-1534796636912-3b95b3ab5986?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2071&q=80"


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
