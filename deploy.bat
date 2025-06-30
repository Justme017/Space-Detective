@echo off
echo 🚀 Space Detective - Deployment Helper (Windows)
echo ==========================================

REM Check if git is initialized
if not exist ".git" (
    echo 📁 Initializing Git repository...
    git init
    echo ✅ Git initialized
)

REM Add all files
echo 📦 Adding files to Git...
git add .

REM Commit changes
echo 💾 Committing changes...
set /p commit_msg="Enter commit message (or press Enter for default): "
if "%commit_msg%"=="" set commit_msg=Update Space Detective app
git commit -m "%commit_msg%"
echo ✅ Changes committed

REM Check for remote and push
echo 📤 Attempting to push to GitHub...
git push origin main 2>nul
if errorlevel 1 (
    echo 🔗 No remote origin found or push failed
    echo Please add your GitHub repository URL:
    set /p repo_url="GitHub repository URL: "
    if not "%repo_url%"=="" (
        git remote add origin "%repo_url%"
        echo 📤 Pushing to GitHub...
        git push -u origin main
    )
)

echo.
echo 🎉 Deployment preparation complete!
echo.
echo Next steps:
echo 1. Go to https://share.streamlit.io
echo 2. Sign in with GitHub
echo 3. Click 'New app'
echo 4. Select your repository
echo 5. Set main file path: Merai v1/main.py
echo 6. Click 'Deploy!'
echo.
echo Your app will be live at: https://your-app-name.streamlit.app
pause
