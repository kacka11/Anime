@echo off
chcp 65001 >nul
set NAPCAT_DIR=D:\QQNT\versions\9.9.29-47354\resources\app\napcat
set QQ_PATH=D:\QQNT\QQ.exe

echo Starting QQ with NapCat...
start "" "%NAPCAT_DIR%\napimain.exe" "%QQ_PATH%" "%NAPCAT_DIR%\napiloader.dll" "%NAPCAT_DIR%\nativeLoader.cjs"
echo.
echo NapCat starting... Please wait for QQ to login.
echo Once QQ is logged in, OneBot HTTP API will be available at http://localhost:3000
echo.
echo You can check the dashboard at http://localhost:6099
pause
