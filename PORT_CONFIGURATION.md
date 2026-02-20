# Port Configuration Reference

## 🎯 Standard Ports

```
Frontend: Port 3000
Backend:  Port 8000
```

## ✅ Current Configuration

### Frontend (Port 3000)
- Production build runs on port 3000
- Vite dev server runs on port 5173 (development only)
- Both work with the same backend

### Backend (Port 8000)
- API server runs on port 8000
- All API endpoints accessible at port 8000

## 🌐 Access URLs

### Local Development:
```
Frontend:  http://localhost:3000
Backend:   http://localhost:8000
Dev Server: http://localhost:5173 (Vite)
```

### Network Access:
```
Frontend:  http://192.168.20.122:3000
Backend:   http://192.168.20.122:8000
Dev Server: http://192.168.20.122:5173 (Vite)
```

### Production:
```
Frontend:  http://your-domain.com:3000 (or port 80/443 with nginx)
Backend:   http://your-domain.com:8000 (or reverse proxy)
```

## 🔧 Configuration Files

### .env
```env
APP_BASE_URL=http://localhost:3000          # Frontend URL
BACKEND_PORT=8000                            # Backend port
VITE_API_BASE_URL=                          # Empty = auto-detect
```

### docker-compose.yml
```yaml
backend:
  ports:
    - "8000:8000"    # Backend port

frontend:
  ports:
    - "3000:80"      # Frontend port (nginx serves on 80 inside container)
```

### Frontend Auto-Detection
```javascript
// Automatically uses port 8000 for backend
return `http://${hostname}:8000`;
```

## 📋 Port Usage Summary

| Service | Port | Protocol | Purpose |
|---------|------|----------|---------|
| Frontend (Production) | 3000 | HTTP | React production build |
| Frontend (Dev) | 5173 | HTTP | Vite dev server |
| Backend API | 8000 | HTTP | FastAPI server |
| PostgreSQL | 5434 | TCP | Database |

## 🚀 Starting Services

### Development Mode:
```bash
# Backend (port 8000)
cd backend
python main.py

# Frontend Dev Server (port 5173)
cd frontend
npm run dev

# Frontend Production Build (port 3000)
cd frontend
npm run build
npm run preview
```

### Docker Mode:
```bash
# Starts both services
docker-compose up

# Access:
# Frontend: http://localhost:3000
# Backend:  http://localhost:8000
```

## 🔍 Verification

### Check if ports are in use:
```bash
# Windows
netstat -ano | findstr :3000
netstat -ano | findstr :8000

# Linux/Mac
lsof -i :3000
lsof -i :8000
```

### Test backend:
```bash
curl http://localhost:8000/health
```

### Test frontend:
```bash
# Open in browser
http://localhost:3000
```

## ⚙️ Changing Ports (If Needed)

### Backend Port:
1. Update `.env`: `BACKEND_PORT=9000`
2. Update `docker-compose.yml`: `"9000:8000"`
3. Update frontend auto-detection to use new port

### Frontend Port:
1. Update `docker-compose.yml`: `"4000:80"`
2. Update `APP_BASE_URL` in `.env`
3. Update CORS_ORIGINS to include new port

## 🎯 Current Setup Works With:

✅ `http://localhost:3000` → `http://localhost:8000`
✅ `http://192.168.20.122:3000` → `http://192.168.20.122:8000`
✅ `http://your-domain.com:3000` → `http://your-domain.com:8000`

**Auto-detection ensures frontend always calls backend on port 8000!**

---

**Standard Configuration:**
- Frontend: 3000
- Backend: 8000
- Everything configured correctly! ✅
