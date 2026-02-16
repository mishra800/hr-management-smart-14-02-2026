# PowerShell Dependency Check Script for Docker Deployment
# This script verifies all dependencies are properly configured for Windows

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "HR Management System - Dependency Check" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

$allChecksPass = $true

# Check Docker
Write-Host "Checking Docker..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version
    Write-Host "✓ Docker installed: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker not found. Please install Docker Desktop." -ForegroundColor Red
    $allChecksPass = $false
}

# Check Docker Compose
Write-Host "Checking Docker Compose..." -ForegroundColor Yellow
try {
    $composeVersion = docker-compose --version
    Write-Host "✓ Docker Compose installed: $composeVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker Compose not found. Please install Docker Compose." -ForegroundColor Red
    $allChecksPass = $false
}

# Check if Docker daemon is running
Write-Host "Checking Docker daemon..." -ForegroundColor Yellow
try {
    docker info | Out-Null
    Write-Host "✓ Docker daemon is running" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker daemon is not running. Please start Docker Desktop." -ForegroundColor Red
    $allChecksPass = $false
}

# Check required files
Write-Host ""
Write-Host "Checking required files..." -ForegroundColor Yellow

$files = @(
    "docker-compose.yml",
    "backend\Dockerfile",
    "backend\requirements.txt",
    "backend\main.py",
    "frontend\Dockerfile",
    "frontend\package.json",
    "frontend\nginx.conf"
)

foreach ($file in $files) {
    if (Test-Path $file) {
        Write-Host "✓ $file exists" -ForegroundColor Green
    } else {
        Write-Host "✗ $file not found" -ForegroundColor Red
        $allChecksPass = $false
    }
}

# Check environment file
Write-Host ""
Write-Host "Checking environment configuration..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "✓ .env file exists" -ForegroundColor Green
    
    $envContent = Get-Content .env -Raw
    
    if ($envContent -match "POSTGRES_PASSWORD" -and $envContent -notmatch "POSTGRES_PASSWORD=your_secure_password") {
        Write-Host "✓ Database password configured" -ForegroundColor Green
    } else {
        Write-Host "⚠ Warning: Please set POSTGRES_PASSWORD in .env" -ForegroundColor Yellow
    }
    
    if ($envContent -match "SECRET_KEY" -and $envContent -notmatch "SECRET_KEY=your-jwt-secret") {
        Write-Host "✓ JWT secret key configured" -ForegroundColor Green
    } else {
        Write-Host "⚠ Warning: Please set SECRET_KEY in .env" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠ .env file not found. Copying from .env.docker..." -ForegroundColor Yellow
    if (Test-Path ".env.docker") {
        Copy-Item .env.docker .env
        Write-Host "✓ Created .env from template" -ForegroundColor Green
        Write-Host "⚠ Please edit .env with your configuration" -ForegroundColor Yellow
    } else {
        Write-Host "✗ .env.docker template not found" -ForegroundColor Red
        $allChecksPass = $false
    }
}

# Check disk space
Write-Host ""
Write-Host "Checking disk space..." -ForegroundColor Yellow
$drive = Get-PSDrive -Name C
$freeSpaceGB = [math]::Round($drive.Free / 1GB, 2)
if ($freeSpaceGB -gt 20) {
    Write-Host "✓ Sufficient disk space: ${freeSpaceGB}GB available" -ForegroundColor Green
} else {
    Write-Host "⚠ Warning: Low disk space. ${freeSpaceGB}GB available (20GB recommended)" -ForegroundColor Yellow
}

# Check memory
Write-Host "Checking memory..." -ForegroundColor Yellow
$totalMemGB = [math]::Round((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB, 2)
if ($totalMemGB -ge 4) {
    Write-Host "✓ Sufficient memory: ${totalMemGB}GB" -ForegroundColor Green
} else {
    Write-Host "⚠ Warning: Low memory. ${totalMemGB}GB available (4GB minimum, 8GB recommended)" -ForegroundColor Yellow
}

# Check ports
Write-Host ""
Write-Host "Checking port availability..." -ForegroundColor Yellow
$ports = @(80, 8000, 5432, 6379)
foreach ($port in $ports) {
    $connection = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    if ($connection) {
        Write-Host "⚠ Port $port is already in use" -ForegroundColor Yellow
    } else {
        Write-Host "✓ Port $port is available" -ForegroundColor Green
    }
}

# Summary
Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Dependency Check Complete" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

if ($allChecksPass) {
    Write-Host "All checks passed! ✓" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "1. Review and update .env file with your configuration"
    Write-Host "2. Run: docker-compose up -d"
    Write-Host "3. Initialize database: docker-compose exec backend python create_default_users.py"
    Write-Host "4. Access application at http://localhost"
} else {
    Write-Host "Some checks failed. Please fix the issues above." -ForegroundColor Red
    exit 1
}

Write-Host ""
