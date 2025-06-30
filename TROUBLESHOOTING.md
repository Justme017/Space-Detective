# 🔧 Deployment Troubleshooting Guide

## ❗ Error: "installer returned a non-zero exit code"

This error occurs when Streamlit Cloud can't install the dependencies from requirements.txt.

### 🚀 Quick Fixes:

#### Option 1: Use the Fixed Requirements File
I've updated your `requirements.txt` with compatible versions. Push the updated file:

```bash
git add .
git commit -m "Fix requirements.txt for Streamlit Cloud"
git push origin main
```

#### Option 2: Try Minimal Requirements
If the main requirements still fail, rename files:

```bash
# Backup current requirements
mv "requirements.txt" "requirements_backup.txt"

# Use minimal requirements
mv "requirements_minimal.txt" "requirements.txt"

# Push changes
git add .
git commit -m "Use minimal requirements for deployment"
git push origin main
```

#### Option 3: Manual Package Testing
Test packages individually by creating this minimal requirements.txt:

```
streamlit
pandas
numpy
```

Then gradually add more packages one by one.

### 🔍 Common Issues and Solutions:

1. **Version Conflicts**
   - Remove version pins (>=1.0.0) and use just package names
   - Some packages may conflict with Streamlit Cloud's Python version

2. **Unsupported Packages**
   - `flask` is not needed for Streamlit apps - removed
   - Some packages may not be available on Streamlit Cloud

3. **Python Version Issues**
   - Streamlit Cloud uses Python 3.9-3.11
   - Some packages may require specific Python versions

### 🛠️ Step-by-Step Fix:

1. **Update requirements.txt** (already done)
2. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Fix requirements for deployment"
   git push origin main
   ```
3. **Restart deployment** on Streamlit Cloud
4. **Check logs** for specific error messages

### 📋 Working Requirements.txt:
```
streamlit>=1.28.0
pandas>=1.5.0
numpy>=1.21.0
requests>=2.28.0
plotly>=5.15.0
skyfield>=1.46
beautifulsoup4>=4.11.0
streamlit-folium>=0.13.0
geocoder>=1.38.1
folium>=0.14.0
```

### 🆘 If Still Failing:

Try this ultra-minimal requirements.txt:
```
streamlit
skyfield
pandas
plotly
requests
```

### 🎯 Alternative Deployment Platforms:

If Streamlit Cloud continues to have issues:

1. **Railway.app** - Often more forgiving with dependencies
2. **Render.com** - Good package compatibility  
3. **Heroku** - Professional platform (paid)

### 📞 Next Steps:

1. Push the fixed requirements.txt
2. Wait for Streamlit Cloud to rebuild (may take 5-10 minutes)
3. Check deployment logs for specific errors
4. If still failing, try the minimal requirements approach
