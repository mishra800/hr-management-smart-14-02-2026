# 🐳 Docker Deployment Guide

Complete guide for deploying the Smart HR Management System using Docker.

## ⚠️ Important: Face Recognition

Face recognition is **disabled by default** to avoid complex build dependencies. The app works perfectly without it - attendance marking uses photo capture and all features work normally. See [FACE_RECOGNITION_SETUP.md](FACE_RECOGNITION_SETUP.md) if you need to enable it.

## 📋 Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- 4GB RAM minimum (8GB recommended)
- 20GB disk space

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone https://gitlab.dhanushinfotech.com/dhanush/dhanush_opensource/smart-hr-management-system.git
cd smart-hr-management-system
```

### 2. Configure Environment
```bash
# Copy environment template
cp .env.docker .env

# Edit .env with your configuration
nano .env  # or use your preferred editor
```

### 3. Start Services
```bash
# Production deployment (without face recognition)
docker-compose up -d

# Development deployment (with hot reload)
docker-compose -f docker-compose.dev.yml up -d
```

### 4. Initialize Database
```bash
# Run database migrations
docker-compose exec backend alembic upgrade head

# Create default users
docker-compose exec backend python create_default_users.py

# Initialize capabilities
docker-compose exec backend python initialize_capabilities.py

# (Optional) Create sample data
docker-compose exec backend python create_employee_records.py
docker-compose exec backend python create_sample_jobs.py
```

### 5. Access Application
- **Frontend**: http://localhost (or configured port)
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Database**: localhost:5432

## 📦 Services Overview

### Production Stack (docker-compose.yml)
```
┌─────────────────────────────────────────┐
│           Frontend (Nginx)              │
│         Port: 80 (configurable)         │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│        Backend API (FastAPI)            │
│         Port: 8000 (configurable)       │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│      PostgreSQL Database                │
│         Port: 5432 (configurable)       │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│      Redis Cache (Optional)             │
│         Port: 6379 (configurable)       │
└─────────────────────────────────────────┘
```

## 🔧 Configuration

### Environment Variables (.env)

#### Required Variables
```env
# Database
POSTGRES_DB=hr_management
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password

# Backend
SECRET_KEY=your-jwt-secret-key-min-32-chars
ENVIRONMENT=production
DEBUG=False

# Frontend
VITE_API_BASE_URL=http://localhost:8000
```

#### Optional Variables
```env
# AI Features
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...

# Email
SMTP_SERVER=smtp.gmail.com
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Twilio (SMS/WhatsApp)
TWILIO_ACCOUNT_SID=...
TWILIO_AUTH_TOKEN=...
```

## 🛠️ Docker Commands

### Service Management
```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Restart specific service
docker-compose restart backend

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# View all logs
docker-compose logs -f
```

### Container Management
```bash
# List running containers
docker-compose ps

# Execute command in container
docker-compose exec backend bash
docker-compose exec postgres psql -U postgres -d hr_management

# View resource usage
docker stats
```

### Database Operations
```bash
# Backup database
docker-compose exec postgres pg_dump -U postgres hr_management > backup.sql

# Restore database
docker-compose exec -T postgres psql -U postgres hr_management < backup.sql

# Access database shell
docker-compose exec postgres psql -U postgres -d hr_management
```

### Cleanup
```bash
# Stop and remove containers
docker-compose down

# Remove containers and volumes (WARNING: deletes data)
docker-compose down -v

# Remove all unused Docker resources
docker system prune -a
```

## 🔄 Updates & Maintenance

### Update Application
```bash
# Pull latest code
git pull origin main

# Rebuild and restart services
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Run migrations
docker-compose exec backend alembic upgrade head
```

### Scale Services
```bash
# Scale backend to 3 instances
docker-compose up -d --scale backend=3

# Note: Requires load balancer configuration
```

## 🐛 Troubleshooting

### Backend Won't Start
```bash
# Check logs
docker-compose logs backend

# Common issues:
# 1. Database not ready - wait 30 seconds and retry
# 2. Port already in use - change BACKEND_PORT in .env
# 3. Missing dependencies - rebuild: docker-compose build backend
```

### Database Connection Issues
```bash
# Check database is running
docker-compose ps postgres

# Test connection
docker-compose exec backend python -c "from app.database import test_db_connection; test_db_connection()"

# Check database logs
docker-compose logs postgres
```

### Frontend Build Fails
```bash
# Check Node version
docker-compose exec frontend node --version

# Rebuild frontend
docker-compose build --no-cache frontend
docker-compose up -d frontend
```

### Permission Issues
```bash
# Fix upload directory permissions
sudo chown -R 1000:1000 backend/uploads

# Fix log directory permissions
sudo chown -R 1000:1000 backend/logs
```

## 📊 Monitoring

### Health Checks
```bash
# Check service health
docker-compose ps

# Backend health endpoint
curl http://localhost:8000/health

# Frontend health
curl http://localhost:80
```

### Resource Monitoring
```bash
# Real-time resource usage
docker stats

# Container logs
docker-compose logs -f --tail=100
```

## 🔒 Security Best Practices

### Production Checklist
- [ ] Change default passwords in .env
- [ ] Use strong SECRET_KEY (min 32 characters)
- [ ] Set DEBUG=False
- [ ] Configure CORS_ORIGINS properly
- [ ] Use HTTPS in production
- [ ] Regular database backups
- [ ] Keep Docker images updated
- [ ] Limit container resources
- [ ] Use Docker secrets for sensitive data
- [ ] Enable firewall rules
- [ ] Regular security audits

### Secure Environment Variables
```bash
# Use Docker secrets (recommended for production)
echo "your_secret_password" | docker secret create postgres_password -

# Update docker-compose.yml to use secrets
```

## 🌐 Production Deployment

### With Reverse Proxy (Nginx/Traefik)
```nginx
# Nginx configuration example
server {
    listen 80;
    server_name hr.yourdomain.com;

    location / {
        proxy_pass http://localhost:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### SSL/TLS Configuration
```bash
# Using Let's Encrypt with Certbot
sudo certbot --nginx -d hr.yourdomain.com
```

### Docker Swarm (Multi-node)
```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml hr_stack

# Scale services
docker service scale hr_stack_backend=3
```

### Kubernetes Deployment
```bash
# Convert docker-compose to Kubernetes
kompose convert -f docker-compose.yml

# Apply to cluster
kubectl apply -f .
```

## 📈 Performance Optimization

### Database Optimization
```sql
-- Create indexes for better performance
CREATE INDEX idx_employees_email ON employees(email);
CREATE INDEX idx_attendance_date ON attendance(date);
CREATE INDEX idx_leave_requests_status ON leave_requests(status);
```

### Caching with Redis
```python
# Enable Redis caching in backend
# Update backend/app/cache.py
```

### Resource Limits
```yaml
# Add to docker-compose.yml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

## 🔄 CI/CD Integration

### GitLab CI Example
```yaml
# .gitlab-ci.yml
deploy:
  stage: deploy
  script:
    - docker-compose down
    - docker-compose pull
    - docker-compose up -d
  only:
    - main
```

### GitHub Actions Example
```yaml
# .github/workflows/deploy.yml
name: Deploy
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy
        run: |
          docker-compose down
          docker-compose up -d --build
```

## 📞 Support

For issues and questions:
- Check logs: `docker-compose logs -f`
- Review documentation: `/docs`
- Contact DevOps team

## 📝 Version Information

- Docker Compose Version: 3.8
- Python: 3.13.7
- Node.js: 20.19.0
- PostgreSQL: 14
- Redis: 7
- Nginx: Alpine

---

**Last Updated**: 2026-02-16
**Maintained By**: DevOps Team
