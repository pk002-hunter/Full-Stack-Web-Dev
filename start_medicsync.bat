@echo off
echo Starting MedicSync System...
echo.

echo [1/3] Starting Node.js Backend...
cd backend
start "MedicSync Backend" cmd /k "npm start"
cd ..

echo [2/3] Starting Django Frontend...
start "MedicSync Frontend" cmd /k "python manage.py runserver"

echo [3/3] Opening Browser...
timeout /t 3 /nobreak >nul
start http://localhost:8000

echo.
echo System started!
echo - Backend: http://localhost:3000
echo - Frontend: http://localhost:8000
echo.
echo Press any key to run system test...
pause >nul

python test_system.py

echo.
echo Press any key to exit...
pause >nul