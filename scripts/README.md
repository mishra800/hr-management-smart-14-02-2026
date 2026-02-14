# Scripts Directory

This folder contains utility scripts for managing the HR Management System.

## Available Scripts

### 🚀 Setup Scripts

#### `setup-project.cmd`
Complete initial setup for the entire project.
- Creates .env files from templates
- Installs all dependencies (backend & frontend)
- Tests database connection
- Creates default users

**Usage:**
```cmd
scripts\setup-project.cmd
```

#### `setup-database.cmd`
Database-specific setup.
- Tests database connection
- Creates default users and sample data

**Usage:**
```cmd
scripts\setup-database.cmd
```

### ▶️ Start Scripts

#### `start-backend.cmd`
Starts the FastAPI backend server.
- Installs/updates Python dependencies
- Starts server on http://localhost:8000
- Enables auto-reload for development

**Usage:**
```cmd
scripts\start-backend.cmd
```

#### `start-frontend.cmd`
Starts the React frontend development server.
- Installs/updates Node dependencies
- Starts server on http://localhost:5173

**Usage:**
```cmd
scripts\start-frontend.cmd
```

## Quick Start Workflow

1. **First Time Setup:**
   ```cmd
   scripts\setup-project.cmd
   ```

2. **Daily Development:**
   ```cmd
   # Terminal 1
   scripts\start-backend.cmd
   
   # Terminal 2
   scripts\start-frontend.cmd
   ```

3. **Reset Database:**
   ```cmd
   scripts\setup-database.cmd
   ```

## Default Credentials

After running setup, you can login with:

- **Super Admin:** admin@company.com / admin123
- **HR Manager:** hr@company.com / hr123
- **Employee:** employee@company.com / emp123

## Troubleshooting

### Backend won't start
- Check if Python 3.8+ is installed: `python --version`
- Verify database connection in `backend/.env`
- Run: `cd backend && python test_db_connection.py`

### Frontend won't start
- Check if Node.js 16+ is installed: `node --version`
- Clear node_modules: `cd frontend && rmdir /s /q node_modules && npm install`

### Database connection errors
- Verify PostgreSQL is running
- Check DATABASE_URL in `backend/.env`
- Ensure database exists and credentials are correct
