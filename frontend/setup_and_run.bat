@echo off
echo ===================================================
echo Setting up Vue.js Frontend Development Environment
echo ===================================================

REM Check if Node.js is installed
where node >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Node.js is not installed or not in PATH. Please install Node.js first.
    exit /b 1
)

REM Check npm version
echo Node.js is installed. Checking npm...
call npm --version >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo npm is not installed or not working correctly. Please check your Node.js installation.
    exit /b 1
)

REM Install dependencies
echo Installing dependencies...
call npm install
if %ERRORLEVEL% neq 0 (
    echo Failed to install dependencies.
    exit /b 1
)

REM Create .env file if it doesn't exist
if not exist .env (
    echo Creating .env file...
    echo VITE_API_URL=http://localhost:8000/api > .env
    echo .env file created with default API URL.
)

REM Start development server
echo.
echo Starting Vue.js development server...
echo.
echo Access the frontend at http://localhost:3000/
echo.
echo The development server will automatically reload when you make changes to the code.
echo Press CTRL+C to stop the server.
echo.
call npm run dev

echo.
echo Development server stopped.
