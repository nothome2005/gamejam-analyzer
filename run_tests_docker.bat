@echo off
chcp 65001 > nul
echo Запуск 41 тесту всередині Docker контейнера...
docker compose run --rm test
echo.
pause
