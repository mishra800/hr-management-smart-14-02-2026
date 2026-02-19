# HR Management System - Production Deployment Script (PowerShell)
# This script deploys the application using Docker Compose

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "HR Management System - Production Deploy" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Check if .env file exists
if (-not (Test-Path .env)) {
    Write-Host "❌ Error: .env file not found!" -ForegroundColor Red
    Write-Host "Please copy .env.production to .env and configure it with your production values"
    exit 1
}

# Check if Docker is running
try {
    docker info | Out-Null
} catch {
    Write-Host "❌ Error: Docker is not running!" -ForegroundColor Red
    Write-Host "Please start Docker Desktop and try again"
    exit 1
}

# Load environment variables
Get-Content .env | ForEach-Object {
    if ($_ -match '^([^=]+)=(.*)$') {
        $name = $matches[1]
        $value = $matches[2]
        [Environment]::SetEnvironmentVariable($name, $value, "Process")
    }
}

# Validate critical environment variables
$SECRET_KEY = [Environment]::GetEnvironmentVariable("SECRET_KEY", "Process")
$POSTGRES_PASSWORD = [Environment]::GetEnvironmentVariable("POSTGRES_PASSWORD", "Process")

if ($SECRET_KEY -eq "CHANGE_THIS_TO_SECURE_RANDOM_STRING_MIN_32_CHARS") {
    Write-Host "❌ Error: SECRET_KEY not configured!" -ForegroundColor Red
    Write-Host "Please update SECRET_KEY in .env file"
    exit 1
}

if ($POSTGRES_PASSWORD -eq "CHANGE_THIS_SECURE_PASSWORD") {
    Write-Host "❌ Error: POSTGRES_PASSWORD not configured!" -ForegroundColor Red
    Write-Host "Please update POSTGRES_PASSWORD in .env file"
    exit 1
}

Write-Host ""
Write-Host "🔍 Pre-deployment checks..." -ForegroundColor Yellow
Write-Host "✓ .env file found" -ForegroundColor Green
Write-Host "✓ Docker is running" -ForegroundColor Green
Write-Host "✓ Environment variables configured" -ForegroundColor Green

Write-Host ""
Write-Host "🛑 Stopping existing containers..." -ForegroundColor Yellow
docker-compose down

Write-Host ""
Write-Host "🧹 Cleaning up old images (optional)..." -ForegroundColor Yellow
$cleanup = Read-Host "Remove old Docker images? (y/N)"
if ($cleanup -eq "y" -or $cleanup -eq "Y") {
    docker system prune -f
}

Write-Host ""
Write-Host "🏗️  Building Docker images..." -ForegroundColor Yellow
docker-compose build --no-cache

Write-Host ""
Write-Host "🚀 Starting services..." -ForegroundColor Yellow
docker-compose up -d

Write-Host ""
Write-Host "⏳ Waiting for services to be healthy..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Check service health
Write-Host ""
Write-Host "🏥 Checking service health..." -ForegroundColor Yellow

# Check PostgreSQL
$postgresStatus = docker-compose ps | Select-String "postgres.*Up"
if ($postgresStatus) {
    Write-Host "✓ PostgreSQL is running" -ForegroundColor Green
} else {
    Write-Host "❌ PostgreSQL failed to start" -ForegroundColor Red
    docker-compose logs postgres
    exit 1
}

# Check Backend
$backendStatus = docker-compose ps | Select-String "backend.*Up"
if ($backendStatus) {
    Write-Host "✓ Backend is running" -ForegroundColor Green
    
    # Wait for backend to be ready
    Write-Host "⏳ Waiting for backend to be ready..." -ForegroundColor Yellow
    $BACKEND_PORT = [Environment]::GetEnvironmentVariable("BACKEND_PORT", "Process")
    if (-not $BACKEND_PORT) { $BACKEND_PORT = "8000" }
    
    $ready = $false
    for ($i = 1; $i -le 30; $i++) {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:$BACKEND_PORT/health" -UseBasicParsing -TimeoutSec 2
            if ($response.StatusCode -eq 200) {
                Write-Host "✓ Backend health check passed" -ForegroundColor Green
                $ready = $true
                break
            }
        } catch {
            Start-Sleep -Seconds 2
        }
    }
    
    if (-not $ready) {
        Write-Host "❌ Backend health check failed" -ForegroundColor Red
        docker-compose logs backend
        exit 1
    }
} else {
    Write-Host "❌ Backend failed to start" -ForegroundColor Red
    docker-compose logs backend
    exit 1
}

# Check Frontend
$frontendStatus = docker-compose ps | Select-String "frontend.*Up"
if ($frontendStatus) {
    Write-Host "✓ Frontend is running" -ForegroundColor Green
} else {
    Write-Host "❌ Frontend failed to start" -ForegroundColor Red
    docker-compose logs frontend
    exit 1
}

$FRONTEND_PORT = [Environment]::GetEnvironmentVariable("FRONTEND_PORT", "Process")
if (-not $FRONTEND_PORT) { $FRONTEND_PORT = "80" }

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✅ Deployment successful!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📊 Service URLs:" -ForegroundColor Yellow
Write-Host "   Frontend: http://localhost:$FRONTEND_PORT"
Write-Host "   Backend:  http://localhost:$BACKEND_PORT"
Write-Host "   API Docs: http://localhost:$BACKEND_PORT/docs"
Write-Host ""
Write-Host "📝 Useful commands:" -ForegroundColor Yellow
Write-Host "   View logs:        docker-compose logs -f"
Write-Host "   Stop services:    docker-compose down"
Write-Host "   Restart services: docker-compose restart"
Write-Host "   View status:      docker-compose ps"
Write-Host ""
Write-Host "🔐 Next steps:" -ForegroundColor Yellow
Write-Host "   1. Initialize database: docker-compose exec backend python initialize_capabilities.py"
Write-Host "   2. Create default users: docker-compose exec backend python create_default_users.py"
Write-Host "   3. Access the application at http://localhost:$FRONTEND_PORT"
Write-Host ""
