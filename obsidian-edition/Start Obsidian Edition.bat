@echo off
rem Opens the Loader. Its "Play Shattered Lands" button starts Dark Sun with the dice log.
pushd "%~dp0"
call "%~dp0dsloader\find-python.bat"
if errorlevel 1 exit /b 1
%PY% -m dsloader view
if errorlevel 1 pause
