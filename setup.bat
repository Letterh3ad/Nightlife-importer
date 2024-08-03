@echo off
setlocal enabledelayedexpansion

REM Define the directory and file names
set "EXE_DIR=exe_files"
set "SCRIPT_FILE=tag_maker_autoloader.py"
set "GITHUB_URL=https://raw.githubusercontent.com/Letterh3ad/Nightlife-importer/main/Tag_maker_autoloader.py?token=GHSAT0AAAAAACVOYW3FYLAXVLRWOJ7IK7V2ZVNW7QQ"

REM Define directories to be created
set "CATEGORIES_DIR=categories"
set "CATEGORIES_UPDATED_DIR=categories_updated"
set "CATEGORY_LIST_FILE=categories_list.txt"

REM Download the Tag_maker_autoloader.py file from GitHub
echo Downloading %SCRIPT_FILE% from %GITHUB_URL%
curl -L -o "%SCRIPT_FILE%" "%GITHUB_URL%"

REM Check if the download was successful
if not exist "%SCRIPT_FILE%" (
    echo Failed to download %SCRIPT_FILE%.
    exit /b 1
)

REM Create necessary directories if they do not exist
if not exist "%CATEGORIES_DIR%" (
    echo Creating directory %CATEGORIES_DIR%
    mkdir "%CATEGORIES_DIR%"
)

if not exist "%CATEGORIES_UPDATED_DIR%" (
    echo Creating directory %CATEGORIES_UPDATED_DIR%
    mkdir "%CATEGORIES_UPDATED_DIR%"
)

if not exist "%CATEGORY_LIST_FILE%" (
    echo Creating file %CATEGORY_LIST_FILE%
    type nul > "%CATEGORY_LIST_FILE%"
)

REM Create the exe_files directory if it does not exist
if not exist "%EXE_DIR%" (
    echo Creating directory %EXE_DIR%
    mkdir "%EXE_DIR%"
)

REM Read the file and extract import statements
set "modules="
for /f "usebackq tokens=1,* delims= " %%a in ("%SCRIPT_FILE%") do (
    if "%%a"=="import" (
        set "module=%%b"
        set "module=!module:~0,-1!"
        if "!module!" neq "" (
            set "modules=!modules! !module!"
        )
    )
)

REM Install the modules using pip
if defined modules (
    echo Installing modules: %modules%
    pip install %modules%
) else (
    echo No modules to install
)

REM Check if pyinstaller is installed, if not, install it
python -m pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller not found. Installing PyInstaller...
    pip install pyinstaller
)

REM Change to the exe_files directory
cd /d "%EXE_DIR%"

REM Create executable from the script in the same directory as the script
echo Creating executable from %SCRIPT_FILE%...
pyinstaller --onefile ..\%SCRIPT_FILE%

echo Done!
pause
