#!/usr/bin/env python3
"""
Test script to verify the Vercel geolocation service is working properly.
This simulates what the main app does to get location data.

Usage: python test_vercel_location.py
"""

import time
import webbrowser

def test_vercel_service():
    """Test the Vercel geolocation service in a browser."""
    print("🧪 Testing Vercel Geolocation Service")
    print("=" * 50)
    
    vercel_url = "https://geolocation-page.vercel.app/"
    local_file = "geolocation.html"
    
    print(f"🌐 Testing Vercel service: {vercel_url}")
    print("📱 This will open the service in your browser...")
    print("💡 You should see location coordinates if GPS is working")
    print("\n⏳ Opening browser in 3 seconds...")
    
    for i in range(3, 0, -1):
        print(f"   {i}...")
        time.sleep(1)
    
    # Open Vercel service
    webbrowser.open(vercel_url)
    
    print(f"\n🔧 You can also test the local file: {local_file}")
    print("📝 Instructions:")
    print("   1. Allow location access when prompted")
    print("   2. You should see your coordinates")
    print("   3. If it works, the main app will work too!")
    
    print(f"\n🚀 To deploy your own version:")
    print("   1. Go to vercel.com")
    print("   2. Upload the geolocation.html file")
    print("   3. Update the URL in main.py if needed")
    
    print(f"\n✅ If you see coordinates, the Vercel logic is working!")
    print(f"❌ If you see errors, check browser permissions or try a different browser")

if __name__ == "__main__":
    test_vercel_service()
