# Network Access Configuration Guide

## 🎯 Automatic Environment Detection

Your HR Management System now automatically detects the environment and configures itself accordingly!

## 🌐 How It Works

### Frontend Auto-Detection
The frontend automatically detects which URL to use for the backend API:

| Access Method | Frontend URL | Backend API URL | Use Case |
|--------------|--------------|-----------------|----------|
| Localhost | `http://localhost:5173` | `http://localhost:8000` | Local development |
| Your Computer | `http://192.168.20.122:5173` | `http://192.168.20.122:8000` | Testing from other devices |
| Production | `https://dhanush-hr.netlify.app` | Production API | Live deployment |

### Backend CORS Support
The backend accepts requests from:
- ✅ `localhost:5173`, `localhost:5174`, `localhost:3000` (local development)
- ✅ `192.168.20.122:5173`, `192.168.20.122:5174`, `192.168.20.122:3000`, `192.168.20.122:8000` (network access)
- ✅ `https://dhanush-hr.netlify.app` (production)
- ✅ Any additional origins from `FRONTEND_URL` or `ADDITIONAL_CORS_ORIGINS` in `.env`

## 🚀 Usage Scenarios

### Scenario 1: Local Development
```bash
# Start backend
cd backend
python main.py

# Start frontend (in another terminal)
cd frontend
npm run dev
```
Access: `http://localhost:5173`
- Frontend automatically calls `http://localhost:8000`

### Scenario 2: Testing from Phone/Tablet on Same Network
```bash
# Same as above, but access from another device
```
Access: `http://192.168.20.122:5173` (from your phone/tablet)
- Frontend automatically calls `http://192.168.20.122:8000`
- No configuration changes needed!

### Scenario 3: Production Deployment
Deploy to Netlify/Vercel/etc.
- Frontend automatically detects production domain
- Update production API URL in `frontend/src/config/api.js` if needed

## 🔧 Manual Override (Optional)

If you need to manually set the API URL, use the `.env` file:

```env
# Force specific API URL (overrides auto-detection)
VITE_API_BASE_URL=http://your-custom-url:8000
```

## 🐛 Debugging

Check the browser console for API configuration:
```
🌐 API Configuration: {
  hostname: "192.168.20.122",
  apiBaseUrl: "http://192.168.20.122:8000",
  environment: "development"
}
```

Check backend logs for CORS configuration:
```
CORS Configuration: Environment=development, Origins=9 configured
CORS Origins: ['http://localhost:5173', ...]
```

## 📝 Adding New Origins

To add additional allowed origins, update `.env`:

```env
# Add comma-separated origins
ADDITIONAL_CORS_ORIGINS=http://192.168.1.100:3000,http://another-domain.com
```

## 🔒 Security Notes

- Localhost and LAN IPs are safe for development
- Production should use HTTPS only
- Never set `CORS_ALLOW_ALL=true` in production
- The system automatically prevents wildcard CORS in production

## ✅ Benefits

1. **Zero Configuration**: Works out of the box for most scenarios
2. **Flexible**: Supports localhost, LAN, and production
3. **Secure**: Proper CORS configuration prevents unauthorized access
4. **Developer Friendly**: No need to change configs when switching between environments
5. **Network Testing**: Easy to test from mobile devices on same network

## 🎉 Result

One codebase that works everywhere:
- ✅ Local development on your machine
- ✅ Testing from other devices on your network
- ✅ Production deployment
- ✅ No manual URL changes needed!
