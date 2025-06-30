import streamlit as st
import streamlit.components.v1 as components

st.title("Space Detective - Live User Location")

# Initialize session state
if 'location_fetched' not in st.session_state:
    st.session_state.location_fetched = False

if st.button("🌍 Get My Location", type="primary"):
    st.session_state.location_fetched = True

if st.session_state.location_fetched:
    # Embed your Vercel geolocation service
    components.html("""
    <iframe 
        src="https://geolocation-page.vercel.app/" 
        width="100%" 
        height="400" 
        style="border: 2px solid #ddd; border-radius: 10px;">
    </iframe>
    """, height=450)
    
    if st.button("🔄 Try Again"):
        st.session_state.location_fetched = False
        st.rerun()

else:
    st.info("""
    📍 **How it works:**
    1. Click the "Get My Location" button above
    2. Allow location access when your browser asks
    3. Your coordinates will be displayed
    
    ⚠️ **Note:** Location access requires HTTPS and user permission.
    """)