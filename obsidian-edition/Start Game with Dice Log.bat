@echo off
rem Starts Dark Sun with the dice log helper loaded, then opens the Loader.
cd /d "%~dp0"
call "%~dp0dsloader\find-python.bat"
if errorlevel 1 exit /b 1
%PY% -m dsloader launch
if errorlevel 1 pause
