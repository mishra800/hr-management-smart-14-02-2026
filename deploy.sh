#!/bin/bash

# HR Management System - Production Deployment Script
# This script deploys the application using Docker Compose

set -e

echo "========================================"
echo "HR Management System - Production Deploy"
echo "========================================"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please copy .env.production to .env and configure it with your production values"
    exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running!"
    echo "Please start Docker and try again"
    exit 1
fi

# Load environment variables
source .env

# Validate critical environment variables
if [ "$SECRET_KEY" = "CHANGE_THIS_TO_SECURE_RANDOM_STRING_MIN_32_CHARS" ]; then
    echo "❌ Error: SECRET_KEY not configured!"
    echo "Please update SECRET_KEY in .env file"
    exit 1
fi

if [ "$POSTGRES_PASSWORD" = "CHANGE_THIS_SECURE_PASSWORD" ]; then
    echo "❌ Error: POSTGRES_PASSWORD not configured!"
    echo "Please update POSTGRES_PASSWORD in .env file"
    exit 1
fi

echo ""
echo "🔍 Pre-deployment checks..."
echo "✓ .env file found"
echo "✓ Docker is running"
echo "✓ Environment variables configured"

echo ""
echo "🛑 Stopping existing containers..."
docker-compose down

echo ""
echo "🧹 Cleaning up old images (optional)..."
read -p "Remove old Docker images? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker system prune -f
fi

echo ""
echo "🏗️  Building Docker images..."
docker-compose build --no-cache

echo ""
echo "🚀 Starting services..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be healthy..."
sleep 10

# Check service health
echo ""
echo "🏥 Checking service health..."

# Check PostgreSQL
if docker-compose ps | grep -q "postgres.*Up"; then
    echo "✓ PostgreSQL is running"
else
    echo "❌ PostgreSQL failed to start"
    docker-compose logs postgres
    exit 1
fi

# Check Backend
if docker-compose ps | grep -q "backend.*Up"; then
    echo "✓ Backend is running"
    
    # Wait for backend to be ready
    echo "⏳ Waiting for backend to be ready..."
    for i in {1..30}; do
        if curl -f http://localhost:${BACKEND_PORT:-8000}/health > /dev/null 2>&1; then
            echo "✓ Backend health check passed"
            break
        fi
        if [ $i -eq 30 ]; then
            echo "❌ Backend health check failed"
            docker-compose logs backend
            exit 1
        fi
        sleep 2
    done
else
    echo "❌ Backend failed to start"
    docker-compose logs backend
    exit 1
fi

# Check Frontend
if docker-compose ps | grep -q "frontend.*Up"; then
    echo "✓ Frontend is running"
else
    echo "❌ Frontend failed to start"
    docker-compose logs frontend
    exit 1
fi

echo ""
echo "========================================"
echo "✅ Deployment successful!"
echo "========================================"
echo ""
echo "📊 Service URLs:"
echo "   Frontend: http://localhost:${FRONTEND_PORT:-80}"
echo "   Backend:  http://localhost:${BACKEND_PORT:-8000}"
echo "   API Docs: http://localhost:${BACKEND_PORT:-8000}/docs"
echo ""
echo "📝 Useful commands:"
echo "   View logs:        docker-compose logs -f"
echo "   Stop services:    docker-compose down"
echo "   Restart services: docker-compose restart"
echo "   View status:      docker-compose ps"
echo ""
echo "🔐 Next steps:"
echo "   1. Initialize database: docker-compose exec backend python initialize_capabilities.py"
echo "   2. Create default users: docker-compose exec backend python create_default_users.py"
echo "   3. Access the application at http://localhost:${FRONTEND_PORT:-80}"
echo ""
