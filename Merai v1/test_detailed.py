import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from utils.astro_utils import get_visible_objects, enhance_visible_objects
from utils.constellation_utils import load_constellation_data
from utils.wiki_utils import get_object_description
from datetime import datetime
from skyfield.api import utc

# Test individual star descriptions
print("Testing individual star descriptions...")
print("=" * 50)

# Test specific stars that should be visible
test_stars = ['Sun', 'Sirius', 'Canopus', 'Rigel', 'Mimosa', 'Hadar']

for star in test_stars:
    try:
        desc = get_object_description(star)
        print(f"{star}:")
        print(f"  Description type: {type(desc)}")
        print(f"  Description length: {len(desc) if desc else 0}")
        print(f"  Description is None: {desc is None}")
        print(f"  Description is empty: {desc == ''}")
        print(f"  Description preview: {repr(desc[:100]) if desc else 'No description'}")
        print()
    except Exception as e:
        print(f"Error with {star}: {e}")
        import traceback
        traceback.print_exc()
        print()

# Test the entire flow with one object
print("Testing full flow with Sun...")
print("=" * 50)

lat, lon = 34.05, -118.24
dt = datetime.now(utc)

visible_objects = get_visible_objects(lat, lon, dt)
if visible_objects:
    # Find the Sun object
    sun_obj = None
    for obj in visible_objects:
        if obj.get('type') == 'Sun':
            sun_obj = obj
            break
    
    if sun_obj:
        print("Original Sun object:")
        print(f"  Name: {sun_obj.get('name')}")
        print(f"  Type: {sun_obj.get('type')}")
        print(f"  Has fetched_description: {'fetched_description' in sun_obj}")
        print()
        
        # Test enhancement
        constellation_map = load_constellation_data()
        enhanced_objects = enhance_visible_objects([sun_obj], constellation_map)
        
        if enhanced_objects:
            enhanced_sun = enhanced_objects[0]
            print("Enhanced Sun object:")
            print(f"  Name: {enhanced_sun.get('name')}")
            print(f"  Type: {enhanced_sun.get('type')}")
            print(f"  Has fetched_description: {'fetched_description' in enhanced_sun}")
            if 'fetched_description' in enhanced_sun:
                desc = enhanced_sun['fetched_description']
                print(f"  Description type: {type(desc)}")
                print(f"  Description: {repr(desc[:200])}")
