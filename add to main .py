import streamlit as st
import streamlit.components.v1 as components
from streamlit_javascript import st_javascript

st.title("Space Detective - Live User Location")

# Initialize session state
if 'location_data' not in st.session_state:
    st.session_state.location_data = None

if st.button("🌍 Get My Location", type="primary"):
    with st.spinner("Getting your location..."):
        # Use your Vercel service to get location
        location = st_javascript("""
        () => {
            return new Promise((resolve) => {
                const iframe = document.createElement('iframe');
                iframe.src = 'https://geolocation-page.vercel.app/';
                iframe.style.display = 'none';
                
                const messageHandler = (event) => {
                    if (event.origin === 'https://geolocation-page.vercel.app') {
                        window.removeEventListener('message', messageHandler);
                        document.body.removeChild(iframe);
                        resolve(event.data);
                    }
                };
                
                window.addEventListener('message', messageHandler);
                document.body.appendChild(iframe);
                
                setTimeout(() => {
                    window.removeEventListener('message', messageHandler);
                    if (document.body.contains(iframe)) {
                        document.body.removeChild(iframe);
                    }
                    resolve({error: 'Timeout'});
                }, 15000);
            });
        }
        """, key="location_request")
        
        if location:
            st.session_state.location_data = location
            st.rerun()

# Display results
if st.session_state.location_data:
    location = st.session_state.location_data
    
    if "error" in location:
        st.error(f"❌ Error: {location['error']}")
        st.info("💡 Please allow location access and try again")
    else:
        st.success("✅ Location detected successfully!")
        
        # Display location details
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📍 Latitude", f"{location['latitude']:.6f}")
        with col2:
            st.metric("📍 Longitude", f"{location['longitude']:.6f}")
        with col3:
            st.metric("🎯 Accuracy", f"{location.get('accuracy', 0):.0f}m")
        
        # Show coordinates
        st.info(f"🗺️ **Coordinates:** ({location['latitude']:.4f}, {location['longitude']:.4f})")
        
        # Show on map
        st.subheader("📍 Your Location on Map")
        st.map([{
            "lat": location['latitude'], 
            "lon": location['longitude']
        }])
    
    # Reset button
    if st.button("🔄 Get Location Again"):
        st.session_state.location_data = None
        st.rerun()

else:
    st.info("""
    📍 **How it works:**
    1. Click the "Get My Location" button above
    2. Allow location access when your browser asks
    3. Your accurate coordinates will be displayed with a map
    
    ⚠️ **Note:** This uses browser geolocation for maximum accuracy.
    """)