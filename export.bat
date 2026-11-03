@echo off
rem Builds a standalone game: export\LanternWanderer.exe (one file, no Godot needed to play it).
set "GODOT=C:\Users\Administrator\Godot\Godot_v4.7.2-stable_win64_console.exe"
if not exist "%GODOT%" (
  echo Godot was not found at %GODOT%
  pause
  exit /b 1
)
cd /d "%~dp0"
if not exist export mkdir export
if not exist export\.gdignore type nul > export\.gdignore
"%GODOT%" --headless --path . --export-release "Windows Desktop" export/LanternWanderer.exe
echo.
echo Done: %~dp0export\LanternWanderer.exe
pause
