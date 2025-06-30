#!/usr/bin/env python3
"""
Diagnostic script to test Aladin Lite connectivity and identify issues.
"""

import streamlit as st
import requests
import time

def test_connectivity():
    """Test connectivity to various Aladin Lite services."""
    st.title("🔧 Aladin Lite Connectivity Diagnostic")
    
    st.markdown("This tool tests connectivity to Aladin Lite services to help diagnose loading issues.")
    
    if st.button("🧪 Run Connectivity Tests"):
        
        # Test URLs
        test_urls = {
            "Aladin Lite Main CDN": "https://aladin.cds.unistra.fr/aladin.min.js",
            "Aladin Lite Backup CDN": "https://aladin.u-strasbg.fr/aladin.min.js",
            "jQuery CDN": "https://code.jquery.com/jquery-3.6.0.min.js",
            "CDS Server": "https://cds.unistra.fr/",
            "Alternative Aladin": "https://alasky.cds.unistra.fr/"
        }
        
        results = {}
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, (name, url) in enumerate(test_urls.items()):
            status_text.text(f"Testing {name}...")
            
            try:
                start_time = time.time()
                response = requests.get(url, timeout=10)
                end_time = time.time()
                
                if response.status_code == 200:
                    results[name] = {
                        "status": "✅ Success",
                        "response_time": f"{(end_time - start_time):.2f}s",
                        "size": f"{len(response.content)} bytes"
                    }
                else:
                    results[name] = {
                        "status": f"❌ HTTP {response.status_code}",
                        "response_time": f"{(end_time - start_time):.2f}s",
                        "size": "N/A"
                    }
            except requests.exceptions.Timeout:
                results[name] = {
                    "status": "⏰ Timeout",
                    "response_time": ">10s",
                    "size": "N/A"
                }
            except requests.exceptions.ConnectionError:
                results[name] = {
                    "status": "🚫 Connection Error",
                    "response_time": "N/A",
                    "size": "N/A"
                }
            except Exception as e:
                results[name] = {
                    "status": f"❌ Error: {str(e)[:50]}",
                    "response_time": "N/A",
                    "size": "N/A"
                }
            
            progress_bar.progress((i + 1) / len(test_urls))
        
        status_text.text("Tests completed!")
        
        # Display results
        st.subheader("📊 Test Results")
        
        for name, result in results.items():
            with st.expander(f"{result['status']} {name}"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Status", result['status'])
                with col2:
                    st.metric("Response Time", result['response_time'])
                with col3:
                    st.metric("Content Size", result['size'])
        
        # Recommendations
        st.subheader("💡 Recommendations")
        
        success_count = sum(1 for r in results.values() if "Success" in r['status'])
        
        if success_count == len(results):
            st.success("🎉 All services are accessible! Aladin Lite should work properly.")
        elif success_count >= 2:
            st.warning("⚠️ Some services are accessible. Aladin Lite might work with fallbacks.")
        else:
            st.error("🚫 Most services are inaccessible. Check your internet connection or firewall settings.")
            
        # Troubleshooting tips
        with st.expander("🔧 Troubleshooting Tips"):
            st.markdown("""
            **If you're having connection issues:**
            
            1. **Firewall/Proxy**: Corporate networks often block external astronomical databases
            2. **DNS Issues**: Try using a different DNS server (8.8.8.8, 1.1.1.1)
            3. **VPN**: Try connecting through a VPN if available
            4. **Alternative Access**: Use the external links provided in the fallback section
            5. **Browser**: Try a different browser or incognito/private mode
            6. **Extensions**: Disable ad blockers or privacy extensions temporarily
            
            **If specific CDNs fail:**
            - The app will automatically try backup URLs
            - Use the "Simple" version of the atlas in the main app
            - External links are provided as fallbacks
            """)

def simple_atlas_test():
    """Simple embedded atlas test."""
    st.subheader("🔭 Simple Atlas Test")
    
    target = st.selectbox("Test Object:", ["Sirius", "M31", "Jupiter", "Moon"])
    
    if st.button("Load Simple Atlas"):
        from aladin_simple import simple_aladin_lite_component
        simple_aladin_lite_component(target, "diagnostic-test")

def main():
    st.set_page_config(
        page_title="Aladin Lite Diagnostics",
        page_icon="🔧",
        layout="wide"
    )
    
    test_connectivity()
    st.markdown("---")
    simple_atlas_test()

if __name__ == "__main__":
    main()
