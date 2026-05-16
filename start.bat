@echo off
echo Starting Voz ciudadana System...
docker-compose up -d --build
echo System started successfully!
echo Frontend: http://localhost:3000
echo Backend: http://localhost:8000
pause
