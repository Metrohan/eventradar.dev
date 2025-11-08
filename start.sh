#!/bin/bash

echo "🚀 Starting TechEventRadar - Modern Full-Stack Application"
echo "=================================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Create necessary directories
mkdir -p backend/instance
mkdir -p frontend/public/images

# Copy static files to frontend public directory
if [ -d "static/images" ]; then
    cp -r static/images/* frontend/public/ 2>/dev/null || true
fi

echo "📦 Building and starting services with Docker Compose..."
docker-compose up --build -d

echo "⏳ Waiting for services to be ready..."
sleep 10

echo "✅ Services started successfully!"
echo ""
echo "🌐 Access your application:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Documentation: http://localhost:8000/docs"
echo ""
echo "🔧 Admin Login:"
echo "   Username: admin"
echo "   Password: password"
echo ""
echo "📊 To view logs: docker-compose logs -f"
echo "🛑 To stop: docker-compose down"


