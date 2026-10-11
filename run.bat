@echo off
:: ============================================================
::  AI Career Mentor Agent — Windows Launcher
::  Double-click this file to install dependencies and start
::  the Streamlit application in your default browser.
:: ============================================================

title AI Career Mentor Agent

echo.
echo  ==========================================================
echo   AI Career Mentor ^& Skill-Gap Agent
echo   Powered by Groq ^| LLaMA 3.3 70B
echo  ==========================================================
echo.

:: --- Install / upgrade dependencies ---
echo  [1/2] Installing dependencies from requirements.txt ...
echo.
pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo  ERROR: pip install failed. Make sure Python is installed
    echo  and added to your PATH.
    pause
    exit /b 1
)

echo.
echo  [2/2] Starting Streamlit application ...
echo.
echo  The app will open at: http://localhost:8501
echo  Press Ctrl+C in this window to stop the server.
echo.

streamlit run app.py

pause
