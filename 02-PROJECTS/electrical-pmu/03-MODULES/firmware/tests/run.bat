@echo off
REM ============================================================
REM  Build and run the ICU regression suite (415+ assertions).
REM  Run this after ANY change to cluster_core.h, stats.h,
REM  can_map.h, vehicle_model.h or channels.h.
REM
REM  Needs g++ on PATH — open the w64devkit shell first.
REM ============================================================
cd /d "%~dp0"
echo Building test.exe ...
g++ test_suite.cpp -o test.exe -std=c++17 -O2
if %ERRORLEVEL% NEQ 0 (
  echo BUILD FAILED — are you in the w64devkit shell?
  exit /b 1
)
test.exe
if %ERRORLEVEL% NEQ 0 (
  echo.
  echo *** TESTS FAILED — do not flash the Teensy until this is green ***
  exit /b 1
)
echo All tests passed.
