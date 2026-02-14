@echo off
echo ========================================
echo HR Management System - Database Setup
echo ========================================
echo.

cd backend

echo [1/2] Testing database connection...
python test_db_connection.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Database connection failed!
    echo Please check your DATABASE_URL in backend/.env
    echo.
    pause
    exit /b 1
)

echo.
echo [2/2] Creating default users...
python create_default_users.py

echo.
echo ========================================
echo Database setup complete!
echo ========================================
echo.
echo Next steps:
echo   1. Start backend: scripts\start-backend.cmd
echo   2. Start frontend: scripts\start-frontend.cmd
echo.
pause
