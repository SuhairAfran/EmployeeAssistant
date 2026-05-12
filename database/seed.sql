-- ============================================================
-- HR Leave Modules Seed Data
-- ============================================================

ALTER TABLE users
    ADD COLUMN IF NOT EXISTS gender VARCHAR(10) NOT NULL DEFAULT 'male',
    ADD COLUMN IF NOT EXISTS is_married BOOLEAN NOT NULL DEFAULT FALSE;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_enum e
        JOIN pg_type t ON t.oid = e.enumtypid
        WHERE t.typname = 'leave_type'
          AND e.enumlabel = 'miscarriage'
    ) THEN
        ALTER TYPE leave_type ADD VALUE 'miscarriage' AFTER 'maternity';
    END IF;
END $$;

-- ============================================================
-- Step 1: Reset existing data (dependency-safe order)
-- ============================================================

-- Delete leave balances first (depends on users)
DELETE FROM leave_balances;

-- Delete leave requests
DELETE FROM leave_requests;

-- Delete holiday calendar
DELETE FROM holiday_calendar;

-- Delete users (departments.head_id will be set to NULL by ON DELETE SET NULL)
DELETE FROM users;

-- Delete departments
DELETE FROM departments;

-- ============================================================
-- Step 2: Insert Departments
-- ============================================================

-- Agentic AI Department
INSERT INTO departments (id, name, code, is_active) VALUES
('550e8400-e29b-41d4-a716-446655440001', 'Agentic AI', 'AAI', true);

-- Power Platform Department
INSERT INTO departments (id, name, code, is_active) VALUES
('550e8400-e29b-41d4-a716-446655440002', 'Power Platform', 'PP', true);

-- Human Resource Department
INSERT INTO departments (id, name, code, is_active) VALUES
('550e8400-e29b-41d4-a716-446655440003', 'Human Resource', 'HR', true);

-- IT Department
INSERT INTO departments (id, name, code, is_active) VALUES
('550e8400-e29b-41d4-a716-446655440004', 'IT', 'IT', true);

-- ============================================================
-- Step 3: Insert Users (20 total)
-- Distribution: 2 admins, 4 managers, 2 IT, 2 HR, 10 employees
-- ============================================================

-- Admin 1 (Head of Agentic AI) - Male, Married
INSERT INTO users (id, employee_id, email, full_name, password_hash, role, department_id, designation, date_of_joining, gender, is_married, is_active, preferred_lang) VALUES
('a1b2c3d4-e5f6-7890-abcd-ef1234567890', '1', 'admin.1@novigosolutions.com', 'Rajesh Kumar', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5N8B5N9F8Y8Y2', 'admin', '550e8400-e29b-41d4-a716-446655440001', 'Director', '2026-05-01', 'male', true, true, 'en');

-- Admin 2 (Head of Power Platform) - Female, Single
INSERT INTO users (id, employee_id, email, full_name, password_hash, role, department_id, designation, date_of_joining, gender, is_married, is_active, preferred_lang) VALUES
('a1b2c3d4-e5f6-7890-abcd-ef1234567891', '2', 'admin.2@novigosolutions.com', 'Priya Sharma', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5N8B5N9F8Y8Y2', 'admin', '550e8400-e29b-41d4-a716-446655440002', 'Director', '2026-05-01', 'female', false, true, 'en');

-- Manager 1 (Agentic AI Manager) - Male, Married, reports to Admin 1
INSERT INTO users (id, employee_id, email, full_name, password_hash, role, department_id, manager_id, designation, date_of_joining, gender, is_married, is_active, preferred_lang) VALUES
('a1b2c3d4-e5f6-7890-abcd-ef1234567892', '3', 'manager.1@novigosolutions.com', 'Amit Patel', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5N8B5N9F8Y8Y2', 'manager', '550e8400-e29b-41d4-a716-446655440001', 'a1b2c3d4-e5f6-7890-abcd-ef1234567890', 'Engineering Manager', '2026-05-01', 'male', true, true, 'en');

-- Manager 2 (Power Platform Manager) - Female, Married, reports to Admin 2
INSERT INTO users (id, employee_id, email, full_name, password_hash, role, department_id, manager_id, designation, date_of_joining, gender, is_married, is_active, preferred_lang) VALUES
('a1b2c3d4-e5f6-7890-abcd-ef1234567893', '4', 'manager.2@novigosolutions.com', 'Sneha Gupta', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5N8B5N9F8Y8Y2', 'manager', '550e8400-e29b-41d4-a716-446655440002', 'a1b2c3d4-e5f6-7890-abcd-ef1234567891', 'Development Manager', '2026-05-01', 'female', true, true, 'en');

-- Manager 3 (IT Manager) - Male, Single, reports to Admin 1
INSERT INTO users (id, employee_id, email, full_name, password_hash, role, department_id, manager_id, designation, date_of_joining, gender, is_married, is_active, preferred_lang) VALUES
('a1b2c3d4-e5f6-7890-abcd-ef1234567894', '5', 'manager.3@novigosolutions.com', 'Vikram Singh', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5N8B5N9F8Y8Y2', 'manager', '550e8400-e29b-41d4-a716-446655440004', 'a1b2c3d4-e5f6-7890-abcd-ef1234567890', 'IT Manager', '2026-05-01', 'male', false, true, 'en');

-- Manager 4 (HR Manager) - Female, Married, reports to Admin 2
INSERT INTO users (id, employee_id, email, full_name, password_hash, role, department_id, manager_id, designation, date_of_joining, gender, is_married, is_active, preferred_lang) VALUES
('a1b2c3d4-e5f6-7890-abcd-ef1234567895', '6', 'manager.4@novigosolutions.com', 'Neha Reddy', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5N8B5N9F8Y8Y2', 'manager', '550e8400-e29b-41d4-a716-446655440003', 'a1b2c3d4-e5f6-7890-abcd-ef1234567891', 'HR Manager', '2026-05-01', 'female', true, true, 'en');

-- IT Team Member 1 - Male, Single, reports to IT Manager
INSERT INTO users (id, employee_id, email, full_name, password_hash, role, department_id, manager_id, designation, date_of_joining, gender, is_married, is_active, preferred_lang) VALUES
('a1b2c3d4-e5f6-7890-abcd-ef1234567896', '7', 'it.1@novigosolutions.com', 'Arjun Mehta', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5N8B5N9F8Y8Y2', 'it_team', '550e8400-e29b-41d4-a716-446655440004', 'a1b2c3d4-e5f6-7890-abcd-ef1234567894', 'System Administrator', '2026-05-01', 'male', false, true, 'en');

-- IT Team Member 2 - Female, Married, reports to IT Manager
INSERT INTO users (id, employee_id, email, full_name, password_hash, role, department_id, manager_id, designation, date_of_joining, gender, is_married, is_active, preferred_lang) VALUES
('a1b2c3d4-e5f6-7890-abcd-ef1234567897', '8', 'it.2@novigosolutions.com', 'Pooja Nair', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5N8B5N9F8Y8Y2', 'it_team', '550e8400-e29b-41d4-a716-446655440004', 'a1b2c3d4-e5f6-7890-abcd-ef1234567894', 'Network Engineer', '2026-05-01', 'female', true, true, 'en');

-- HR Team Member 1 - Female, Single, reports to HR Manager
INSERT INTO users (id, employee_id, email, full_name, password_hash, role, department_id, manager_id, designation, date_of_joining, gender, is_married, is_active, preferred_lang) VALUES
('a1b2c3d4-e5f6-7890-abcd-ef1234567898', '9', 'hr.1@novigosolutions.com', 'Kavita Iyer', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5N8B5N9F8Y8Y2', 'hr_team', '550e8400-e29b-41d4-a716-446655440003', 'a1b2c3d4-e5f6-7890-abcd-ef1234567895', 'HR Specialist', '2026-05-01', 'female', false, true, 'en');

-- HR Team Member 2 - Male, Married, reports to HR Manager
INSERT INTO users (id, employee_id, email, full_name, password_hash, role, department_id, manager_id, designation, date_of_joining, gender, is_married, is_active, preferred_lang) VALUES
('a1b2c3d4-e5f6-7890-abcd-ef1234567899', '10', 'hr.2@novigosolutions.com', 'Rahul Joshi', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5N8B5N9F8Y8Y2', 'hr_team', '550e8400-e29b-41d4-a716-446655440003', 'a1b2c3d4-e5f6-7890-abcd-ef1234567895', 'Recruiter', '2026-05-01', 'male', true, true, 'en');

-- Employee 1 (Agentic AI) - Male, Single, reports to Manager 1
INSERT INTO users (id, employee_id, email, full_name, password_hash, role, department_id, manager_id, designation, date_of_joining, gender, is_married, is_active, preferred_lang) VALUES
('a1b2c3d4-e5f6-7890-abcd-ef12345678a0', '11', 'emp.1@novigosolutions.com', 'Suresh Kumar', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5N8B5N9F8Y8Y2', 'employee', '550e8400-e29b-41d4-a716-446655440001', 'a1b2c3d4-e5f6-7890-abcd-ef1234567892', 'ML Engineer', '2026-05-01', 'male', false, true, 'en');

-- Employee 2 (Agentic AI) - Female, Married, reports to Manager 1
INSERT INTO users (id, employee_id, email, full_name, password_hash, role, department_id, manager_id, designation, date_of_joining, gender, is_married, is_active, preferred_lang) VALUES
('a1b2c3d4-e5f6-7890-abcd-ef12345678a1', '12', 'emp.2@novigosolutions.com', 'Anita Desai', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5N8B5N9F8Y8Y2', 'employee', '550e8400-e29b-41d4-a716-446655440001', 'a1b2c3d4-e5f6-7890-abcd-ef1234567892', 'Data Scientist', '2026-05-01', 'female', true, true, 'en');

-- Employee 3 (Agentic AI) - Male, Married, reports to Manager 1
INSERT INTO users (id, employee_id, email, full_name, password_hash, role, department_id, manager_id, designation, date_of_joining, gender, is_married, is_active, preferred_lang) VALUES
('a1b2c3d4-e5f6-7890-abcd-ef12345678a2', '13', 'emp.3@novigosolutions.com', 'Deepak Verma', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5N8B5N9F8Y8Y2', 'employee', '550e8400-e29b-41d4-a716-446655440001', 'a1b2c3d4-e5f6-7890-abcd-ef1234567892', 'AI Engineer', '2026-05-01', 'male', true, true, 'en');

-- Employee 4 (Agentic AI) - Female, Single, reports to Manager 1
INSERT INTO users (id, employee_id, email, full_name, password_hash, role, department_id, manager_id, designation, date_of_joining, gender, is_married, is_active, preferred_lang) VALUES
('a1b2c3d4-e5f6-7890-abcd-ef12345678a3', '14', 'emp.4@novigosolutions.com', 'Meera Krishnan', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5N8B5N9F8Y8Y2', 'employee', '550e8400-e29b-41d4-a716-446655440001', 'a1b2c3d4-e5f6-7890-abcd-ef1234567892', 'Research Scientist', '2026-05-01', 'female', false, true, 'en');

-- Employee 5 (Agentic AI) - Male, Single, reports to Manager 1
INSERT INTO users (id, employee_id, email, full_name, password_hash, role, department_id, manager_id, designation, date_of_joining, gender, is_married, is_active, preferred_lang) VALUES
('a1b2c3d4-e5f6-7890-abcd-ef12345678a4', '15', 'emp.5@novigosolutions.com', 'Karthik Rajan', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5N8B5N9F8Y8Y2', 'employee', '550e8400-e29b-41d4-a716-446655440001', 'a1b2c3d4-e5f6-7890-abcd-ef1234567892', 'ML Engineer', '2026-05-01', 'male', false, true, 'en');

-- Employee 6 (Power Platform) - Female, Married, reports to Manager 2
INSERT INTO users (id, employee_id, email, full_name, password_hash, role, department_id, manager_id, designation, date_of_joining, gender, is_married, is_active, preferred_lang) VALUES
('a1b2c3d4-e5f6-7890-abcd-ef12345678a5', '16', 'emp.6@novigosolutions.com', 'Lakshmi Menon', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5N8B5N9F8Y8Y2', 'employee', '550e8400-e29b-41d4-a716-446655440002', 'a1b2c3d4-e5f6-7890-abcd-ef1234567893', 'Power Apps Developer', '2026-05-01', 'female', true, true, 'en');

-- Employee 7 (Power Platform) - Male, Single, reports to Manager 2
INSERT INTO users (id, employee_id, email, full_name, password_hash, role, department_id, manager_id, designation, date_of_joining, gender, is_married, is_active, preferred_lang) VALUES
('a1b2c3d4-e5f6-7890-abcd-ef12345678a6', '17', 'emp.7@novigosolutions.com', 'Naveen Babu', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5N8B5N9F8Y8Y2', 'employee', '550e8400-e29b-41d4-a716-446655440002', 'a1b2c3d4-e5f6-7890-abcd-ef1234567893', 'Power Automate Developer', '2026-05-01', 'male', false, true, 'en');

-- Employee 8 (Power Platform) - Female, Single, reports to Manager 2
INSERT INTO users (id, employee_id, email, full_name, password_hash, role, department_id, manager_id, designation, date_of_joining, gender, is_married, is_active, preferred_lang) VALUES
('a1b2c3d4-e5f6-7890-abcd-ef12345678a7', '18', 'emp.8@novigosolutions.com', 'Divya Pillai', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5N8B5N9F8Y8Y2', 'employee', '550e8400-e29b-41d4-a716-446655440002', 'a1b2c3d4-e5f6-7890-abcd-ef1234567893', 'Power BI Developer', '2026-05-01', 'female', false, true, 'en');

-- Employee 9 (Power Platform) - Male, Married, reports to Manager 2
INSERT INTO users (id, employee_id, email, full_name, password_hash, role, department_id, manager_id, designation, date_of_joining, gender, is_married, is_active, preferred_lang) VALUES
('a1b2c3d4-e5f6-7890-abcd-ef12345678a8', '19', 'emp.9@novigosolutions.com', 'Prakash Nair', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5N8B5N9F8Y8Y2', 'employee', '550e8400-e29b-41d4-a716-446655440002', 'a1b2c3d4-e5f6-7890-abcd-ef1234567893', 'Power Platform Architect', '2026-05-01', 'male', true, true, 'en');

-- Employee 10 (Power Platform) - Female, Single, reports to Manager 2
INSERT INTO users (id, employee_id, email, full_name, password_hash, role, department_id, manager_id, designation, date_of_joining, gender, is_married, is_active, preferred_lang) VALUES
('a1b2c3d4-e5f6-7890-abcd-ef12345678a9', '20', 'emp.10@novigosolutions.com', 'Swati Sharma', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5N8B5N9F8Y8Y2', 'employee', '550e8400-e29b-41d4-a716-446655440002', 'a1b2c3d4-e5f6-7890-abcd-ef1234567893', 'Power Apps Developer', '2026-05-01', 'female', false, true, 'en');

-- ============================================================
-- Step 4: Update Department Heads
-- ============================================================

-- Set department heads
UPDATE departments SET head_id = 'a1b2c3d4-e5f6-7890-abcd-ef1234567890' WHERE id = '550e8400-e29b-41d4-a716-446655440001'; -- Agentic AI head: Admin 1
UPDATE departments SET head_id = 'a1b2c3d4-e5f6-7890-abcd-ef1234567891' WHERE id = '550e8400-e29b-41d4-a716-446655440002'; -- Power Platform head: Admin 2
UPDATE departments SET head_id = 'a1b2c3d4-e5f6-7890-abcd-ef1234567895' WHERE id = '550e8400-e29b-41d4-a716-446655440003'; -- HR head: Manager 4
UPDATE departments SET head_id = 'a1b2c3d4-e5f6-7890-abcd-ef1234567894' WHERE id = '550e8400-e29b-41d4-a716-446655440004'; -- IT head: Manager 3

-- ============================================================
-- Step 5: Insert 2026 Holidays (10 mandatory, all weekdays)
-- ============================================================

INSERT INTO holiday_calendar (holiday_date, name, is_optional) VALUES
('2026-01-14', 'Makar Sankranti / Pongal', false),
('2026-01-26', 'Republic Day', false),
('2026-03-19', 'Ugadi / Gudi Padwa', false),
('2026-04-03', 'Good Friday', false),
('2026-05-01', 'May Day', false),
('2026-05-28', 'Bakrid / Eid ul-Adha', false),
('2026-09-14', 'Ganesh Chathurthi / Vinayaka Chaturthi', false),
('2026-10-02', 'Mahatma Gandhi Jayanti', false),
('2026-10-21', 'Dussehra / Dasara', false),
('2026-11-10', 'Diwali / Deepavali', false);

-- ============================================================
-- Step 6: Insert 2027 Holidays (10 mandatory, all weekdays)
-- ============================================================

INSERT INTO holiday_calendar (holiday_date, name, is_optional) VALUES
('2027-01-14', 'Makar Sankranti / Pongal', false),
('2027-01-26', 'Republic Day', false),
('2027-03-22', 'Holi', false),
('2027-04-06', 'Good Friday', false),
('2027-04-19', 'Ugadi / Gudi Padwa', false),
('2027-06-17', 'Bakri Id / Eid ul-Adha', false),
('2027-08-15', 'Independence Day', false),
('2027-09-02', 'Vinayaka Chaturthi / Ganesh Chaturthi', false),
('2027-10-02', 'Mahatma Gandhi Jayanti', false),
('2027-10-20', 'Dussehra / Dasara', false);

-- ============================================================
-- Step 7: Insert 2026 Leave Balances
-- Policy:
-- - earned: 14 days (everyone)
-- - sick: 6 days (everyone)
-- - maternity: 182 days (females only)
-- - miscarriage: 42 days (females only)
-- - paternity: 3 days (married males only)
-- - bereavement: 3 days (everyone)
-- - unpaid: 0 (only for medical/emergency after earned exhausted)
-- - compensatory: 0 (not seeded)
-- ============================================================

-- Helper: Insert balances for all users (common types)
INSERT INTO leave_balances (user_id, year, leave_type, entitled_days, used_days, pending_days, carried_over)
SELECT id, 2026, 'earned', 14, 0, 0, 0 FROM users;

INSERT INTO leave_balances (user_id, year, leave_type, entitled_days, used_days, pending_days, carried_over)
SELECT id, 2026, 'sick', 6, 0, 0, 0 FROM users;

INSERT INTO leave_balances (user_id, year, leave_type, entitled_days, used_days, pending_days, carried_over)
SELECT id, 2026, 'bereavement', 3, 0, 0, 0 FROM users;

-- Maternity leave (females only)
INSERT INTO leave_balances (user_id, year, leave_type, entitled_days, used_days, pending_days, carried_over)
SELECT id, 2026, 'maternity', 182, 0, 0, 0 FROM users WHERE gender = 'female';

-- Miscarriage leave (females only)
INSERT INTO leave_balances (user_id, year, leave_type, entitled_days, used_days, pending_days, carried_over)
SELECT id, 2026, 'miscarriage', 42, 0, 0, 0 FROM users WHERE gender = 'female';

-- Paternity leave (married males only)
INSERT INTO leave_balances (user_id, year, leave_type, entitled_days, used_days, pending_days, carried_over)
SELECT id, 2026, 'paternity', 3, 0, 0, 0 FROM users WHERE gender = 'male' AND is_married = true;

-- Compensatory and unpaid (0 for everyone)
INSERT INTO leave_balances (user_id, year, leave_type, entitled_days, used_days, pending_days, carried_over)
SELECT id, 2026, 'compensatory', 0, 0, 0, 0 FROM users;

INSERT INTO leave_balances (user_id, year, leave_type, entitled_days, used_days, pending_days, carried_over)
SELECT id, 2026, 'unpaid', 0, 0, 0, 0 FROM users;

-- ============================================================
-- Step 8: Idempotent IT permission upgrades (existing DBs)
-- ============================================================
-- New permissions for IT policy / KB tools. Safe to re-run.

INSERT INTO permissions (code, description, module) VALUES
    ('it:policy:read', 'Read IT policy documents',        'it'),
    ('it:kb:search',   'Search IT knowledge base / FAQs', 'it')
ON CONFLICT (code) DO NOTHING;

-- Grant to employee + manager (idempotent — only inserts missing rows)
INSERT INTO role_permissions (role, perm_id)
SELECT 'employee'::user_role, p.id
FROM permissions p
WHERE p.code IN ('it:policy:read', 'it:kb:search')
  AND NOT EXISTS (
      SELECT 1 FROM role_permissions rp
      WHERE rp.role = 'employee'::user_role AND rp.perm_id = p.id
  );

INSERT INTO role_permissions (role, perm_id)
SELECT 'manager'::user_role, p.id
FROM permissions p
WHERE p.code IN ('it:policy:read', 'it:kb:search')
  AND NOT EXISTS (
      SELECT 1 FROM role_permissions rp
      WHERE rp.role = 'manager'::user_role AND rp.perm_id = p.id
  );

-- IT team: grant all IT permissions (idempotent)
INSERT INTO role_permissions (role, perm_id)
SELECT 'it_team'::user_role, p.id
FROM permissions p
WHERE p.module = 'it'
  AND NOT EXISTS (
      SELECT 1 FROM role_permissions rp
      WHERE rp.role = 'it_team'::user_role AND rp.perm_id = p.id
  );

-- Admin: all permissions (idempotent)
INSERT INTO role_permissions (role, perm_id)
SELECT 'admin'::user_role, p.id
FROM permissions p
WHERE NOT EXISTS (
    SELECT 1 FROM role_permissions rp
    WHERE rp.role = 'admin'::user_role AND rp.perm_id = p.id
);

-- ============================================================
-- Step 9: IT Inventory (20 assets)
-- ============================================================

DELETE FROM it_inventory;

-- 8 laptops assigned to specific employees
INSERT INTO it_inventory (asset_tag, asset_type, brand, model, serial_no, status, assigned_to, assigned_at, purchase_date, warranty_until, location) VALUES
('LAP-001', 'laptop', 'Dell',   'Latitude 7440',  'DLT7440-A001', 'assigned', 'a1b2c3d4-e5f6-7890-abcd-ef1234567890', NOW() - INTERVAL '120 days', '2025-09-15', '2028-09-15', 'Bangalore HQ'),
('LAP-002', 'laptop', 'Dell',   'Latitude 7440',  'DLT7440-A002', 'assigned', 'a1b2c3d4-e5f6-7890-abcd-ef1234567892', NOW() - INTERVAL '110 days', '2025-09-15', '2028-09-15', 'Bangalore HQ'),
('LAP-003', 'laptop', 'Dell',   'Latitude 5440',  'DLT5440-A003', 'assigned', 'a1b2c3d4-e5f6-7890-abcd-ef12345678a0', NOW() - INTERVAL '100 days', '2025-10-01', '2028-10-01', 'Bangalore HQ'),
('LAP-004', 'laptop', 'Dell',   'Latitude 5440',  'DLT5440-A004', 'assigned', 'a1b2c3d4-e5f6-7890-abcd-ef12345678a1', NOW() - INTERVAL '95 days',  '2025-10-01', '2028-10-01', 'Bangalore HQ'),
('LAP-005', 'laptop', 'Lenovo', 'ThinkPad T14',   'LTP-T14-A005', 'assigned', 'a1b2c3d4-e5f6-7890-abcd-ef12345678a2', NOW() - INTERVAL '90 days',  '2025-10-15', '2028-10-15', 'Bangalore HQ'),
('LAP-006', 'laptop', 'Lenovo', 'ThinkPad T14',   'LTP-T14-A006', 'assigned', 'a1b2c3d4-e5f6-7890-abcd-ef12345678a5', NOW() - INTERVAL '85 days',  '2025-10-15', '2028-10-15', 'Bangalore HQ'),
('LAP-007', 'laptop', 'HP',     'EliteBook 840',  'HPEB840-A007', 'assigned', 'a1b2c3d4-e5f6-7890-abcd-ef12345678a6', NOW() - INTERVAL '80 days',  '2025-11-01', '2028-11-01', 'Bangalore HQ'),
('LAP-008', 'laptop', 'HP',     'EliteBook 840',  'HPEB840-A008', 'assigned', 'a1b2c3d4-e5f6-7890-abcd-ef12345678a8', NOW() - INTERVAL '75 days',  '2025-11-01', '2028-11-01', 'Bangalore HQ'),

-- 4 available laptops
('LAP-009', 'laptop', 'Dell',   'Latitude 5440',  'DLT5440-A009', 'available', NULL, NULL, '2026-01-10', '2029-01-10', 'IT Storeroom'),
('LAP-010', 'laptop', 'Dell',   'Latitude 5440',  'DLT5440-A010', 'available', NULL, NULL, '2026-01-10', '2029-01-10', 'IT Storeroom'),
('LAP-011', 'laptop', 'Lenovo', 'ThinkPad T14',   'LTP-T14-A011', 'available', NULL, NULL, '2026-02-05', '2029-02-05', 'IT Storeroom'),
('LAP-012', 'laptop', 'HP',     'EliteBook 840',  'HPEB840-A012', 'available', NULL, NULL, '2026-02-15', '2029-02-15', 'IT Storeroom'),

-- 4 monitors (mix of assigned + available)
('MON-001', 'monitor', 'Dell',   'U2723QE 27"',   'DLU2723-M001', 'assigned', 'a1b2c3d4-e5f6-7890-abcd-ef1234567890', NOW() - INTERVAL '120 days', '2025-09-15', '2028-09-15', 'Bangalore HQ'),
('MON-002', 'monitor', 'Dell',   'U2723QE 27"',   'DLU2723-M002', 'assigned', 'a1b2c3d4-e5f6-7890-abcd-ef1234567892', NOW() - INTERVAL '110 days', '2025-09-15', '2028-09-15', 'Bangalore HQ'),
('MON-003', 'monitor', 'LG',     '27UP850 27"',   'LG27UP-M003',  'available', NULL, NULL, '2026-01-20', '2029-01-20', 'IT Storeroom'),
('MON-004', 'monitor', 'LG',     '27UP850 27"',   'LG27UP-M004',  'available', NULL, NULL, '2026-01-20', '2029-01-20', 'IT Storeroom'),

-- 2 VPN tokens
('VPN-001', 'vpn_token', 'YubiKey', '5C NFC',     'YK5C-V001',    'assigned', 'a1b2c3d4-e5f6-7890-abcd-ef1234567894', NOW() - INTERVAL '180 days', '2025-08-01', '2030-08-01', 'IT Storeroom'),
('VPN-002', 'vpn_token', 'YubiKey', '5C NFC',     'YK5C-V002',    'available', NULL, NULL, '2026-03-01', '2031-03-01', 'IT Storeroom'),

-- 2 docking stations
('DOC-001', 'docking_station', 'Dell', 'WD19 Thunderbolt', 'DLWD19-D001', 'assigned',  'a1b2c3d4-e5f6-7890-abcd-ef1234567890', NOW() - INTERVAL '120 days', '2025-09-15', '2028-09-15', 'Bangalore HQ'),
('DOC-002', 'docking_station', 'Dell', 'WD19 Thunderbolt', 'DLWD19-D002', 'available', NULL, NULL, '2026-02-15', '2029-02-15', 'IT Storeroom');

-- ============================================================
-- Step 10: Known Issues / FAQ knowledge base (15 entries)
-- ============================================================

DELETE FROM known_issues;

INSERT INTO known_issues (title, category, description, workaround, is_active) VALUES
-- Laptop
('Slow laptop boot after Windows November update',
 'laptop',
 'Several Dell Latitude 7440 / 5440 users report 3–5 minute boot times after the November Windows cumulative update (KB5031356). Root cause: outdated Intel Management Engine driver.',
 'Install Dell Command Update and apply all pending firmware/driver patches. Reboot twice. If issue persists, raise a ticket and IT will reimage.',
 true),
('Laptop battery drains overnight while shut down',
 'laptop',
 'Some laptops lose 15–25% charge overnight even when fully shut down. Caused by USB wake-from-S5 enabled in BIOS.',
 'Boot to BIOS (F2 at startup) → Power Management → disable "Wake on USB" and "Deep Sleep Control" set to Enabled. Save and reboot.',
 true),
('Built-in keyboard intermittently unresponsive',
 'laptop',
 'Keyboard stops responding randomly on Lenovo ThinkPad T14. External USB keyboard works fine.',
 'Open Device Manager → Keyboards → uninstall "HID Keyboard Device" → reboot. Windows reinstalls the driver. If recurring, IT will replace the keyboard FRU.',
 true),

-- VPN
('VPN connection drops every ~30 minutes',
 'vpn',
 'Cisco AnyConnect users on home Wi-Fi see the tunnel disconnect every 30 minutes. Caused by aggressive NAT timeout on consumer routers.',
 'Open AnyConnect → Preferences → enable "Block connections to untrusted servers" OFF and "Auto-Reconnect" ON. As a permanent fix, request a YubiKey-backed always-on VPN profile via an IT ticket.',
 true),
('Slow VPN speeds (< 5 Mbps) on home internet',
 'vpn',
 'Throughput on Cisco AnyConnect drops below 5 Mbps even on a 100 Mbps line. Caused by DTLS being blocked by some ISPs.',
 'In AnyConnect → Settings → uncheck "Enable DTLS". This forces TLS-only and typically restores normal speeds (some latency overhead).',
 true),

-- Email
('Outlook desktop not syncing new emails',
 'email',
 'Outlook 365 desktop shows old mail but stops pulling new mail. Web Outlook works fine.',
 'File → Account Settings → Account Settings → select your account → Repair. If still failing, close Outlook, delete the OST file at %localappdata%\\Microsoft\\Outlook\\, reopen Outlook to rebuild.',
 true),
('Calendar invites not appearing in Outlook',
 'email',
 'Meeting invites land in inbox but never auto-process onto the calendar.',
 'File → Options → Mail → uncheck "Delete meeting requests and notifications from inbox after responding". Then File → Options → Calendar → check "Automatically accept meeting requests".',
 true),

-- Network
('Wi-Fi keeps dropping on 4th-floor conference rooms',
 'network',
 'Known weak coverage zone in 4F-Atlas, 4F-Gemini conference rooms. AP replacement scheduled for next quarter.',
 'Use the wired ethernet drops in the rooms (cables in the credenza) or tether to phone hotspot for critical calls. Report any new dead zones via IT ticket.',
 true),
('Internet slow only when on company Wi-Fi (CORP-WIFI)',
 'network',
 'Throughput drops to <10 Mbps on CORP-WIFI during 10am–12pm peak hours. CORP-IOT and guest networks unaffected.',
 'Forget and rejoin CORP-WIFI. If still slow, switch to wired or use CORP-WIFI-5G (5 GHz only) which is less congested.',
 true),

-- Software install
('Microsoft Teams crashes on startup after update',
 'software_install',
 'Teams (new version) crashes immediately after launch. Affects users on Windows 11 22H2.',
 'Quit Teams from system tray. Delete %appdata%\\Microsoft\\Teams\\ and %localappdata%\\Packages\\MSTeams_*. Reinstall via Software Center.',
 true),
('Zoom audio not working on Bluetooth headset',
 'software_install',
 'Zoom shows headset connected but audio routes to laptop speakers / mic.',
 'Zoom Settings → Audio → set Speaker AND Microphone to your headset name (not "System Default"). Reconnect the headset before joining the meeting.',
 true),

-- Access
('Locked out after multiple password attempts',
 'access',
 'Active Directory account locks for 30 minutes after 5 failed attempts.',
 'Wait 30 minutes for auto-unlock OR raise a ticket with category=access for immediate unlock. To reset password, visit https://passwords.novigosolutions.com from a corporate device.',
 true),
('MFA push notifications not arriving on phone',
 'access',
 'Microsoft Authenticator does not show approval prompts when signing in.',
 'Open Authenticator → tap your account → "Check for notifications". If still failing, on the phone: Settings → Apps → Authenticator → Notifications → enable all categories. Battery optimization for Authenticator must be OFF.',
 true),

-- Printer
('Print queue stuck — jobs not printing',
 'printer',
 'Print jobs accumulate in queue with status "Spooling" or "Error – Printing".',
 'Settings → Bluetooth & Devices → Printers → select printer → Open print queue → Cancel all. Then services.msc → restart "Print Spooler". Resubmit the job.',
 true),

-- Hardware
('External monitor flickers on USB-C connection',
 'hardware',
 'Monitor flickers / disconnects every few minutes when connected via USB-C dock.',
 'Use a Thunderbolt 3/4 cable rated for full power delivery (not a generic USB-C cable). If using DisplayPort over USB-C, ensure dock firmware is current via Dell Command Update.',
 true);

-- ============================================================
-- Seed Complete
-- ============================================================
