@echo off
echo ===================================================
echo Setting up Django Backend Development Environment
echo ===================================================

REM Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Python is not installed or not in PATH. Please install Python first.
    exit /b 1
)

REM Check if venv exists, create if not
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
    if %ERRORLEVEL% neq 0 (
        echo Failed to create virtual environment. Please check your Python installation.
        exit /b 1
    )
    echo Virtual environment created successfully.
) else (
    echo Virtual environment already exists.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate
if %ERRORLEVEL% neq 0 (
    echo Failed to activate virtual environment.
    exit /b 1
)

REM Install requirements
echo Installing dependencies...
pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo Failed to install dependencies.
    exit /b 1
)

REM Check if .env file exists, create from example if not
if not exist .env (
    echo Creating .env file from template...
    copy .env.example .env
    echo Please edit the .env file with your database credentials.
)

REM Run migrations
echo Applying database migrations...
python manage.py migrate
if %ERRORLEVEL% neq 0 (
    echo Failed to apply migrations. Please check your database settings.
    exit /b 1
)

REM Ask to create a superuser
echo.
echo Would you like to create a superuser? (y/n)
set /p create_superuser=
if /i "%create_superuser%"=="y" (
    python manage.py createsuperuser
)

REM Start the development server
echo.
echo Starting Django development server...
echo Access the API at http://localhost:8000/api/
echo Access the admin at http://localhost:8000/admin/
echo Access API documentation at http://localhost:8000/api/schema/swagger-ui/
echo Press CTRL+C to stop the server.
echo.
python manage.py runserver

REM Deactivate the virtual environment when server is stopped
call venv\Scripts\deactivate.bat
echo Development server stopped. Virtual environment deactivated.
