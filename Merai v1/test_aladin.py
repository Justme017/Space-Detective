#!/usr/bin/env python3
"""
Simple test script for the Aladin Lite integration.
Run this to test the Aladin Lite component independently.
"""

import streamlit as st
from aladin_lite import aladin_lite_component

def main():
    st.set_page_config(
        page_title="Aladin Lite Test",
        page_icon="🔭",
        layout="wide"
    )
    
    st.title("🔭 Aladin Lite Integration Test")
    st.markdown("This is a simple test of the Aladin Lite sky atlas component.")
    
    # Test objects
    test_objects = [
        "M31",      # Andromeda Galaxy
        "M42",      # Orion Nebula
        "Sirius",   # Brightest star
        "Jupiter",  # Planet
        "Moon",     # Moon
        "Vega",     # Bright star
        "M13",      # Hercules Globular Cluster
        "NGC 7000"  # North America Nebula
    ]
    
    st.subheader("Select a test object:")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        selected_object = st.selectbox(
            "Choose an object to view:",
            options=test_objects,
            index=0
        )
    
    with col2:
        fov = st.slider(
            "Field of View (degrees)",
            min_value=1.0,
            max_value=180.0,
            value=60.0,
            step=5.0
        )
    
    with col3:
        survey_options = {
            "DSS2 Color": "P/DSS2/color",
            "DSS2 Red": "P/DSS2/red",
            "2MASS J": "P/2MASS/J"
        }
        
        survey_name = st.selectbox(
            "Survey",
            options=list(survey_options.keys()),
            index=0
        )
        survey = survey_options[survey_name]
    
    st.info(f"🎯 Viewing: **{selected_object}** | Survey: **{survey_name}** | FOV: **{fov}°**")
    
    # Test the Aladin Lite component
    aladin_lite_component(
        target=selected_object,
        key="test-aladin-viewer",
        fov=fov,
        survey=survey,
        height=500,
        show_catalog=True
    )
    
    st.markdown("""
    ### 🔍 Instructions:
    - Use the mouse wheel to zoom in and out
    - Click and drag to pan around the sky
    - Try different objects and surveys from the dropdowns above
    - The component should update smoothly without reloading
    """)

if __name__ == "__main__":
    main()
