# HR Management System

A comprehensive HR Management System with FastAPI backend and React frontend, featuring employee management, attendance tracking, leave management, recruitment, and more.

## 🎯 Current Status

**Backend Status**: ✅ **Stable & Running**
- 23/45+ routers successfully implemented
- Comprehensive error handling system
- JWT authentication with role-based access control
- Mock data implementation (database integration in progress)

**Frontend Status**: ✅ **Fully Functional**
- Complete React-based UI
- All HR modules implemented
- Responsive design with Tailwind CSS

## 🚀 Features

### Core HR Modules
- **👤 Employee Management** - Complete employee lifecycle
- **⏰ Attendance System** - Real-time tracking with face recognition support
- **🏖️ Leave Management** - Comprehensive leave request and approval system
- **💰 Payroll Management** - Automated payroll processing
- **🎯 Recruitment System** - End-to-end hiring workflow
- **📊 Performance Management** - Employee performance tracking
- **🎓 Learning & Development** - Training and skill management
- **🏢 Asset Management** - IT asset tracking and assignment

### Advanced Features
- **🤖 AI Assistant** - Intelligent HR support
- **📈 Analytics & Reporting** - Comprehensive HR insights
- **🔔 Notifications** - Real-time system notifications
- **📱 Mobile Support** - Mobile-friendly attendance system
- **🎉 Employee Engagement** - Recognition and feedback systems

## 🛠️ Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **JWT Authentication** - Secure token-based auth
- **Comprehensive Error Handling** - Standardized error responses
- **Role-Based Access Control** - Multi-level permissions

### Frontend
- **React 18** - Modern React with hooks
- **Tailwind CSS** - Utility-first styling
- **Axios** - HTTP client for API calls
- **Context API** - State management

## 📋 Prerequisites

- **Python 3.8+**
- **Node.js 16+**
- **npm or yarn**

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)
```bash
# Clone the repository
git clone <your-repo-url>
cd hr-management-system

# Run the complete setup
scripts\setup-project.cmd
```

### Option 2: Manual Setup

#### 1. Backend Setup
```bash
cd backend

# Create environment file
copy .env.example .env
# Edit .env with your database credentials

# Install dependencies
pip install -r requirements.txt

# Setup database and create default users
python test_db_connection.py
python create_default_users.py
```

#### 2. Frontend Setup
```bash
cd frontend

# Create environment file
copy .env.example .env

# Install dependencies
npm install
```

#### 3. Start the Application
```bash
# Terminal 1: Start Backend
scripts\start-backend.cmd

# Terminal 2: Start Frontend
scripts\start-frontend.cmd
```

## 🌐 Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 🔐 Default Login Credentials

| Role | Email | Password |
|------|-------|----------|
| Super Admin | admin@company.com | admin123 |
| HR Manager | hr@company.com | hr123 |
| Manager | manager@company.com | manager123 |
| Employee | employee@company.com | emp123 |

## 📚 Documentation

- **[Quick Reference](QUICK_REFERENCE.md)** - Common commands and quick help
- **[Getting Started Guide](docs/GETTING_STARTED.md)** - Complete setup and first steps
- **[Database Setup](docs/DATABASE_SETUP.md)** - Database configuration and troubleshooting
- **[Scripts Reference](scripts/README.md)** - Available utility scripts
- **[Complete Documentation](COMPLETE_APPLICATION_DOCUMENTATION.md)** - Full system documentation
- **[What's Implemented](WHAT_IS_IMPLEMENTED.md)** - Current feature status
- **[Cleanup Summary](CLEANUP_SUMMARY.md)** - Recent project cleanup details

## 🔧 Development

### Project Structure
```
├── backend/           # FastAPI backend
│   ├── app/          # Application code
│   ├── main.py       # FastAPI app entry point
│   └── requirements.txt
├── frontend/         # React frontend
│   ├── src/          # Source code
│   ├── public/       # Static assets
│   └── package.json
└── README.md
```

### Key Backend Features
- ✅ **23 Working Routers** - Core HR functionality
- ✅ **JWT Authentication** - Secure user management
- ✅ **Error Handling** - Comprehensive error system
- ✅ **Role-Based Access** - Multi-level permissions
- ✅ **CORS Support** - Frontend integration ready

### API Endpoints
- `/auth/*` - Authentication endpoints
- `/employees/*` - Employee management
- `/attendance/*` - Attendance tracking
- `/leave/*` - Leave management
- `/recruitment/*` - Hiring workflow
- `/assets/*` - Asset management
- `/dashboard/*` - Analytics and insights

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Check the documentation files
- Review the API documentation at `/docs`
- Create an issue in the repository

---

**Status**: ✅ Production Ready (Mock Data) | 🔄 Database Integration In Progress
```

### 4. Run the application
```bash
cd backend
python main.py
```

The API will be available at `http://localhost:8000`

## 📚 API Documentation

Once running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🌐 Deployment

This backend is ready for deployment on:
- **Vercel** (Recommended)
- **Railway**
- **Heroku**
- **AWS Lambda**

### Deploy to Vercel
1. Install Vercel CLI: `npm i -g vercel`
2. Run: `vercel` in the backend directory
3. Set environment variables in Vercel dashboard

## 🔧 Environment Variables

Required environment variables:

```env
DATABASE_URL=postgresql://user:password@host:port/database
SECRET_KEY=your-jwt-secret-key
ENVIRONMENT=production
DEBUG=False
```

Optional (for enhanced features):
```env
OPENAI_API_KEY=your-openai-key
GEMINI_API_KEY=your-gemini-key
SMTP_SERVER=smtp.gmail.com
SMTP_USERNAME=your-email
SMTP_PASSWORD=your-password
```

## 📁 Project Structure

```
backend/
├── app/
│   ├── routers/          # API route handlers
│   ├── models.py         # Database models
│   ├── schemas.py        # Pydantic schemas
│   ├── database.py       # Database configuration
│   └── services/         # Business logic services
├── main.py              # FastAPI application entry point
├── requirements.txt     # Python dependencies
└── vercel.json         # Vercel deployment config
```

## 🔐 Security Features

- JWT token authentication
- Password hashing with bcrypt
- CORS protection
- Input validation with Pydantic
- SQL injection prevention with SQLAlchemy ORM

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a merge request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Create an issue on GitLab
- Check the API documentation at `/docs`
- Review the deployment guide in `DEPLOYMENT_GUIDE.md`