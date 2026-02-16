# 📋 Docker Deployment Checklist

Complete checklist for deploying Smart HR Management System with Docker.

## ✅ Pre-Deployment Checklist

### 1. System Requirements
- [ ] Docker Engine 20.10+ installed
- [ ] Docker Compose 2.0+ installed
- [ ] Minimum 4GB RAM (8GB recommended)
- [ ] Minimum 20GB free disk space
- [ ] Ports available: 80, 8000, 5432, 6379

### 2. Files Verification
- [ ] `docker-compose.yml` exists
- [ ] `backend/Dockerfile` exists
- [ ] `backend/requirements.txt` exists
- [ ] `frontend/Dockerfile` exists
- [ ] `frontend/nginx.conf` exists
- [ ] `.env.docker` template exists

### 3. Configuration
- [ ] Copy `.env.docker` to `.env`
- [ ] Set `POSTGRES_PASSWORD` (strong password)
- [ ] Set `SECRET_KEY` (min 32 characters)
- [ ] Configure `CORS_ORIGINS` for your domain
- [ ] Set `VITE_API_BASE_URL` to your backend URL
- [ ] Review all environment variables

### 4. Optional Services
- [ ] Configure SMTP for email notifications
- [ ] Add OpenAI API key (if using AI features)
- [ ] Add Gemini API key (alternative AI)
- [ ] Configure Twilio (if using SMS/WhatsApp)
- [ ] Set up LinkedIn OAuth (if using one-click apply)

## 🚀 Deployment Steps

### Step 1: Run Dependency Check
```bash
# Windows
.\check_dependencies.ps1

# Linux/Mac
chmod +x check_dependencies.sh
./check_dependencies.sh
```
- [ ] All checks passed

### Step 2: Build and Start Services
```bash
# Production
docker-compose up -d

# Development (with hot reload)
docker-compose -f docker-compose.dev.yml up -d
```
- [ ] All containers started successfully
- [ ] No error messages in logs

### Step 3: Verify Services
```bash
# Check container status
docker-compose ps
```
- [ ] postgres: healthy
- [ ] backend: healthy
- [ ] frontend: healthy
- [ ] redis: healthy (if enabled)

### Step 4: Initialize Database
```bash
# Run migrations
docker-compose exec backend alembic upgrade head

# Create default users
docker-compose exec backend python create_default_users.py

# (Optional) Create sample data
docker-compose exec backend python create_employee_records.py
docker-compose exec backend python create_sample_jobs.py
```
- [ ] Migrations completed
- [ ] Default users created
- [ ] Sample data loaded (optional)

### Step 5: Test Application
- [ ] Frontend accessible at http://localhost
- [ ] Backend API accessible at http://localhost:8000
- [ ] API docs accessible at http://localhost:8000/docs
- [ ] Can login with default credentials
- [ ] Dashboard loads correctly

## 🔒 Security Checklist

### Production Security
- [ ] Changed all default passwords
- [ ] Generated strong SECRET_KEY (32+ characters)
- [ ] Set DEBUG=False
- [ ] Configured proper CORS_ORIGINS
- [ ] Enabled HTTPS (if applicable)
- [ ] Configured firewall rules
- [ ] Limited container resources
- [ ] Enabled Docker secrets (recommended)
- [ ] Regular backup schedule configured
- [ ] Monitoring and logging enabled

### Database Security
- [ ] Strong database password
- [ ] Database not exposed to public internet
- [ ] Regular backups configured
- [ ] Backup restoration tested
- [ ] Database encryption enabled (if required)

### Application Security
- [ ] JWT tokens expire properly
- [ ] Password hashing verified
- [ ] File upload restrictions configured
- [ ] Rate limiting enabled (if applicable)
- [ ] Input validation working
- [ ] XSS protection enabled
- [ ] CSRF protection enabled

## 📊 Post-Deployment Verification

### Functional Testing
- [ ] User registration works
- [ ] User login works
- [ ] Dashboard displays correctly
- [ ] Employee management functional
- [ ] Attendance system working
- [ ] Leave management operational
- [ ] Recruitment system functional
- [ ] File uploads working
- [ ] Email notifications sending (if configured)

### Performance Testing
- [ ] Page load times acceptable (< 3s)
- [ ] API response times good (< 200ms)
- [ ] Database queries optimized
- [ ] No memory leaks
- [ ] CPU usage normal
- [ ] Disk usage monitored

### Monitoring Setup
- [ ] Container logs accessible
- [ ] Health checks responding
- [ ] Resource usage monitored
- [ ] Error tracking configured
- [ ] Backup verification automated
- [ ] Alert system configured

## 🔄 Maintenance Checklist

### Daily
- [ ] Check container status
- [ ] Review error logs
- [ ] Monitor disk space
- [ ] Verify backups completed

### Weekly
- [ ] Review application logs
- [ ] Check database performance
- [ ] Verify backup integrity
- [ ] Update security patches

### Monthly
- [ ] Update Docker images
- [ ] Review and rotate logs
- [ ] Performance optimization
- [ ] Security audit
- [ ] Backup restoration test

## 🐛 Troubleshooting Checklist

### If Backend Won't Start
- [ ] Check logs: `docker-compose logs backend`
- [ ] Verify database is running
- [ ] Check environment variables
- [ ] Verify port 8000 is available
- [ ] Rebuild container: `docker-compose build backend`

### If Frontend Won't Load
- [ ] Check logs: `docker-compose logs frontend`
- [ ] Verify backend is accessible
- [ ] Check VITE_API_BASE_URL configuration
- [ ] Verify port 80 is available
- [ ] Clear browser cache

### If Database Connection Fails
- [ ] Check postgres container: `docker-compose ps postgres`
- [ ] Verify DATABASE_URL in .env
- [ ] Check database logs: `docker-compose logs postgres`
- [ ] Test connection: `docker-compose exec postgres psql -U postgres`
- [ ] Verify network connectivity

### If Performance is Slow
- [ ] Check resource usage: `docker stats`
- [ ] Review database queries
- [ ] Check disk space
- [ ] Verify network latency
- [ ] Consider scaling services

## 📝 Default Credentials

### Application Users
| Role | Email | Password |
|------|-------|----------|
| Super Admin | admin@company.com | admin123 |
| HR Manager | hr@company.com | hr123 |
| Manager | manager@company.com | manager123 |
| Employee | employee@company.com | emp123 |

⚠️ **IMPORTANT**: Change these passwords immediately after first login!

### Database
- **Username**: postgres (or from .env)
- **Password**: Set in .env file
- **Database**: hr_management (or from .env)

## 🎯 Success Criteria

Deployment is successful when:
- [ ] All containers running and healthy
- [ ] Application accessible via browser
- [ ] Users can login successfully
- [ ] All core features functional
- [ ] No critical errors in logs
- [ ] Performance meets requirements
- [ ] Security measures in place
- [ ] Backups configured and tested
- [ ] Monitoring and alerts active
- [ ] Documentation updated

## 📞 Support Contacts

- **DevOps Team**: devops@company.com
- **Backend Issues**: backend-team@company.com
- **Frontend Issues**: frontend-team@company.com
- **Database Issues**: dba@company.com

## 📚 Additional Resources

- [Docker Deployment Guide](DOCKER_DEPLOYMENT.md)
- [Getting Started Guide](docs/GETTING_STARTED.md)
- [Database Setup Guide](docs/DATABASE_SETUP.md)
- [API Documentation](http://localhost:8000/docs)

---

**Deployment Date**: _____________
**Deployed By**: _____________
**Environment**: Production / Staging / Development
**Version**: _____________

**Sign-off**:
- DevOps Lead: _____________
- Technical Lead: _____________
- Project Manager: _____________
