# Production Deployment Checklist

## ✅ Changes Pushed to GitLab

Branch: `production-ready`
Remote: `gitlab` (https://gitlab.dhanushinfotech.com/dhanush/dhanush_opensource/smart-hr-management-system.git)

## What's Deployed

### Face Recognition Configuration
- ✅ Using **DeepFace** (not dlib - no build errors!)
- ✅ `requirements_full.txt` with face recognition dependencies
- ✅ `Dockerfile.full` configured for DeepFace
- ✅ `docker-compose.yml` uses Dockerfile.full
- ✅ `face_recognition_utils.py` rewritten for DeepFace

## Deployment Steps

### 1. On Production Server

```bash
# Clone/Pull latest code
git clone https://gitlab.dhanushinfotech.com/dhanush/dhanush_opensource/smart-hr-management-system.git
cd smart-hr-management-system
git checkout production-ready

# Or if already cloned:
git pull gitlab production-ready
```

### 2. Configure Environment

```bash
# Copy and edit environment file
cp .env.docker .env
nano .env

# Set these variables:
# - POSTGRES_PASSWORD (change from default!)
# - SECRET_KEY (generate new one!)
# - SMTP credentials (for emails)
# - API keys (optional: OPENAI_API_KEY, GEMINI_API_KEY)
```

### 3. Build and Deploy

```bash
# Build (first time: 5-10 minutes)
docker-compose build

# Start services
docker-compose up -d

# Check logs
docker logs hr_backend

# Should see: "INFO: DeepFace face recognition loaded successfully"
```

### 4. Initialize Database

```bash
# Run migrations
docker exec hr_backend alembic upgrade head

# Create default users
docker exec hr_backend python create_default_users.py

# Initialize capabilities
docker exec hr_backend python initialize_capabilities.py

# Optional: Create sample data
docker exec hr_backend python create_employee_records.py
docker exec hr_backend python create_sample_jobs.py
```

### 5. Verify Deployment

```bash
# Check all services are running
docker-compose ps

# Check backend health
curl http://localhost:8000/health

# Check frontend
curl http://localhost:80

# Check face recognition
docker logs hr_backend | grep -i "deepface\|face"
```

## Important Notes

### ✅ Correct Configuration

Your deployment **WILL USE**:
- `Dockerfile.full` (configured in docker-compose.yml)
- `requirements_full.txt` (referenced in Dockerfile.full)
- Face recognition with DeepFace

### Requirements Files

- `requirements.txt` - Basic deployment (no face recognition)
- `requirements_full.txt` - **YOUR DEPLOYMENT** (with face recognition)

### Build Time & Resources

- **First build**: 5-10 minutes (downloads TensorFlow models)
- **Subsequent builds**: 2-3 minutes (cached layers)
- **Docker image size**: ~2GB (includes TensorFlow)
- **RAM required**: 2GB minimum, 4GB recommended
- **CPU**: 2-4 cores recommended

### Face Recognition Performance

- Per verification: ~2-3 seconds
- Accuracy: High (Facenet model)
- Threshold: 60% match required (configurable)
- Models: Downloaded on first use (~100MB)

## Post-Deployment

### 1. Test Face Recognition

1. Login as admin
2. Go to employee profile
3. Upload profile photo
4. Mark attendance with photo
5. Verify face matching works

### 2. Monitor Logs

```bash
# Watch logs
docker logs -f hr_backend

# Check for errors
docker logs hr_backend | grep -i error

# Check face recognition
docker logs hr_backend | grep -i face
```

### 3. Performance Tuning

If slow:
- Reduce image sizes (max 800x800px)
- Increase server resources
- Consider GPU-enabled Docker

## Troubleshooting

### Build Fails

```bash
# Clean rebuild
docker-compose down -v
docker system prune -a
docker-compose build --no-cache
```

### Face Recognition Not Working

```bash
# Check if loaded
docker logs hr_backend | grep "DeepFace"

# Verify dependencies
docker exec hr_backend pip list | grep -E "deepface|tensorflow|opencv"

# Check profile images directory
docker exec hr_backend ls -la uploads/profile_images/
```

### Out of Memory

```bash
# Increase Docker memory limit
# Docker Desktop: Settings > Resources > Memory > 4GB+

# Or reduce workers in Dockerfile.full
# Change: --workers 2
# To:     --workers 1
```

## Rollback Plan

If face recognition causes issues:

```bash
# Edit docker-compose.yml
# Change: dockerfile: Dockerfile.full
# To:     dockerfile: Dockerfile

# Rebuild and restart
docker-compose build
docker-compose up -d
```

App will work without face recognition (attendance uses photo capture only).

## Security Checklist

- [ ] Changed default POSTGRES_PASSWORD
- [ ] Generated new SECRET_KEY
- [ ] Configured SMTP for emails
- [ ] Set up SSL/TLS (if using domain)
- [ ] Configured firewall rules
- [ ] Set up backups for postgres_data volume
- [ ] Reviewed CORS_ORIGINS setting

## Documentation

- **Quick Start**: `DEPLOY_WITH_FACE_RECOGNITION.md`
- **Face Recognition Details**: `FACE_RECOGNITION_ENABLED.md`
- **Alternative Options**: `FACE_RECOGNITION_SETUP.md`
- **Docker Guide**: `DOCKER_DEPLOYMENT.md`
- **DevOps Handover**: `DEVOPS_HANDOVER.md`

## Support

If you encounter issues:

1. Check logs: `docker logs hr_backend`
2. Review documentation files above
3. Verify environment variables in `.env`
4. Check system resources (RAM, disk space)

## Success Indicators

✅ All containers running: `docker-compose ps`
✅ Backend healthy: `curl http://localhost:8000/health`
✅ Frontend accessible: `http://localhost:80`
✅ Face recognition loaded: Check logs for "DeepFace"
✅ Database initialized: Default users created
✅ No errors in logs

---

**Deployment Date**: _____________
**Deployed By**: _____________
**Server**: _____________
**Notes**: _____________
