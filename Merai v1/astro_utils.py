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

    # Diagnostic print: Show all names from the ephemeris
    print("Bodies loaded from ephemeris:", planets.names())

    for name in planets.names():
        if name == 'earth': # Skip Earth itself
            continue
        try:
            body = planets[name] # Renamed for clarity, includes Sun, Moon, planets
            alt, az, _ = observer.at(t).observe(body).apparent().altaz()

            if alt.degrees > 0: # If above the horizon
                pretty_name = name.replace(' barycenter', '').capitalize()
                
                # Determine object type
                if name.lower() == 'sun':
                    obj_type = 'Sun'
                elif name.lower() == 'moon':
                    obj_type = 'Moon'
                # Check for planets (ensure 'Earth' is not miscategorized if it were processed)
                elif pretty_name in ['Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto']: # Pluto is still in DE421
                    obj_type = 'Planet'
                else:
                    # For other bodies in DE421 that are not Sun, Moon, or the main planets (e.g., asteroid barycenters if any)
                    # We might want to filter these out or categorize them differently if they appear.
                    # For now, let's assign a generic type or skip.
                    # To be safe, let's only include known types for now or assign a generic 'Celestial Body'.
                    # For this iteration, we'll focus on Sun, Moon, and Planets.
                    # If pretty_name is not one of the above, it might be something like 'Earthmoon' (Moon's barycenter)
                    # or other specific points in the ephemeris. We'll skip these for now to keep the list clean.
                    if pretty_name not in ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto']:
                        continue # Skip other less common barycenters or points for now

                visible.append({
                    'name': pretty_name,
                    'type': obj_type,
                    'altitude': round(alt.degrees, 2),
                    'azimuth': round(az.degrees, 2)
                    # HIP ID and constellation are not applicable to Sun, Moon, Planets
                })
        except Exception as e:
            # print(f"Could not process {name}: {e}") # Optional: for debugging
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
