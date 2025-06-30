# Space Detective - Deployment Instructions

## 🚀 Quick Deploy to Streamlit Cloud

### Step 1: Prepare Your Project
1. Make sure all files are in the "Merai v1" folder
2. Check that requirements.txt includes all dependencies
3. Test locally: `streamlit run "Merai v1/main.py"`

### Step 2: Upload to GitHub
```bash
# Initialize git repository
git init

# Add all files
git add .

# Commit changes
git commit -m "Initial deployment of Space Detective app"

# Add your GitHub repository
git remote add origin https://github.com/justme017/space-detective.git

# Push to GitHub
git push -u origin main
```

### Step 3: Deploy on Streamlit Cloud
1. Go to https://share.streamlit.io
2. Sign in with your GitHub account
3. Click "New app"
4. Select your repository: "space-detective"
5. Set main file path: `Merai v1/main.py`
6. **IMPORTANT:** Leave requirements file path as default (`requirements.txt`) - it's now in the root directory
7. Click "Deploy!"

### Step 4: Configure Advanced Settings (Optional)
- Set Python version: 3.9+
- Add secrets if needed
- Configure custom domain

## � Streamlit Cloud - Recommended & Simplified

This project is now optimized specifically for **Streamlit Cloud** deployment - the easiest and most reliable option for this app.

## 🔧 Troubleshooting

### Common Issues:
1. **Import errors**: Make sure all modules are in requirements.txt
2. **File paths**: Use relative paths from the main.py location
3. **API keys**: Use Streamlit secrets for sensitive data
4. **Memory limits**: Some platforms have memory restrictions

### Solutions:
- Test locally first
- Check deployment logs
- Use environment variables
- Optimize for cloud deployment

## 📝 Deployment Checklist

- [ ] All dependencies in requirements.txt
- [ ] No absolute file paths
- [ ] API keys in secrets (if any)
- [ ] Test app locally
- [ ] Repository is public (for free deployment)
- [ ] Main file path is correct

## 🎯 Recommended: Streamlit Cloud
- **Free** for public repositories
- **Easy** one-click deployment
- **Official** Streamlit support
- **Automatic** updates from GitHub
