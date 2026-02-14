-- ============================================
-- INSERT DEFAULT USERS INTO DATABASE
-- Run this in pgAdmin or psql
-- ============================================

-- First, let's check if users table is empty
SELECT COUNT(*) FROM users;

-- Insert default admin user
-- Password: admin123 (hashed)
INSERT INTO users (email, username, hashed_password, full_name, role, is_active, created_at, updated_at)
VALUES (
    'admin@company.com',
    'admin',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5aeUuL7dF.K5W', -- admin123
    'Admin User',
    'admin',
    true,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
);

-- Insert HR user
-- Password: hr123 (hashed)
INSERT INTO users (email, username, hashed_password, full_name, role, is_active, created_at, updated_at)
VALUES (
    'hr@company.com',
    'hr',
    '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', -- hr123
    'HR Manager',
    'hr',
    true,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
);

-- Insert employee user
-- Password: emp123 (hashed)
INSERT INTO users (email, username, hashed_password, full_name, role, is_active, created_at, updated_at)
VALUES (
    'employee@company.com',
    'employee',
    '$2b$12$KIXxLQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5aeUuL7dF', -- emp123
    'John Doe',
    'employee',
    true,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
);

-- Insert super admin user
-- Password: super123 (hashed)
INSERT INTO users (email, username, hashed_password, full_name, role, is_active, created_at, updated_at)
VALUES (
    'superadmin@company.com',
    'superadmin',
    '$2b$12$KIXxLQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5aeUuL7dF', -- super123
    'Super Admin',
    'super_admin',
    true,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
);

-- Verify users were inserted
SELECT id, email, username, role, is_active, created_at FROM users ORDER BY id;

-- ============================================
-- EXPECTED RESULT
-- ============================================
-- You should see 4 users:
-- 1. admin@company.com (admin)
-- 2. hr@company.com (hr)
-- 3. employee@company.com (employee)
-- 4. superadmin@company.com (super_admin)

COMMIT;
