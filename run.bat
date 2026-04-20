@echo off
echo ===================================================
echo     CXR Intelli-Assist - Application Launcher
echo ===================================================
echo.
echo Starting FastAPI Backend Server...
start "Backend Server (FastAPI)" cmd /k ".\venv\Scripts\activate.bat && python main.py"

echo Starting Vite Frontend Server...
start "Frontend Server (Vite React)" cmd /k "cd frontend && npm run dev"

echo.
echo Both servers are booting up in separate terminal windows!
echo Once they are ready, your frontend will be accessible at http://localhost:5173/
echo Tip: Close the opened terminal windows when you want to stop the servers.
echo.
pause
