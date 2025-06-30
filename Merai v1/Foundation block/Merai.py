import geocoder
from skyfield.api import load, Topos
from datetime import datetime
import requests
from io import BytesIO
from PIL import Image
import html
from skyfield.api import utc
import re
import matplotlib.pyplot as plt
from skyfield.data import hipparcos
from skyfield.api import Star
import streamlit as st
import pydeck as pdk
from datetime import date, time
import pandas as pd

# Step 1: Get User Location (Working well do not touch )
def get_user_location():
    permission = input("Do you allow access to your location? (yes/no): ").strip().lower()
    if permission != 'yes':
        print("Location access denied. Exiting.")
        exit()
    g = geocoder.ip('me')
    if g.ok:
        lat, lon = g.latlng
        address = g.city + ", " + g.country if g.city and g.country else "Unknown location"
        print(f"Detected location: {address} ({lat}, {lon})")
        return lat, lon, address
    else:
        print("Could not determine location.")
        exit()

# Step 1.1: Get User date time or real time (Working well do not touch )
def get_user_datetime():
    user_input = input("Enter date and time in YYYY-MM-DD HH:MM (24h, local) or press Enter for now: ").strip()
    if not user_input:
        return None  # Use current time
    try:
        dt = datetime.strptime(user_input, "%Y-%m-%d %H:%M")
        dt = dt.replace(tzinfo=utc)  # Make datetime timezone-aware (UTC)
        return dt
    except Exception:
        print("Invalid format. Using current time.")
        return None

# Step 2: Retrieve Astronomical Data
def get_visible_objects(lat, lon, user_dt=None):
    ts = load.timescale()
    if user_dt:
        t = ts.from_datetime(user_dt)
    else:
        t = ts.now()
    planets = load('de421.bsp')
    earth = planets['earth']
    observer = earth + Topos(latitude_degrees=lat, longitude_degrees=lon)
    visible = []
    
    # For Planets, Sun, Moon
    for name in planets.names():
        if name == 'earth':
            continue
        try:
            planet = planets[name]
            alt, az, _ = observer.at(t).observe(planet).apparent().altaz()
            if alt.degrees > 0:
                pretty_name = name.replace(' barycenter', '').capitalize()
                obj_type = 'Planet' if pretty_name in ['Mercury','Venus','Earth','Mars','Jupiter','Saturn','Uranus','Neptune','Pluto'] else pretty_name
                visible.append({
                    'name': pretty_name,
                    'type': obj_type,
                    'altitude': round(alt.degrees, 2),
                    'azimuth': round(az.degrees, 2),
                    'raw_name': name
                })
        except Exception:
            continue
    # for Bright stars (Hipparcos, mag < 2.0)
    with load.open(hipparcos.URL) as f:
        stars = hipparcos.load_dataframe(f)
    bright_stars = stars[stars['magnitude'] < 2.0]
    for hip, star_row in bright_stars.iterrows():
        star = Star(ra_hours=star_row['ra_hours'], dec_degrees=star_row['dec_degrees'])
        astrometric = observer.at(t).observe(star)
        alt, az, _ = astrometric.apparent().altaz()
        if alt.degrees > 0:
            # Try to get a common name from 'proper', else fetch from Wikipedia description, else None
            star_name = star_row.get('proper')
            if isinstance(star_name, str) and star_name.strip():
                common_name = star_name.strip()
            else:
                # Try to get name from Wikipedia description
                desc = get_object_description(f"HIP {hip}")
                if desc:
                    match = re.match(r"([A-Z][a-zA-Z0-9\-]*) ", desc)
                    if match:
                        common_name = match.group(1)
                    else:
                        common_name = None
                else:
                    common_name = None
            if common_name:
                name_to_use = f"Common Name: {common_name} | Name: HIP {hip}"
            else:
                name_to_use = f"Common Name: None | Name: HIP {hip}"
            constellation = star_row['constellation'] if 'constellation' in star_row else ''
            visible.append({
                'name': name_to_use,
                'type': 'Star',
                'altitude': round(alt.degrees, 2),
                'azimuth': round(az.degrees, 2),
                'raw_name': f"HIP {hip}",
                'constellation': constellation
            })
    # Remove duplicates and sort by altitude descending
    seen = set()
    unique_visible = []
    for obj in sorted(visible, key=lambda x: -x['altitude']):
        key = (obj['name'], obj['type'])
        if key not in seen:
            seen.add(key)
            unique_visible.append(obj)
    return unique_visible

# Step 3: Retrieve and Display Object Images
def get_object_image_url(name):
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

def display_image(image_url, title, wiki_name=None):
    if wiki_name is None:
        wiki_name = title
    desc = get_object_description(wiki_name)
    print(f"Description for {title}:\n{desc}\n" if desc else f"No description found for {title}.")
    if not image_url:
        print(f"No image found for {title}.")
        return
    try:
        resp = requests.get(image_url, timeout=5)
        if resp.status_code == 200:
            img = Image.open(BytesIO(resp.content))
            plt.imshow(img)
            plt.axis('off')
            plt.title(title)
            plt.show()
        else:
            print(f"Could not retrieve image for {title}.")
    except Exception:
        print(f"Could not retrieve image for {title}.")

# New helper function to get a readable description from Wikipedia API
def get_object_description(name):
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{name}"
    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            if 'extract' in data:
                return html.unescape(data['extract'])
    except Exception:
        pass
    return None

# Main Program
def main():
    st.set_page_config(page_title="What's Up? Astronomy Dashboard", layout="wide")
    st.title("What's Up? Astronomy Dashboard")
    st.write("This dashboard shows visible astronomical objects from your location and time.")

    # --- Location Section ---
    st.header("1. Location")
    col1, col2 = st.columns(2)
    use_auto = col1.checkbox("Detect my location automatically", value=True)
    manual = col2.checkbox("Enter location manually")
    lat, lon, address = None, None, None
    if use_auto:
        g = geocoder.ip('me')
        if g.ok:
            lat, lon = g.latlng
            address = g.city + ", " + g.country if g.city and g.country else "Unknown location"
            st.success(f"Detected location: {address} ({lat}, {lon})")
        else:
            st.error("Could not determine location.")
            st.stop()
    elif manual:
        lat = st.number_input("Latitude", value=28.6139, format="%.6f")
        lon = st.number_input("Longitude", value=77.2090, format="%.6f")
        address = "Manual Entry"
        st.info(f"Using manual location: ({lat}, {lon})")
    else:
        st.warning("Please select a location method.")
        st.stop()
    st.map(pd.DataFrame({"lat": [lat], "lon": [lon]}))

    # --- Time Section ---
    st.header("2. Date and Time")
    col1, col2 = st.columns(2)
    d = col1.date_input("Date", value=date.today())
    t = col2.time_input("Time", value=datetime.now().time())
    dt = datetime.combine(d, t).replace(tzinfo=utc)
    if st.button("Set to Now"):
        dt = datetime.now().replace(tzinfo=utc)
        st.experimental_rerun()

    # --- Object Filtering ---
    st.header("3. Object Filters")
    show_stars = st.checkbox("Show Stars", value=True)
    show_planets = st.checkbox("Show Planets", value=True)
    show_sun = st.checkbox("Show Sun", value=True)
    show_moon = st.checkbox("Show Moon", value=True)

    # --- Fetch Data ---
    st.header("4. Visible Astronomical Objects")
    with st.spinner("Fetching visible astronomical objects..."):
        visible_objects = get_visible_objects(lat, lon, dt)
    if not visible_objects:
        st.warning("No astronomical objects are currently visible from your location.")
        st.stop()

    # --- Filtering & Sorting ---
    filtered = []
    for obj in visible_objects:
        if obj['type'] == 'Star' and not show_stars:
            continue
        if obj['type'] == 'Planet' and not show_planets:
            continue
        if obj['name'] == 'Sun' and not show_sun:
            continue
        if obj['name'] == 'Moon' and not show_moon:
            continue
        filtered.append(obj)
    sort_by = st.selectbox("Sort by", ["Altitude (desc)", "Azimuth (asc)", "Type"])
    if sort_by == "Altitude (desc)":
        filtered = sorted(filtered, key=lambda x: -x['altitude'])
    elif sort_by == "Azimuth (asc)":
        filtered = sorted(filtered, key=lambda x: x['azimuth'])
    elif sort_by == "Type":
        filtered = sorted(filtered, key=lambda x: x['type'])

    # --- Table ---
    table_data = []
    for obj in filtered:
        # Always show constellation if available, and try to extract from star_row if missing
        constellation = obj.get('constellation', '')
        if not constellation and 'Constellation:' in obj['name']:
            match = re.search(r"Constellation: ([^|]+)", obj['name'])
            if match:
                constellation = match.group(1).strip()
        # For stars, also try to extract from raw_name if missing
        if obj['type'] == 'Star' and not constellation:
            hip_match = re.search(r"HIP (\d+)", obj['raw_name']) if 'raw_name' in obj else None
            if hip_match:
                hip_num = int(hip_match.group(1))
                try:
                    with load.open(hipparcos.URL) as f:
                        stars = hipparcos.load_dataframe(f)
                    star_row = stars.loc[hip_num]
                    if 'constellation' in star_row and isinstance(star_row['constellation'], str):
                        constellation = star_row['constellation']
                except Exception:
                    pass
        # Try to extract constellation from Wikipedia description if still missing
        if not constellation:
            desc = get_object_description(obj['name'])
            if desc:
                match = re.search(r"constellation ([A-Za-z ]+)[,\.]", desc, re.IGNORECASE)
                if match:
                    constellation = match.group(1).strip()
        if obj['type'] == 'Star':
            hip_match = re.search(r"HIP (\d+)", obj['name'])
            hip_name = f"HIP {hip_match.group(1)}" if hip_match else obj['name']
            common_name_match = re.search(r"Common Name: ([^|]+)", obj['name'])
            common_name = common_name_match.group(1).strip() if common_name_match else None
            if common_name and common_name.lower() != 'none' and common_name.strip() and not common_name.lower().startswith('hip') and not common_name.strip().isdigit():
                display_name = f"{common_name} ({hip_name}) (Star)"
            else:
                display_name = f"{hip_name} ({hip_name}) (Star)"
            table_data.append({
                'Name': display_name,
                'Type': obj['type'],
                'Constellation': constellation,
                'Altitude (°)': obj['altitude'],
                'Azimuth (°)': obj['azimuth']
            })
        else:
            table_data.append({
                'Name': f"{obj['name']} ({obj['type']})",
                'Type': obj['type'],
                'Constellation': constellation,
                'Altitude (°)': obj['altitude'],
                'Azimuth (°)': obj['azimuth']
            })
    st.dataframe(pd.DataFrame(table_data))

    # --- Sky Chart Visualization ---
    st.header("5. Sky Chart (Experimental)")
    try:
        import matplotlib.pyplot as plt
        import numpy as np
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.set_xlim(0, 360)
        ax.set_ylim(0, 90)
        ax.set_xlabel('Azimuth (°)')
        ax.set_ylabel('Altitude (°)')
        ax.set_title('Sky Chart: Altitude vs Azimuth')
        for obj in filtered:
            color = 'yellow' if obj['name'] == 'Sun' else ('gray' if obj['name'] == 'Moon' else ('red' if obj['type'] == 'Planet' else 'white'))
            ax.scatter(obj['azimuth'], obj['altitude'], color=color, label=obj['name'], s=60, edgecolor='black')
            ax.text(obj['azimuth'], obj['altitude']+2, obj['name'], fontsize=8, ha='center', color=color)
        ax.set_facecolor('navy')
        ax.grid(True, color='white', alpha=0.2)
        handles, labels = ax.get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        ax.legend(by_label.values(), by_label.keys(), loc='lower left', fontsize=7)
        st.pyplot(fig)
    except Exception as e:
        st.info("Sky chart not available: " + str(e))

    # --- Details Section ---
    st.header("6. Learn More About Each Object")
    for obj in filtered:
        # Always show constellation if available, and try to extract from star_row if missing
        constellation = obj.get('constellation', '')
        if not constellation and 'Constellation:' in obj['name']:
            match = re.search(r"Constellation: ([^|]+)", obj['name'])
            if match:
                constellation = match.group(1).strip()
        if obj['type'] == 'Star' and not constellation:
            hip_match = re.search(r"HIP (\d+)", obj['raw_name']) if 'raw_name' in obj else None
            if hip_match:
                hip_num = int(hip_match.group(1))
                try:
                    with load.open(hipparcos.URL) as f:
                        stars = hipparcos.load_dataframe(f)
                    star_row = stars.loc[hip_num]
                    if 'constellation' in star_row and isinstance(star_row['constellation'], str):
                        constellation = star_row['constellation']
                except Exception:
                    pass
        with st.expander(f"Details: {obj['name']}"):
            if obj['type'] == 'Star':
                hip_match = re.search(r"HIP (\d+)", obj['name'])
                hip_name = f"HIP {hip_match.group(1)}" if hip_match else obj['name']
                common_name_match = re.search(r"Common Name: ([^|]+)", obj['name'])
                common_name = common_name_match.group(1).strip() if common_name_match else None
                if not (common_name and common_name.lower() != 'none' and common_name.strip() and not common_name.lower().startswith('hip') and not common_name.strip().isdigit()):
                    desc = get_object_description(hip_name)
                    if desc:
                        match = re.match(r"([A-Z][a-zA-Z0-9\-]*)[ ,]", desc)
                        if match:
                            common_name = match.group(1)
                if common_name and common_name.lower() != 'none' and common_name.strip() and not common_name.lower().startswith('hip') and not common_name.strip().isdigit():
                    display_name = f"{common_name} ({hip_name}) (Star)"
                else:
                    display_name = f"{hip_name} ({hip_name}) (Star)"
                st.markdown(f"**Name:** {display_name}")
                st.markdown(f"**Type:** {obj['type']}")
                st.markdown(f"**Constellation:** {constellation if constellation else 'Unknown'}")
                st.markdown(f"**Altitude:** {obj['altitude']}°")
                st.markdown(f"**Azimuth:** {obj['azimuth']}°")
                image_url = None
                wiki_name = None
                if common_name and common_name.lower() != 'none' and common_name.strip() and not common_name.lower().startswith('hip') and not common_name.strip().isdigit():
                    image_url = get_object_image_url(common_name + " (star)")
                    wiki_name = common_name + " (star)"
                    if not image_url:
                        image_url = get_object_image_url(common_name + " (astronomy)")
                        wiki_name = common_name + " (astronomy)"
                    if not image_url:
                        image_url = get_object_image_url(common_name)
                        wiki_name = common_name
                if not image_url:
                    image_url = get_object_image_url(hip_name)
                    wiki_name = hip_name
                if not image_url and 'desc' in locals() and desc:
                    bayer_match = re.search(r"designation ([^,\. ]+)", desc, re.IGNORECASE)
                    if bayer_match:
                        bayer_name = bayer_match.group(1)
                        image_url = get_object_image_url(bayer_name)
                        wiki_name = bayer_name
                desc = get_object_description(wiki_name) if wiki_name else None
                if desc:
                    st.info(desc)
                if image_url:
                    st.image(image_url, caption=wiki_name, use_column_width=True)
                else:
                    st.warning("No image found.")
            elif obj['name'] in ['Sun', 'Moon']:
                st.markdown(f"**Name:** {obj['name']}")
                st.markdown(f"**Type:** {obj['type']}")
                st.markdown(f"**Altitude:** {obj['altitude']}°")
                st.markdown(f"**Azimuth:** {obj['azimuth']}°")
                st.markdown(f"**Constellation:** {constellation if constellation else 'N/A'}")
                wiki_name = obj['name']
                image_url = get_object_image_url(obj['name'])
                desc = get_object_description(wiki_name)
                if desc:
                    st.info(desc)
                if image_url:
                    st.image(image_url, caption=wiki_name, use_column_width=True)
                else:
                    st.warning("No image found.")
            elif obj['type'] == 'Planet':
                st.markdown(f"**Name:** {obj['name']}")
                st.markdown(f"**Type:** {obj['type']}")
                st.markdown(f"**Altitude:** {obj['altitude']}°")
                st.markdown(f"**Azimuth:** {obj['azimuth']}°")
                st.markdown(f"**Constellation:** {constellation if constellation else 'N/A'}")
                wiki_name = obj['name'] + " (planet)"
                image_url = get_object_image_url(wiki_name)
                desc = get_object_description(wiki_name)
                if desc:
                    st.info(desc)
                if image_url:
                    st.image(image_url, caption=wiki_name, use_column_width=True)
                else:
                    st.warning("No image found.")
            else:
                st.markdown(f"**Name:** {obj['name']}")
                st.markdown(f"**Type:** {obj['type']}")
                st.markdown(f"**Altitude:** {obj['altitude']}°")
                st.markdown(f"**Azimuth:** {obj['azimuth']}°")
                st.markdown(f"**Constellation:** {constellation if constellation else 'N/A'}")
                wiki_name = obj['name']
                image_url = get_object_image_url(wiki_name)
                desc = get_object_description(wiki_name)
                if desc:
                    st.info(desc)
                if image_url:
                    st.image(image_url, caption=wiki_name, use_column_width=True)
                else:
                    st.warning("No image found.")

    # --- Export Section ---
    st.header("7. Export Visible Objects")
    if table_data:
        df = pd.DataFrame(table_data)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download visible objects as CSV",
            data=csv,
            file_name='visible_objects.csv',
            mime='text/csv',
        )

    # --- Help & About ---
    st.sidebar.title("Help & About")
    st.sidebar.info("""
**How to use:**
- Choose your location (auto/manual)
- Set date and time
- Filter object types
- Explore the sky chart and details
- Download the visible list

**Tips:**
- Use dark mode for night viewing (Streamlit settings)
- Click on object names for more info
- For best results, use a desktop browser
""")
    st.sidebar.markdown("---")
    st.sidebar.write("Made with :star: by Shubham Mehta")

if __name__ == "__main__":
    main()
