# Merai - A Space Detective 🔭

A beautiful and interactive Streamlit web application for exploring visible astronomical objects from any location and time. Discover planets, stars, and celestial objects with detailed information and an interactive sky chart.

## ✨ Features

- **🌍 Location Detection**: Automatic location detection or manual selection on an interactive map
- **🕒 Custom Date/Time**: View the sky from any date and time
- **⭐ Celestial Objects**: Display visible planets, stars, and other astronomical objects
- **📖 Rich Information**: Detailed descriptions and images from Wikipedia
- **🌟 Interactive Sky Chart**: Visual representation of the night sky with zoom controls
- **🎨 Beautiful UI**: Space-themed design with responsive layout
- **✨ Constellation Mapping**: Star objects mapped to their constellations

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher
- Internet connection (for API calls)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/Justme017/Space-Detective
cd "Space-Detective-1/Merai v1"
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. **Run the application**
   ```bash
   cd "Merai v1"
   streamlit run main.py
   ```

4. **Open your browser** to `http://localhost:8501` and start exploring!

## 📁 Project Structure

```
Merai v1/
├── main.py                 # Main Streamlit application
├── astro_utils.py          # Astronomical calculations and object detection
├── wiki_utils.py           # Wikipedia API integration
├── location_utils.py       # Location detection utilities
├── constellation_utils.py  # Constellation mapping
├── skychart_utils.py       # Sky chart generation
├── requirements.txt        # Python dependencies
├── de421.bsp              # JPL planetary ephemeris data
├── hip_main.dat           # Hipparcos star catalog
├── hygdata_v41.csv        # HYG star database
└── test_imports.py        # Import verification script
```

## 🛠️ Core Modules

### `main.py`
The main application built with Streamlit, organized as a class-based architecture:

- **MeraiApp**: Main application class with modular methods
- **Location handling**: Automatic detection and manual map selection  
- **Object enhancement**: Enriches astronomical data with Wikipedia content
- **Interactive UI**: Beautiful space-themed interface with responsive design

### `astro_utils.py`
Handles astronomical calculations using Skyfield:

- **Planetary positions**: Calculates positions of planets, sun, and moon
- **Star visibility**: Processes Hipparcos catalog for bright stars
- **Coordinate conversion**: Converts celestial coordinates to altitude/azimuth
- **Robust error handling**: Gracefully handles data processing errors

### `wiki_utils.py`
Integrates with Wikipedia API for rich content:

- **Image fetching**: Gets object images from Wikipedia
- **Description extraction**: Retrieves and cleans object descriptions
- **Name parsing**: Extracts common names from descriptions

### `location_utils.py`
Provides location detection capabilities:

- **IP-based geolocation**: Automatic location detection using geocoder
- **Datetime utilities**: UTC timezone handling

### `constellation_utils.py`
Maps stars to their constellations:

- **HYG database processing**: Loads star-constellation mappings
- **Constellation names**: Full constellation names from abbreviations

## 🎨 User Interface

### Design Features
- **Space theme**: Dark gradient backgrounds with golden accents
- **Responsive layout**: Adapts to different screen sizes
- **Interactive elements**: Hover effects and smooth transitions
- **Visual feedback**: Loading spinners and status messages
- **Accessible design**: Clear typography and color contrast

### Key Sections
1. **Location Selection**: Choose between auto-detection or map selection
2. **Date/Time Picker**: Set observation time with intuitive controls
3. **Object Tiles**: Beautiful cards showing astronomical objects
4. **Sky Chart**: Interactive visualization of the night sky

## 🔌 APIs Used

### Public APIs (No Authentication Required)
- **Wikipedia REST API**: Object descriptions and images
- **IP Geolocation**: Automatic location detection via geocoder

### Data Sources
- **NASA JPL DE421**: Planetary position data
- **Hipparcos Catalog**: Star positions and brightness
- **HYG Database**: Star-constellation mappings

## ⚙️ Configuration

### Constants (in main.py)
```python
MAX_DESC_LEN = 120      # Maximum description length in tiles
TILE_HEIGHT = 550       # Height of object tiles in pixels
ZOOM_LEVELS = [0.7, 1.0, 1.3, 1.6, 2.0]  # Available zoom levels
```

### Data Files
- `de421.bsp`: JPL planetary ephemeris (required)
- `hip_main.dat`: Hipparcos star catalog (required)
- `hygdata_v41.csv`: HYG star database with constellations (optional)

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **NASA JPL**: Planetary ephemeris data
- **ESA Hipparcos**: Star catalog data
- **Wikipedia**: Object descriptions and images
- **Streamlit**: Web application framework
- **Skyfield**: Astronomical calculations

## 🐛 Bug Reports

If you encounter any issues, please check the troubleshooting section above or create an issue with:
- Python version
- Operating system
- Error message (if any)
- Steps to reproduce

---

**Built with ❤️ using Python, Streamlit, and Skyfield**