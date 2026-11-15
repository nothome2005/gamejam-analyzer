@echo off
chcp 65001 > nul
echo Запуск Game Jam Analyzer у Docker контейнері...
docker compose up -d
echo.
echo Сервер запущено!
echo Відкриття Swagger UI у браузері...
start http://localhost:8000/docs
echo.
echo Щоб переглядати логи в реальному часі, виконайте:
echo   docker compose logs -f api
echo.
pause
