-- ============================================================
-- Enterprise AI Copilot — Full Database Schema
-- PostgreSQL 15+ with pgvector extension
-- ============================================================

-- Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "vector";           -- pgvector for RAG embeddings

-- ============================================================
-- ENUMS
-- ============================================================

CREATE TYPE user_role AS ENUM (
    'employee', 'manager', 'hr_team', 'it_team', 'finance_team', 'admin'
);

CREATE TYPE leave_status AS ENUM (
    'pending', 'approved', 'rejected', 'cancelled'
);

CREATE TYPE leave_type AS ENUM (
    'casual', 'sick', 'earned', 'maternity', 'paternity',
    'bereavement', 'compensatory', 'unpaid'
);

CREATE TYPE ticket_status AS ENUM (
    'open', 'in_progress', 'on_hold', 'resolved', 'closed'
);

CREATE TYPE ticket_priority AS ENUM (
    'low', 'medium', 'high', 'critical'
);

CREATE TYPE ticket_category AS ENUM (
    'laptop', 'vpn', 'email', 'printer', 'network',
    'software_install', 'hardware', 'access', 'other'
);

CREATE TYPE asset_status AS ENUM (
    'available', 'assigned', 'in_repair', 'retired', 'lost'
);

CREATE TYPE asset_type AS ENUM (
    'laptop', 'monitor', 'keyboard', 'mouse', 'vpn_token',
    'software_license', 'headset', 'docking_station', 'other'
);

CREATE TYPE request_status AS ENUM (
    'pending', 'manager_approved', 'it_approved',
    'rejected', 'fulfilled', 'cancelled'
);

CREATE TYPE reimbursement_category AS ENUM (
    'travel', 'internet', 'food', 'client_meeting',
    'training', 'office_supplies', 'other'
);

CREATE TYPE reimbursement_status AS ENUM (
    'draft', 'submitted', 'under_review', 'approved',
    'rejected', 'paid'
);

CREATE TYPE approval_entity AS ENUM (
    'leave', 'asset_request', 'reimbursement', 'it_action'
);

CREATE TYPE approval_decision AS ENUM (
    'pending', 'approved', 'rejected', 'escalated'
);

CREATE TYPE doc_department AS ENUM (
    'hr', 'it', 'finance', 'general'
);

-- ============================================================
-- CORE: USERS & DEPARTMENTS
-- ============================================================

CREATE TABLE departments (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name        VARCHAR(100) NOT NULL UNIQUE,
    code        VARCHAR(20)  NOT NULL UNIQUE,           -- 'HR', 'IT', 'FIN', 'ENG'
    head_id     UUID,                                   -- FK set later (circular ref)
    is_active   BOOLEAN NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    employee_id     VARCHAR(20) NOT NULL UNIQUE,        -- 'EMP-001'
    email           VARCHAR(255) NOT NULL UNIQUE,
    full_name       VARCHAR(200) NOT NULL,
    password_hash   TEXT NOT NULL,
    role            user_role NOT NULL DEFAULT 'employee',
    department_id   UUID REFERENCES departments(id) ON DELETE SET NULL,
    manager_id      UUID REFERENCES users(id) ON DELETE SET NULL,
    designation     VARCHAR(150),
    date_of_joining DATE,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    preferred_lang  VARCHAR(10) NOT NULL DEFAULT 'en',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Resolve circular ref: departments.head_id → users.id
ALTER TABLE departments
    ADD CONSTRAINT fk_dept_head FOREIGN KEY (head_id)
    REFERENCES users(id) ON DELETE SET NULL;

-- ============================================================
-- RBAC: FINE-GRAINED PERMISSIONS
-- ============================================================

CREATE TABLE permissions (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code        VARCHAR(100) NOT NULL UNIQUE,          -- 'leave:approve', 'ticket:view_all'
    description TEXT,
    module      VARCHAR(50) NOT NULL                   -- 'hr', 'it', 'finance'
);

CREATE TABLE role_permissions (
    role        user_role NOT NULL,
    perm_id     UUID NOT NULL REFERENCES permissions(id) ON DELETE CASCADE,
    PRIMARY KEY (role, perm_id)
);

CREATE TABLE user_permission_overrides (
    user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    perm_id     UUID NOT NULL REFERENCES permissions(id) ON DELETE CASCADE,
    granted     BOOLEAN NOT NULL DEFAULT TRUE,         -- TRUE=grant, FALSE=revoke
    reason      TEXT,
    granted_by  UUID REFERENCES users(id),
    expires_at  TIMESTAMPTZ,
    PRIMARY KEY (user_id, perm_id)
);

-- ============================================================
-- HR MODULE
-- ============================================================

CREATE TABLE leave_balances (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    year            INTEGER NOT NULL,
    leave_type      leave_type NOT NULL,
    entitled_days   NUMERIC(5,1) NOT NULL DEFAULT 0,
    used_days       NUMERIC(5,1) NOT NULL DEFAULT 0,
    pending_days    NUMERIC(5,1) NOT NULL DEFAULT 0,   -- approved but not yet taken
    carried_over    NUMERIC(5,1) NOT NULL DEFAULT 0,
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (user_id, year, leave_type)
);

CREATE TABLE leave_requests (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    leave_type      leave_type NOT NULL,
    start_date      DATE NOT NULL,
    end_date        DATE NOT NULL,
    business_days   NUMERIC(4,1) NOT NULL,             -- computed, excludes weekends/holidays
    reason          TEXT,
    status          leave_status NOT NULL DEFAULT 'pending',
    applied_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    reviewed_by     UUID REFERENCES users(id),
    reviewed_at     TIMESTAMPTZ,
    reviewer_note   TEXT,
    is_half_day     BOOLEAN NOT NULL DEFAULT FALSE,
    half_day_slot   VARCHAR(10),                       -- 'morning' | 'afternoon'
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT valid_dates CHECK (end_date >= start_date),
    CONSTRAINT valid_business_days CHECK (business_days > 0)
);

CREATE TABLE holiday_calendar (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    holiday_date DATE NOT NULL,
    name        VARCHAR(200) NOT NULL,
    year        INTEGER NOT NULL GENERATED ALWAYS AS (EXTRACT(YEAR FROM holiday_date)::INT) STORED,
    is_optional BOOLEAN NOT NULL DEFAULT FALSE,
    UNIQUE (holiday_date, is_optional)
);

-- ============================================================
-- IT MODULE
-- ============================================================

CREATE TABLE it_tickets (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ticket_no       VARCHAR(20) NOT NULL UNIQUE,       -- 'TKT-20240001'
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    category        ticket_category NOT NULL,
    subject         VARCHAR(500) NOT NULL,
    description     TEXT NOT NULL,
    priority        ticket_priority NOT NULL DEFAULT 'medium',
    status          ticket_status NOT NULL DEFAULT 'open',
    assigned_to     UUID REFERENCES users(id),
    parent_ticket   UUID REFERENCES it_tickets(id),   -- for duplicate linking
    resolution      TEXT,
    is_known_issue  BOOLEAN NOT NULL DEFAULT FALSE,
    outage_ref      VARCHAR(100),                      -- reference to outage/maintenance ID
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    resolved_at     TIMESTAMPTZ,
    sla_due_at      TIMESTAMPTZ                        -- computed based on priority
);

CREATE TABLE it_ticket_comments (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ticket_id   UUID NOT NULL REFERENCES it_tickets(id) ON DELETE CASCADE,
    author_id   UUID NOT NULL REFERENCES users(id),
    comment     TEXT NOT NULL,
    is_internal BOOLEAN NOT NULL DEFAULT FALSE,        -- internal IT note vs user-visible
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE maintenance_schedule (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title           VARCHAR(300) NOT NULL,
    affected_system VARCHAR(200) NOT NULL,
    starts_at       TIMESTAMPTZ NOT NULL,
    ends_at         TIMESTAMPTZ NOT NULL,
    description     TEXT,
    created_by      UUID REFERENCES users(id),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE known_issues (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title           VARCHAR(300) NOT NULL,
    category        ticket_category NOT NULL,
    description     TEXT NOT NULL,
    workaround      TEXT,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    reported_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    resolved_at     TIMESTAMPTZ
);

CREATE TABLE it_inventory (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    asset_tag       VARCHAR(50) NOT NULL UNIQUE,
    asset_type      asset_type NOT NULL,
    brand           VARCHAR(100),
    model           VARCHAR(200),
    serial_no       VARCHAR(100) UNIQUE,
    status          asset_status NOT NULL DEFAULT 'available',
    assigned_to     UUID REFERENCES users(id),
    assigned_at     TIMESTAMPTZ,
    purchase_date   DATE,
    warranty_until  DATE,
    location        VARCHAR(200),
    notes           TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE asset_requests (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    asset_type      asset_type NOT NULL,
    justification   TEXT NOT NULL,
    status          request_status NOT NULL DEFAULT 'pending',
    manager_id      UUID REFERENCES users(id),
    manager_action  TIMESTAMPTZ,
    manager_note    TEXT,
    it_actioned_by  UUID REFERENCES users(id),
    it_action_at    TIMESTAMPTZ,
    it_note         TEXT,
    asset_id        UUID REFERENCES it_inventory(id), -- assigned asset (post-approval)
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================
-- FINANCE MODULE
-- ============================================================

CREATE TABLE payroll_records (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    pay_month       DATE NOT NULL,                     -- first day of month
    gross_salary    NUMERIC(12,2) NOT NULL,
    basic           NUMERIC(12,2) NOT NULL,
    hra             NUMERIC(12,2) NOT NULL DEFAULT 0,
    allowances      NUMERIC(12,2) NOT NULL DEFAULT 0,
    pf_employee     NUMERIC(12,2) NOT NULL DEFAULT 0,
    pf_employer     NUMERIC(12,2) NOT NULL DEFAULT 0,
    tds             NUMERIC(12,2) NOT NULL DEFAULT 0,
    professional_tax NUMERIC(12,2) NOT NULL DEFAULT 0,
    other_deductions NUMERIC(12,2) NOT NULL DEFAULT 0,
    net_salary      NUMERIC(12,2) NOT NULL,
    payslip_url     TEXT,                              -- S3/storage URL
    generated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (user_id, pay_month)
);

CREATE TABLE reimbursements (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    claim_no        VARCHAR(20) NOT NULL UNIQUE,       -- 'CLM-20240001'
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    category        reimbursement_category NOT NULL,
    amount          NUMERIC(10,2) NOT NULL,
    currency        CHAR(3) NOT NULL DEFAULT 'INR',
    description     TEXT NOT NULL,
    expense_date    DATE NOT NULL,
    receipt_url     TEXT,                              -- stored file URL
    status          reimbursement_status NOT NULL DEFAULT 'draft',
    submitted_at    TIMESTAMPTZ,
    reviewed_by     UUID REFERENCES users(id),
    reviewed_at     TIMESTAMPTZ,
    reviewer_note   TEXT,
    paid_at         TIMESTAMPTZ,
    payment_ref     VARCHAR(100),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT positive_amount CHECK (amount > 0)
);

CREATE TABLE tax_declarations (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    fiscal_year     VARCHAR(10) NOT NULL,              -- '2024-25'
    regime          VARCHAR(20) NOT NULL DEFAULT 'new', -- 'old' | 'new'
    section_80c     NUMERIC(12,2) NOT NULL DEFAULT 0,
    section_80d     NUMERIC(12,2) NOT NULL DEFAULT 0,
    hra_claimed     NUMERIC(12,2) NOT NULL DEFAULT 0,
    lta_claimed     NUMERIC(12,2) NOT NULL DEFAULT 0,
    other_deductions NUMERIC(12,2) NOT NULL DEFAULT 0,
    submitted_at    TIMESTAMPTZ,
    is_final        BOOLEAN NOT NULL DEFAULT FALSE,
    UNIQUE (user_id, fiscal_year)
);

-- ============================================================
-- APPROVAL WORKFLOW (unified)
-- ============================================================

CREATE TABLE approvals (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_type     approval_entity NOT NULL,
    entity_id       UUID NOT NULL,                     -- FK to leave_requests / asset_requests / reimbursements
    approver_id     UUID NOT NULL REFERENCES users(id),
    step            INTEGER NOT NULL DEFAULT 1,        -- approval chain step
    decision        approval_decision NOT NULL DEFAULT 'pending',
    note            TEXT,
    decided_at      TIMESTAMPTZ,
    expires_at      TIMESTAMPTZ,                       -- auto-escalate after this
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================
-- MEMORY & CONTEXT (AI-specific)
-- ============================================================

CREATE TABLE user_memory (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    memory_key      VARCHAR(100) NOT NULL,             -- 'preferred_lang', 'frequent_request', 'last_ticket_type'
    memory_value    JSONB NOT NULL,
    source          VARCHAR(50) DEFAULT 'inferred',    -- 'inferred' | 'explicit'
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (user_id, memory_key)
);

CREATE TABLE conversation_sessions (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_key     VARCHAR(200) NOT NULL UNIQUE,      -- 'user:{id}:session:{ts}'
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    messages        JSONB NOT NULL DEFAULT '[]',       -- [{role, content, ts}]
    agent_used      VARCHAR(50),
    started_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_active_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ended_at        TIMESTAMPTZ
);

-- ============================================================
-- RAG: DOCUMENT STORE
-- ============================================================

CREATE TABLE rag_documents (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    filename        VARCHAR(500) NOT NULL,
    department      doc_department NOT NULL,
    doc_type        VARCHAR(100),                      -- 'policy', 'sop', 'handbook', 'faq'
    roles_allowed   user_role[] NOT NULL DEFAULT ARRAY['employee']::user_role[],
    file_url        TEXT,
    ingested_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    chunk_count     INTEGER NOT NULL DEFAULT 0,
    metadata        JSONB NOT NULL DEFAULT '{}'
);

CREATE TABLE rag_chunks (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id     UUID NOT NULL REFERENCES rag_documents(id) ON DELETE CASCADE,
    chunk_index     INTEGER NOT NULL,
    content         TEXT NOT NULL,
    embedding       VECTOR(1536),                      -- OpenAI text-embedding-3-small dimension
    token_count     INTEGER,
    metadata        JSONB NOT NULL DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (document_id, chunk_index)
);

-- ============================================================
-- AUDIT & LOGGING
-- ============================================================

CREATE TABLE audit_logs (
    id              UUID DEFAULT uuid_generate_v4(),
    user_id         UUID REFERENCES users(id),
    session_id      UUID REFERENCES conversation_sessions(id),
    action          VARCHAR(200) NOT NULL,
    entity_type     VARCHAR(100),
    entity_id       UUID,
    agent_used      VARCHAR(100),
    tool_used       VARCHAR(100),
    llm_model       VARCHAR(100),
    status          VARCHAR(50) NOT NULL DEFAULT 'success',
    error_message   TEXT,
    latency_ms      INTEGER,
    token_count     INTEGER,
    ip_address      INET,
    metadata        JSONB NOT NULL DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (id, created_at)  -- Fix: Composite primary key includes the partition key
) PARTITION BY RANGE (created_at);

-- Monthly partitions for audit_logs (create as needed)
CREATE TABLE audit_logs_2024_01
    PARTITION OF audit_logs FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
CREATE TABLE audit_logs_2025_01
    PARTITION OF audit_logs FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');

-- ============================================================
-- INDEXES (performance-critical paths)
-- ============================================================

-- Users
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_dept ON users(department_id);
CREATE INDEX idx_users_manager ON users(manager_id);

-- Leaves
CREATE INDEX idx_leaves_user ON leave_requests(user_id);
CREATE INDEX idx_leaves_status ON leave_requests(status);
CREATE INDEX idx_leaves_dates ON leave_requests(start_date, end_date);

-- IT Tickets
CREATE INDEX idx_tickets_user ON it_tickets(user_id);
CREATE INDEX idx_tickets_status ON it_tickets(status);
CREATE INDEX idx_tickets_assignee ON it_tickets(assigned_to);
CREATE INDEX idx_tickets_created ON it_tickets(created_at DESC);

-- Reimbursements
CREATE INDEX idx_reimb_user ON reimbursements(user_id);
CREATE INDEX idx_reimb_status ON reimbursements(status);

-- Approvals
CREATE INDEX idx_approvals_entity ON approvals(entity_type, entity_id);
CREATE INDEX idx_approvals_approver ON approvals(approver_id, decision);

-- RAG (HNSW index for fast ANN search)
CREATE INDEX idx_rag_embedding ON rag_chunks
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);
CREATE INDEX idx_rag_doc ON rag_chunks(document_id);

-- Audit
CREATE INDEX idx_audit_user ON audit_logs(user_id, created_at DESC);
CREATE INDEX idx_audit_action ON audit_logs(action, created_at DESC);

-- ============================================================
-- FUNCTIONS & TRIGGERS
-- ============================================================

-- Auto-update updated_at on row change
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;

DO $$ DECLARE t TEXT;
BEGIN
  FOREACH t IN ARRAY ARRAY[
    'users', 'departments', 'leave_requests', 'leave_balances',
    'it_tickets', 'it_inventory', 'asset_requests',
    'reimbursements', 'payroll_records'
  ]
  LOOP
    EXECUTE format(
      'CREATE TRIGGER trg_%s_updated_at
       BEFORE UPDATE ON %I
       FOR EACH ROW EXECUTE FUNCTION set_updated_at()', t, t
    );
  END LOOP;
END $$;

-- Auto-generate ticket numbers
CREATE SEQUENCE ticket_seq START 1;
CREATE OR REPLACE FUNCTION generate_ticket_no()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    NEW.ticket_no := 'TKT-' || TO_CHAR(NOW(), 'YYYY') ||
                     LPAD(nextval('ticket_seq')::TEXT, 5, '0');
    RETURN NEW;
END;
$$;
CREATE TRIGGER trg_ticket_no
    BEFORE INSERT ON it_tickets
    FOR EACH ROW EXECUTE FUNCTION generate_ticket_no();

-- Auto-generate claim numbers
CREATE SEQUENCE claim_seq START 1;
CREATE OR REPLACE FUNCTION generate_claim_no()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    NEW.claim_no := 'CLM-' || TO_CHAR(NOW(), 'YYYY') ||
                    LPAD(nextval('claim_seq')::TEXT, 5, '0');
    RETURN NEW;
END;
$$;
CREATE TRIGGER trg_claim_no
    BEFORE INSERT ON reimbursements
    FOR EACH ROW EXECUTE FUNCTION generate_claim_no();

-- ============================================================
-- SEED: BASE PERMISSIONS
-- ============================================================

INSERT INTO permissions (code, description, module) VALUES
-- HR
('hr:policy:read',          'Read HR policy documents',         'hr'),
('hr:leave:apply',          'Apply for leave',                  'hr'),
('hr:leave:view_own',       'View own leave requests',          'hr'),
('hr:leave:view_team',      'View team leave requests',         'hr'),
('hr:leave:approve',        'Approve/reject leave requests',    'hr'),
('hr:leave:view_all',       'View all leave requests',          'hr'),
-- IT
('it:ticket:create',        'Create support ticket',            'it'),
('it:ticket:view_own',      'View own tickets',                 'it'),
('it:ticket:view_all',      'View all tickets',                 'it'),
('it:ticket:assign',        'Assign ticket to engineer',        'it'),
('it:ticket:resolve',       'Mark ticket resolved',             'it'),
('it:asset:request',        'Request new asset',                'it'),
('it:asset:approve',        'Approve asset requests',           'it'),
('it:inventory:view',       'View IT inventory',                'it'),
('it:inventory:manage',     'Manage inventory records',         'it'),
-- Finance
('finance:payslip:view_own','View own payslips',                'finance'),
('finance:payslip:view_all','View all payslips',                'finance'),
('finance:claim:submit',    'Submit reimbursement claim',       'finance'),
('finance:claim:view_own',  'View own claims',                  'finance'),
('finance:claim:approve',   'Approve reimbursement claims',     'finance'),
('finance:report:view',     'View finance reports',             'finance'),
('finance:tax:view_own',    'View own tax details',             'finance');

-- Role → permissions mapping
INSERT INTO role_permissions (role, perm_id)
SELECT 'employee'::user_role, id FROM permissions WHERE code IN (
    'hr:policy:read', 'hr:leave:apply', 'hr:leave:view_own',
    'it:ticket:create', 'it:ticket:view_own', 'it:asset:request',
    'finance:payslip:view_own', 'finance:claim:submit',
    'finance:claim:view_own', 'finance:tax:view_own'
);

INSERT INTO role_permissions (role, perm_id)
SELECT 'manager'::user_role, id FROM permissions WHERE code IN (
    'hr:policy:read', 'hr:leave:apply', 'hr:leave:view_own',
    'hr:leave:view_team', 'hr:leave:approve',
    'it:ticket:create', 'it:ticket:view_own', 'it:asset:request',
    'finance:payslip:view_own', 'finance:claim:submit', 'finance:claim:view_own',
    'finance:tax:view_own'
);

INSERT INTO role_permissions (role, perm_id)
SELECT 'hr_team'::user_role, id FROM permissions WHERE module = 'hr';

INSERT INTO role_permissions (role, perm_id)
SELECT 'it_team'::user_role, id FROM permissions WHERE module = 'it';

INSERT INTO role_permissions (role, perm_id)
SELECT 'finance_team'::user_role, id FROM permissions WHERE module = 'finance'
UNION ALL
SELECT 'finance_team'::user_role, id FROM permissions WHERE code = 'hr:policy:read';

INSERT INTO role_permissions (role, perm_id)
SELECT 'admin'::user_role, id FROM permissions;