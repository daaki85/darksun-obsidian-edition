@echo off
rem Opens the Loader. Its "Start the game" button starts Dark Sun with the dice log.
cd /d "%~dp0"
call "%~dp0dsloader\find-python.bat"
if errorlevel 1 exit /b 1
%PY% -m dsloader view
if errorlevel 1 pause
