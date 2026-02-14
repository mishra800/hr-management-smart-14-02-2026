-- ============================================
-- COMPLETE HR MANAGEMENT SYSTEM DATABASE SCHEMA
-- PostgreSQL Database Setup Script
-- Version: 1.0 - Complete & Final
-- ============================================
-- This is the ONLY script you need to run
-- It includes ALL tables (core + advanced features)
-- Run this on a NEW database or it will DROP existing tables
-- ============================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- DROP EXISTING TABLES (CLEAN SLATE)
-- ============================================
DROP TABLE IF EXISTS referrals CASCADE;
DROP TABLE IF EXISTS application_form_fields CASCADE;
DROP TABLE IF EXISTS candidate_communications CASCADE;
DROP TABLE IF EXISTS employee_documents CASCADE;
DROP TABLE IF EXISTS infrastructure_requests CASCADE;
DROP TABLE IF EXISTS ai_interview_logs CASCADE;
DROP TABLE IF EXISTS ai_interviews CASCADE;
DROP TABLE IF EXISTS linkedin_profiles CASCADE;
DROP TABLE IF EXISTS notification_logs CASCADE;
DROP TABLE IF EXISTS notification_preferences CASCADE;
DROP TABLE IF EXISTS permissions CASCADE;
DROP TABLE IF EXISTS bulk_upload_files CASCADE;
DROP TABLE IF EXISTS bulk_uploads CASCADE;
DROP TABLE IF EXISTS application_stage_history CASCADE;
DROP TABLE IF EXISTS application_comments CASCADE;
DROP TABLE IF EXISTS interview_feedback CASCADE;
DROP TABLE IF EXISTS interview_feedback_templates CASCADE;
DROP TABLE IF EXISTS interview_slots CASCADE;
DROP TABLE IF EXISTS interviews CASCADE;
DROP TABLE IF EXISTS interviewer_availability CASCADE;
DROP TABLE IF EXISTS agency_submissions CASCADE;
DROP TABLE IF EXISTS agencies CASCADE;
DROP TABLE IF EXISTS talent_pool CASCADE;
DROP TABLE IF EXISTS audit_logs CASCADE;
DROP TABLE IF EXISTS system_settings CASCADE;
DROP TABLE IF EXISTS wfh_requests CASCADE;
DROP TABLE IF EXISTS learning_progress CASCADE;
DROP TABLE IF EXISTS learning_modules CASCADE;
DROP TABLE IF EXISTS documents CASCADE;
DROP TABLE IF EXISTS announcements CASCADE;
DROP TABLE IF EXISTS notifications CASCADE;
DROP TABLE IF EXISTS meeting_bookings CASCADE;
DROP TABLE IF EXISTS meeting_rooms CASCADE;
DROP TABLE IF EXISTS performance_reviews CASCADE;
DROP TABLE IF EXISTS payroll CASCADE;
DROP TABLE IF EXISTS asset_acknowledgments CASCADE;
DROP TABLE IF EXISTS asset_requests CASCADE;
DROP TABLE IF EXISTS assets CASCADE;
DROP TABLE IF EXISTS job_applications CASCADE;
DROP TABLE IF EXISTS job_postings CASCADE;
DROP TABLE IF EXISTS leave_balances CASCADE;
DROP TABLE IF EXISTS leave_requests CASCADE;
DROP TABLE IF EXISTS leave_types CASCADE;
DROP TABLE IF EXISTS attendance CASCADE;
DROP TABLE IF EXISTS employees CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- ============================================
-- CORE TABLES
-- ============================================

-- Users table (Core authentication)
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(50) DEFAULT 'employee',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Employees table (Extended employee information)
CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    employee_id VARCHAR(50) UNIQUE,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    email VARCHAR(255),
    phone VARCHAR(20),
    department VARCHAR(100),
    position VARCHAR(100),
    hire_date DATE,
    salary DECIMAL(10,2),
    manager_id INTEGER REFERENCES employees(id),
    status VARCHAR(20) DEFAULT 'active',
    profile_image VARCHAR(255),
    address TEXT,
    emergency_contact_name VARCHAR(255),
    emergency_contact_phone VARCHAR(20),
    date_of_birth DATE,
    wedding_anniversary_date DATE,
    profile_summary TEXT,
    profile_completion_percentage INTEGER DEFAULT 0,
    wfh_status VARCHAR(20) DEFAULT 'office',
    is_immediate_joiner BOOLEAN DEFAULT false,
    onboarding_status VARCHAR(50) DEFAULT 'initiated',
    it_setup_status VARCHAR(50) DEFAULT 'pending',
    pan_number VARCHAR(20),
    aadhaar_number VARCHAR(20),
    gender VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- ATTENDANCE TABLES
-- ============================================

-- Attendance table
CREATE TABLE attendance (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER REFERENCES employees(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    check_in_time TIMESTAMP,
    check_out_time TIMESTAMP,
    break_start_time TIMESTAMP,
    break_end_time TIMESTAMP,
    total_hours DECIMAL(4,2),
    status VARCHAR(20) DEFAULT 'present',
    location VARCHAR(255),
    ip_address INET,
    face_recognition_verified BOOLEAN DEFAULT false,
    photo_url VARCHAR(255),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(employee_id, date)
);

-- ============================================
-- LEAVE MANAGEMENT TABLES
-- ============================================

-- Leave types table
CREATE TABLE leave_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    max_days_per_year INTEGER,
    carry_forward_allowed BOOLEAN DEFAULT false,
    requires_approval BOOLEAN DEFAULT true,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Leave requests table
CREATE TABLE leave_requests (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER REFERENCES employees(id) ON DELETE CASCADE,
    leave_type_id INTEGER REFERENCES leave_types(id),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    days_requested INTEGER NOT NULL,
    reason TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    approved_by INTEGER REFERENCES employees(id),
    approved_at TIMESTAMP,
    rejection_reason TEXT,
    emergency_leave BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Leave balances table
CREATE TABLE leave_balances (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER REFERENCES employees(id) ON DELETE CASCADE,
    leave_type_id INTEGER REFERENCES leave_types(id),
    year INTEGER NOT NULL,
    allocated_days INTEGER DEFAULT 0,
    used_days INTEGER DEFAULT 0,
    remaining_days INTEGER DEFAULT 0,
    carried_forward INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(employee_id, leave_type_id, year)
);

-- ============================================
-- RECRUITMENT TABLES
-- ============================================

-- Job postings table
CREATE TABLE job_postings (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    department VARCHAR(100),
    location VARCHAR(255),
    employment_type VARCHAR(50),
    description TEXT,
    requirements TEXT,
    salary_min DECIMAL(10,2),
    salary_max DECIMAL(10,2),
    status VARCHAR(20) DEFAULT 'active',
    posted_by INTEGER REFERENCES employees(id),
    posted_date DATE DEFAULT CURRENT_DATE,
    closing_date DATE,
    workflow_mode VARCHAR(20) DEFAULT 'flexible',
    current_step INTEGER DEFAULT 0,
    requisition_status VARCHAR(20) DEFAULT 'approved',
    application_link_code VARCHAR(100) UNIQUE,
    qr_code_url TEXT,
    allow_linkedin_apply BOOLEAN DEFAULT false,
    allow_bulk_upload BOOLEAN DEFAULT true,
    blind_hiring_enabled BOOLEAN DEFAULT false,
    required_skills JSONB DEFAULT '[]',
    min_experience_years INTEGER,
    max_experience_years INTEGER,
    remote_allowed BOOLEAN DEFAULT false,
    hiring_manager_id INTEGER REFERENCES employees(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Job applications table
CREATE TABLE job_applications (
    id SERIAL PRIMARY KEY,
    job_posting_id INTEGER REFERENCES job_postings(id) ON DELETE CASCADE,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    resume_path VARCHAR(255),
    cover_letter TEXT,
    status VARCHAR(20) DEFAULT 'applied',
    applied_date DATE DEFAULT CURRENT_DATE,
    interview_date TIMESTAMP,
    interview_notes TEXT,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    ai_fit_score DECIMAL(4,2) DEFAULT 0.0,
    source VARCHAR(50) DEFAULT 'direct',
    tags JSONB DEFAULT '[]',
    is_starred BOOLEAN DEFAULT false,
    blind_hiring_enabled BOOLEAN DEFAULT false,
    identity_revealed_at TIMESTAMP,
    revealed_by INTEGER REFERENCES users(id),
    linkedin_profile_url TEXT,
    years_of_experience INTEGER,
    current_company VARCHAR(255),
    current_position VARCHAR(255),
    expected_salary DECIMAL(10,2),
    notice_period_days INTEGER,
    skills JSONB DEFAULT '[]',
    education JSONB DEFAULT '[]',
    certifications JSONB DEFAULT '[]',
    stage_changed_at TIMESTAMP,
    stage_changed_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- ASSET MANAGEMENT TABLES
-- ============================================

-- Assets table
CREATE TABLE assets (
    id SERIAL PRIMARY KEY,
    asset_tag VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    description TEXT,
    serial_number VARCHAR(255),
    purchase_date DATE,
    purchase_cost DECIMAL(10,2),
    warranty_expiry DATE,
    status VARCHAR(20) DEFAULT 'available',
    location VARCHAR(255),
    assigned_to INTEGER REFERENCES employees(id),
    assigned_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Asset requests table
CREATE TABLE asset_requests (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER REFERENCES employees(id) ON DELETE CASCADE,
    asset_category VARCHAR(100),
    description TEXT,
    justification TEXT,
    priority VARCHAR(20) DEFAULT 'medium',
    status VARCHAR(20) DEFAULT 'pending',
    requested_date DATE DEFAULT CURRENT_DATE,
    approved_by INTEGER REFERENCES employees(id),
    approved_date DATE,
    fulfilled_date DATE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Asset acknowledgments table
CREATE TABLE asset_acknowledgments (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER REFERENCES employees(id) ON DELETE CASCADE,
    asset_id INTEGER REFERENCES assets(id) ON DELETE CASCADE,
    acknowledgment_type VARCHAR(50),
    acknowledged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    digital_signature TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- PAYROLL TABLES
-- ============================================

-- Payroll table
CREATE TABLE payroll (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER REFERENCES employees(id) ON DELETE CASCADE,
    pay_period_start DATE NOT NULL,
    pay_period_end DATE NOT NULL,
    basic_salary DECIMAL(10,2),
    overtime_hours DECIMAL(4,2) DEFAULT 0,
    overtime_rate DECIMAL(6,2) DEFAULT 0,
    overtime_pay DECIMAL(10,2) DEFAULT 0,
    allowances DECIMAL(10,2) DEFAULT 0,
    deductions DECIMAL(10,2) DEFAULT 0,
    tax_deduction DECIMAL(10,2) DEFAULT 0,
    net_pay DECIMAL(10,2),
    status VARCHAR(20) DEFAULT 'draft',
    processed_by INTEGER REFERENCES employees(id),
    processed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- PERFORMANCE TABLES
-- ============================================

-- Performance reviews table
CREATE TABLE performance_reviews (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER REFERENCES employees(id) ON DELETE CASCADE,
    reviewer_id INTEGER REFERENCES employees(id),
    review_period_start DATE,
    review_period_end DATE,
    overall_rating INTEGER CHECK (overall_rating >= 1 AND overall_rating <= 5),
    goals_achievement TEXT,
    strengths TEXT,
    areas_for_improvement TEXT,
    development_plan TEXT,
    status VARCHAR(20) DEFAULT 'draft',
    submitted_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- MEETING TABLES
-- ============================================

-- Meeting rooms table
CREATE TABLE meeting_rooms (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    location VARCHAR(255),
    capacity INTEGER,
    equipment TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Meeting bookings table
CREATE TABLE meeting_bookings (
    id SERIAL PRIMARY KEY,
    room_id INTEGER REFERENCES meeting_rooms(id) ON DELETE CASCADE,
    booked_by INTEGER REFERENCES employees(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    attendees TEXT,
    status VARCHAR(20) DEFAULT 'confirmed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- NOTIFICATION TABLES
-- ============================================

-- Notifications table
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    recipient_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    type VARCHAR(50) DEFAULT 'info',
    is_read BOOLEAN DEFAULT false,
    action_url VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    read_at TIMESTAMP
);

-- ============================================
-- ANNOUNCEMENT TABLES
-- ============================================

-- Announcements table
CREATE TABLE announcements (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    author_id INTEGER REFERENCES employees(id),
    target_audience VARCHAR(100) DEFAULT 'all',
    priority VARCHAR(20) DEFAULT 'normal',
    is_active BOOLEAN DEFAULT true,
    publish_date DATE DEFAULT CURRENT_DATE,
    expiry_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- DOCUMENT TABLES
-- ============================================

-- Documents table
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    file_path VARCHAR(255) NOT NULL,
    file_type VARCHAR(50),
    file_size INTEGER,
    category VARCHAR(100),
    uploaded_by INTEGER REFERENCES employees(id),
    access_level VARCHAR(20) DEFAULT 'public',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- LEARNING TABLES
-- ============================================

-- Learning modules table
CREATE TABLE learning_modules (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    content TEXT,
    category VARCHAR(100),
    difficulty_level VARCHAR(20) DEFAULT 'beginner',
    estimated_duration INTEGER,
    is_mandatory BOOLEAN DEFAULT false,
    is_active BOOLEAN DEFAULT true,
    created_by INTEGER REFERENCES employees(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Learning progress table
CREATE TABLE learning_progress (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER REFERENCES employees(id) ON DELETE CASCADE,
    module_id INTEGER REFERENCES learning_modules(id) ON DELETE CASCADE,
    status VARCHAR(20) DEFAULT 'not_started',
    progress_percentage INTEGER DEFAULT 0,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    score INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(employee_id, module_id)
);

-- ============================================
-- WFH TABLES
-- ============================================

-- Work from home requests table
CREATE TABLE wfh_requests (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER REFERENCES employees(id) ON DELETE CASCADE,
    request_date DATE NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    reason TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    approved_by INTEGER REFERENCES employees(id),
    approved_at TIMESTAMP,
    rejection_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- SYSTEM TABLES
-- ============================================

-- System settings table
CREATE TABLE system_settings (
    id SERIAL PRIMARY KEY,
    setting_key VARCHAR(255) UNIQUE NOT NULL,
    setting_value TEXT,
    description TEXT,
    category VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Audit logs table
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    action VARCHAR(255) NOT NULL,
    table_name VARCHAR(100),
    record_id INTEGER,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- ADVANCED FEATURE TABLES
-- ============================================

-- Talent Pool Management
CREATE TABLE talent_pool (
    id SERIAL PRIMARY KEY,
    candidate_name VARCHAR(255) NOT NULL,
    candidate_email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),
    resume_url TEXT,
    skills JSONB DEFAULT '[]',
    experience_years INTEGER,
    tags JSONB DEFAULT '[]',
    source VARCHAR(100),
    original_application_id INTEGER REFERENCES job_applications(id),
    ai_fit_score DECIMAL(4,2) DEFAULT 0.0,
    added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_contacted TIMESTAMP,
    status VARCHAR(20) DEFAULT 'active',
    notes TEXT,
    created_by INTEGER REFERENCES employees(id),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Agency Management
CREATE TABLE agencies (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    contact_person VARCHAR(255),
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),
    commission_percentage DECIMAL(5,2) DEFAULT 10.0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE agency_submissions (
    id SERIAL PRIMARY KEY,
    agency_id INTEGER REFERENCES agencies(id),
    application_id INTEGER REFERENCES job_applications(id),
    job_posting_id INTEGER REFERENCES job_postings(id),
    submitted_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    commission_amount DECIMAL(10,2),
    commission_paid BOOLEAN DEFAULT false,
    payment_date TIMESTAMP,
    notes TEXT
);

-- Interview Management
CREATE TABLE interviewer_availability (
    id SERIAL PRIMARY KEY,
    interviewer_id INTEGER REFERENCES users(id),
    day_of_week INTEGER CHECK (day_of_week >= 0 AND day_of_week <= 6),
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE interviews (
    id SERIAL PRIMARY KEY,
    application_id INTEGER REFERENCES job_applications(id),
    interviewer_id INTEGER REFERENCES users(id),
    scheduled_time TIMESTAMP,
    meeting_link VARCHAR(500),
    status VARCHAR(20) DEFAULT 'scheduled',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE interview_slots (
    id SERIAL PRIMARY KEY,
    interview_id INTEGER REFERENCES interviews(id),
    slot_start TIMESTAMP NOT NULL,
    slot_end TIMESTAMP NOT NULL,
    is_booked BOOLEAN DEFAULT false,
    booked_by_application_id INTEGER REFERENCES job_applications(id),
    meeting_link TEXT,
    meeting_platform VARCHAR(50) DEFAULT 'zoom',
    calendar_event_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE interview_feedback_templates (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    questions JSONB NOT NULL,
    created_by INTEGER REFERENCES users(id),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE interview_feedback (
    id SERIAL PRIMARY KEY,
    interview_id INTEGER REFERENCES interviews(id),
    template_id INTEGER REFERENCES interview_feedback_templates(id),
    responses JSONB NOT NULL,
    overall_rating INTEGER CHECK (overall_rating >= 1 AND overall_rating <= 5),
    recommendation VARCHAR(50),
    notes TEXT,
    submitted_by INTEGER REFERENCES users(id),
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Collaboration Features
CREATE TABLE application_comments (
    id SERIAL PRIMARY KEY,
    application_id INTEGER REFERENCES job_applications(id),
    user_id INTEGER REFERENCES users(id),
    comment TEXT NOT NULL,
    is_internal BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE application_stage_history (
    id SERIAL PRIMARY KEY,
    application_id INTEGER REFERENCES job_applications(id),
    from_stage VARCHAR(50),
    to_stage VARCHAR(50) NOT NULL,
    changed_by INTEGER REFERENCES users(id),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Bulk Upload Tracking
CREATE TABLE bulk_uploads (
    id SERIAL PRIMARY KEY,
    job_posting_id INTEGER REFERENCES job_postings(id),
    uploaded_by INTEGER REFERENCES users(id),
    total_files INTEGER DEFAULT 0,
    successful_parses INTEGER DEFAULT 0,
    failed_parses INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'processing',
    error_log JSONB DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

CREATE TABLE bulk_upload_files (
    id SERIAL PRIMARY KEY,
    bulk_upload_id INTEGER REFERENCES bulk_uploads(id),
    filename VARCHAR(255),
    file_url TEXT,
    application_id INTEGER REFERENCES job_applications(id),
    parse_status VARCHAR(20) DEFAULT 'pending',
    parse_error TEXT,
    parsed_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- RBAC & Permissions
CREATE TABLE permissions (
    id SERIAL PRIMARY KEY,
    role VARCHAR(50) NOT NULL,
    resource VARCHAR(100) NOT NULL,
    action VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(role, resource, action)
);

-- Notification Preferences
CREATE TABLE notification_preferences (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) UNIQUE,
    email_enabled BOOLEAN DEFAULT true,
    sms_enabled BOOLEAN DEFAULT false,
    whatsapp_enabled BOOLEAN DEFAULT false,
    phone_number VARCHAR(20),
    whatsapp_number VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE notification_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    type VARCHAR(20),
    subject VARCHAR(255),
    message TEXT,
    status VARCHAR(20) DEFAULT 'sent',
    error_message TEXT,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- LinkedIn Integration
CREATE TABLE linkedin_profiles (
    id SERIAL PRIMARY KEY,
    application_id INTEGER REFERENCES job_applications(id),
    linkedin_id VARCHAR(255) UNIQUE,
    profile_url TEXT,
    profile_data JSONB,
    imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- AI Interview System
CREATE TABLE ai_interviews (
    id SERIAL PRIMARY KEY,
    application_id INTEGER REFERENCES job_applications(id),
    status VARCHAR(20) DEFAULT 'pending',
    overall_score DECIMAL(4,2) DEFAULT 0.0,
    emotional_tone VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE ai_interview_logs (
    id SERIAL PRIMARY KEY,
    interview_id INTEGER REFERENCES ai_interviews(id),
    question TEXT,
    candidate_response TEXT,
    ai_evaluation TEXT,
    score DECIMAL(4,2),
    sentiment VARCHAR(50),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Infrastructure Requests (IT Provisioning)
CREATE TABLE infrastructure_requests (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER REFERENCES employees(id) NOT NULL,
    laptop_provided BOOLEAN DEFAULT false,
    email_setup_completed BOOLEAN DEFAULT false,
    wifi_setup_completed BOOLEAN DEFAULT false,
    id_card_provided BOOLEAN DEFAULT false,
    biometric_setup_completed BOOLEAN DEFAULT false,
    email_address_created VARCHAR(255),
    id_card_number VARCHAR(100),
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Employee Documents
CREATE TABLE employee_documents (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER REFERENCES employees(id),
    document_type VARCHAR(100),
    document_url VARCHAR(500),
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_verified BOOLEAN DEFAULT false,
    ocr_confidence DECIMAL(4,2) DEFAULT 0.0,
    rejection_reason VARCHAR(500)
);

-- Communication History
CREATE TABLE candidate_communications (
    id SERIAL PRIMARY KEY,
    application_id INTEGER REFERENCES job_applications(id),
    type VARCHAR(20),
    direction VARCHAR(20),
    subject VARCHAR(255),
    message TEXT,
    sent_by INTEGER REFERENCES users(id),
    status VARCHAR(20) DEFAULT 'sent',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Custom Application Forms
CREATE TABLE application_form_fields (
    id SERIAL PRIMARY KEY,
    job_posting_id INTEGER REFERENCES job_postings(id),
    field_name VARCHAR(100) NOT NULL,
    field_type VARCHAR(50) NOT NULL,
    field_label VARCHAR(255) NOT NULL,
    is_required BOOLEAN DEFAULT false,
    options JSONB,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Referral System
CREATE TABLE referrals (
    id SERIAL PRIMARY KEY,
    referred_by_employee_id INTEGER REFERENCES employees(id),
    application_id INTEGER REFERENCES job_applications(id),
    referral_bonus_amount DECIMAL(10,2),
    bonus_paid BOOLEAN DEFAULT false,
    bonus_paid_date TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- CREATE INDEXES FOR PERFORMANCE
-- ============================================

CREATE INDEX idx_employees_user_id ON employees(user_id);
CREATE INDEX idx_employees_department ON employees(department);
CREATE INDEX idx_employees_manager_id ON employees(manager_id);
CREATE INDEX idx_attendance_employee_date ON attendance(employee_id, date);
CREATE INDEX idx_attendance_date ON attendance(date);
CREATE INDEX idx_leave_requests_employee ON leave_requests(employee_id);
CREATE INDEX idx_leave_requests_status ON leave_requests(status);
CREATE INDEX idx_job_applications_status ON job_applications(status);
CREATE INDEX idx_job_applications_job_id ON job_applications(job_posting_id);
CREATE INDEX idx_assets_status ON assets(status);
CREATE INDEX idx_assets_assigned_to ON assets(assigned_to);
CREATE INDEX idx_notifications_recipient ON notifications(recipient_id);
CREATE INDEX idx_notifications_read ON notifications(is_read);
CREATE INDEX idx_audit_logs_user ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_created ON audit_logs(created_at);
CREATE INDEX idx_talent_pool_email ON talent_pool(candidate_email);
CREATE INDEX idx_talent_pool_status ON talent_pool(status);
CREATE INDEX idx_infrastructure_requests_employee ON infrastructure_requests(employee_id);
CREATE INDEX idx_infrastructure_requests_status ON infrastructure_requests(status);
CREATE INDEX idx_employee_documents_employee ON employee_documents(employee_id);
CREATE INDEX idx_interviews_application ON interviews(application_id);
CREATE INDEX idx_interviews_interviewer ON interviews(interviewer_id);
CREATE INDEX idx_application_comments_application ON application_comments(application_id);
CREATE INDEX idx_application_stage_history_application ON application_stage_history(application_id);
CREATE INDEX idx_bulk_uploads_job ON bulk_uploads(job_posting_id);
CREATE INDEX idx_notification_preferences_user ON notification_preferences(user_id);
CREATE INDEX idx_ai_interviews_application ON ai_interviews(application_id);

-- ============================================
-- CREATE TRIGGERS FOR UPDATED_AT
-- ============================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_employees_updated_at BEFORE UPDATE ON employees FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_attendance_updated_at BEFORE UPDATE ON attendance FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_leave_requests_updated_at BEFORE UPDATE ON leave_requests FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_leave_balances_updated_at BEFORE UPDATE ON leave_balances FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_job_postings_updated_at BEFORE UPDATE ON job_postings FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_job_applications_updated_at BEFORE UPDATE ON job_applications FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_assets_updated_at BEFORE UPDATE ON assets FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_asset_requests_updated_at BEFORE UPDATE ON asset_requests FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_payroll_updated_at BEFORE UPDATE ON payroll FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_performance_reviews_updated_at BEFORE UPDATE ON performance_reviews FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_meeting_bookings_updated_at BEFORE UPDATE ON meeting_bookings FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_announcements_updated_at BEFORE UPDATE ON announcements FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_documents_updated_at BEFORE UPDATE ON documents FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_learning_modules_updated_at BEFORE UPDATE ON learning_modules FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_learning_progress_updated_at BEFORE UPDATE ON learning_progress FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_wfh_requests_updated_at BEFORE UPDATE ON wfh_requests FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_system_settings_updated_at BEFORE UPDATE ON system_settings FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_infrastructure_requests_updated_at BEFORE UPDATE ON infrastructure_requests FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_talent_pool_updated_at BEFORE UPDATE ON talent_pool FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_agencies_updated_at BEFORE UPDATE ON agencies FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_application_comments_updated_at BEFORE UPDATE ON application_comments FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_notification_preferences_updated_at BEFORE UPDATE ON notification_preferences FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- INSERT ESSENTIAL DATA
-- ============================================

-- Insert default leave types
INSERT INTO leave_types (name, description, max_days_per_year, carry_forward_allowed, requires_approval) VALUES
('Annual Leave', 'Yearly vacation leave', 21, true, true),
('Sick Leave', 'Medical leave', 10, false, true),
('Emergency Leave', 'Urgent personal matters', 5, false, true),
('Maternity Leave', 'Maternity leave', 90, false, true),
('Paternity Leave', 'Paternity leave', 15, false, true),
('Bereavement Leave', 'Family bereavement', 5, false, true),
('Study Leave', 'Educational purposes', 10, false, true);

-- Insert default meeting rooms
INSERT INTO meeting_rooms (name, location, capacity, equipment) VALUES
('Conference Room A', 'Floor 1', 10, 'Projector, Whiteboard, Video Conferencing'),
('Conference Room B', 'Floor 2', 6, 'TV Screen, Whiteboard'),
('Board Room', 'Floor 3', 20, 'Large Screen, Audio System, Video Conferencing'),
('Small Meeting Room', 'Floor 1', 4, 'Whiteboard'),
('Training Room', 'Floor 2', 15, 'Projector, Audio System, Flipchart');

-- Insert essential system settings
INSERT INTO system_settings (setting_key, setting_value, description, category) VALUES
('company_name', 'Your Company Name', 'Company name displayed in the system', 'general'),
('working_hours_per_day', '8', 'Standard working hours per day', 'attendance'),
('overtime_rate_multiplier', '1.5', 'Overtime pay rate multiplier', 'payroll'),
('max_leave_days_per_request', '30', 'Maximum leave days per single request', 'leave'),
('face_recognition_enabled', 'true', 'Enable face recognition for attendance', 'attendance'),
('email_notifications_enabled', 'true', 'Enable email notifications', 'notifications'),
('auto_approve_wfh_requests', 'false', 'Automatically approve WFH requests', 'wfh'),
('backup_frequency', 'daily', 'Database backup frequency', 'system'),
('session_timeout_minutes', '60', 'User session timeout in minutes', 'security'),
('password_min_length', '8', 'Minimum password length requirement', 'security');

-- Insert default RBAC permissions
INSERT INTO permissions (role, resource, action) VALUES
-- Super Admin - Full Access
('super_admin', '*', '*'),
-- Admin Permissions
('admin', 'users', 'create'),
('admin', 'users', 'read'),
('admin', 'users', 'update'),
('admin', 'users', 'delete'),
('admin', 'employees', 'create'),
('admin', 'employees', 'read'),
('admin', 'employees', 'update'),
('admin', 'employees', 'delete'),
('admin', 'job_postings', 'create'),
('admin', 'job_postings', 'read'),
('admin', 'job_postings', 'update'),
('admin', 'job_postings', 'delete'),
('admin', 'applications', 'read'),
('admin', 'applications', 'update'),
('admin', 'system_settings', 'update'),
-- HR Permissions
('hr', 'employees', 'create'),
('hr', 'employees', 'read'),
('hr', 'employees', 'update'),
('hr', 'job_postings', 'create'),
('hr', 'job_postings', 'read'),
('hr', 'job_postings', 'update'),
('hr', 'applications', 'read'),
('hr', 'applications', 'update'),
('hr', 'leave_requests', 'approve'),
('hr', 'attendance', 'read'),
('hr', 'payroll', 'create'),
('hr', 'payroll', 'read'),
-- Manager Permissions
('manager', 'employees', 'read'),
('manager', 'leave_requests', 'approve'),
('manager', 'attendance', 'read'),
('manager', 'performance_reviews', 'create'),
('manager', 'performance_reviews', 'read'),
-- Employee Permissions
('employee', 'attendance', 'create'),
('employee', 'attendance', 'read'),
('employee', 'leave_requests', 'create'),
('employee', 'leave_requests', 'read'),
('employee', 'documents', 'read'),
('employee', 'announcements', 'read'),
-- Assets Team Permissions
('assets_team', 'assets', 'create'),
('assets_team', 'assets', 'read'),
('assets_team', 'assets', 'update'),
('assets_team', 'asset_requests', 'read'),
('assets_team', 'asset_requests', 'update'),
('assets_team', 'asset_acknowledgments', 'read');

-- ============================================
-- VERIFICATION QUERIES
-- ============================================

-- Check if all tables were created successfully
SELECT schemaname, tablename, tableowner
FROM pg_tables 
WHERE schemaname = 'public' 
ORDER BY tablename;

-- Check essential data counts
SELECT 'leave_types' as table_name, COUNT(*) as record_count FROM leave_types
UNION ALL
SELECT 'meeting_rooms', COUNT(*) FROM meeting_rooms
UNION ALL
SELECT 'system_settings', COUNT(*) FROM system_settings
UNION ALL
SELECT 'permissions', COUNT(*) FROM permissions
ORDER BY table_name;

COMMIT;

-- ============================================
-- FINAL SUCCESS MESSAGE
-- ============================================

DO $$
DECLARE
    table_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO table_count FROM pg_tables WHERE schemaname = 'public';
    
    RAISE NOTICE '========================================';
    RAISE NOTICE '✅ HR MANAGEMENT SYSTEM DATABASE SETUP COMPLETE!';
    RAISE NOTICE '========================================';
    RAISE NOTICE '📊 Total Tables Created: %', table_count;
    RAISE NOTICE '🔧 Core Tables: 23 (Users, Employees, Attendance, Leave, etc.)';
    RAISE NOTICE '🚀 Advanced Tables: 15 (Talent Pool, Interviews, AI, etc.)';
    RAISE NOTICE '📝 Seed Data Added:';
    RAISE NOTICE '   - Leave Types: 7';
    RAISE NOTICE '   - Meeting Rooms: 5';
    RAISE NOTICE '   - System Settings: 10';
    RAISE NOTICE '   - RBAC Permissions: Configured';
    RAISE NOTICE '🔒 Indexes: Created for performance';
    RAISE NOTICE '⚡ Triggers: Auto-update timestamps enabled';
    RAISE NOTICE '========================================';
    RAISE NOTICE '🎉 Database is ready for use!';
    RAISE NOTICE '📱 Connect your application to:';
    RAISE NOTICE '   Host: 192.168.20.68';
    RAISE NOTICE '   Port: 5434';
    RAISE NOTICE '   Database: hr_management';
    RAISE NOTICE '========================================';
END $$;
