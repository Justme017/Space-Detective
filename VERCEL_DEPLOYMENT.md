# Vercel Deployment Instructions for Merai Location Service

## Step 1: Prepare the HTML File

1. Create a new folder for your Vercel deployment:
   ```
   mkdir merai-geolocation
   cd merai-geolocation
   ```

2. Copy the `index.html` file from the `vercel-deployment` folder to your new folder.

## Step 2: Deploy to Vercel

### Option A: Using Vercel CLI

1. Install Vercel CLI:
   ```bash
   npm install -g vercel
   ```

2. In your project folder, run:
   ```bash
   vercel
   ```

3. Follow the prompts:
   - Choose "Deploy"
   - Set project name (e.g., "merai-geolocation")
   - Confirm settings

### Option B: Using Vercel Web Interface

1. Go to [vercel.com](https://vercel.com) and sign up/login
2. Click "New Project"
3. Import from Git or drag and drop your folder
4. Set the project name
5. Click "Deploy"

## Step 3: Get Your Deployment URL

After deployment, you'll get a URL like:
`https://merai-geolocation-abc123.vercel.app`

## Step 4: Update Streamlit App

In your `main.py` file, replace this line:
```python
GEOLOCATION_SERVICE_URL = "https://your-app-name.vercel.app"
```

With your actual Vercel URL:
```python
GEOLOCATION_SERVICE_URL = "https://merai-geolocation-abc123.vercel.app"
```

## Step 5: Test the Integration

1. Run your Streamlit app:
   ```bash
   streamlit run main.py
   ```

2. Select "Detect my location" and allow location access when prompted

## Troubleshooting

- **CORS Issues**: The HTML page should automatically work with any domain
- **HTTPS Required**: Geolocation only works on HTTPS. Vercel provides HTTPS by default
- **Timeout**: The default timeout is 10 seconds. Users will fall back to IP-based location if browser geolocation fails

## File Structure

Your deployment folder should look like:
```
merai-geolocation/
├── index.html
└── README.md (optional)
```

## Notes

- The HTML file is self-contained with no external dependencies
- Works with all modern browsers that support geolocation
- Automatically sends location data back to the parent Streamlit app
- Falls back gracefully if geolocation is denied or unavailable
