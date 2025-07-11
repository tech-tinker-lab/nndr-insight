@echo off
echo ========================================
echo NNDR Insight AI Environment Setup
echo ========================================
echo.

echo [1/4] Installing AI dependencies...
echo Installing from requirements.txt...
pip install -r requirements.txt

echo.
echo Installing any missing core packages...
pip install scikit-learn>=1.3.0 pyyaml>=6.0 requests>=2.28.0

echo.
echo [2/4] Testing AI functionality...
python test_ai_functionality.py

echo.
echo [3/4] Starting backend server...
echo Starting backend server in background...
start "NNDR Backend" cmd /k "cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

echo.
echo [4/4] Starting frontend...
echo Starting frontend in background...
start "NNDR Frontend" cmd /k "cd frontend && npm start"

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo AI Features Available:
echo - Government data pattern detection
echo - Standards compliance checking (BS7666, INSPIRE, OS)
echo - Intelligent column mapping
echo - Data quality assessment
echo - Automatic configuration suggestions
echo.
echo Test the AI features by uploading government datasets!
echo.
pause 