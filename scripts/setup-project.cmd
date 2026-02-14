@echo off
echo ========================================
echo HR Management System - Initial Setup
echo ========================================
echo.

echo [1/4] Setting up backend...
cd backend
if not exist .env (
    echo Creating .env file from template...
    copy .env.example .env
    echo Please edit backend/.env with your database credentials
    pause
)
echo Installing Python dependencies...
python -m pip install -r requirements.txt
cd ..

echo.
echo [2/4] Setting up frontend...
cd frontend
if not exist .env (
    echo Creating .env file from template...
    copy .env.example .env
)
echo Installing Node dependencies...
call npm install
cd ..

echo.
echo [3/4] Testing database connection...
cd backend
python test_db_connection.py
cd ..

echo.
echo [4/4] Creating default users...
cd backend
python create_default_users.py
cd ..

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo To start the application:
echo   1. Backend:  scripts\start-backend.cmd
echo   2. Frontend: scripts\start-frontend.cmd
echo.
echo Default login credentials:
echo   Super Admin: admin@company.com / admin123
echo   HR:          hr@company.com / hr123
echo   Employee:    employee@company.com / emp123
echo.
pause
