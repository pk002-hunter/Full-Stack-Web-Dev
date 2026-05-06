@echo off
echo ==========================================
echo   Shutting down MedicSync System...
echo ==========================================
echo.

echo Stopping Node.js Backend...
taskkill /F /FI "WINDOWTITLE eq MedicSync Backend*" /T >nul 2>&1

echo Stopping ESP32 Simulator...
taskkill /F /FI "WINDOWTITLE eq ESP32 Simulator*" /T >nul 2>&1

echo Stopping Django Frontend...
taskkill /F /FI "WINDOWTITLE eq MedicSync Django*" /T >nul 2>&1

echo.
echo ==========================================
echo   All servers successfully stopped!
echo ==========================================
echo.
pause
