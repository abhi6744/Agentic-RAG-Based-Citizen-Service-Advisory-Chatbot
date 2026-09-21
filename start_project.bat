@echo off
echo ===================================================
echo Starting Akshaya Advisory Project
echo ===================================================

echo [1/2] Starting FastAPI Backend...
start "Akshaya Backend" cmd /k "cd akshaya-backend && .\venv\Scripts\activate && uvicorn app.main:app --port 8000"

echo [2/2] Starting Expo Web Frontend...
cd akshaya-frontend
call npx expo start --web --clear
