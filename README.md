# Smart HR Management System

A comprehensive, modern HR management system built with React (Frontend) and FastAPI (Backend), featuring AI-powered recruitment, attendance tracking, performance management, and more.

## 🚀 Features

### Core Modules
- **Employee Management** - Complete employee lifecycle management
- **Attendance Tracking** - Real-time attendance with face recognition support
- **Leave Management** - Automated leave requests and approvals
- **Recruitment** - AI-powered candidate screening and assessment
- **Performance Reviews** - 360-degree feedback and goal tracking
- **Payroll** - Automated salary calculations and payslips
- **Asset Management** - IT asset tracking and acknowledgments
- **Learning & Development** - Training modules and progress tracking
- **Onboarding** - Streamlined new hire onboarding process

### Advanced Features
- **AI-Powered Recruitment** - Resume parsing, candidate scoring, AI interviews
- **Predictive Analytics** - Attrition prediction, workforce planning
- **Face Recognition** - Attendance verification (optional)
- **Multi-role Access Control** - Admin, HR, Manager, Employee roles
- **Real-time Notifications** - Email and in-app notifications
- **Mobile Responsive** - Works on all devices
- **Dark Mode** - Professional theme support
- **API Documentation** - Interactive Swagger/OpenAPI docs

## 📋 Prerequisites

- **Docker** and **Docker Compose** (recommended)
- OR manually:
  - Python 3.10+
  - Node.js 20+
  - PostgreSQL 14+

## 🏃 Quick Start

### Using Docker (Recommended)

1. **Clone the repository**
```bash
git clone <repository-url>
cd smart-hr-management-system
```

2. **Configure environment**
```bash
cp .env.production .env
# Edit .env with your configuration
```

3. **Deploy**
```bash
# Linux/Mac
chmod +x deploy.sh
./deploy.sh

# Windows
.\deploy.ps1
```

4. **Initialize database**
```bash
docker-compose exec backend python initialize_capabilities.py
docker-compose exec backend python create_default_users.py
```

5. **Access the application**
- Frontend: http://localhost
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

**Default Login:**
- Email: `admin@company.com`
- Password: `admin123` (change immediately!)

### Manual Installation

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed manual installation instructions.

## 📚 Documentation

- [Deployment Guide](DEPLOYMENT.md) - Complete deployment instructions
- [Production Checklist](PRODUCTION_CHECKLIST.md) - Pre-deployment checklist
- [API Documentation](http://localhost:8000/docs) - Interactive API docs (after deployment)

## 🏗️ Architecture

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
                    └─────────────┘
```

## 🛠️ Technology Stack

### Frontend
- React 18
- Vite
- Tailwind CSS
- Axios
- React Router
- Recharts (for analytics)

### Backend
- FastAPI
- SQLAlchemy
- PostgreSQL
- JWT Authentication
- Pydantic
- DeepFace (optional, for face recognition)
- OpenAI/Gemini (optional, for AI features)

### DevOps
- Docker & Docker Compose
- Nginx
- Redis (optional)

## 📦 Project Structure

```
smart-hr-management-system/
├── backend/
│   ├── app/
│   │   ├── routers/          # API endpoints
│   │   ├── models.py          # Database models
│   │   ├── schemas.py         # Pydantic schemas
│   │   ├── database.py        # Database configuration
│   │   └── *_service.py       # Business logic services
│   ├── main.py                # FastAPI application
│   ├── requirements.txt       # Python dependencies
│   └── Dockerfile.full        # Docker configuration
├── frontend/
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── pages/             # Page components
│   │   ├── api/               # API client
│   │   └── config/            # Configuration
│   ├── package.json           # Node dependencies
│   └── Dockerfile             # Docker configuration
├── docker-compose.yml         # Docker Compose configuration
├── deploy.sh                  # Deployment script (Linux/Mac)
├── deploy.ps1                 # Deployment script (Windows)
└── README.md                  # This file
```

## 🔧 Configuration

### Environment Variables

**Backend (.env):**
```bash
DATABASE_URL=postgresql://user:password@host:port/database
SECRET_KEY=your-secret-key-min-32-chars
DEBUG=False
ENVIRONMENT=production
CORS_ORIGINS=http://your-domain.com
SMTP_SERVER=smtp.gmail.com
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

**Frontend (.env):**
```bash
VITE_API_BASE_URL=http://your-domain.com:8000
```

See `.env.production` for complete configuration template.

## 🧪 Testing

```bash
# Backend tests
docker-compose exec backend pytest

# Frontend tests
docker-compose exec frontend npm test

# Check backend health
curl http://localhost:8000/health
```

## 📊 Monitoring

### Health Checks
- Backend: http://localhost:8000/health
- Frontend: http://localhost
- Database: `docker-compose exec postgres pg_isready`

### Logs
```bash
# View all logs
docker-compose logs -f

# View specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Service Status
```bash
docker-compose ps
```

## 🔐 Security

- JWT-based authentication
- Password hashing with bcrypt
- Role-based access control (RBAC)
- SQL injection protection (SQLAlchemy ORM)
- XSS protection
- CORS configuration
- Rate limiting (configurable)
- Secure session management

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

[Your License Here]

## 👥 Support

For issues and questions:
- Check [DEPLOYMENT.md](DEPLOYMENT.md) for deployment help
- Review [PRODUCTION_CHECKLIST.md](PRODUCTION_CHECKLIST.md) for production setup
- Check logs: `docker-compose logs -f`
- Open an issue on GitHub

## 🎯 Roadmap

- [ ] Mobile app (React Native)
- [ ] Advanced analytics dashboard
- [ ] Integration with third-party HR tools
- [ ] Multi-language support
- [ ] Advanced reporting
- [ ] Blockchain-based document verification
- [ ] AI-powered career path recommendations

## 📸 Screenshots

[Add screenshots here]

## 🙏 Acknowledgments

- FastAPI for the amazing backend framework
- React team for the frontend library
- All open-source contributors

---

**Version:** 1.0.0  
**Last Updated:** 2024  
**Status:** Production Ready ✅
