@echo off
echo ==========================================
echo   MedicSync Tactical Command System
echo ==========================================
echo.

echo [1/3] Starting Node.js Backend + ESP32 Simulator...
cd backend
start "MedicSync Backend" cmd /k "node server.js"
timeout /t 2 /nobreak >nul
start "ESP32 Simulator" cmd /k "node simulate-esp32.js"
cd ..

echo [2/3] Starting Django Server...
start "MedicSync Django" cmd /k "python manage.py runserver"

echo [3/3] Opening Browser (waiting for servers to boot)...
timeout /t 4 /nobreak >nul
start http://localhost:8000

echo.
echo ==========================================
echo   System is running!
echo   Backend  : http://localhost:3000
echo   Frontend : http://localhost:8000
echo ==========================================
echo.
echo Close the 3 terminal windows to stop the system.
echo.
pause >nul