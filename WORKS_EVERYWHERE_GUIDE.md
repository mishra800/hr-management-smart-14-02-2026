# Works Everywhere Guide - Local & Deployment

## 🎯 Your Current Configuration

Your `.env` file is **PERFECTLY configured** to work on both your local laptop AND deployment without any changes!

## ✅ Current Settings (Perfect!)

```env
# Backend
APP_BASE_URL=http://localhost:3000
VITE_API_BASE_URL=                    # Empty = auto-detection enabled!
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,...,http://192.168.20.122:3000,...
```

## 🚀 How It Works

### 1. Frontend Auto-Detection (VITE_API_BASE_URL is empty)

When `VITE_API_BASE_URL` is empty, the frontend automatically detects the hostname:

```javascript
// Access via localhost
http://localhost:3000 → calls → http://localhost:8000 ✅

// Access via your laptop's IP
http://192.168.20.122:3000 → calls → http://192.168.20.122:8000 ✅

// Access via deployment domain
http://your-domain.com → calls → http://your-domain.com:8000 ✅
```

**Magic!** The frontend uses whatever hostname you access it from!

### 2. Backend APP_BASE_URL (localhost default)

```env
APP_BASE_URL=http://localhost:3000
```

This is used for:
- Email verification links
- Password reset links
- Candidate portal links

**For Local:** Works perfectly with localhost
**For Deployment:** Override in production `.env` with your domain

### 3. CORS Origins (Includes both localhost and IP)

```env
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,...,http://192.168.20.122:3000,...
```

This allows requests from:
- ✅ localhost (your laptop)
- ✅ 192.168.20.122 (network access)
- ✅ Any additional origins you add

## 📋 Usage Scenarios

### Scenario 1: Working on Your Laptop
```bash
# Start servers
cd backend && python main.py
cd frontend && npm run dev

# Access
http://localhost:3000 ✅ Works!
http://localhost:5173 ✅ Works!
```

**What happens:**
- Frontend detects hostname = "localhost"
- Calls backend at http://localhost:8000
- CORS allows localhost origins
- Everything works!

### Scenario 2: Testing from Phone/Tablet (Same Network)
```bash
# Same servers running on your laptop

# Access from phone
http://192.168.20.122:3000 ✅ Works!
http://192.168.20.122:5173 ✅ Works!
```

**What happens:**
- Frontend detects hostname = "192.168.20.122"
- Calls backend at http://192.168.20.122:8000
- CORS allows 192.168.20.122 origins
- Everything works!

### Scenario 3: Production Deployment
```bash
# Deploy to your server

# Update production .env ONLY:
APP_BASE_URL=https://your-domain.com
CORS_ORIGINS=https://your-domain.com,http://localhost:3000,...
VITE_API_BASE_URL=  # Keep empty!

# Access
https://your-domain.com ✅ Works!
```

**What happens:**
- Frontend detects hostname = "your-domain.com"
- Calls backend at https://your-domain.com:8000
- CORS allows your-domain.com
- Everything works!

## 🔑 Key Points

### 1. VITE_API_BASE_URL = Empty (IMPORTANT!)
```env
VITE_API_BASE_URL=
```
- ✅ Empty = Auto-detection enabled
- ✅ Works on localhost
- ✅ Works on any IP address
- ✅ Works on any domain
- ❌ Don't set a value unless you need to override

### 2. APP_BASE_URL = localhost (Good Default)
```env
APP_BASE_URL=http://localhost:3000
```
- ✅ Works for local development
- ✅ Override in production .env
- Used for email links only

### 3. CORS_ORIGINS = Include All
```env
CORS_ORIGINS=localhost + IP + production domain
```
- ✅ Include localhost for local dev
- ✅ Include your IP for network testing
- ✅ Add production domain when deploying

## 📝 For Production Deployment

When deploying, create a production `.env` with:

```env
# Production .env (on your server)
APP_BASE_URL=https://your-domain.com
VITE_API_BASE_URL=  # Keep empty for auto-detection!
CORS_ORIGINS=https://your-domain.com,https://www.your-domain.com

# Other production settings
ENVIRONMENT=production
DEBUG=False
SECRET_KEY=your-secure-random-key
```

## ✨ Why This Works

### Auto-Detection Logic:
```javascript
function getApiBaseUrl() {
  // 1. Check env var (if set, use it)
  if (import.meta.env.VITE_API_BASE_URL) {
    return import.meta.env.VITE_API_BASE_URL;
  }
  
  // 2. Auto-detect from hostname
  const hostname = window.location.hostname;
  
  // Use same hostname with port 8000
  return `http://${hostname}:8000`;
}
```

**Result:** Frontend always calls the correct backend URL based on how you access it!

## 🎉 Summary

Your current configuration is **PERFECT**:

✅ **Works on localhost** - No changes needed
✅ **Works on network IP** - No changes needed  
✅ **Works on deployment** - Just override APP_BASE_URL in production
✅ **No code changes** - Same code everywhere
✅ **Auto-detection** - Frontend is smart!

## 🚫 What NOT to Do

❌ Don't set VITE_API_BASE_URL to a specific URL (breaks auto-detection)
❌ Don't hardcode IPs in code (we removed all of them)
❌ Don't change .env between local and network testing

## ✅ What TO Do

✅ Keep VITE_API_BASE_URL empty
✅ Keep APP_BASE_URL as localhost for local dev
✅ Include both localhost and IP in CORS_ORIGINS
✅ Override APP_BASE_URL in production .env only

---

**Your setup is ready to use everywhere without any changes!** 🎉
