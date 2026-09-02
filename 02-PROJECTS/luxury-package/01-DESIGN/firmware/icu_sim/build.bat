@echo off
REM ============================================================
REM  Build the RX-7 ICU cluster simulator
REM
REM  Needs g++. If you don't have one, get w64devkit:
REM    https://github.com/skeeto/w64devkit/releases
REM    Download the .zip, unzip to C:\w64devkit, run w64devkit.exe,
REM    then cd here and run:  ./build.bat
REM
REM  No SDL, no libraries to install. Only gdi32/user32, which are
REM  already on every Windows machine.
REM ============================================================

echo Building sim.exe ...
g++ sim_win32.cpp -o sim.exe -std=c++17 -O2 -lgdi32 -luser32

if %ERRORLEVEL% NEQ 0 (
  echo.
  echo BUILD FAILED.
  echo   - "g++ is not recognized"    ^-^-^>  you are not in the w64devkit shell
  echo   - "cluster_core.h not found" ^-^-^>  the ..\icu folder must be beside this one
  exit /b 1
)

echo.
echo Built sim.exe   -   run it with:   sim.exe
