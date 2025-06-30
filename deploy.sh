#!/bin/bash
# Quick deployment script for Space Detective

echo "🚀 Space Detective - Deployment Helper"
echo "======================================"

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📁 Initializing Git repository..."
    git init
    echo "✅ Git initialized"
fi

# Add all files
echo "📦 Adding files to Git..."
git add .

# Check if there are changes to commit
if git diff --staged --quiet; then
    echo "ℹ️  No changes to commit"
else
    echo "💾 Committing changes..."
    read -p "Enter commit message (or press Enter for default): " commit_msg
    if [ -z "$commit_msg" ]; then
        commit_msg="Update Space Detective app"
    fi
    git commit -m "$commit_msg"
    echo "✅ Changes committed"
fi

# Check if remote origin exists
if git remote get-url origin >/dev/null 2>&1; then
    echo "🌐 Remote origin already exists"
    echo "📤 Pushing to GitHub..."
    git push origin main
else
    echo "🔗 No remote origin found"
    echo "Please add your GitHub repository URL:"
    read -p "GitHub repository URL: " repo_url
    if [ ! -z "$repo_url" ]; then
        git remote add origin "$repo_url"
        echo "📤 Pushing to GitHub..."
        git push -u origin main
    fi
fi

echo ""
echo "🎉 Deployment preparation complete!"
echo ""
echo "Next steps:"
echo "1. Go to https://share.streamlit.io"
echo "2. Sign in with GitHub"
echo "3. Click 'New app'"
echo "4. Select your repository"
echo "5. Set main file path: Merai v1/main.py"
echo "6. Click 'Deploy!'"
echo ""
echo "Your app will be live at: https://your-app-name.streamlit.app"
