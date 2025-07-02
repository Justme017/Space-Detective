# utils/astro_utils.py

"""
Astronomical utility functions for the Space Detective application.
"""

import os
from skyfield.api import load, Topos, Star
from skyfield.data import hipparcos
from utils.wiki_utils import get_object_description, extract_name_from_description

# --- Data Paths ---
# Assumes you have a folder `data/` at your project root containing these files
BASE_DIR       = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR       = os.path.join(BASE_DIR, "data")
DE421_PATH     = os.path.join(DATA_DIR, "de421.bsp")
HIPP_PATH      = os.path.join(DATA_DIR, "hip_main.dat")

def _get_visible_planets(observer, t, planets):
    visible_planets = []
    names = [
        ("sun","Sun"), ("moon","Moon"), ("mercury","Planet"),
        ("venus","Planet"), ("mars","Planet"), ("jupiter","Planet"),
        ("saturn","Planet"), ("uranus","Planet"), ("neptune","Planet"),
        ("pluto","Planet")
    ]
    for obj_name, obj_type in names:
        try:
            body = planets[obj_name]
            alt, az, _ = observer.at(t).observe(body).apparent().altaz()
            if alt.degrees > 0:
                visible_planets.append({
                    "name": obj_name.capitalize(),
                    "type": obj_type,
                    "altitude": round(alt.degrees, 2),
                    "azimuth": round(az.degrees, 2),
                })
        except Exception:
            continue
    return visible_planets

def _get_visible_stars(observer, t):
    visible_stars = []
    if not os.path.isfile(HIPP_PATH):
        print(f"Warning: HIP catalog not found at {HIPP_PATH}")
        return []
    with open(HIPP_PATH, "rb") as f:
        stars = hipparcos.load_dataframe(f)
    bright = stars[stars["magnitude"] < 2.0]
    for hip_id, row in bright.iterrows():
        try:
            star = Star(ra_hours=row["ra_hours"], dec_degrees=row["dec_degrees"])
            alt, az, _ = observer.at(t).observe(star).apparent().altaz()
            if alt.degrees > 0:
                name = row.get("proper") or f"HIP {int(hip_id)}"
                visible_stars.append({
                    "name": name,
                    "hip_id": f"HIP {int(hip_id)}",
                    "hip_int": int(hip_id),
                    "type": "Star",
                    "altitude": round(alt.degrees, 2),
                    "azimuth": round(az.degrees, 2),
                })
        except Exception:
            continue
    return visible_stars

def get_visible_objects(lat, lon, user_dt=None):
    ts = load.timescale()
    t  = ts.from_datetime(user_dt) if user_dt else ts.now()

    if not os.path.isfile(DE421_PATH):
        print(f"Warning: ephemeris not found at {DE421_PATH}")
        return []

    planets  = load(DE421_PATH)
    observer = planets["earth"] + Topos(latitude_degrees=lat, longitude_degrees=lon)

    planets_list = _get_visible_planets(observer, t, planets)
    stars_list   = _get_visible_stars(observer, t)
    return planets_list + stars_list

def enhance_visible_objects(visible_objects, constellation_map):
    enhanced = []
    for obj in visible_objects:
        key = obj.get("hip_id") if obj["type"] == "Star" else obj["name"]
        desc = get_object_description(key) or ""
        obj["fetched_description"] = desc
        if obj["type"] == "Star":
            hip = obj.get("hip_int")
            obj["constellation"] = constellation_map.get(hip, "Unknown")
            name_from_desc = extract_name_from_description(desc)
            if name_from_desc:
                obj["name"] = name_from_desc
        else:
            obj["constellation"] = "N/A"
        enhanced.append(obj)
    return enhanced
