@echo off
REM install_karmalentil.bat
REM Windows installation script for KarmaLentil

echo ==========================================
echo KarmaLentil Installation
echo ==========================================
echo.

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0
set SCRIPT_DIR=%SCRIPT_DIR:~0,-1%

REM Find Houdini user directory
set HOUDINI_USER_DIR=
for %%v in (20.5 20.0 19.5) do (
    if exist "%USERPROFILE%\Documents\houdini%%v" (
        set HOUDINI_USER_DIR=%USERPROFILE%\Documents\houdini%%v
        goto found
    )
)

:found
if "%HOUDINI_USER_DIR%"=="" (
    echo Error: Could not find Houdini user directory
    echo Please manually add to houdini.env:
    echo   KARMALENTIL_PATH = "%SCRIPT_DIR%"
    pause
    exit /b 1
)

echo Found Houdini directory: %HOUDINI_USER_DIR%
echo.

echo Select installation method:
echo   1. Package file (recommended - automatic loading)
echo   2. houdini.env (manual - requires restart)
echo.
set /p choice="Choice [1]: "
if "%choice%"=="" set choice=1

if "%choice%"=="1" (
    REM Create packages directory
    if not exist "%HOUDINI_USER_DIR%\packages" mkdir "%HOUDINI_USER_DIR%\packages"

    REM Create package JSON
    set PACKAGE_FILE=%HOUDINI_USER_DIR%\packages\karmalentil.json

    (
        echo {
        echo     "env": [
        echo         {
        echo             "KARMALENTIL_PATH": "%SCRIPT_DIR:\=/%"
        echo         },
        echo         {
        echo             "KARMALENTIL": "$KARMALENTIL_PATH"
        echo         },
        echo         {
        echo             "HOUDINI_PATH": "$KARMALENTIL_PATH;&"
        echo         },
        echo         {
        echo             "PYTHONPATH": "$KARMALENTIL_PATH/python;&"
        echo         }
        echo     ]
        echo }
    ) > "%PACKAGE_FILE%"

    echo.
    echo Package file created: %PACKAGE_FILE%
    echo.
    echo Installation complete!
    echo.
    echo Next steps:
    echo   1. Launch Houdini
    echo   2. Find 'karmalentil' shelf
    echo   3. Click 'Lentil Camera' to create a camera
    echo.

) else if "%choice%"=="2" (
    REM Add to houdini.env
    set ENV_FILE=%HOUDINI_USER_DIR%\houdini.env

    REM Backup existing env file
    if exist "%ENV_FILE%" (
        copy "%ENV_FILE%" "%ENV_FILE%.backup" >nul
        echo Backed up existing houdini.env
    )

    REM Add KarmaLentil configuration
    (
        echo.
        echo # KarmaLentil - Polynomial Optics Plugin
        echo KARMALENTIL_PATH = "%SCRIPT_DIR:\=/%"
        echo KARMALENTIL = "$KARMALENTIL_PATH"
        echo HOUDINI_PATH = "$KARMALENTIL_PATH;&"
        echo PYTHONPATH = "$KARMALENTIL_PATH/python;&"
    ) >> "%ENV_FILE%"

    echo.
    echo Updated houdini.env: %ENV_FILE%
    echo.
    echo Installation complete!
    echo.
    echo Next steps:
    echo   1. Restart Houdini (required)
    echo   2. Find 'karmalentil' shelf
    echo   3. Click 'Lentil Camera' to create a camera
    echo.

) else (
    echo Invalid choice. Exiting.
    pause
    exit /b 1
)

echo ==========================================
echo For help, see: %SCRIPT_DIR%\README.md
echo ==========================================
echo.
pause
