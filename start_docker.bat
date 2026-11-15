@echo off
echo Starting Game Jam Analyzer in Docker...
docker compose up -d
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Failed to start Docker. Please ensure Docker Desktop is running.
    echo.
    pause
    exit /b %errorlevel%
)
echo.
echo [OK] Server is running!
echo Opening Swagger UI at http://localhost:8000/docs ...
start http://localhost:8000/docs
echo.
echo To inspect live logs, run:
echo   docker compose logs -f api
echo.
pause
