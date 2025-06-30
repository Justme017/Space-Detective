import streamlit as st
import streamlit.components.v1 as components
import json

def aladin_lite_component(target: str, key: str = "aladin-lite-viewer", 
                         fov: float = 60, survey: str = "P/DSS2/color", 
                         height: int = 500, show_catalog: bool = True):
    """
    Embeds an Aladin Lite sky atlas component in a Streamlit app using the official API.

    This component creates a stable container for the Aladin Lite instance and uses
    the official JavaScript API to manage the view. It supports various configuration
    options and handles object targeting efficiently.

    Args:
        target (str): The name of the astronomical object to view (e.g., "M31", "Mars", "Sirius").
        key (str): A unique and stable key for the Streamlit component.
        fov (float): Field of view in degrees (default: 60).
        survey (str): The survey to display (default: "P/DSS2/color").
        height (int): Height of the component in pixels (default: 500).
        show_catalog (bool): Whether to show catalog overlays (default: True).
    """
    
    # Sanitize the target name for JavaScript
    safe_target = target.replace('"', '\\"').replace("'", "\\'")
    
    # Create the HTML template with the official Aladin Lite API
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
                overflow: hidden;
                position: relative;
            }}
            .aladin-info {{
                position: absolute;
                top: 10px;
                left: 10px;
                background: rgba(0, 0, 0, 0.8);
                color: #fff;
                padding: 8px 12px;
                border-radius: 4px;
                font-size: 12px;
                z-index: 1000;
            }}
            .aladin-loading {{
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                color: #fff;
                font-size: 16px;
                z-index: 999;
                text-align: center;
            }}
            .aladin-error {{
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                color: #ff6b6b;
                font-size: 14px;
                z-index: 999;
                text-align: center;
                max-width: 80%;
            }}
        </style>
    </head>
    <body>
        <div id="aladin-lite-div">
            <div class="aladin-loading" id="loading-indicator">
                🔭 Loading sky atlas for {safe_target}...
            </div>
            <div class="aladin-info" id="target-info" style="display: none;">
                Target: {safe_target}
            </div>
        </div>
        
        <!-- Try multiple CDN sources for jQuery -->
        <script src="https://code.jquery.com/jquery-3.6.0.min.js" 
                onerror="this.onerror=null; this.src='https://ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js'"></script>
        
        <!-- Try multiple sources for Aladin Lite -->
        <script>
        // Function to load Aladin Lite with fallback URLs
        function loadAladinScript() {{
            const aladinUrls = [
                'https://aladin.cds.unistra.fr/aladin.min.js',
                'https://aladin.u-strasbg.fr/aladin.min.js',
                'https://alasky.cds.unistra.fr/aladin.min.js'
            ];
            
            let currentUrlIndex = 0;
            
            function tryLoadScript() {{
                if (currentUrlIndex >= aladinUrls.length) {{
                    showError('Unable to load Aladin Lite from any CDN. Please check your internet connection.');
                    return;
                }}
                
                const script = document.createElement('script');
                script.src = aladinUrls[currentUrlIndex];
                
                script.onload = function() {{
                    console.log('Aladin Lite loaded from:', aladinUrls[currentUrlIndex]);
                    initAladin();
                }};
                
                script.onerror = function() {{
                    console.warn('Failed to load from:', aladinUrls[currentUrlIndex]);
                    currentUrlIndex++;
                    tryLoadScript();
                }};
                
                document.head.appendChild(script);
            }}
            
            tryLoadScript();
        }}
        
        function showError(message) {{
            const loadingEl = document.getElementById('loading-indicator');
            if (loadingEl) {{
                loadingEl.className = 'aladin-error';
                loadingEl.innerHTML = '❌ ' + message + '<br><br>🔄 <a href="#" onclick="location.reload()" style="color: #4dabf7;">Click to retry</a>';
            }}
        }}
        </script>
        
        <script type="text/javascript">
            let aladin;
            let initializationTimeout;
            
            // Function to initialize Aladin Lite with better error handling
            function initAladin() {{
                // Clear any existing timeout
                if (initializationTimeout) {{
                    clearTimeout(initializationTimeout);
                }}
                
                // Set a timeout for initialization
                initializationTimeout = setTimeout(function() {{
                    showError('Aladin Lite initialization timed out. The service may be temporarily unavailable.');
                }}, 15000); // 15 second timeout
                
                try {{
                    console.log("Initializing Aladin Lite...");
                    
                    // Check if A (Aladin) is available
                    if (typeof A === 'undefined') {{
                        throw new Error('Aladin Lite library not loaded');
                    }}
                    
                    // Configuration options - simplified for better compatibility
                    const aladinConfig = {{
                        target: "{safe_target}",
                        fov: {fov},
                        survey: "{survey}",
                        showReticle: true,
                        showZoomControl: true,
                        showFullscreenControl: false,
                        showLayersControl: true,
                        showGotoControl: true,
                        showShareControl: false,
                        showFrame: true,
                        showCooGrid: false,
                        fullScreen: false,
                        reticleColor: "#ff0000",
                        reticleSize: 22
                    }};
                    
                    console.log("Aladin config:", aladinConfig);
                    
                    // Initialize Aladin Lite
                    aladin = A.aladin('#aladin-lite-div', aladinConfig);
                    
                    // Set up event handlers
                    aladin.on('ready', function() {{
                        console.log("Aladin Lite is ready");
                        clearTimeout(initializationTimeout);
                        
                        // Hide loading indicator
                        const loadingEl = document.getElementById('loading-indicator');
                        if (loadingEl) loadingEl.style.display = 'none';
                        
                        // Show target info
                        const targetEl = document.getElementById('target-info');
                        if (targetEl) targetEl.style.display = 'block';
                        
                        // Go to target object
                        setTimeout(function() {{
                            gotoTarget("{safe_target}");
                        }}, 500);
                        
                        // Add catalog layers if enabled (simplified)
                        if ({str(show_catalog).lower()}) {{
                            setTimeout(function() {{
                                try {{
                                    // Add basic star catalog
                                    const hipCat = A.catalogFromURL('https://alasky.cds.unistra.fr/cats/I/239/hip_main', 
                                        {{name: 'Bright Stars', color: '#ffa500', sourceSize: 8}});
                                    if (hipCat) {{
                                        aladin.addCatalog(hipCat);
                                    }}
                                }} catch (catError) {{
                                    console.log("Could not load star catalog:", catError);
                                }}
                            }}, 1000);
                        }}
                    }});
                    
                    aladin.on('error', function(error) {{
                        console.error("Aladin Lite error:", error);
                        clearTimeout(initializationTimeout);
                        showError('Error loading sky survey data. The target object may not be found in the current survey.');
                    }});
                    
                }} catch (error) {{
                    console.error("Failed to initialize Aladin Lite:", error);
                    clearTimeout(initializationTimeout);
                    showError('Failed to initialize sky atlas: ' + error.message);
                }}
            }}
            
            // Function to go to a specific target with better error handling
            function gotoTarget(targetName) {{
                if (!aladin || !targetName) {{
                    console.warn("Aladin not ready or no target specified");
                    return;
                }}
                
                try {{
                    console.log("Going to target:", targetName);
                    aladin.gotoObject(targetName);
                    
                    // Update target info
                    const targetEl = document.getElementById('target-info');
                    if (targetEl) {{
                        targetEl.innerHTML = `Target: ${{targetName}}`;
                    }}
                    
                }} catch (error) {{
                    console.error("Error going to target:", error);
                    
                    // Try fallback - go to center of sky
                    try {{
                        console.log("Trying fallback coordinates...");
                        aladin.gotoRaDec(0, 0);
                    }} catch (fallbackError) {{
                        console.error("Fallback also failed:", fallbackError);
                    }}
                }}
            }}
            
            // Initialize when DOM and scripts are ready
            $(document).ready(function() {{
                console.log("DOM ready, checking for Aladin...");
                
                // Check if jQuery loaded
                if (typeof $ === 'undefined') {{
                    showError('jQuery failed to load. Please check your internet connection.');
                    return;
                }}
                
                // Try to load Aladin if not already loaded
                if (typeof A === 'undefined') {{
                    console.log("Aladin not found, attempting to load...");
                    loadAladinScript();
                }} else {{
                    console.log("Aladin already available, initializing...");
                    setTimeout(initAladin, 100);
                }}
            }});
            
            // Handle window resize
            $(window).resize(function() {{
                if (aladin && aladin.view) {{
                    try {{
                        aladin.view.requestRedraw();
                    }} catch (error) {{
                        console.log("Resize redraw failed:", error);
                    }}
                }}
            }});
            
        </script>
    </body>
    </html>
    '''
    
    # Embed the component in Streamlit
    components.html(html_template, height=height + 40, scrolling=False)

