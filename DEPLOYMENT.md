# HR Management System - Production Deployment Guide

## Prerequisites

- Docker and Docker Compose installed
- Minimum 4GB RAM, 20GB disk space
- PostgreSQL database (can use Docker container)
- Domain name (optional, for production)

## Quick Start

### 1. Clone and Configure

```bash
# Clone the repository
git clone <repository-url>
cd smart-hr-management-system

# Copy environment template
cp .env.example .env

# Edit .env with your production values
nano .env  # or use your preferred editor
```

### 2. Configure Environment Variables

**Critical variables to update in `.env`:**

```bash
# Generate a secure SECRET_KEY (minimum 32 characters)
SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")

# Set a strong PostgreSQL password
POSTGRES_PASSWORD=<your-secure-password>

# Update database URL with your password
DATABASE_URL=postgresql://postgres:<your-secure-password>@postgres:5432/hr_management

# Set your domain or IP
VITE_API_BASE_URL=http://your-domain.com:8000
CORS_ORIGINS=http://your-domain.com,https://your-domain.com

# Configure email (for notifications)
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-specific-password
FROM_EMAIL=noreply@yourcompany.com
```

### 3. Deploy

**Linux/Mac:**
```bash
chmod +x deploy.sh
./deploy.sh
```

**Windows:**
```powershell
.\deploy.ps1
```

### 4. Initialize Database

```bash
# Initialize capabilities and permissions
docker-compose exec backend python initialize_capabilities.py

# Create default admin user
docker-compose exec backend python create_default_users.py

# (Optional) Create sample data
docker-compose exec backend python create_employee_records.py
docker-compose exec backend python create_sample_jobs.py
```

### 5. Access the Application

- **Frontend:** http://localhost (or your domain)
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs

**Default Login:**
- Email: `admin@company.com`
- Password: `admin123` (change immediately!)

## Production Checklist

### Security

- [ ] Change default SECRET_KEY to a secure random string
- [ ] Set strong POSTGRES_PASSWORD
- [ ] Change default admin password after first login
- [ ] Set DEBUG=False in backend .env
- [ ] Configure CORS_ORIGINS to only allow your domain
- [ ] Enable HTTPS (use reverse proxy like Nginx)
- [ ] Set up firewall rules
- [ ] Enable database backups

### Configuration

- [ ] Configure SMTP for email notifications
- [ ] Set up proper domain name
- [ ] Configure SSL certificates
- [ ] Set up monitoring and logging
- [ ] Configure backup strategy

### Optional Features

- [ ] Configure AI features (OpenAI/Gemini API keys)
- [ ] Set up Twilio for SMS/WhatsApp notifications
- [ ] Configure LinkedIn OAuth for one-click apply
- [ ] Enable face recognition (requires additional setup)

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Frontend  │────▶│   Backend   │────▶│  PostgreSQL │
│   (React)   │     │  (FastAPI)  │     │  Database   │
│   Port 80   │     │  Port 8000  │     │  Port 5432  │
└─────────────┘     └─────────────┘     └─────────────┘
                            │
                            ▼
                    ┌─────────────┐
                    │    Redis    │
                    │  (Optional) │
                    │  Port 6379  │
                    └─────────────┘
```

## Docker Services

### PostgreSQL
- **Image:** postgres:14-alpine
- **Port:** 5432
- **Volume:** postgres_data
- **Health Check:** Enabled

### Backend
- **Build:** backend/Dockerfile.full
- **Port:** 8000
- **Features:** FastAPI, Face Recognition (DeepFace), AI Integration
- **Workers:** 2 (configurable)
- **Health Check:** /health endpoint

### Frontend
- **Build:** frontend/Dockerfile
- **Port:** 80
- **Server:** Nginx
- **Features:** React, Vite, Responsive UI

### Redis (Optional)
- **Image:** redis:7-alpine
- **Port:** 6379
- **Volume:** redis_data
- **Use:** Caching, sessions

## Management Commands

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres
```

### Restart Services
```bash
# All services
docker-compose restart

# Specific service
docker-compose restart backend
```

### Stop Services
```bash
docker-compose down
```

### Update Application
```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Database Backup
```bash
# Backup
docker-compose exec postgres pg_dump -U postgres hr_management > backup.sql

# Restore
docker-compose exec -T postgres psql -U postgres hr_management < backup.sql
```

### Access Database
```bash
docker-compose exec postgres psql -U postgres -d hr_management
```

### Execute Python Scripts
```bash
docker-compose exec backend python <script-name>.py
```

## Monitoring

### Health Checks

- **Backend:** http://localhost:8000/health
- **Frontend:** http://localhost
- **Database:** `docker-compose exec postgres pg_isready`

### Service Status
```bash
docker-compose ps
```

### Resource Usage
```bash
docker stats
```

## Troubleshooting

### Backend won't start
```bash
# Check logs
docker-compose logs backend

# Common issues:
# - Database connection failed: Check DATABASE_URL
# - Port already in use: Change BACKEND_PORT in .env
# - Missing dependencies: Rebuild with --no-cache
```

### Frontend won't start
```bash
# Check logs
docker-compose logs frontend

# Common issues:
# - Build failed: Check Node.js version
# - API connection failed: Check VITE_API_BASE_URL
# - Port already in use: Change FRONTEND_PORT in .env
```

### Database connection issues
```bash
# Check database status
docker-compose exec postgres pg_isready

# Check connection from backend
docker-compose exec backend python -c "from app.database import test_db_connection; test_db_connection()"

# Reset database (WARNING: deletes all data)
docker-compose down -v
docker-compose up -d
```

### Performance issues
```bash
# Increase backend workers (edit docker-compose.yml)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]

# Allocate more resources to Docker
# Docker Desktop → Settings → Resources
```

## Scaling

### Horizontal Scaling

Use Docker Swarm or Kubernetes for multi-instance deployment:

```bash
# Docker Swarm example
docker swarm init
docker stack deploy -c docker-compose.yml hr-system
```

### Load Balancing

Add Nginx reverse proxy for load balancing:

```nginx
upstream backend {
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
}

server {
    listen 80;
    location /api {
        proxy_pass http://backend;
    }
}
```

## Security Best Practices

1. **Use HTTPS in production**
   - Set up SSL certificates (Let's Encrypt)
   - Configure reverse proxy (Nginx/Traefik)

2. **Secure database**
   - Use strong passwords
   - Restrict network access
   - Enable SSL connections

3. **Regular updates**
   - Keep Docker images updated
   - Update dependencies regularly
   - Monitor security advisories

4. **Backup strategy**
   - Automated daily backups
   - Off-site backup storage
   - Test restore procedures

5. **Monitoring**
   - Set up logging (ELK stack)
   - Monitor resource usage
   - Set up alerts

## Support

For issues and questions:
- Check logs: `docker-compose logs -f`
- Review documentation
- Check GitHub issues
- Contact support team

## License

[Your License Here]
