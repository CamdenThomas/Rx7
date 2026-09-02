@echo off
REM ============================================================
REM  Build and run ALL firmware test suites:
REM    test_suite.cpp  — ICU renderer regression (415 assertions)
REM    test_bt817.cpp  — BT817 display driver, mocked SPI (35)
REM    test_dcu.cpp    — DCU climate/comfort logic (33)
REM  Run after ANY change to cluster_core.h, stats.h, can_map.h,
REM  bt817.h, climate.h, vehicle_model.h or channels.h.
REM
REM  Needs g++ on PATH — open the w64devkit shell first.
REM ============================================================
cd /d "%~dp0"

echo Building test.exe ...
g++ test_suite.cpp -o test.exe -std=c++17 -O2
if %ERRORLEVEL% NEQ 0 goto :buildfail
test.exe
if %ERRORLEVEL% NEQ 0 goto :testfail

echo Building test_bt817.exe ...
g++ test_bt817.cpp -o test_bt817.exe -std=c++17 -O2 -I..\icu
if %ERRORLEVEL% NEQ 0 goto :buildfail
test_bt817.exe
if %ERRORLEVEL% NEQ 0 goto :testfail

echo Building test_dcu.exe ...
g++ test_dcu.cpp -o test_dcu.exe -std=c++17 -O2 -I..\dcu
if %ERRORLEVEL% NEQ 0 goto :buildfail
test_dcu.exe
if %ERRORLEVEL% NEQ 0 goto :testfail

echo.
echo All suites passed.
exit /b 0

:buildfail
echo BUILD FAILED — are you in the w64devkit shell?
exit /b 1

:testfail
echo.
echo *** TESTS FAILED — do not flash a Teensy until this is green ***
exit /b 1
