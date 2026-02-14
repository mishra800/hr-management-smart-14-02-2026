@echo off
echo ========================================
echo Starting HR Management Backend Server
echo ========================================
echo.

cd backend

echo [1/2] Installing dependencies...
python -m pip install -q -r requirements.txt

echo [2/2] Starting server...
echo Server will be available at: http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo.

python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
