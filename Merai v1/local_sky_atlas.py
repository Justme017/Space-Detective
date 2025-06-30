import streamlit as st
import streamlit.components.v1 as components
import base64

def offline_sky_atlas_component(target: str, key: str = "offline-sky-atlas"):
    """
    Creates an offline-capable sky atlas component that works without external CDNs.
    Uses a simple star map visualization that works entirely locally.
    
    Args:
        target (str): The astronomical object name
        key (str): Unique component key
    """
    
    # Create a simple local sky map using HTML5 Canvas and basic astronomy
    html_content = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Local Sky Atlas - {target}</title>
        <style>
            body {{
                margin: 0;
                padding: 0;
                background: #000;
                font-family: Arial, sans-serif;
                color: white;
            }}
            #sky-container {{
                width: 100%;
                height: 500px;
                position: relative;
                background: radial-gradient(circle, #001122 0%, #000000 100%);
                border: 2px solid #333;
                border-radius: 8px;
                overflow: hidden;
            }}
            #sky-canvas {{
                width: 100%;
                height: 100%;
                cursor: crosshair;
            }}
            .sky-info {{
                position: absolute;
                top: 10px;
                left: 10px;
                background: rgba(0, 0, 0, 0.8);
                padding: 10px;
                border-radius: 5px;
                font-size: 14px;
                z-index: 100;
            }}
            .sky-controls {{
                position: absolute;
                top: 10px;
                right: 10px;
                background: rgba(0, 0, 0, 0.8);
                padding: 10px;
                border-radius: 5px;
                z-index: 100;
            }}
            .control-btn {{
                background: #333;
                color: white;
                border: 1px solid #555;
                padding: 5px 10px;
                margin: 2px;
                border-radius: 3px;
                cursor: pointer;
                font-size: 12px;
            }}
            .control-btn:hover {{
                background: #555;
            }}
            .target-highlight {{
                position: absolute;
                width: 20px;
                height: 20px;
                border: 2px solid #ff0000;
                border-radius: 50%;
                pointer-events: none;
                z-index: 50;
            }}
        </style>
    </head>
    <body>
        <div id="sky-container">
            <canvas id="sky-canvas" width="800" height="500"></canvas>
            
            <div class="sky-info">
                <strong>🎯 Target: {target}</strong><br>
                <span id="coordinates">RA: --h --m, Dec: --° --'</span><br>
                <span id="mouse-coords">Mouse: --, --</span>
            </div>
            
            <div class="sky-controls">
                <button class="control-btn" onclick="zoomIn()">🔍 Zoom In</button>
                <button class="control-btn" onclick="zoomOut()">🔍 Zoom Out</button><br>
                <button class="control-btn" onclick="resetView()">🏠 Reset</button>
                <button class="control-btn" onclick="toggleGrid()">📐 Grid</button>
            </div>
            
            <div id="target-marker" class="target-highlight" style="display: none;"></div>
        </div>

        <script>
            const canvas = document.getElementById('sky-canvas');
            const ctx = canvas.getContext('2d');
            let zoom = 1;
            let offsetX = 0;
            let offsetY = 0;
            let showGrid = true;
            let targetFound = false;
            
            // Simple star catalog (bright stars with approximate coordinates)
            const brightStars = [
                {{name: 'Sirius', ra: 101.3, dec: -16.7, mag: -1.46, color: '#ffffff'}},
                {{name: 'Canopus', ra: 95.9, dec: -52.7, mag: -0.74, color: '#fff8dc'}},
                {{name: 'Arcturus', ra: 213.9, dec: 19.2, mag: -0.05, color: '#ffb347'}},
                {{name: 'Vega', ra: 279.2, dec: 38.8, mag: 0.03, color: '#ffffff'}},
                {{name: 'Capella', ra: 79.2, dec: 45.9, mag: 0.08, color: '#fff8dc'}},
                {{name: 'Rigel', ra: 78.6, dec: -8.2, mag: 0.13, color: '#b0e0e6'}},
                {{name: 'Procyon', ra: 114.8, dec: 5.2, mag: 0.34, color: '#fff8dc'}},
                {{name: 'Betelgeuse', ra: 88.8, dec: 7.4, mag: 0.50, color: '#ff6347'}},
                {{name: 'Achernar', ra: 24.6, dec: -57.2, mag: 0.46, color: '#b0e0e6'}},
                {{name: 'Altair', ra: 297.7, dec: 8.9, mag: 0.77, color: '#ffffff'}},
                {{name: 'Aldebaran', ra: 68.9, dec: 16.5, mag: 0.85, color: '#ff6347'}},
                {{name: 'Antares', ra: 247.4, dec: -26.4, mag: 1.09, color: '#ff0000'}},
                {{name: 'Spica', ra: 201.3, dec: -11.2, mag: 1.04, color: '#b0e0e6'}},
                {{name: 'Pollux', ra: 116.3, dec: 28.0, mag: 1.14, color: '#ffb347'}},
                {{name: 'Fomalhaut', ra: 344.4, dec: -29.6, mag: 1.16, color: '#ffffff'}},
                {{name: 'Deneb', ra: 310.4, dec: 45.3, mag: 1.25, color: '#ffffff'}},
                {{name: 'Regulus', ra: 152.1, dec: 11.9, mag: 1.35, color: '#b0e0e6'}}
            ];
            
            // Planets (simplified positions - in reality these change)
            const planets = [
                {{name: 'Mars', ra: 45.0, dec: 15.0, mag: 0.5, color: '#ff4500'}},
                {{name: 'Jupiter', ra: 180.0, dec: -5.0, mag: -2.0, color: '#ffd700'}},
                {{name: 'Saturn', ra: 270.0, dec: 20.0, mag: 0.8, color: '#faf0e6'}},
                {{name: 'Venus', ra: 30.0, dec: 10.0, mag: -4.0, color: '#ffd700'}}
            ];
            
            // Messier objects (simplified)
            const messierObjects = [
                {{name: 'M31', ra: 10.7, dec: 41.3, mag: 3.4, color: '#dda0dd'}},
                {{name: 'M42', ra: 83.8, dec: -5.4, mag: 4.0, color: '#ff69b4'}},
                {{name: 'M13', ra: 250.4, dec: 36.5, mag: 5.8, color: '#dda0dd'}},
                {{name: 'M57', ra: 283.4, dec: 33.0, mag: 8.8, color: '#00ffff'}}
            ];
            
            function drawSky() {{
                // Clear canvas
                ctx.fillStyle = '#000011';
                ctx.fillRect(0, 0, canvas.width, canvas.height);
                
                // Draw coordinate grid
                if (showGrid) {{
                    drawGrid();
                }}
                
                // Draw stars
                brightStars.forEach(star => {{
                    drawCelestialObject(star, 3);
                }});
                
                // Draw planets
                planets.forEach(planet => {{
                    drawCelestialObject(planet, 5);
                }});
                
                // Draw Messier objects
                messierObjects.forEach(obj => {{
                    drawCelestialObject(obj, 2);
                }});
                
                // Highlight target if found
                highlightTarget('{target}');
            }}
            
            function drawGrid() {{
                ctx.strokeStyle = '#333333';
                ctx.lineWidth = 0.5;
                
                // Draw RA lines (vertical)
                for (let ra = 0; ra < 360; ra += 30) {{
                    const x = (ra / 360) * canvas.width * zoom + offsetX;
                    if (x >= 0 && x <= canvas.width) {{
                        ctx.beginPath();
                        ctx.moveTo(x, 0);
                        ctx.lineTo(x, canvas.height);
                        ctx.stroke();
                    }}
                }}
                
                // Draw Dec lines (horizontal)
                for (let dec = -90; dec <= 90; dec += 30) {{
                    const y = ((90 - dec) / 180) * canvas.height * zoom + offsetY;
                    if (y >= 0 && y <= canvas.height) {{
                        ctx.beginPath();
                        ctx.moveTo(0, y);
                        ctx.lineTo(canvas.width, y);
                        ctx.stroke();
                    }}
                }}
            }}
            
            function drawCelestialObject(obj, baseSize) {{
                const x = (obj.ra / 360) * canvas.width * zoom + offsetX;
                const y = ((90 - obj.dec) / 180) * canvas.height * zoom + offsetY;
                
                if (x >= -20 && x <= canvas.width + 20 && y >= -20 && y <= canvas.height + 20) {{
                    const size = Math.max(1, baseSize - obj.mag) * zoom;
                    
                    ctx.fillStyle = obj.color;
                    ctx.beginPath();
                    ctx.arc(x, y, size, 0, Math.PI * 2);
                    ctx.fill();
                    
                    // Draw object name if zoomed in enough
                    if (zoom > 1.5) {{
                        ctx.fillStyle = '#ffffff';
                        ctx.font = '10px Arial';
                        ctx.fillText(obj.name, x + size + 2, y - 2);
                    }}
                }}
            }}
            
            function highlightTarget(targetName) {{
                const allObjects = [...brightStars, ...planets, ...messierObjects];
                const target = allObjects.find(obj => 
                    obj.name.toLowerCase() === targetName.toLowerCase() ||
                    obj.name.toLowerCase().includes(targetName.toLowerCase())
                );
                
                if (target) {{
                    const x = (target.ra / 360) * canvas.width * zoom + offsetX;
                    const y = ((90 - target.dec) / 180) * canvas.height * zoom + offsetY;
                    
                    // Draw target circle
                    ctx.strokeStyle = '#ff0000';
                    ctx.lineWidth = 2;
                    ctx.beginPath();
                    ctx.arc(x, y, 15, 0, Math.PI * 2);
                    ctx.stroke();
                    
                    // Update coordinates display
                    const raHours = Math.floor(target.ra / 15);
                    const raMinutes = Math.floor((target.ra / 15 - raHours) * 60);
                    const decDegrees = Math.floor(Math.abs(target.dec));
                    const decMinutes = Math.floor((Math.abs(target.dec) - decDegrees) * 60);
                    const decSign = target.dec >= 0 ? '+' : '-';
                    
                    document.getElementById('coordinates').innerHTML = 
                        `RA: ${{raHours}}h ${{raMinutes}}m, Dec: ${{decSign}}${{decDegrees}}° ${{decMinutes}}'`;
                    
                    targetFound = true;
                }} else {{
                    document.getElementById('coordinates').innerHTML = 
                        `Target "${{targetName}}" not found in catalog`;
                }}
            }}
            
            // Control functions
            function zoomIn() {{
                zoom = Math.min(zoom * 1.5, 5);
                drawSky();
            }}
            
            function zoomOut() {{
                zoom = Math.max(zoom / 1.5, 0.5);
                drawSky();
            }}
            
            function resetView() {{
                zoom = 1;
                offsetX = 0;
                offsetY = 0;
                drawSky();
            }}
            
            function toggleGrid() {{
                showGrid = !showGrid;
                drawSky();
            }}
            
            // Mouse interaction
            canvas.addEventListener('mousemove', function(e) {{
                const rect = canvas.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                
                const ra = ((x - offsetX) / zoom / canvas.width) * 360;
                const dec = 90 - ((y - offsetY) / zoom / canvas.height) * 180;
                
                document.getElementById('mouse-coords').innerHTML = 
                    `Mouse: RA ${{ra.toFixed(1)}}°, Dec ${{dec.toFixed(1)}}°`;
            }});
            
            // Pan functionality
            let isDragging = false;
            let lastX, lastY;
            
            canvas.addEventListener('mousedown', function(e) {{
                isDragging = true;
                lastX = e.clientX;
                lastY = e.clientY;
            }});
            
            canvas.addEventListener('mousemove', function(e) {{
                if (isDragging) {{
                    offsetX += e.clientX - lastX;
                    offsetY += e.clientY - lastY;
                    lastX = e.clientX;
                    lastY = e.clientY;
                    drawSky();
                }}
            }});
            
            canvas.addEventListener('mouseup', function() {{
                isDragging = false;
            }});
            
            canvas.addEventListener('wheel', function(e) {{
                e.preventDefault();
                if (e.deltaY < 0) {{
                    zoomIn();
                }} else {{
                    zoomOut();
                }}
            }});
            
            // Initialize
            function resizeCanvas() {{
                const container = document.getElementById('sky-container');
                canvas.width = container.clientWidth;
                canvas.height = container.clientHeight - 4;
                drawSky();
            }}
            
            window.addEventListener('resize', resizeCanvas);
            window.addEventListener('load', function() {{
                resizeCanvas();
                // Center on target if found
                if (targetFound) {{
                    // Auto-center logic could go here
                }}
            }});
        </script>
    </body>
    </html>
    '''
    
    # Display the component
    components.html(html_content, height=540, scrolling=False)


def create_simple_sky_info_card(target: str):
    """Create a simple information card about the target object."""
    
    # Basic object information
    object_info = {
        'Sirius': {'type': 'Star', 'constellation': 'Canis Major', 'distance': '8.6 light-years', 'magnitude': '-1.46'},
        'Vega': {'type': 'Star', 'constellation': 'Lyra', 'distance': '25 light-years', 'magnitude': '0.03'},
        'Mars': {'type': 'Planet', 'constellation': 'Variable', 'distance': '~200 million km', 'magnitude': 'Variable'},
        'Jupiter': {'type': 'Planet', 'constellation': 'Variable', 'distance': '~600 million km', 'magnitude': '-2.0'},
        'M31': {'type': 'Galaxy', 'constellation': 'Andromeda', 'distance': '2.5 million light-years', 'magnitude': '3.4'},
        'M42': {'type': 'Nebula', 'constellation': 'Orion', 'distance': '1,344 light-years', 'magnitude': '4.0'}
    }
    
    info = object_info.get(target, {
        'type': 'Unknown', 
        'constellation': 'Unknown', 
        'distance': 'Unknown', 
        'magnitude': 'Unknown'
    })
    
    st.info(f"""
    **📍 Object Information:**
    - **Type:** {info['type']}
    - **Constellation:** {info['constellation']}
    - **Distance:** {info['distance']}
    - **Magnitude:** {info['magnitude']}
    """)


def local_sky_atlas_component(target: str, key: str = "local-sky-atlas"):
    """
    Main function to create a local sky atlas that works without internet.
    """
    st.markdown("### 🌌 Local Sky Atlas")
    st.markdown("*This sky map works entirely offline and shows bright stars, planets, and deep-sky objects.*")
    
    # Display the interactive sky map
    offline_sky_atlas_component(target, key)
    
    # Add object information
    create_simple_sky_info_card(target)
    
    # Usage instructions
    with st.expander("🔍 How to use the Local Sky Atlas", expanded=False):
        st.markdown("""
        **Navigation:**
        - **Click and drag** to pan around the sky
        - **Mouse wheel** to zoom in/out
        - **Zoom In/Out buttons** for precise control
        - **Reset button** to return to original view
        - **Grid button** to toggle coordinate grid
        
        **Features:**
        - **Red circle** highlights your target object
        - **White dots** are bright stars
        - **Colored dots** are planets and deep-sky objects
        - **Mouse coordinates** show RA/Dec position
        - **Object labels** appear when zoomed in
        
        **Note:** This is a simplified sky map with approximate positions.
        For precise observations, use professional astronomy software.
        """)
