#!/bin/bash

# Dependency Check Script for Docker Deployment
# This script verifies all dependencies are properly configured

echo "=========================================="
echo "HR Management System - Dependency Check"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Docker
echo "Checking Docker..."
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version)
    echo -e "${GREEN}✓${NC} Docker installed: $DOCKER_VERSION"
else
    echo -e "${RED}✗${NC} Docker not found. Please install Docker."
    exit 1
fi

# Check Docker Compose
echo "Checking Docker Compose..."
if command -v docker-compose &> /dev/null; then
    COMPOSE_VERSION=$(docker-compose --version)
    echo -e "${GREEN}✓${NC} Docker Compose installed: $COMPOSE_VERSION"
else
    echo -e "${RED}✗${NC} Docker Compose not found. Please install Docker Compose."
    exit 1
fi

# Check if Docker daemon is running
echo "Checking Docker daemon..."
if docker info &> /dev/null; then
    echo -e "${GREEN}✓${NC} Docker daemon is running"
else
    echo -e "${RED}✗${NC} Docker daemon is not running. Please start Docker."
    exit 1
fi

# Check required files
echo ""
echo "Checking required files..."

FILES=(
    "docker-compose.yml"
    "backend/Dockerfile"
    "backend/requirements.txt"
    "backend/main.py"
    "frontend/Dockerfile"
    "frontend/package.json"
    "frontend/nginx.conf"
)

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $file exists"
    else
        echo -e "${RED}✗${NC} $file not found"
        exit 1
    fi
done

# Check environment file
echo ""
echo "Checking environment configuration..."
if [ -f ".env" ]; then
    echo -e "${GREEN}✓${NC} .env file exists"
    
    # Check critical variables
    if grep -q "POSTGRES_PASSWORD" .env && ! grep -q "POSTGRES_PASSWORD=your_secure_password" .env; then
        echo -e "${GREEN}✓${NC} Database password configured"
    else
        echo -e "${YELLOW}⚠${NC} Warning: Please set POSTGRES_PASSWORD in .env"
    fi
    
    if grep -q "SECRET_KEY" .env && ! grep -q "SECRET_KEY=your-jwt-secret" .env; then
        echo -e "${GREEN}✓${NC} JWT secret key configured"
    else
        echo -e "${YELLOW}⚠${NC} Warning: Please set SECRET_KEY in .env"
    fi
else
    echo -e "${YELLOW}⚠${NC} .env file not found. Copying from .env.docker..."
    if [ -f ".env.docker" ]; then
        cp .env.docker .env
        echo -e "${GREEN}✓${NC} Created .env from template"
        echo -e "${YELLOW}⚠${NC} Please edit .env with your configuration"
    else
        echo -e "${RED}✗${NC} .env.docker template not found"
        exit 1
    fi
fi

# Check disk space
echo ""
echo "Checking disk space..."
AVAILABLE_SPACE=$(df -BG . | tail -1 | awk '{print $4}' | sed 's/G//')
if [ "$AVAILABLE_SPACE" -gt 20 ]; then
    echo -e "${GREEN}✓${NC} Sufficient disk space: ${AVAILABLE_SPACE}GB available"
else
    echo -e "${YELLOW}⚠${NC} Warning: Low disk space. ${AVAILABLE_SPACE}GB available (20GB recommended)"
fi

# Check memory
echo "Checking memory..."
TOTAL_MEM=$(free -g | awk '/^Mem:/{print $2}')
if [ "$TOTAL_MEM" -ge 4 ]; then
    echo -e "${GREEN}✓${NC} Sufficient memory: ${TOTAL_MEM}GB"
else
    echo -e "${YELLOW}⚠${NC} Warning: Low memory. ${TOTAL_MEM}GB available (4GB minimum, 8GB recommended)"
fi

# Check ports
echo ""
echo "Checking port availability..."
PORTS=(80 8000 5432 6379)
for port in "${PORTS[@]}"; do
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠${NC} Port $port is already in use"
    else
        echo -e "${GREEN}✓${NC} Port $port is available"
    fi
done

# Summary
echo ""
echo "=========================================="
echo "Dependency Check Complete"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Review and update .env file with your configuration"
echo "2. Run: docker-compose up -d"
echo "3. Initialize database: docker-compose exec backend python create_default_users.py"
echo "4. Access application at http://localhost"
echo ""
