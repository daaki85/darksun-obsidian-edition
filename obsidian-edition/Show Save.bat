@echo off
rem Drag a SAVEnn.SAV file onto this file to see the party stored in it.
cd /d "%~dp0"
call "%~dp0dsloader\find-python.bat"
if errorlevel 1 exit /b 1
if "%~1"=="" (
  echo Drag a save file such as SAVE01.SAV onto "Show Save.bat" to see its party.
  pause
  exit /b 1
)
%PY% -m dsloader save "%~1"
pause
