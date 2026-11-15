@echo off
echo Running test suite inside Docker container...
docker compose run --rm test
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Tests failed or Docker is not running.
    echo.
    pause
    exit /b %errorlevel%
)
echo.
echo [OK] All tests finished successfully.
echo.
pause
