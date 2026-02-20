# Quick Deployment Checklist

## After You Deploy - Update These 3 Things:

### 1. Open `.env` file

### 2. Update these 3 variables:

```env
# Your backend URL (where frontend sends API requests)
VITE_API_BASE_URL=https://your-backend-url

# Your frontend URL (for emails, redirects)
APP_BASE_URL=https://your-frontend-url

# Both URLs (for security/CORS)
CORS_ORIGINS=https://your-frontend-url,https://your-backend-url
```

### 3. Restart services:

```bash
docker-compose restart
```

## That's It! ✅

---

## Example:

**You deployed:**
- Frontend at: `https://myapp.vercel.app`
- Backend at: `https://myapp-api.railway.app`

**Update .env:**
```env
VITE_API_BASE_URL=https://myapp-api.railway.app
APP_BASE_URL=https://myapp.vercel.app
CORS_ORIGINS=https://myapp.vercel.app,https://myapp-api.railway.app
DEBUG=False
ENVIRONMENT=production
```

**Restart:**
```bash
docker-compose down && docker-compose up -d
```

**Test:**
- Open `https://myapp.vercel.app`
- Try logging in
- Check browser console (F12) for errors

---

## Troubleshooting:

### CORS Error?
Add your frontend URL to `CORS_ORIGINS`

### Can't connect to backend?
Check `VITE_API_BASE_URL` is correct

### Still not working?
Run: `python verify_env.py`

---

## Full Guides:
- [URL_CONFIGURATION_SIMPLE.md](URL_CONFIGURATION_SIMPLE.md) - Visual guide
- [DEPLOYMENT_URL_GUIDE.md](DEPLOYMENT_URL_GUIDE.md) - Detailed scenarios
