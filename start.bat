@echo off
echo 🚀 Starting TechEventRadar - Modern Full-Stack Application
echo ==================================================

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not running. Please start Docker and try again.
    pause
    exit /b 1
)

REM Create necessary directories
if not exist "backend\instance" mkdir backend\instance
if not exist "frontend\public\images" mkdir frontend\public\images

REM Copy static files to frontend public directory
if exist "static\images" (
    xcopy "static\images\*" "frontend\public\" /E /I /Y >nul 2>&1
)

echo 📦 Building and starting services with Docker Compose...
docker-compose up --build -d

echo ⏳ Waiting for services to be ready...
timeout /t 10 /nobreak >nul

echo ✅ Services started successfully!
echo.
echo 🌐 Access your application:
echo    Frontend: http://localhost:3000
echo    Backend API: http://localhost:8000
echo    API Documentation: http://localhost:8000/docs
echo.
echo 🔧 Admin Login:
echo    Username: admin
echo    Password: password
echo.
echo 📊 To view logs: docker-compose logs -f
echo 🛑 To stop: docker-compose down
echo.
pause


