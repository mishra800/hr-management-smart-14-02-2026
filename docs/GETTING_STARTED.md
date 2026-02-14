# Getting Started with HR Management System

## Overview

This guide will help you set up and run the HR Management System on your local machine.

## Prerequisites

Before you begin, ensure you have:

- **Python 3.8+** - [Download](https://www.python.org/downloads/)
- **Node.js 16+** - [Download](https://nodejs.org/)
- **PostgreSQL 12+** - [Download](https://www.postgresql.org/download/)
- **Git** - [Download](https://git-scm.com/downloads)

## Installation Steps

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd hr-management-system
```

### 2. Run Automated Setup

```cmd
scripts\setup-project.cmd
```

This script will:
- Create .env files from templates
- Install Python dependencies
- Install Node.js dependencies
- Test database connection
- Create default users

### 3. Configure Environment

Edit `backend/.env` with your database credentials:
```env
DATABASE_URL=postgresql://username:password@localhost:5432/hr_management_db
SECRET_KEY=your-secret-key-here
```

Edit `frontend/.env` if needed:
```env
VITE_API_BASE_URL=http://localhost:8000
```

### 4. Start the Application

**Terminal 1 - Backend:**
```cmd
scripts\start-backend.cmd
```

**Terminal 2 - Frontend:**
```cmd
scripts\start-frontend.cmd
```

## Access the Application

- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

## Default Login Credentials

| Role | Email | Password |
|------|-------|----------|
| Super Admin | admin@company.com | admin123 |
| HR Manager | hr@company.com | hr123 |
| Manager | manager@company.com | manager123 |
| Employee | employee@company.com | emp123 |

## First Steps After Login

### As Super Admin

1. **Configure System Capabilities**
   - Navigate to Super Admin panel
   - Set module access for different roles
   - Configure system settings

2. **Add Employees**
   - Go to Employees section
   - Add employee records
   - Assign roles and departments

3. **Set Up Departments**
   - Configure organizational structure
   - Assign managers
   - Set up reporting hierarchy

### As HR Manager

1. **Review Pending Requests**
   - Check leave requests
   - Review asset requests
   - Process onboarding tasks

2. **Manage Recruitment**
   - Post job openings
   - Review applications
   - Schedule interviews

3. **Configure Policies**
   - Set leave policies
   - Configure attendance rules
   - Define approval workflows

### As Employee

1. **Complete Profile**
   - Update personal information
   - Add emergency contacts
   - Upload profile picture

2. **Mark Attendance**
   - Check in/out daily
   - View attendance history
   - Request corrections if needed

3. **Request Leave**
   - Submit leave requests
   - Check leave balance
   - View leave calendar

## Common Tasks

### Adding a New Employee

1. Login as HR/Admin
2. Navigate to Employees → Add Employee
3. Fill in employee details
4. Assign role and department
5. Set reporting manager
6. Save and send invitation email

### Processing Leave Requests

1. Navigate to Leave Management
2. View pending requests
3. Review leave details
4. Approve or reject with comments
5. Employee receives notification

### Managing Attendance

1. Employees mark attendance daily
2. HR can view attendance reports
3. Generate monthly attendance sheets
4. Handle attendance corrections

### Running Payroll

1. Navigate to Payroll section
2. Select pay period
3. Review employee hours
4. Process payroll
5. Generate pay slips

## Troubleshooting

### Backend Issues

**Port already in use:**
```cmd
# Find process using port 8000
netstat -ano | findstr :8000
# Kill the process
taskkill /PID <process-id> /F
```

**Database connection error:**
- Verify PostgreSQL is running
- Check DATABASE_URL in backend/.env
- Test connection: `cd backend && python test_db_connection.py`

### Frontend Issues

**Port already in use:**
- Frontend will automatically try port 5174, 5175, etc.
- Or manually specify: `npm run dev -- --port 3000`

**API connection error:**
- Ensure backend is running
- Check VITE_API_BASE_URL in frontend/.env
- Verify CORS settings in backend

### General Issues

**Module not found errors:**
```cmd
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

**Permission errors:**
- Run terminal as Administrator (Windows)
- Check file permissions

## Next Steps

- Read [API Documentation](http://localhost:8000/docs)
- Explore [Feature Guide](FEATURES.md)
- Check [Development Guide](DEVELOPMENT.md)
- Review [Deployment Guide](DEPLOYMENT.md)

## Getting Help

- Check the [FAQ](FAQ.md)
- Review [Troubleshooting Guide](TROUBLESHOOTING.md)
- Open an issue on GitHub
- Contact support team
