#!/usr/bin/env python3
"""
Test script for the geolocation.html service.

This script starts a simple Python HTTP server to host the local 
`geolocation.html` file and then opens it in a web browser. This allows for 
easy local testing of the geolocation functionality without needing to deploy it.

Usage: python test_vercel_location.py
"""

import http.server
import socketserver
import webbrowser
import os

PORT = 8000
FILENAME = "geolocation.html"

def run_test():
    """Starts a local server and opens the geolocation test page."""
    if not os.path.exists(FILENAME):
        print(f"Error: {FILENAME} not found in the current directory.")
        return

    Handler = http.server.SimpleHTTPRequestHandler

    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"✅ Local test server running at http://localhost:{PORT}/")
        print(f"🚀 Opening {FILENAME} in your browser...")
        
        webbrowser.open_new_tab(f"http://localhost:{PORT}/{FILENAME}")
        
        print("\n--- Instructions ---")
        print("1. Your browser should ask for location permission. Click 'Allow'.")
        print("2. The page should display your coordinates if successful.")
        print("3. If it works here, it will work in the main Streamlit app.")
        print("4. Press Ctrl+C in this terminal to stop the server.")

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Server stopped.")

if __name__ == "__main__":
    run_test()
