import streamlit as st
import streamlit.components.v1 as components

def aladin_lite_component(target: str, key: str = "aladin-lite-viewer", 
                         fov: float = 60, survey: str = "P/DSS2/color", 
                         height: int = 500, show_catalog: bool = True):
    """
    Embeds an Aladin Lite v3 sky atlas component in a Streamlit app.

    Uses the latest Aladin Lite v3 API with improved reliability and error handling.

    Args:
        target (str): The name of the astronomical object to view.
        key (str): A unique key for the Streamlit component.
        fov (float): Field of view in degrees (default: 60).
        survey (str): The survey to display (default: "P/DSS2/color").
        height (int): Height of the component in pixels (default: 500).
        show_catalog (bool): Whether to show catalog overlays (default: True).
    """
    
    # Sanitize the target name for JavaScript
    safe_target = target.replace('"', '\\"').replace("'", "\\'")
    
    # Create the HTML template with Aladin Lite v3
    html_template = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Aladin Lite Sky Atlas</title>
        <style>
            body {{
                margin: 0;
                padding: 0;
                font-family: Arial, sans-serif;
                background: #000;
            }}
            #aladin-lite-div {{
                width: 100%;
                height: {height}px;
                background: #000;
                border: 1px solid #333;
                border-radius: 8px;
                position: relative;
            }}
            .loading-overlay {{
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: #000;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                color: #fff;
                font-size: 16px;
                z-index: 1000;
            }}
            .error-overlay {{
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: #1a1a1a;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                color: #ff6b6b;
                font-size: 14px;
                text-align: center;
                padding: 20px;
                box-sizing: border-box;
                z-index: 1000;
            }}
            .spinner {{
                border: 3px solid #333;
                border-top: 3px solid #4dabf7;
                border-radius: 50%;
                width: 30px;
                height: 30px;
                animation: spin 1s linear infinite;
                margin-bottom: 15px;
            }}
            @keyframes spin {{
                0% {{ transform: rotate(0deg); }}
                100% {{ transform: rotate(360deg); }}
            }}
            .retry-btn {{
                background: #4dabf7;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                cursor: pointer;
                margin-top: 10px;
                font-size: 12px;
            }}
            .retry-btn:hover {{
                background: #3b9ade;
            }}
        </style>
    </head>
    <body>
        <div id="aladin-lite-div">
            <div class="loading-overlay" id="loading-overlay">
                <div class="spinner"></div>
                <div>Loading sky atlas for {safe_target}...</div>
                <div style="font-size: 12px; color: #888; margin-top: 10px;">
                    This may take a few moments
                </div>
            </div>
        </div>
        
        <script type="text/javascript" 
                src="https://aladin.cds.unistra.fr/AladinLite/api/v3/latest/js/aladin.js" 
                charset="utf-8" 
                onload="initializeAladin()" 
                onerror="handleScriptError()"></script>
        
        <script type="text/javascript">
            let aladin;
            let retryCount = 0;
            const maxRetries = 3;
            
            function showError(message, canRetry = true) {{
                const container = document.getElementById('aladin-lite-div');
                const errorDiv = document.createElement('div');
                errorDiv.className = 'error-overlay';
                errorDiv.innerHTML = `
                    <div>❌ ${{message}}</div>
                    ${{canRetry && retryCount < maxRetries - 1 ? `
                        <button class="retry-btn" onclick="retryInitialization()">
                            🔄 Try Again
                        </button>
                        <div style="font-size: 11px; margin-top: 10px; color: #666;">
                            Attempt ${{retryCount + 1}} of ${{maxRetries}}
                        </div>
                    ` : `
                        <div style="font-size: 12px; margin-top: 10px; color: #888;">
                            Please try the Local (Offline) atlas option
                        </div>
                    `}}
                `;
                container.innerHTML = '';
                container.appendChild(errorDiv);
            }}
            
            function handleScriptError() {{
                console.error('Failed to load Aladin Lite script');
                showError('Unable to load sky atlas library. Please check your internet connection.');
            }}
            
            function retryInitialization() {{
                if (retryCount < maxRetries - 1) {{
                    retryCount++;
                    location.reload();
                }} else {{
                    showError('Unable to load sky atlas after multiple attempts.', false);
                }}
            }}
            
            function initializeAladin() {{
                try {{
                    // Remove loading overlay
                    const loadingOverlay = document.getElementById('loading-overlay');
                    if (loadingOverlay) {{
                        loadingOverlay.style.display = 'none';
                    }}
                    
                    // Check if Aladin is available
                    if (typeof A === 'undefined') {{
                        throw new Error('Aladin Lite library not available');
                    }}
                    
                    // Initialize Aladin Lite
                    aladin = A.aladin('#aladin-lite-div', {{
                        survey: '{survey}',
                        fov: {fov},
                        target: '{safe_target}',
                        showReticle: true,
                        showZoomControl: true,
                        showFullscreenControl: true,
                        showLayersControl: {str(show_catalog).lower()},
                        showGoto: true,
                        showFrame: false,
                        showCooGrid: false,
                        reticleColor: '#ff0000',
                        reticleSize: 22
                    }});
                    
                    console.log('Aladin Lite initialized successfully for:', '{safe_target}');
                    
                }} catch (error) {{
                    console.error('Error initializing Aladin Lite:', error);
                    showError('Failed to initialize sky atlas: ' + error.message);
                }}
            }}
        </script>
    </body>
    </html>
    '''
    
    # Display the component
    try:
        components.html(html_template, height=height + 50, scrolling=False)
    except Exception as e:
        st.error(f"Failed to load sky atlas component: {str(e)}")
        st.info("💡 **Tip**: Try using the 'Local (Offline)' atlas option instead.")


def create_fallback_message(target: str):
    """
    Create a fallback message when Aladin Lite cannot be loaded.
    
    Args:
        target (str): The target astronomical object name.
    """
    st.error("🌐 **Online Sky Atlas Unavailable**")
    st.markdown(f"""
    The online sky atlas could not be loaded for **{target}**. This can happen due to:
    
    - **Network connectivity issues**
    - **CDN service interruptions** 
    - **Browser security restrictions**
    - **Firewall or proxy blocking**
    
    ### 💡 **Recommended Solutions:**
    
    1. **Switch to Local Atlas**: Use the "Local (Offline)" option above
    2. **Check Connection**: Ensure stable internet connectivity
    3. **Refresh Page**: Sometimes a simple refresh helps
    4. **Try Different Browser**: Some browsers have stricter security settings
    
    The Local (Offline) atlas provides excellent sky viewing without requiring internet access!
    """)
