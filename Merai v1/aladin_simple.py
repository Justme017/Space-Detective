import streamlit as st
import streamlit.components.v1 as components

def simple_aladin_lite_component(target: str, key: str = "simple-aladin-viewer"):
    """
    A simplified Aladin Lite component with better error handling and fallback options.
    
    Args:
        target (str): The name of the astronomical object to view
        key (str): Unique key for the component
    """
    
    # Sanitize target name
    safe_target = target.replace('"', '\\"').replace("'", "\\'")
    
    # Simple HTML with embedded Aladin Lite
    html_content = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Aladin Lite - {safe_target}</title>
        <style>
            body {{ margin: 0; padding: 0; background: #000; font-family: Arial, sans-serif; }}
            #aladin-div {{ width: 100%; height: 500px; background: #000; border: 1px solid #333; }}
            .status {{ 
                position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); 
                color: white; text-align: center; z-index: 999; 
            }}
            .error {{ color: #ff6b6b; }}
            .success {{ color: #51cf66; }}
        </style>
    </head>
    <body>
        <div id="aladin-div">
            <div id="status" class="status">🔭 Loading Aladin Lite...</div>
        </div>
        
        <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
        <script>
            // Fallback if jQuery doesn't load
            if (typeof jQuery === 'undefined') {{
                document.getElementById('status').innerHTML = '❌ Unable to load required libraries';
                document.getElementById('status').className = 'status error';
            }} else {{
                // Try to load Aladin
                $.getScript('https://aladin.cds.unistra.fr/aladin.min.js')
                .done(function() {{
                    console.log('Aladin script loaded successfully');
                    initAladin();
                }})
                .fail(function() {{
                    console.log('Primary Aladin URL failed, trying backup...');
                    $.getScript('https://aladin.u-strasbg.fr/aladin.min.js')
                    .done(function() {{
                        console.log('Aladin backup script loaded');
                        initAladin();
                    }})
                    .fail(function() {{
                        console.log('All Aladin URLs failed');
                        showFallback();
                    }});
                }});
            }}
            
            function initAladin() {{
                try {{
                    if (typeof A === 'undefined') {{
                        throw new Error('Aladin library not available');
                    }}
                    
                    var aladin = A.aladin('#aladin-div', {{
                        target: "{safe_target}",
                        fov: 60,
                        survey: "P/DSS2/color",
                        showReticle: true,
                        showZoomControl: true,
                        showGotoControl: true
                    }});
                    
                    aladin.on('ready', function() {{
                        document.getElementById('status').style.display = 'none';
                        console.log('Aladin ready for target: {safe_target}');
                    }});
                    
                    aladin.on('error', function(error) {{
                        console.error('Aladin error:', error);
                        document.getElementById('status').innerHTML = '⚠️ Could not load sky data for {safe_target}';
                        document.getElementById('status').className = 'status error';
                    }});
                    
                }} catch (error) {{
                    console.error('Init error:', error);
                    showFallback();
                }}
            }}
            
            function showFallback() {{
                document.getElementById('status').innerHTML = 
                    '🌌 Sky Atlas Unavailable<br><br>' +
                    '📍 Target: {safe_target}<br>' +
                    '🔗 <a href="https://aladin.cds.unistra.fr/aladin.gml?target={safe_target}" target="_blank" style="color: #4dabf7;">View in full Aladin Lite</a>';
                document.getElementById('status').className = 'status error';
            }}
        </script>
    </body>
    </html>
    '''
    
    # Display the component
    components.html(html_content, height=520, scrolling=False)


def create_fallback_sky_info(target: str):
    """
    Create a fallback information panel when Aladin Lite fails to load.
    """
    st.error("🌌 Interactive Sky Atlas Unavailable")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown(f"""
        **🎯 Target Object:** {target}
        
        **Alternative Options:**
        - [View in Aladin Lite (External)]({f"https://aladin.cds.unistra.fr/aladin.gml?target={target.replace(' ', '%20')}"})
        - [SIMBAD Database]({f"http://simbad.u-strasbg.fr/simbad/sim-basic?Ident={target.replace(' ', '+')}"})
        - [NASA/IPAC Database]({f"https://ned.ipac.caltech.edu/byname?objname={target.replace(' ', '+')}"})
        """)
    
    with col2:
        st.info("""
        **🔧 Troubleshooting:**
        - Check your internet connection
        - Try refreshing the page
        - Some corporate firewalls block external astronomical databases
        - The service may be temporarily unavailable
        """)

# Main function with fallback
def robust_aladin_component(target: str, key: str = "robust-aladin", **kwargs):
    """
    Robust Aladin component with fallback options.
    """
    try:
        # Try the simple version first
        simple_aladin_lite_component(target, key)
        
        # Add a fallback info section
        with st.expander("🆘 If the sky atlas doesn't load...", expanded=False):
            create_fallback_sky_info(target)
            
    except Exception as e:
        st.error(f"Error loading sky atlas: {str(e)}")
        create_fallback_sky_info(target)
