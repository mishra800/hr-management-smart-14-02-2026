# 🚀 DevOps Team Handover Document

## 📦 Project Overview

**Project Name**: Smart HR Management System  
**Repository**: https://gitlab.dhanushinfotech.com/dhanush/dhanush_opensource/smart-hr-management-system  
**Architecture**: Microservices (Frontend + Backend + Database)  
**Deployment Method**: Docker Compose  

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│     Frontend (React 19 + Nginx)         │
│     Container: hr_frontend              │
│     Port: 80 (configurable)             │
│     Image: Custom (Node 20.19.0)        │
└─────────────────────────────────────────┘
                    ↓ HTTP
┌─────────────────────────────────────────┐
│     Backend (FastAPI + Python 3.13)     │
│     Container: hr_backend               │
│     Port: 8000 (configurable)           │
│     Image: Custom (Python 3.13-slim)    │
└─────────────────────────────────────────┘
                    ↓ PostgreSQL Protocol
┌─────────────────────────────────────────┐
│     Database (PostgreSQL 14)            │
│     Container: hr_postgres              │
│     Port: 5432 (configurable)           │
│     Image: postgres:14-alpine           │
└─────────────────────────────────────────┘
                    ↓ (Optional)
┌─────────────────────────────────────────┐
│     Cache (Redis 7)                     │
│     Container: hr_redis                 │
│     Port: 6379 (configurable)           │
│     Image: redis:7-alpine               │
└─────────────────────────────────────────┘
```

---

## 📁 Repository Structure

```
smart-hr-management-system/
├── backend/                    # FastAPI Backend
│   ├── app/                   # Application code
│   │   ├── routers/          # API endpoints (45+ files)
│   │   ├── models.py         # Database models (50+ tables)
│   │   ├── schemas.py        # Pydantic schemas
│   │   ├── database.py       # Database connection
│   │   └── ...
│   ├── Dockerfile            # Production Dockerfile
│   ├── Dockerfile.full       # With AI/ML dependencies
│   ├── requirements.txt      # Core dependencies
│   ├── requirements_full.txt # All dependencies
│   ├── main.py              # Application entry point
│   └── .env                 # Environment variables
│
├── frontend/                  # React Frontend
│   ├── src/                  # Source code
│   │   ├── pages/           # Page components (30+)
│   │   ├── components/      # Reusable components (100+)
│   │   ├── api/             # API client
│   │   └── ...
│   ├── Dockerfile           # Production Dockerfile
│   ├── nginx.conf           # Nginx configuration
│   ├── package.json         # Node dependencies
│   └── .env                 # Environment variables
│
├── docs/                     # Documentation
│   ├── GETTING_STARTED.md
│   └── DATABASE_SETUP.md
│
├── docker-compose.yml        # Production deployment
├── docker-compose.dev.yml    # Development deployment
├── .env.docker              # Environment template
├── .dockerignore            # Docker ignore rules
├── DOCKER_DEPLOYMENT.md     # Deployment guide
├── DEPLOYMENT_CHECKLIST.md  # Deployment checklist
└── check_dependencies.*     # Dependency check scripts
```

---

## 🔧 Technology Stack

### Backend
- **Language**: Python 3.13.7
- **Framework**: FastAPI 0.119.1
- **Server**: Uvicorn 0.38.0
- **ORM**: SQLAlchemy 2.0.44
- **Database Driver**: psycopg2-binary 2.9.11
- **Authentication**: JWT (python-jose 3.5.0)
- **Password Hashing**: bcrypt (passlib 1.7.4)

### Frontend
- **Language**: JavaScript/JSX
- **Framework**: React 19.2.0
- **Build Tool**: Vite 7.2.4
- **Styling**: Tailwind CSS 3.4.17
- **HTTP Client**: Axios 1.13.2
- **Routing**: React Router DOM 7.9.6
- **Web Server**: Nginx (Alpine)

### Database
- **RDBMS**: PostgreSQL 14
- **Tables**: 50+ tables
- **Features**: JSONB, Indexes, Foreign Keys, Triggers

### Cache (Optional)
- **Cache**: Redis 7
- **Use Cases**: Session storage, API caching

---

## 🚀 Deployment Instructions

### Quick Start
```bash
# 1. Clone repository
git clone https://gitlab.dhanushinfotech.com/dhanush/dhanush_opensource/smart-hr-management-system.git
cd smart-hr-management-system

# 2. Configure environment
cp .env.docker .env
nano .env  # Edit with your values

# 3. Run dependency check
./check_dependencies.sh  # Linux/Mac
.\check_dependencies.ps1  # Windows

# 4. Start services
docker-compose up -d

# 5. Initialize database
docker-compose exec backend alembic upgrade head
docker-compose exec backend python create_default_users.py

# 6. Access application
# Frontend: http://localhost
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Production Deployment
```bash
# Use production compose file
docker-compose -f docker-compose.yml up -d

# With custom environment
docker-compose --env-file .env.production up -d
```

### Development Deployment
```bash
# Use development compose file (with hot reload)
docker-compose -f docker-compose.dev.yml up -d
```

---

## 🔐 Environment Variables

### Critical Variables (MUST CONFIGURE)
```env
# Database
POSTGRES_PASSWORD=<strong-password>

# Backend Security
SECRET_KEY=<32-character-random-string>

# Environment
ENVIRONMENT=production
DEBUG=False
```

### Optional Variables
```env
# AI Features
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...

# Email
SMTP_USERNAME=...
SMTP_PASSWORD=...

# SMS/WhatsApp
TWILIO_ACCOUNT_SID=...
TWILIO_AUTH_TOKEN=...
```

See `.env.docker` for complete list.

---

## 📊 Resource Requirements

### Minimum Requirements
- **CPU**: 2 cores
- **RAM**: 4GB
- **Disk**: 20GB
- **Network**: 100 Mbps

### Recommended for Production
- **CPU**: 4+ cores
- **RAM**: 8GB+
- **Disk**: 50GB+ SSD
- **Network**: 1 Gbps

### Container Resource Limits
```yaml
backend:
  cpus: '2'
  memory: 2G

frontend:
  cpus: '1'
  memory: 512M

postgres:
  cpus: '2'
  memory: 2G
```

---

## 🔍 Monitoring & Health Checks

### Health Endpoints
- **Backend**: `http://localhost:8000/health`
- **Frontend**: `http://localhost:80`
- **Database**: `docker-compose exec postgres pg_isready`

### Container Health
```bash
# Check all containers
docker-compose ps

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres

# Resource usage
docker stats
```

### Application Metrics
- API response times: < 200ms (average)
- Page load times: < 3s
- Database queries: Optimized with indexes
- Concurrent users: 1000+ (with proper scaling)

---

## 🔄 Backup & Recovery

### Database Backup
```bash
# Manual backup
docker-compose exec postgres pg_dump -U postgres hr_management > backup_$(date +%Y%m%d).sql

# Automated backup (add to cron)
0 2 * * * cd /path/to/app && docker-compose exec -T postgres pg_dump -U postgres hr_management > /backups/hr_$(date +\%Y\%m\%d).sql
```

### Database Restore
```bash
# Restore from backup
docker-compose exec -T postgres psql -U postgres hr_management < backup_20260216.sql
```

### Volume Backup
```bash
# Backup volumes
docker run --rm -v hr_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_data.tar.gz /data

# Restore volumes
docker run --rm -v hr_postgres_data:/data -v $(pwd):/backup alpine tar xzf /backup/postgres_data.tar.gz -C /
```

---

## 🔧 Maintenance Tasks

### Daily
- Monitor container status
- Check error logs
- Verify disk space

### Weekly
- Review application logs
- Database performance check
- Security updates

### Monthly
- Update Docker images
- Backup verification
- Performance optimization
- Security audit

---

## 🐛 Common Issues & Solutions

### Issue: Backend won't start
```bash
# Check logs
docker-compose logs backend

# Solutions:
# 1. Database not ready - wait 30s
# 2. Port in use - change BACKEND_PORT
# 3. Missing deps - rebuild: docker-compose build backend
```

### Issue: Database connection failed
```bash
# Check database
docker-compose ps postgres
docker-compose logs postgres

# Test connection
docker-compose exec backend python -c "from app.database import test_db_connection; test_db_connection()"
```

### Issue: Frontend build fails
```bash
# Rebuild frontend
docker-compose build --no-cache frontend
docker-compose up -d frontend
```

### Issue: Out of disk space
```bash
# Clean up Docker
docker system prune -a
docker volume prune

# Remove old images
docker image prune -a
```

---

## 🔒 Security Considerations

### Production Security Checklist
- [ ] Change all default passwords
- [ ] Use strong SECRET_KEY (32+ chars)
- [ ] Set DEBUG=False
- [ ] Configure CORS properly
- [ ] Enable HTTPS
- [ ] Use Docker secrets
- [ ] Limit container resources
- [ ] Regular security updates
- [ ] Enable firewall
- [ ] Implement rate limiting
- [ ] Regular backups
- [ ] Monitor logs for suspicious activity

### Network Security
```bash
# Restrict database access
# Only allow backend container to access postgres

# Use Docker networks
# Containers communicate via internal network
# Only expose necessary ports to host
```

---

## 📈 Scaling Strategy

### Horizontal Scaling
```bash
# Scale backend instances
docker-compose up -d --scale backend=3

# Requires load balancer (Nginx/HAProxy)
```

### Vertical Scaling
```yaml
# Increase container resources
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 4G
```

### Database Scaling
- Read replicas for read-heavy workloads
- Connection pooling (PgBouncer)
- Query optimization
- Caching layer (Redis)

---

## 🔗 Integration Points

### External Services
- **Email**: SMTP (Gmail, SendGrid, etc.)
- **SMS**: Twilio
- **AI**: OpenAI, Google Gemini
- **OAuth**: LinkedIn
- **Storage**: Local filesystem (can be replaced with S3)

### API Endpoints
- **Base URL**: `http://localhost:8000`
- **Documentation**: `http://localhost:8000/docs`
- **Health Check**: `http://localhost:8000/health`
- **Total Endpoints**: 300+

---

## 📞 Support & Contacts

### Technical Contacts
- **DevOps Lead**: devops@company.com
- **Backend Team**: backend-team@company.com
- **Frontend Team**: frontend-team@company.com
- **DBA**: dba@company.com

### Documentation
- **Deployment Guide**: [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md)
- **Checklist**: [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)
- **Getting Started**: [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md)
- **Database Setup**: [docs/DATABASE_SETUP.md](docs/DATABASE_SETUP.md)

### Repository
- **GitLab**: https://gitlab.dhanushinfotech.com/dhanush/dhanush_opensource/smart-hr-management-system
- **Branch**: main (production-ready)

---

## ✅ Handover Checklist

- [ ] Repository access granted
- [ ] Environment variables documented
- [ ] Deployment scripts tested
- [ ] Backup procedures verified
- [ ] Monitoring setup complete
- [ ] Documentation reviewed
- [ ] Security measures implemented
- [ ] Team training completed
- [ ] Support contacts shared
- [ ] Runbook created

---

## 📝 Notes

### Known Limitations
- Face recognition features require additional dependencies (Dockerfile.full)
- AI features require API keys
- Email notifications require SMTP configuration

### Future Enhancements
- Kubernetes deployment manifests
- CI/CD pipeline integration
- Advanced monitoring (Prometheus/Grafana)
- Log aggregation (ELK stack)
- Auto-scaling configuration

---

**Handover Date**: 2026-02-16  
**Prepared By**: Development Team  
**Reviewed By**: _______________  
**Accepted By**: _______________  

---

**Status**: ✅ Ready for Production Deployment
