@echo off
rem Starts Dark Sun: Wake of the Ravager (its folder found, or chosen on the Loader's Options tab),
rem then opens the Loader beside it.
pushd "%~dp0"
call "%~dp0dsloader\find-python.bat"
if errorlevel 1 exit /b 1
%PY% -m dsloader launch --ravager
if errorlevel 1 pause
