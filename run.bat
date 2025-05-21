@echo off

rem Check if Python is installed
where python > nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed. Please install Python.
    exit /b 1
)

rem Check if venv directory exists
if not exist .venv (
    echo Creating a virtual environment...
    python -m venv .venv
)

rem Activate the virtual environment
call .venv\Scripts\activate

rem Upgrade pip (commented out)gi
rem python -m pip install --upgrade pip

rem Install requirements (commented out)
  rem python -m pip install -r requirements.txt

rem Remove previous migrations if any (be careful with this step, it supprime les anciennes migrations)
echo Removing old migrations...
rmdir /s /q migrations

rem Regenerate the migrations
echo Generating new migrations...

     rem flask --app __init__.py db init
     rem flask --app __init__.py db migrate -m "Regenerate database schema"
     rem flask --app __init__.py db upgrade

rem Set Flask environment to development and run Flask in debug mode
echo Running Flask app in debug mode...
set "FLASK_ENV=development"
flask --app __init__ run --host=0.0.0.0 --port=5000 --debug
