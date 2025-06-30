"""
Version information for Merai - A Space Detective
"""

__version__ = "2.0.0"
__release_name__ = "Live App Release"
__release_date__ = "2025-06-30"
__status__ = "Production"

# Version components
VERSION_MAJOR = 2
VERSION_MINOR = 0
VERSION_PATCH = 0

# Release information
RELEASE_NOTES_URL = "https://github.com/your-username/Space-Detective-1/releases/tag/v2.0.0"
APP_URL = "https://your-space-detective-app.streamlit.app"

def get_version_string():
    """Get formatted version string."""
    return f"v{__version__} - {__release_name__}"

def get_full_version_info():
    """Get complete version information."""
    return {
        "version": __version__,
        "release_name": __release_name__,
        "release_date": __release_date__,
        "status": __status__,
        "major": VERSION_MAJOR,
        "minor": VERSION_MINOR,
        "patch": VERSION_PATCH
    }
