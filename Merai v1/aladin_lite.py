import streamlit as st
import streamlit.components.v1 as components

def aladin_lite_component(target: str, key: str = "aladin-lite-viewer", 
                         fov: float = 60, survey: str = "P/DSS2/color", 
                         height: int = 500, show_catalog: bool = True):
    """
    Embeds a simple and reliable Aladin Lite sky atlas component.
    
    Uses the most basic, proven Aladin Lite v2 implementation that works consistently.
    """
    
    # Sanitize the target name for JavaScript
    safe_target = target.replace('"', '\\"').replace("'", "\\'")
    
    # Ultra-simple Aladin Lite implementation - just the basics that work
    html_template = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <script src="https://code.jquery.com/jquery-1.12.1.min.js"></script>
        <script src="https://aladin.u-strasbg.fr/AladinLite/api/v2/latest/js/aladin.min.js"></script>
        <style>
            #aladin-lite-div {{
                width: 100%;
                height: {height}px;
                background: #000;
                border: 1px solid #333;
                border-radius: 8px;
            }}
            .error-msg {{
                color: #ff6b6b;
                text-align: center;
                padding: 20px;
                background: #000;
                border-radius: 8px;
            }}
        </style>
    </head>
    <body>
        <div id="aladin-lite-div"></div>
        <script>
            $(document).ready(function() {{
                try {{
                    var aladin = A.aladin('#aladin-lite-div', {{
                        survey: "{survey}",
                        fov: {fov},
                        target: "{safe_target}",
                        showReticle: true,
                        showZoomControl: true
                    }});
                }} catch (e) {{
                    document.getElementById('aladin-lite-div').innerHTML = 
                        '<div class="error-msg">❌ Sky atlas unavailable<br><small>Use Local atlas instead</small></div>';
                }}
            }});
        </script>
    </body>
    </html>
    '''
    
    # Display the component
    components.html(html_template, height=height + 20, scrolling=False)


def create_fallback_message(target: str):
    """
    Create a fallback message when Aladin Lite cannot be loaded.
    """
    st.error("🌐 **Online Sky Atlas Unavailable**")
    st.info(f"💡 **Try the Local (Offline) atlas** for reliable sky viewing of **{target}**!")
