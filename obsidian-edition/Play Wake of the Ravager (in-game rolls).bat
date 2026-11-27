@echo off
rem Starts Dark Sun: Wake of the Ravager (its folder found, or chosen on the Loader's Options tab) with
rem the in-game rolls, THAC0, saves and spell slots, and no Loader window (the dice log runs unseen
rem until the game closes).
pushd "%~dp0"
call "%~dp0dsloader\find-python.bat"
if errorlevel 1 exit /b 1
start "" %PYW% -m dsloader play --ravager
