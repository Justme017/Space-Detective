import requests
import os

# --- Constants ---
_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
STATIONS_URL = "https://celestrak.org/NORAD/elements/gp.php?GROUP=stations&FORMAT=tle"
BRIGHTEST_URL = "https://celestrak.org/NORAD/elements/gp.php?GROUP=visual&FORMAT=tle"

STATIONS_FILE = os.path.join(_CURRENT_DIR, "stations.tle")
BRIGHTEST_FILE = os.path.join(_CURRENT_DIR, "brightest.tle")

def download_file(url, filename):
    """Downloads a file from a URL and saves it locally."""
    try:
        print(f"Downloading {url}...")
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(response.text)
        print(f"Successfully saved to {filename}")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading {url}: {e}")

if __name__ == "__main__":
    print("Starting TLE data download...")
    download_file(STATIONS_URL, STATIONS_FILE)
    download_file(BRIGHTEST_URL, BRIGHTEST_FILE)
    print("\nTLE data download complete.")
    print(f"Satellite data has been stored in '{_CURRENT_DIR}'.")
