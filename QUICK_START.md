# 🚀 Quick Start Guide

## Prerequisites

- Docker & Docker Compose (recommended)
- OR: Python 3.10+, Node.js 20+, PostgreSQL 14+

## 1. Setup Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your configuration
# Update DATABASE_URL, SECRET_KEY, etc.

# Verify configuration
python verify_env.py
```

## 2. Start Application

### Using Docker (Recommended):
```bash
# Deploy everything
docker-compose up -d

# Initialize database
docker-compose exec backend python initialize_capabilities.py
docker-compose exec backend python create_default_users.py
```

### Manual Setup:
```bash
# Backend
cd backend
python main.py

# Frontend (in another terminal)
cd frontend
npm install
npm run dev
```

## 3. Access Application

- **Frontend**: http://localhost:5173 (dev) or http://localhost (production)
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 4. Login

### Default Accounts:

| Email | Password | Role |
|-------|----------|------|
| admin@company.com | admin123 | Admin |
| hr@company.com | hr123 | HR |
| manager@company.com | manager123 | Manager |
| employee@company.com | password123 | Employee |

**⚠️ Change these passwords immediately in production!**

## 5. After Deployment

When you deploy and get URLs, update `.env`:

```env
# Your backend URL
VITE_API_BASE_URL=https://your-backend-url.com

# Your frontend URL
APP_BASE_URL=https://your-frontend-url.com

# Both URLs for CORS
CORS_ORIGINS=https://your-frontend-url.com,https://your-backend-url.com

# Production settings
DEBUG=False
ENVIRONMENT=production
```

Then restart:
```bash
docker-compose restart
```

## Troubleshooting

### Backend won't start
```bash
# Check database connection
python verify_env.py

# View logs
docker-compose logs backend
```

### Frontend can't connect
```bash
# Check VITE_API_BASE_URL in .env
cat .env | grep VITE_API_BASE_URL

# Restart frontend
docker-compose restart frontend
```

### CORS errors
Add your frontend domain to `CORS_ORIGINS` in `.env`

## More Documentation

- **README.md** - Full project overview
- **DEPLOYMENT.md** - Detailed deployment guide
- **URL_CONFIGURATION_SIMPLE.md** - URL configuration guide
- **QUICK_DEPLOYMENT_CHECKLIST.md** - Deployment checklist
- **CHANGELOG.md** - Version history

## Need Help?

Run the verification script:
```bash
python verify_env.py
```

It will check your configuration and show what's missing.
