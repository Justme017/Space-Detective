#!/usr/bin/env python3
"""
Test script for the Local Sky Atlas - works completely offline!
"""

import streamlit as st
from local_sky_atlas import local_sky_atlas_component

def main():
    st.set_page_config(
        page_title="Local Sky Atlas Test",
        page_icon="🌌",
        layout="wide"
    )
    
    st.title("🌌 Local Sky Atlas Test")
    st.markdown("*This sky atlas works completely offline - no internet required!*")
    
    st.success("✅ **Perfect for localhost development!** No CDN dependencies or internet connection needed.")
    
    # Test objects that are included in the local catalog
    test_objects = [
        "Sirius",    # Brightest star
        "Vega",      # Summer star
        "Mars",      # Red planet
        "Jupiter",   # Giant planet
        "M31",       # Andromeda Galaxy
        "M42",       # Orion Nebula
        "Betelgeuse", # Red giant
        "Rigel",     # Blue giant
        "Altair",    # Summer triangle
        "Antares",   # Red supergiant
        "Fomalhaut", # Autumn star
        "Deneb"      # Distant supergiant
    ]
    
    st.subheader("🎯 Select a Test Object:")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        selected_object = st.selectbox(
            "Choose an object to view:",
            options=test_objects,
            index=0,
            help="All these objects are included in the local star catalog"
        )
    
    with col2:
        st.metric("Test Status", "🟢 Ready", help="Local atlas is always ready - no internet needed!")
    
    # Display the local sky atlas
    local_sky_atlas_component(target=selected_object, key="test-local-atlas")
    
    # Show benefits of local atlas
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.success("""
        **✅ Offline Benefits:**
        - No internet required
        - No CDN dependencies  
        - Works on localhost
        - Fast loading
        - No external requests
        """)
    
    with col2:
        st.info("""
        **🎯 Features:**
        - Interactive zoom/pan
        - Target highlighting
        - Coordinate display
        - Object information
        - Bright star catalog
        """)
    
    with col3:
        st.warning("""
        **⚠️ Limitations:**
        - Simplified star catalog
        - Approximate positions
        - Limited deep-sky objects
        - No live survey data
        - Static planet positions
        """)
    
    # Instructions
    with st.expander("📖 How to Use", expanded=True):
        st.markdown("""
        ### 🎮 **Interactive Controls:**
        
        **Mouse Navigation:**
        - **Click and drag** → Pan around the sky
        - **Mouse wheel** → Zoom in/out
        - **Hover** → See coordinates
        
        **Button Controls:**
        - **🔍 Zoom In/Out** → Precise zoom control
        - **🏠 Reset** → Return to original view  
        - **📐 Grid** → Toggle coordinate grid
        
        **Visual Elements:**
        - **🔴 Red circle** → Your selected target
        - **⚪ White dots** → Bright stars
        - **🟡 Yellow dots** → Planets
        - **🟣 Purple dots** → Deep-sky objects
        - **📏 Grid lines** → RA/Dec coordinates
        
        ### 💡 **Tips:**
        - Zoom in to see object labels
        - Use the grid to understand coordinates
        - Pan around to explore the entire sky
        - Try different targets to see their positions
        """)

if __name__ == "__main__":
    main()
