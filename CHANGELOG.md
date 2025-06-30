# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-06-30 - "Live App Release"

### 🚀 Major Release - Production Ready

### Added
- **Interactive Sky Atlas**: Multiple viewing modes (Local Offline & Online Aladin Lite)
- **Enhanced Location Detection**: Multi-service location detection with smart fallbacks
- **Streamlit Cloud Optimization**: Ready for cloud deployment with proper file structure
- **Robust Error Handling**: Comprehensive fallback systems and user-friendly error messages
- **Modern UI/UX**: Improved interface with better responsiveness and visual design
- **Professional Documentation**: Complete deployment and troubleshooting guides

### Changed
- **Complete Code Refactor**: Modular architecture with separate utility modules
- **Improved Location Services**: Multiple geocoding APIs with automatic fallback
- **Streamlined Dependencies**: Optimized requirements.txt for cloud deployment
- **Enhanced Sky Visualization**: Better rendering and interactive features

### Fixed
- **Location Detection Issues**: Resolved automatic location detection failures
- **Cloud Deployment**: Fixed Streamlit Cloud compatibility issues
- **Image Rendering**: All images now use proper container width
- **Error Handling**: Better user feedback for network and API issues

### Removed
- **Unnecessary Files**: Cleaned up Docker, Heroku configs, and test files
- **Simple Online Atlas**: Removed redundant atlas option for better UX
- **Development Dependencies**: Removed dev-only packages and cache files

## [1.0.1] - 2025-06-15

### Changed
- Improved map integration and functionality, including automatic location detection.
- Enhanced star information with constellation data from `hygdata_v41.csv`.

## [1.0.0] - 2025-06-14

### Added
- Locates user to provide location-specific astronomical data.
- Date and time input, allowing users to see the cosmos at any specified time and year.
- Integration of the Hipparcos catalogue for star data.

### Fixed

- Various bug fixes to improve stability and accuracy.
