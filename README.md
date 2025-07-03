# Merai - A Space Detective 🔭

A beautiful and interactive Streamlit web application for exploring visible astronomical objects from any location and time. Discover planets, stars, satellites, and space stations with detailed information and an interactive sky chart.

## ✨ Features

- **🌍 Location Detection**: Automatic GPS/IP detection or manual selection on an interactive map.
- **🕒 Custom Date/Time**: View the sky from any date and time.
- **🛰️ Satellite & Space Station Tracking**: Displays visible satellites and space stations based on your location.
- **⭐ Celestial Objects**: Display visible planets, stars, and other astronomical objects.
- **📖 Rich Information**: Detailed descriptions and images from Wikipedia.
- **🌟 Interactive Sky Chart**: Visual representation of the night sky with zoom controls.
- **🗺️ Embedded Sky Maps**: Includes the Aladin Lite sky atlas and a live satellite tracker from Keeptrack.space.
- **🎨 Beautiful UI**: Space-themed design with responsive layout.
- **✨ Constellation Mapping**: Star objects mapped to their constellations.

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher
- Internet connection (for API calls and TLE data downloads)

### Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/Justme017/Space-Detective
    cd "Space-Detective-1/Merai v1"
    ```

2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Download TLE Data**:
    Run the included script to download the latest satellite data. This only needs to be done once or periodically to refresh the data.
    ```bash
    python download_tle_data.py
    ```

4.  **Run the application**:
    ```bash
    streamlit run main.py
    ```

5.  **Open your browser** to `http://localhost:8501` and start exploring!

## 📁 Project Structure

```
Merai v1/
├── main.py                 # Main Streamlit application
├── astro_utils.py          # Astronomical calculations (planets, stars)
├── satellites_utils.py     # Satellite and space station tracking
├── wiki_utils.py           # Wikipedia API integration
├── constellation_utils.py  # Constellation mapping
├── skychart_utils.py       # Sky chart generation
├── app_utils.py            # UI components and styling
├── download_tle_data.py    # Script to download TLE files
├── requirements.txt        # Python dependencies
├── de421.bsp               # JPL planetary ephemeris data
├── hip_main.dat            # Hipparcos star catalog
├── brightest.tle           # TLE data for bright satellites
├── stations.tle            # TLE data for space stations
└── ...
```

## 🛠️ Core Modules

### `main.py`

The main application built with Streamlit. It orchestrates the UI and data fetching from all utility modules.

### `astro_utils.py`

Handles astronomical calculations for planets and stars using Skyfield.

### `satellites_utils.py`

Fetches and calculates the positions of visible satellites and space stations using TLE data from CelesTrak.

### `wiki_utils.py`

Integrates with the Wikipedia API to fetch images and descriptions for celestial objects.

### `app_utils.py`

Contains all the Streamlit UI rendering logic, including the object tiles, sky chart section, and embedded maps.

### `download_tle_data.py`

A simple script to download the required TLE files for satellite tracking.

## 🎨 User Interface

- **Space theme**: Dark gradient backgrounds with golden accents.
- **Responsive layout**: Adapts to different screen sizes.
- **Embedded Content**: Integrates external tools like Aladin Lite and Keeptrack.space for a richer experience.