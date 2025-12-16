@echo off
setlocal

set "HOST_NAME=com.manyfold.bambu"
set "DESCRIPTION=Manyfold Bambu Studio Helper"
set "HOST_SCRIPT=bambu_host.py"

REM Get script directory
set "SCRIPT_DIR=%~dp0"
REM Remove trailing backslash
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"
set "HOST_PATH=%SCRIPT_DIR%\%HOST_SCRIPT%"

echo Installing Manyfold Bambu Host...

REM 0. Check for Python
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Python is not installed or not in PATH.
    echo Attempting to install Python via Winget...
    winget install -e --id Python.Python.3
    
    python --version >nul 2>&1
    IF %ERRORLEVEL% NEQ 0 (
        echo Failed to install Python automatically.
        echo Please install Python manually from https://www.python.org/downloads/
        pause
        exit /b 1
    )
)

REM 1. Get Extension ID
echo Example ID: knldjmfmopnpolahpmmgbagdohdnhkik
REM Check if ID is passed as argument
IF NOT "%~1"=="" (
    SET EXTENSION_ID=%~1
    ECHO Using Extension ID from argument: %~1
) ELSE (
    set /p EXTENSION_ID="Enter your Extension ID (from chrome://extensions): "
)

if "%EXTENSION_ID%"=="" (
    echo Extension ID is required.
    pause
    exit /b 1
)

REM 2. Verify Host Script
if not exist "%HOST_PATH%" (
    echo Error: Could not find %HOST_SCRIPT% at %HOST_PATH%
    exit /b 1
)

REM 3. Create Manifest JSON
set "MANIFEST_JSON={\"name\": \"%HOST_NAME%\", \"description\": \"%DESCRIPTION%\", \"path\": \"%HOST_SCRIPT%\", \"type\": \"stdio\", \"allowed_origins\": [\"chrome-extension://%EXT_ID%/\"]}"

REM Escape quotes for registry? No, manifest is a file. But Windows requires Registry Keys pointing to the manifest.

REM 4. Create Registry Key for Chrome
REG ADD "HKCU\Software\Google\Chrome\NativeMessagingHosts\%HOST_NAME%" /ve /t REG_SZ /d "%SCRIPT_DIR%\manifest.json" /f

REM 5. Create Registry Key for Edge
REG ADD "HKCU\Software\Microsoft\Edge\NativeMessagingHosts\%HOST_NAME%" /ve /t REG_SZ /d "%SCRIPT_DIR%\manifest.json" /f

REM 6. Write Manifest File locally (Registry points here)
set "MANIFEST_FILE=%SCRIPT_DIR%\manifest.json"
(
    echo {
    echo   "name": "%HOST_NAME%",
    echo   "description": "%DESCRIPTION%",
    echo   "path": "%HOST_PATH%",
    echo   "type": "stdio",
    echo   "allowed_origins": [
    echo     "chrome-extension://%EXTENSION_ID%/"
    echo   ]
    echo }
) > "%MANIFEST_FILE%"

echo.
echo Installation Complete!
echo Registry keys added and manifest created at %MANIFEST_FILE%
echo Please reload your extension.
pause
