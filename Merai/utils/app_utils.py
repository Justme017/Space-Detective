# utils/app_utils.py

from datetime import datetime
from utils.wiki_utils import get_object_image_url

MAX_DESC_LEN = 120
ZOOM_LEVELS = [0.7, 1.0, 1.3, 1.6, 2.0]

def format_datetime_utc(dt):
    """
    Convert a Python datetime to a UTC‐formatted string.
    """
    return dt.strftime("%Y-%m-%d %H:%M:%S UTC")

def crop_description(desc):
    """
    Return a short preview of the description,
    adding an ellipsis if it exceeds MAX_DESC_LEN.
    """
    if not desc or desc == "Description not available.":
        return desc
    if len(desc) <= MAX_DESC_LEN:
        return desc
    return desc[:MAX_DESC_LEN].rstrip() + "…"

def get_image_for(obj):
    """
    Return the image URL for an object,
    falling back to Wikipedia‐provided or star placeholder.
    """
    key = obj.get('name') or obj.get('hip_id', '')
    return get_object_image_url(key)
