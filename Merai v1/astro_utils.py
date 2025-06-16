import os
from skyfield.api import load, Topos, Star
from skyfield.data import hipparcos

# Get the directory where astro_utils.py is located
_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Construct absolute paths to the data files
DE421_PATH = os.path.join(_CURRENT_DIR, "de421.bsp")
HIPP_PATH = os.path.join(_CURRENT_DIR, "hip_main.dat")

def get_visible_objects(lat, lon, user_dt=None):
    ts = load.timescale()
    t = ts.from_datetime(user_dt) if user_dt else ts.now()
    planets = load(DE421_PATH)
    earth = planets['earth']
    observer = earth + Topos(latitude_degrees=lat, longitude_degrees=lon)
    visible = []

    # Mapping of integer keys to planet names and types
    PLANET_KEY_MAP = {
        199: ('Mercury', 'Planet'),
        299: ('Venus', 'Planet'),
        399: ('Earth', None),  # skip Earth
        301: ('Moon', 'Moon'),
        499: ('Mars', 'Planet'),
        599: ('Jupiter', 'Planet'),
        699: ('Saturn', 'Planet'),
        799: ('Uranus', 'Planet'),
        899: ('Neptune', 'Planet'),
        999: ('Pluto', 'Planet'),
        10: ('Sun', 'Sun'),
    }

    # Diagnostic print: Show all names from the ephemeris
    print("Bodies loaded from ephemeris:", planets.names())

    for name in planets.names():
        # Handle integer keys for planets
        if isinstance(name, int) and name in PLANET_KEY_MAP:
            pretty_name, obj_type = PLANET_KEY_MAP[name]
            if obj_type is None:
                continue  # skip Earth
            try:
                body = planets[name]
                alt, az, _ = observer.at(t).observe(body).apparent().altaz()
                if alt.degrees > 0:
                    visible.append({
                        'name': pretty_name,
                        'type': obj_type,
                        'altitude': round(alt.degrees, 2),
                        'azimuth': round(az.degrees, 2)
                    })
            except Exception as e:
                print(f"Could not process {name}: {e}")
            continue

        # Handle string names (legacy)
        if name == 'earth':
            continue
        try:
            body = planets[name]
            alt, az, _ = observer.at(t).observe(body).apparent().altaz()
            if alt.degrees > 0:
                pretty_name = str(name).replace(' barycenter', '').capitalize()
                name_str = str(name).lower()
                if name_str == 'sun':
                    obj_type = 'Sun'
                elif name_str == 'moon':
                    obj_type = 'Moon'
                elif pretty_name in ['Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto']:
                    obj_type = 'Planet'
                else:
                    if pretty_name not in ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto']:
                        continue
                visible.append({
                    'name': pretty_name,
                    'type': obj_type,
                    'altitude': round(alt.degrees, 2),
                    'azimuth': round(az.degrees, 2)
                })
        except Exception as e:
            print(f"Could not process {name}: {e}")
            continue
    
    with open(HIPP_PATH, 'rb') as f:
        stars = hipparcos.load_dataframe(f)
    bright_stars = stars[stars['magnitude'] < 2.0]
    for hip, star_row in bright_stars.iterrows():
        star = Star(ra_hours=star_row['ra_hours'], dec_degrees=star_row['dec_degrees'])
        alt, az, _ = observer.at(t).observe(star).apparent().altaz()
        if alt.degrees > 0:
            proper_name = star_row.get('proper')
            hip_id_int = int(hip) # HIP ID as integer for map lookup
            hip_id_str = f"HIP {hip_id_int}"
            
            # Determine the primary display name for H1
            display_name_h1 = proper_name if proper_name and proper_name.strip() else hip_id_str
            
            visible.append({
                'name': display_name_h1, # Primary name for H1 (Common name or HIP ID)
                'hip_id': hip_id_str,    # Always the HIP ID, for H2
                'hip_int': hip_id_int, # Add integer HIP ID for constellation lookup
                'type': 'Star',
                'altitude': round(alt.degrees, 2),
                'azimuth': round(az.degrees, 2)
            })
    return visible
