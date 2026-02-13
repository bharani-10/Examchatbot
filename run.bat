@echo off
echo ========================================
echo   Starting Exam Assistant AI
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.

REM Install requirements
echo Installing dependencies...
pip install -r requirements.txt --quiet
echo.

REM Check for .env file
if not exist ".env" (
    echo WARNING: .env file not found!
    echo Please create a .env file with your GROQ_API_KEY
    echo.
    pause
    exit /b 1
)

REM Run the app
echo Starting Streamlit app...
echo.
streamlit run app.py

pause
