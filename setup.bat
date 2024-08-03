@echo off
setlocal enabledelayedexpansion

REM Define the directory for exe files
set "EXE_DIR=exe_files"

REM Check if tag_maker_autoloader.py exists
if not exist "tag_maker_autoloader.py" (
    echo File tag_maker_autoloader.py not found!
    exit /b 1
)

REM Create the exe_files directory if it does not exist
if not exist "%EXE_DIR%" (
    echo Creating directory %EXE_DIR%
    mkdir "%EXE_DIR%"
)

REM Read the file and extract import statements
set "modules="
for /f "usebackq tokens=1,* delims= " %%a in ("tag_maker_autoloader.py") do (
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

REM Create executable from the script
echo Creating executable from tag_maker_autoloader.py...
pyinstaller --onefile ..\tag_maker_autoloader.py

echo Done!
pause

