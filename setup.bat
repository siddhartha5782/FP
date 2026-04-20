@echo off
echo ===================================================
echo     CXR Intelli-Assist - Project Setup Script
echo ===================================================

echo.
echo [1/3] Creating Python Virtual Environment (venv)...
if not exist "venv\" (
    python -m venv venv
    echo Virtual environment created successfully.
) else (
    echo Virtual environment already exists. Skipping...
)

echo.
echo [2/3] Installing Backend Dependencies...
call .\venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
echo Backend dependencies installed successfully.

echo.
echo [3/3] Installing Frontend Dependencies...
cd frontend
call npm install
cd ..
echo Frontend dependencies installed successfully.

echo.
echo ===================================================
echo Setup Complete! You can now launch the app using run.bat.
echo ===================================================
pause
