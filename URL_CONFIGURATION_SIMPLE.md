# Simple URL Configuration Guide

## Yes! Just Change .env and Restart - That's It!

## The 3 Variables You Need to Update:

```env
# 1. Where is your BACKEND? (Frontend needs to know this)
VITE_API_BASE_URL=https://your-backend-url.com

# 2. Where is your FRONTEND? (Backend needs to know this)
APP_BASE_URL=https://your-frontend-url.com

# 3. Which domains are allowed? (Security - CORS)
CORS_ORIGINS=https://your-frontend-url.com,https://your-backend-url.com
```

## Visual Flow:

```
┌─────────────────────────────────────────────────────────────┐
│                         .env FILE                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  VITE_API_BASE_URL=https://api.myapp.com  ←─────┐         │
│  APP_BASE_URL=https://myapp.com                  │         │
│  CORS_ORIGINS=https://myapp.com,https://api...   │         │
│                                                   │         │
└───────────────────────────────────────────────────┼─────────┘
                                                    │
                    ┌───────────────────────────────┴─────────┐
                    │                                         │
                    ▼                                         ▼
        ┌─────────────────────┐                 ┌─────────────────────┐
        │      FRONTEND       │                 │      BACKEND        │
        │  (React/Vite)       │                 │     (FastAPI)       │
        ├─────────────────────┤                 ├─────────────────────┤
        │                     │                 │                     │
        │ Reads:              │    API Calls    │ Reads:              │
        │ VITE_API_BASE_URL ──┼────────────────>│ CORS_ORIGINS        │
        │                     │                 │ APP_BASE_URL        │
        │ "Send requests to   │                 │                     │
        │  this backend URL"  │                 │ "Accept requests    │
        │                     │                 │  from these URLs"   │
        └─────────────────────┘                 └─────────────────────┘
```

## Real Example:

### You Deploy and Get:
- Frontend: `https://myhrapp.vercel.app`
- Backend: `https://myhrapp-api.railway.app`

### Update .env:
```env
VITE_API_BASE_URL=https://myhrapp-api.railway.app
APP_BASE_URL=https://myhrapp.vercel.app
CORS_ORIGINS=https://myhrapp.vercel.app,https://myhrapp-api.railway.app
```

### Restart:
```bash
docker-compose restart
# or
docker-compose down && docker-compose up -d
```

### Done! ✅
Your frontend will now talk to your backend correctly!

## What Each Variable Does:

### 1. `VITE_API_BASE_URL` (Frontend → Backend)
```javascript
// In your React code, all API calls use this:
axios.get(`${VITE_API_BASE_URL}/api/users`)
// Becomes: https://myhrapp-api.railway.app/api/users
```

### 2. `APP_BASE_URL` (Backend → Frontend)
```python
# In your backend, when sending emails or redirects:
reset_link = f"{APP_BASE_URL}/reset-password?token={token}"
# Becomes: https://myhrapp.vercel.app/reset-password?token=abc123
```

### 3. `CORS_ORIGINS` (Security)
```python
# Backend checks: "Is this request from an allowed domain?"
# If frontend is https://myhrapp.vercel.app
# And CORS_ORIGINS includes it → ✅ Allow
# If not in CORS_ORIGINS → ❌ Block (CORS error)
```

## Common Deployment Platforms:

### Vercel (Frontend) + Railway (Backend)
```env
VITE_API_BASE_URL=https://your-app.railway.app
APP_BASE_URL=https://your-app.vercel.app
CORS_ORIGINS=https://your-app.vercel.app,https://your-app.railway.app
```

### Netlify (Frontend) + Heroku (Backend)
```env
VITE_API_BASE_URL=https://your-app.herokuapp.com
APP_BASE_URL=https://your-app.netlify.app
CORS_ORIGINS=https://your-app.netlify.app,https://your-app.herokuapp.com
```

### AWS (Both)
```env
VITE_API_BASE_URL=https://api.your-domain.com
APP_BASE_URL=https://your-domain.com
CORS_ORIGINS=https://your-domain.com,https://api.your-domain.com
```

### Custom Domain
```env
VITE_API_BASE_URL=https://api.mycompany.com
APP_BASE_URL=https://mycompany.com
CORS_ORIGINS=https://mycompany.com,https://api.mycompany.com
```

## Testing After Update:

### 1. Check Frontend Console
Open browser DevTools (F12) → Console
- Should see API calls going to your backend URL
- No CORS errors

### 2. Test Login
- Try logging in
- If it works → ✅ Configuration correct!
- If CORS error → Add domain to CORS_ORIGINS

### 3. Check Backend Logs
```bash
docker-compose logs backend
# Should see incoming requests from your frontend
```

## Important: Restart is Required!

```bash
# Environment variables are loaded at startup
# So you MUST restart after changing .env

# Docker:
docker-compose restart

# Or full restart:
docker-compose down
docker-compose up -d

# Manual:
# Stop backend (Ctrl+C) and restart: python main.py
# Stop frontend (Ctrl+C) and restart: npm run dev
```

## That's It!

Change 3 variables in `.env` → Restart → Everything works! 🎉
