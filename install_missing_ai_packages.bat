@echo off
echo ========================================
echo Installing Missing AI Packages
echo ========================================
echo.

echo Installing scikit-learn...
pip install scikit-learn>=1.3.0

echo.
echo Installing pyyaml...
pip install pyyaml>=6.0

echo.
echo Installing requests (for API testing)...
pip install requests

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo Now run the AI functionality test:
echo python test_ai_functionality.py
echo.
pause 