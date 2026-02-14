# Database Setup Guide

## Prerequisites

- PostgreSQL 12+ installed and running
- Database created (e.g., `hr_management_db`)
- Database credentials ready

## Quick Setup

### 1. Configure Database Connection

Edit `backend/.env`:
```env
DATABASE_URL=postgresql://username:password@localhost:5432/hr_management_db
```

### 2. Run Setup Script

```cmd
scripts\setup-database.cmd
```

This will:
- Test database connection
- Create all required tables
- Insert default users and sample data

## Manual Setup

### 1. Test Connection

```bash
cd backend
python test_db_connection.py
```

### 2. Create Schema

Run the SQL schema file:
```bash
psql -U username -d hr_management_db -f COMPLETE_HR_DATABASE_SCHEMA.sql
```

### 3. Create Default Users

```bash
cd backend
python create_default_users.py
```

## Default Users

After setup, these users are available:

| Role | Email | Password |
|------|-------|----------|
| Super Admin | admin@company.com | admin123 |
| HR Manager | hr@company.com | hr123 |
| Manager | manager@company.com | manager123 |
| Employee | employee@company.com | emp123 |

## Troubleshooting

### Connection Failed

**Error:** `could not connect to server`
- Verify PostgreSQL is running
- Check host and port in DATABASE_URL
- Ensure firewall allows connection

**Error:** `password authentication failed`
- Verify username and password
- Check pg_hba.conf for authentication method

**Error:** `database does not exist`
- Create database: `createdb hr_management_db`
- Or use pgAdmin to create database

### Tables Not Created

- Check if schema file ran successfully
- Look for errors in backend logs
- Verify user has CREATE TABLE permissions

### Sample Data Issues

- Ensure tables exist before running create_default_users.py
- Check for unique constraint violations
- Clear existing data if re-running: `DELETE FROM users;`

## Database Schema

The system uses these main tables:

- `users` - User authentication and roles
- `employees` - Employee information
- `attendance` - Attendance records
- `leave_requests` - Leave management
- `job_postings` - Recruitment
- `applications` - Job applications
- `assets` - Asset management
- `notifications` - System notifications
- `audit_logs` - System audit trail

See `COMPLETE_HR_DATABASE_SCHEMA.sql` for full schema.
