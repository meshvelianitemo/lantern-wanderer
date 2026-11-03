@echo off
set "GODOT=C:\Users\Administrator\Godot\Godot_v4.7.2-stable_win64.exe"
if not exist "%GODOT%" (
  echo Godot was not found at %GODOT%
  pause
  exit /b 1
)
start "" "%GODOT%" --path "%~dp0." -e
