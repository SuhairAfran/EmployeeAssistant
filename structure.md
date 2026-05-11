# Project Structure

```
├── alembic
│   ├── versions
│   │   └── 06f1ef6a9dd1_initial_schema.py
│   ├── env.py
│   ├── README
│   └── script.py.mako
├── app
│   ├── __pycache__
│   ├── agents
│   │   ├── __pycache__
│   │   ├── __init__.py
│   │   └── state.py
│   ├── api
│   │   ├── routes
│   │   │   ├── __init__.py
│   │   │   ├── approvals.py
│   │   │   └── chat.py
│   │   └── __init__.py
│   ├── graph
│   │   ├── __pycache__
│   │   ├── __init__.py
│   │   └── workflow.py
│   ├── mcp
│   │   ├── __init__.py
│   │   └── server.py
│   ├── middleware
│   │   ├── __pycache__
│   │   ├── __init__.py
│   │   ├── logging.py
│   │   ├── rate_limit.py
│   │   └── rbac.py
│   ├── models
│   │   ├── __pycache__
│   │   └── __init__.py
│   ├── rag
│   │   └── __init__.py
│   ├── schemas
│   │   ├── __init__.py
│   │   └── chat.py
│   ├── tools
│   │   ├── __pycache__
│   │   ├── __init__.py
│   │   ├── email_tools.py
│   │   ├── finance_tools.py
│   │   ├── hr_tools.py
│   │   ├── it_tools.py
│   │   └── rag_tools.py
│   ├── __init__.py
│   ├── config.py
│   ├── database.py
│   └── main.py
├── database
│   ├── __pycache__
│   ├── chroma_db
│   ├── __init__.py
│   ├── database.py
│   └── schema.sql
├── frontend
│   ├── app
│   │   ├── approvals
│   │   │   └── page.tsx
│   │   ├── chat
│   │   │   └── page.tsx
│   │   ├── login
│   │   │   └── page.tsx
│   │   ├── favicon.ico
│   │   ├── globals.css
│   │   ├── layout.tsx
│   │   └── page.tsx
│   ├── components
│   │   ├── AppLayout.tsx
│   │   ├── ChatBubble.tsx
│   │   └── Sidebar.tsx
│   ├── lib
│   │   ├── api.ts
│   │   └── AuthContext.tsx
│   ├── AGENTS.md
│   ├── CLAUDE.md
│   ├── eslint.config.mjs
│   ├── next-env.d.ts
│   ├── next.config.ts
│   ├── package-lock.json
│   ├── package.json
│   ├── postcss.config.mjs
│   ├── README.md
│   └── tsconfig.json
├── rag_docs
│   ├── hr
│   │   └── leave_policy.txt
│   └── it
│       └── hardware_policy.txt
├── scripts
│   ├── __init__.py
│   └── ingest_docs.py
├── alembic.ini
├── get_token.py
├── pyproject.toml
├── requirements.txt
├── scratch_test.py
└── test_openai.py
```

# File Contents

## alembic\env.py

```python
import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# 1. ── IMPORT YOUR SETTINGS AND MODELS HERE ──
from app.config import settings
from database.database import Base
import app.models

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# 2. ── OVERRIDE THE DATABASE URL DYNAMICALLY ──
config.set_main_option("sqlalchemy.url", str(settings.DATABASE_URL).replace("%", "%%"))

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 3. ── SET TARGET METADATA ──
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

## alembic\README

```
Generic single-database configuration with an async dbapi.
```

## alembic\script.py.mako

```mako
"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision: str = ${repr(up_revision)}
down_revision: Union[str, Sequence[str], None] = ${repr(down_revision)}
branch_labels: Union[str, Sequence[str], None] = ${repr(branch_labels)}
depends_on: Union[str, Sequence[str], None] = ${repr(depends_on)}


def upgrade() -> None:
    """Upgrade schema."""
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    """Downgrade schema."""
    ${downgrades if downgrades else "pass"}

```

## alembic\versions\06f1ef6a9dd1_initial_schema.py

```python
"""Initial schema

Revision ID: 06f1ef6a9dd1
Revises: 
Create Date: 2026-05-05 11:54:39.247727

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '06f1ef6a9dd1'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('audit_logs_2025_01')
    op.drop_table('user_permission_overrides')
    op.drop_table('audit_logs_2024_01')
    op.drop_table('tax_declarations')
    op.alter_column('approvals', 'entity_type',
               existing_type=postgresql.ENUM('leave', 'asset_request', 'reimbursement', 'it_action', name='approval_entity'),
               type_=sa.Enum('leave', 'asset_request', 'reimbursement', 'it_action', name='approvalentity'),
               existing_nullable=False)
    op.alter_column('approvals', 'decision',
               existing_type=postgresql.ENUM('pending', 'approved', 'rejected', 'escalated', name='approval_decision'),
               type_=sa.Enum('pending', 'approved', 'rejected', 'escalated', name='approvaldecision'),
               existing_nullable=False,
               existing_server_default=sa.text("'pending'::approval_decision"))
    op.drop_index(op.f('idx_approvals_approver'), table_name='approvals')
    op.drop_index(op.f('idx_approvals_entity'), table_name='approvals')
    op.alter_column('asset_requests', 'asset_type',
               existing_type=postgresql.ENUM('laptop', 'monitor', 'keyboard', 'mouse', 'vpn_token', 'software_license', 'headset', 'docking_station', 'other', name='asset_type'),
               type_=sa.Enum('laptop', 'monitor', 'keyboard', 'mouse', 'vpn_token', 'software_license', 'headset', 'docking_station', 'other', name='assettype'),
               existing_nullable=False)
    op.alter_column('asset_requests', 'status',
               existing_type=postgresql.ENUM('pending', 'manager_approved', 'it_approved', 'rejected', 'fulfilled', 'cancelled', name='request_status'),
               type_=sa.Enum('pending', 'manager_approved', 'it_approved', 'rejected', 'fulfilled', 'cancelled', name='requeststatus'),
               existing_nullable=False,
               existing_server_default=sa.text("'pending'::request_status"))
    op.drop_constraint(op.f('asset_requests_user_id_fkey'), 'asset_requests', type_='foreignkey')
    op.create_foreign_key(None, 'asset_requests', 'users', ['user_id'], ['id'])
    op.alter_column('audit_logs', 'ip_address',
               existing_type=postgresql.INET(),
               nullable=False)
    op.drop_index(op.f('idx_audit_action'), table_name='audit_logs')
    op.drop_index(op.f('idx_audit_user'), table_name='audit_logs')
    op.drop_constraint(op.f('fk_dept_head'), 'departments', type_='foreignkey')
    op.create_foreign_key(None, 'departments', 'users', ['head_id'], ['id'], use_alter=True)
    op.drop_constraint(op.f('holiday_calendar_holiday_date_is_optional_key'), 'holiday_calendar', type_='unique')
    op.drop_column('holiday_calendar', 'year')
    op.alter_column('it_inventory', 'asset_type',
               existing_type=postgresql.ENUM('laptop', 'monitor', 'keyboard', 'mouse', 'vpn_token', 'software_license', 'headset', 'docking_station', 'other', name='asset_type'),
               type_=sa.Enum('laptop', 'monitor', 'keyboard', 'mouse', 'vpn_token', 'software_license', 'headset', 'docking_station', 'other', name='assettype'),
               existing_nullable=False)
    op.alter_column('it_inventory', 'status',
               existing_type=postgresql.ENUM('available', 'assigned', 'in_repair', 'retired', 'lost', name='asset_status'),
               type_=sa.Enum('available', 'assigned', 'in_repair', 'retired', 'lost', name='assetstatus'),
               existing_nullable=False,
               existing_server_default=sa.text("'available'::asset_status"))
    op.alter_column('it_tickets', 'category',
               existing_type=postgresql.ENUM('laptop', 'vpn', 'email', 'printer', 'network', 'software_install', 'hardware', 'access', 'other', name='ticket_category'),
               type_=sa.Enum('laptop', 'vpn', 'email', 'printer', 'network', 'software_install', 'hardware', 'access', 'other', name='ticketcategory'),
               existing_nullable=False)
    op.alter_column('it_tickets', 'priority',
               existing_type=postgresql.ENUM('low', 'medium', 'high', 'critical', name='ticket_priority'),
               type_=sa.Enum('low', 'medium', 'high', 'critical', name='ticketpriority'),
               existing_nullable=False,
               existing_server_default=sa.text("'medium'::ticket_priority"))
    op.alter_column('it_tickets', 'status',
               existing_type=postgresql.ENUM('open', 'in_progress', 'on_hold', 'resolved', 'closed', name='ticket_status'),
               type_=sa.Enum('open', 'in_progress', 'on_hold', 'resolved', 'closed', name='ticketstatus'),
               existing_nullable=False,
               existing_server_default=sa.text("'open'::ticket_status"))
    op.drop_index(op.f('idx_tickets_assignee'), table_name='it_tickets')
    op.drop_index(op.f('idx_tickets_created'), table_name='it_tickets')
    op.drop_index(op.f('idx_tickets_status'), table_name='it_tickets')
    op.drop_index(op.f('idx_tickets_user'), table_name='it_tickets')
    op.drop_constraint(op.f('it_tickets_user_id_fkey'), 'it_tickets', type_='foreignkey')
    op.create_foreign_key(None, 'it_tickets', 'users', ['user_id'], ['id'])
    op.alter_column('known_issues', 'category',
               existing_type=postgresql.ENUM('laptop', 'vpn', 'email', 'printer', 'network', 'software_install', 'hardware', 'access', 'other', name='ticket_category'),
               type_=sa.Enum('laptop', 'vpn', 'email', 'printer', 'network', 'software_install', 'hardware', 'access', 'other', name='ticketcategory'),
               existing_nullable=False)
    op.alter_column('leave_balances', 'leave_type',
               existing_type=postgresql.ENUM('casual', 'sick', 'earned', 'maternity', 'paternity', 'bereavement', 'compensatory', 'unpaid', name='leave_type'),
               type_=sa.Enum('casual', 'sick', 'earned', 'maternity', 'paternity', 'bereavement', 'compensatory', 'unpaid', name='leavetype'),
               existing_nullable=False)
    op.drop_constraint(op.f('leave_balances_user_id_fkey'), 'leave_balances', type_='foreignkey')
    op.create_foreign_key(None, 'leave_balances', 'users', ['user_id'], ['id'])
    op.add_column('leave_requests', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))
    op.alter_column('leave_requests', 'leave_type',
               existing_type=postgresql.ENUM('casual', 'sick', 'earned', 'maternity', 'paternity', 'bereavement', 'compensatory', 'unpaid', name='leave_type'),
               type_=sa.Enum('casual', 'sick', 'earned', 'maternity', 'paternity', 'bereavement', 'compensatory', 'unpaid', name='leavetype'),
               existing_nullable=False)
    op.alter_column('leave_requests', 'status',
               existing_type=postgresql.ENUM('pending', 'approved', 'rejected', 'cancelled', name='leave_status'),
               type_=sa.Enum('pending', 'approved', 'rejected', 'cancelled', name='leavestatus'),
               existing_nullable=False,
               existing_server_default=sa.text("'pending'::leave_status"))
    op.drop_index(op.f('idx_leaves_dates'), table_name='leave_requests')
    op.drop_index(op.f('idx_leaves_status'), table_name='leave_requests')
    op.drop_index(op.f('idx_leaves_user'), table_name='leave_requests')
    op.drop_constraint(op.f('leave_requests_user_id_fkey'), 'leave_requests', type_='foreignkey')
    op.create_foreign_key(None, 'leave_requests', 'users', ['user_id'], ['id'])
    op.drop_constraint(op.f('payroll_records_user_id_fkey'), 'payroll_records', type_='foreignkey')
    op.create_foreign_key(None, 'payroll_records', 'users', ['user_id'], ['id'])
    op.alter_column('rag_chunks', 'embedding',
               existing_type=pgvector.sqlalchemy.vector.VECTOR(dim=1536),
               nullable=False)
    op.drop_index(op.f('idx_rag_doc'), table_name='rag_chunks')
    op.drop_index(op.f('idx_rag_embedding'), table_name='rag_chunks', postgresql_ops={'embedding': 'vector_cosine_ops'}, postgresql_with={'m': '16', 'ef_construction': '64'}, postgresql_using='hnsw')
    op.alter_column('rag_documents', 'department',
               existing_type=postgresql.ENUM('hr', 'it', 'finance', 'general', name='doc_department'),
               type_=sa.Enum('hr', 'it', 'finance', 'general', name='docdepartment'),
               existing_nullable=False)
    op.alter_column('rag_documents', 'roles_allowed',
               existing_type=postgresql.ARRAY(postgresql.ENUM('employee', 'manager', 'hr_team', 'it_team', 'finance_team', 'admin', name='user_role')),
               type_=sa.ARRAY(sa.String()),
               existing_nullable=False,
               existing_server_default=sa.text("ARRAY['employee'::user_role]"))
    op.alter_column('reimbursements', 'category',
               existing_type=postgresql.ENUM('travel', 'internet', 'food', 'client_meeting', 'training', 'office_supplies', 'other', name='reimbursement_category'),
               type_=sa.Enum('travel', 'internet', 'food', 'client_meeting', 'training', 'office_supplies', 'other', name='reimbursementcategory'),
               existing_nullable=False)
    op.alter_column('reimbursements', 'currency',
               existing_type=sa.CHAR(length=3),
               type_=sa.String(length=3),
               existing_nullable=False,
               existing_server_default=sa.text("'INR'::bpchar"))
    op.alter_column('reimbursements', 'status',
               existing_type=postgresql.ENUM('draft', 'submitted', 'under_review', 'approved', 'rejected', 'paid', name='reimbursement_status'),
               type_=sa.Enum('draft', 'submitted', 'under_review', 'approved', 'rejected', 'paid', name='reimbursementstatus'),
               existing_nullable=False,
               existing_server_default=sa.text("'draft'::reimbursement_status"))
    op.drop_index(op.f('idx_reimb_status'), table_name='reimbursements')
    op.drop_index(op.f('idx_reimb_user'), table_name='reimbursements')
    op.drop_constraint(op.f('reimbursements_user_id_fkey'), 'reimbursements', type_='foreignkey')
    op.create_foreign_key(None, 'reimbursements', 'users', ['user_id'], ['id'])
    op.alter_column('role_permissions', 'role',
               existing_type=postgresql.ENUM('employee', 'manager', 'hr_team', 'it_team', 'finance_team', 'admin', name='user_role'),
               type_=sa.Enum('employee', 'manager', 'hr_team', 'it_team', 'finance_team', 'admin', name='userrole'),
               existing_nullable=False)
    op.alter_column('user_memory', 'source',
               existing_type=sa.VARCHAR(length=50),
               nullable=False,
               existing_server_default=sa.text("'inferred'::character varying"))
    op.alter_column('users', 'role',
               existing_type=postgresql.ENUM('employee', 'manager', 'hr_team', 'it_team', 'finance_team', 'admin', name='user_role'),
               type_=sa.Enum('employee', 'manager', 'hr_team', 'it_team', 'finance_team', 'admin', name='userrole'),
               existing_nullable=False,
               existing_server_default=sa.text("'employee'::user_role"))
    op.drop_index(op.f('idx_users_dept'), table_name='users')
    op.drop_index(op.f('idx_users_email'), table_name='users')
    op.drop_index(op.f('idx_users_manager'), table_name='users')
    op.drop_index(op.f('idx_users_role'), table_name='users')
    op.drop_constraint(op.f('users_manager_id_fkey'), 'users', type_='foreignkey')
    op.drop_constraint(op.f('users_department_id_fkey'), 'users', type_='foreignkey')
    op.create_foreign_key(None, 'users', 'departments', ['department_id'], ['id'])
    op.create_foreign_key(None, 'users', 'users', ['manager_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'users', type_='foreignkey')
    op.drop_constraint(None, 'users', type_='foreignkey')
    op.create_foreign_key(op.f('users_department_id_fkey'), 'users', 'departments', ['department_id'], ['id'], ondelete='SET NULL')
    op.create_foreign_key(op.f('users_manager_id_fkey'), 'users', 'users', ['manager_id'], ['id'], ondelete='SET NULL')
    op.create_index(op.f('idx_users_role'), 'users', ['role'], unique=False)
    op.create_index(op.f('idx_users_manager'), 'users', ['manager_id'], unique=False)
    op.create_index(op.f('idx_users_email'), 'users', ['email'], unique=False)
    op.create_index(op.f('idx_users_dept'), 'users', ['department_id'], unique=False)
    op.alter_column('users', 'role',
               existing_type=sa.Enum('employee', 'manager', 'hr_team', 'it_team', 'finance_team', 'admin', name='userrole'),
               type_=postgresql.ENUM('employee', 'manager', 'hr_team', 'it_team', 'finance_team', 'admin', name='user_role'),
               existing_nullable=False,
               existing_server_default=sa.text("'employee'::user_role"))
    op.alter_column('user_memory', 'source',
               existing_type=sa.VARCHAR(length=50),
               nullable=True,
               existing_server_default=sa.text("'inferred'::character varying"))
    op.alter_column('role_permissions', 'role',
               existing_type=sa.Enum('employee', 'manager', 'hr_team', 'it_team', 'finance_team', 'admin', name='userrole'),
               type_=postgresql.ENUM('employee', 'manager', 'hr_team', 'it_team', 'finance_team', 'admin', name='user_role'),
               existing_nullable=False)
    op.drop_constraint(None, 'reimbursements', type_='foreignkey')
    op.create_foreign_key(op.f('reimbursements_user_id_fkey'), 'reimbursements', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.create_index(op.f('idx_reimb_user'), 'reimbursements', ['user_id'], unique=False)
    op.create_index(op.f('idx_reimb_status'), 'reimbursements', ['status'], unique=False)
    op.alter_column('reimbursements', 'status',
               existing_type=sa.Enum('draft', 'submitted', 'under_review', 'approved', 'rejected', 'paid', name='reimbursementstatus'),
               type_=postgresql.ENUM('draft', 'submitted', 'under_review', 'approved', 'rejected', 'paid', name='reimbursement_status'),
               existing_nullable=False,
               existing_server_default=sa.text("'draft'::reimbursement_status"))
    op.alter_column('reimbursements', 'currency',
               existing_type=sa.String(length=3),
               type_=sa.CHAR(length=3),
               existing_nullable=False,
               existing_server_default=sa.text("'INR'::bpchar"))
    op.alter_column('reimbursements', 'category',
               existing_type=sa.Enum('travel', 'internet', 'food', 'client_meeting', 'training', 'office_supplies', 'other', name='reimbursementcategory'),
               type_=postgresql.ENUM('travel', 'internet', 'food', 'client_meeting', 'training', 'office_supplies', 'other', name='reimbursement_category'),
               existing_nullable=False)
    op.alter_column('rag_documents', 'roles_allowed',
               existing_type=sa.ARRAY(sa.String()),
               type_=postgresql.ARRAY(postgresql.ENUM('employee', 'manager', 'hr_team', 'it_team', 'finance_team', 'admin', name='user_role')),
               existing_nullable=False,
               existing_server_default=sa.text("ARRAY['employee'::user_role]"))
    op.alter_column('rag_documents', 'department',
               existing_type=sa.Enum('hr', 'it', 'finance', 'general', name='docdepartment'),
               type_=postgresql.ENUM('hr', 'it', 'finance', 'general', name='doc_department'),
               existing_nullable=False)
    op.create_index(op.f('idx_rag_embedding'), 'rag_chunks', ['embedding'], unique=False, postgresql_ops={'embedding': 'vector_cosine_ops'}, postgresql_with={'m': '16', 'ef_construction': '64'}, postgresql_using='hnsw')
    op.create_index(op.f('idx_rag_doc'), 'rag_chunks', ['document_id'], unique=False)
    op.alter_column('rag_chunks', 'embedding',
               existing_type=pgvector.sqlalchemy.vector.VECTOR(dim=1536),
               nullable=True)
    op.drop_constraint(None, 'payroll_records', type_='foreignkey')
    op.create_foreign_key(op.f('payroll_records_user_id_fkey'), 'payroll_records', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint(None, 'leave_requests', type_='foreignkey')
    op.create_foreign_key(op.f('leave_requests_user_id_fkey'), 'leave_requests', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.create_index(op.f('idx_leaves_user'), 'leave_requests', ['user_id'], unique=False)
    op.create_index(op.f('idx_leaves_status'), 'leave_requests', ['status'], unique=False)
    op.create_index(op.f('idx_leaves_dates'), 'leave_requests', ['start_date', 'end_date'], unique=False)
    op.alter_column('leave_requests', 'status',
               existing_type=sa.Enum('pending', 'approved', 'rejected', 'cancelled', name='leavestatus'),
               type_=postgresql.ENUM('pending', 'approved', 'rejected', 'cancelled', name='leave_status'),
               existing_nullable=False,
               existing_server_default=sa.text("'pending'::leave_status"))
    op.alter_column('leave_requests', 'leave_type',
               existing_type=sa.Enum('casual', 'sick', 'earned', 'maternity', 'paternity', 'bereavement', 'compensatory', 'unpaid', name='leavetype'),
               type_=postgresql.ENUM('casual', 'sick', 'earned', 'maternity', 'paternity', 'bereavement', 'compensatory', 'unpaid', name='leave_type'),
               existing_nullable=False)
    op.drop_column('leave_requests', 'created_at')
    op.drop_constraint(None, 'leave_balances', type_='foreignkey')
    op.create_foreign_key(op.f('leave_balances_user_id_fkey'), 'leave_balances', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.alter_column('leave_balances', 'leave_type',
               existing_type=sa.Enum('casual', 'sick', 'earned', 'maternity', 'paternity', 'bereavement', 'compensatory', 'unpaid', name='leavetype'),
               type_=postgresql.ENUM('casual', 'sick', 'earned', 'maternity', 'paternity', 'bereavement', 'compensatory', 'unpaid', name='leave_type'),
               existing_nullable=False)
    op.alter_column('known_issues', 'category',
               existing_type=sa.Enum('laptop', 'vpn', 'email', 'printer', 'network', 'software_install', 'hardware', 'access', 'other', name='ticketcategory'),
               type_=postgresql.ENUM('laptop', 'vpn', 'email', 'printer', 'network', 'software_install', 'hardware', 'access', 'other', name='ticket_category'),
               existing_nullable=False)
    op.drop_constraint(None, 'it_tickets', type_='foreignkey')
    op.create_foreign_key(op.f('it_tickets_user_id_fkey'), 'it_tickets', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.create_index(op.f('idx_tickets_user'), 'it_tickets', ['user_id'], unique=False)
    op.create_index(op.f('idx_tickets_status'), 'it_tickets', ['status'], unique=False)
    op.create_index(op.f('idx_tickets_created'), 'it_tickets', [sa.literal_column('created_at DESC')], unique=False)
    op.create_index(op.f('idx_tickets_assignee'), 'it_tickets', ['assigned_to'], unique=False)
    op.alter_column('it_tickets', 'status',
               existing_type=sa.Enum('open', 'in_progress', 'on_hold', 'resolved', 'closed', name='ticketstatus'),
               type_=postgresql.ENUM('open', 'in_progress', 'on_hold', 'resolved', 'closed', name='ticket_status'),
               existing_nullable=False,
               existing_server_default=sa.text("'open'::ticket_status"))
    op.alter_column('it_tickets', 'priority',
               existing_type=sa.Enum('low', 'medium', 'high', 'critical', name='ticketpriority'),
               type_=postgresql.ENUM('low', 'medium', 'high', 'critical', name='ticket_priority'),
               existing_nullable=False,
               existing_server_default=sa.text("'medium'::ticket_priority"))
    op.alter_column('it_tickets', 'category',
               existing_type=sa.Enum('laptop', 'vpn', 'email', 'printer', 'network', 'software_install', 'hardware', 'access', 'other', name='ticketcategory'),
               type_=postgresql.ENUM('laptop', 'vpn', 'email', 'printer', 'network', 'software_install', 'hardware', 'access', 'other', name='ticket_category'),
               existing_nullable=False)
    op.alter_column('it_inventory', 'status',
               existing_type=sa.Enum('available', 'assigned', 'in_repair', 'retired', 'lost', name='assetstatus'),
               type_=postgresql.ENUM('available', 'assigned', 'in_repair', 'retired', 'lost', name='asset_status'),
               existing_nullable=False,
               existing_server_default=sa.text("'available'::asset_status"))
    op.alter_column('it_inventory', 'asset_type',
               existing_type=sa.Enum('laptop', 'monitor', 'keyboard', 'mouse', 'vpn_token', 'software_license', 'headset', 'docking_station', 'other', name='assettype'),
               type_=postgresql.ENUM('laptop', 'monitor', 'keyboard', 'mouse', 'vpn_token', 'software_license', 'headset', 'docking_station', 'other', name='asset_type'),
               existing_nullable=False)
    op.add_column('holiday_calendar', sa.Column('year', sa.INTEGER(), sa.Computed('(EXTRACT(year FROM holiday_date))::integer', persisted=True), autoincrement=False, nullable=False))
    op.create_unique_constraint(op.f('holiday_calendar_holiday_date_is_optional_key'), 'holiday_calendar', ['holiday_date', 'is_optional'], postgresql_nulls_not_distinct=False)
    op.drop_constraint(None, 'departments', type_='foreignkey')
    op.create_foreign_key(op.f('fk_dept_head'), 'departments', 'users', ['head_id'], ['id'], ondelete='SET NULL')
    op.create_index(op.f('idx_audit_user'), 'audit_logs', ['user_id', sa.literal_column('created_at DESC')], unique=False)
    op.create_index(op.f('idx_audit_action'), 'audit_logs', ['action', sa.literal_column('created_at DESC')], unique=False)
    op.alter_column('audit_logs', 'ip_address',
               existing_type=postgresql.INET(),
               nullable=True)
    op.drop_constraint(None, 'asset_requests', type_='foreignkey')
    op.create_foreign_key(op.f('asset_requests_user_id_fkey'), 'asset_requests', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.alter_column('asset_requests', 'status',
               existing_type=sa.Enum('pending', 'manager_approved', 'it_approved', 'rejected', 'fulfilled', 'cancelled', name='requeststatus'),
               type_=postgresql.ENUM('pending', 'manager_approved', 'it_approved', 'rejected', 'fulfilled', 'cancelled', name='request_status'),
               existing_nullable=False,
               existing_server_default=sa.text("'pending'::request_status"))
    op.alter_column('asset_requests', 'asset_type',
               existing_type=sa.Enum('laptop', 'monitor', 'keyboard', 'mouse', 'vpn_token', 'software_license', 'headset', 'docking_station', 'other', name='assettype'),
               type_=postgresql.ENUM('laptop', 'monitor', 'keyboard', 'mouse', 'vpn_token', 'software_license', 'headset', 'docking_station', 'other', name='asset_type'),
               existing_nullable=False)
    op.create_index(op.f('idx_approvals_entity'), 'approvals', ['entity_type', 'entity_id'], unique=False)
    op.create_index(op.f('idx_approvals_approver'), 'approvals', ['approver_id', 'decision'], unique=False)
    op.alter_column('approvals', 'decision',
               existing_type=sa.Enum('pending', 'approved', 'rejected', 'escalated', name='approvaldecision'),
               type_=postgresql.ENUM('pending', 'approved', 'rejected', 'escalated', name='approval_decision'),
               existing_nullable=False,
               existing_server_default=sa.text("'pending'::approval_decision"))
    op.alter_column('approvals', 'entity_type',
               existing_type=sa.Enum('leave', 'asset_request', 'reimbursement', 'it_action', name='approvalentity'),
               type_=postgresql.ENUM('leave', 'asset_request', 'reimbursement', 'it_action', name='approval_entity'),
               existing_nullable=False)
    op.create_table('tax_declarations',
    sa.Column('id', sa.UUID(), server_default=sa.text('uuid_generate_v4()'), autoincrement=False, nullable=False),
    sa.Column('user_id', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('fiscal_year', sa.VARCHAR(length=10), autoincrement=False, nullable=False),
    sa.Column('regime', sa.VARCHAR(length=20), server_default=sa.text("'new'::character varying"), autoincrement=False, nullable=False),
    sa.Column('section_80c', sa.NUMERIC(precision=12, scale=2), server_default=sa.text('0'), autoincrement=False, nullable=False),
    sa.Column('section_80d', sa.NUMERIC(precision=12, scale=2), server_default=sa.text('0'), autoincrement=False, nullable=False),
    sa.Column('hra_claimed', sa.NUMERIC(precision=12, scale=2), server_default=sa.text('0'), autoincrement=False, nullable=False),
    sa.Column('lta_claimed', sa.NUMERIC(precision=12, scale=2), server_default=sa.text('0'), autoincrement=False, nullable=False),
    sa.Column('other_deductions', sa.NUMERIC(precision=12, scale=2), server_default=sa.text('0'), autoincrement=False, nullable=False),
    sa.Column('submitted_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
    sa.Column('is_final', sa.BOOLEAN(), server_default=sa.text('false'), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('tax_declarations_user_id_fkey'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('tax_declarations_pkey')),
    sa.UniqueConstraint('user_id', 'fiscal_year', name=op.f('tax_declarations_user_id_fiscal_year_key'), postgresql_include=[], postgresql_nulls_not_distinct=False)
    )
    op.create_table('audit_logs_2024_01',
    sa.Column('id', sa.UUID(), server_default=sa.text('uuid_generate_v4()'), autoincrement=False, nullable=False),
    sa.Column('user_id', sa.UUID(), autoincrement=False, nullable=True),
    sa.Column('session_id', sa.UUID(), autoincrement=False, nullable=True),
    sa.Column('action', sa.VARCHAR(length=200), autoincrement=False, nullable=False),
    sa.Column('entity_type', sa.VARCHAR(length=100), autoincrement=False, nullable=True),
    sa.Column('entity_id', sa.UUID(), autoincrement=False, nullable=True),
    sa.Column('agent_used', sa.VARCHAR(length=100), autoincrement=False, nullable=True),
    sa.Column('tool_used', sa.VARCHAR(length=100), autoincrement=False, nullable=True),
    sa.Column('llm_model', sa.VARCHAR(length=100), autoincrement=False, nullable=True),
    sa.Column('status', sa.VARCHAR(length=50), server_default=sa.text("'success'::character varying"), autoincrement=False, nullable=False),
    sa.Column('error_message', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('latency_ms', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('token_count', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('ip_address', postgresql.INET(), autoincrement=False, nullable=True),
    sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['session_id'], ['conversation_sessions.id'], name=op.f('audit_logs_session_id_fkey')),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('audit_logs_user_id_fkey')),
    sa.PrimaryKeyConstraint('id', 'created_at', name=op.f('audit_logs_2024_01_pkey'))
    )
    op.create_index(op.f('audit_logs_2024_01_user_id_created_at_idx'), 'audit_logs_2024_01', ['user_id', sa.literal_column('created_at DESC')], unique=False)
    op.create_index(op.f('audit_logs_2024_01_action_created_at_idx'), 'audit_logs_2024_01', ['action', sa.literal_column('created_at DESC')], unique=False)
    op.create_table('user_permission_overrides',
    sa.Column('user_id', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('perm_id', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('granted', sa.BOOLEAN(), server_default=sa.text('true'), autoincrement=False, nullable=False),
    sa.Column('reason', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('granted_by', sa.UUID(), autoincrement=False, nullable=True),
    sa.Column('expires_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['granted_by'], ['users.id'], name=op.f('user_permission_overrides_granted_by_fkey')),
    sa.ForeignKeyConstraint(['perm_id'], ['permissions.id'], name=op.f('user_permission_overrides_perm_id_fkey'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('user_permission_overrides_user_id_fkey'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('user_id', 'perm_id', name=op.f('user_permission_overrides_pkey'))
    )
    op.create_table('audit_logs_2025_01',
    sa.Column('id', sa.UUID(), server_default=sa.text('uuid_generate_v4()'), autoincrement=False, nullable=False),
    sa.Column('user_id', sa.UUID(), autoincrement=False, nullable=True),
    sa.Column('session_id', sa.UUID(), autoincrement=False, nullable=True),
    sa.Column('action', sa.VARCHAR(length=200), autoincrement=False, nullable=False),
    sa.Column('entity_type', sa.VARCHAR(length=100), autoincrement=False, nullable=True),
    sa.Column('entity_id', sa.UUID(), autoincrement=False, nullable=True),
    sa.Column('agent_used', sa.VARCHAR(length=100), autoincrement=False, nullable=True),
    sa.Column('tool_used', sa.VARCHAR(length=100), autoincrement=False, nullable=True),
    sa.Column('llm_model', sa.VARCHAR(length=100), autoincrement=False, nullable=True),
    sa.Column('status', sa.VARCHAR(length=50), server_default=sa.text("'success'::character varying"), autoincrement=False, nullable=False),
    sa.Column('error_message', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('latency_ms', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('token_count', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('ip_address', postgresql.INET(), autoincrement=False, nullable=True),
    sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['session_id'], ['conversation_sessions.id'], name=op.f('audit_logs_session_id_fkey')),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('audit_logs_user_id_fkey')),
    sa.PrimaryKeyConstraint('id', 'created_at', name=op.f('audit_logs_2025_01_pkey'))
    )
    op.create_index(op.f('audit_logs_2025_01_user_id_created_at_idx'), 'audit_logs_2025_01', ['user_id', sa.literal_column('created_at DESC')], unique=False)
    op.create_index(op.f('audit_logs_2025_01_action_created_at_idx'), 'audit_logs_2025_01', ['action', sa.literal_column('created_at DESC')], unique=False)
    # ### end Alembic commands ###

```

## app\agents\state.py

```python
"""
Agent State
===========
The single TypedDict that flows through every LangGraph node.
Every node reads from this state and returns a partial update.

Rule: never pass data between nodes via side channels (globals,
      module-level vars, etc.) — everything goes through AgentState.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Annotated, Any, Literal, TypedDict, Dict, Optional

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

from app.models import UserRole


# ── Intent categories ─────────────────────────────────────────────────────────

Intent = Literal[
    # HR
    "hr.policy_query",
    "hr.leave_apply",
    "hr.leave_check_balance",
    "hr.leave_view_history",
    "hr.leave_cancel",
    "hr.leave_check_status",
    # IT
    "it.ticket_create",
    "it.ticket_status",
    "it.asset_request",
    "it.ticket_view",
    # Finance
    "finance.payslip_fetch",
    "finance.reimbursement_submit",
    "finance.reimbursement_status",
    "finance.tax_query",
    # Meta
    "general.greeting",
    "general.unknown",
]

RouteTo = Literal["hr_agent", "it_agent", "finance_agent", "rag_agent", "unknown"]


# ── GEPA: planning and evaluation ─────────────────────────────────────────────

class ActionPlan(TypedDict):
    """Written by the Plan node before tool execution."""
    steps: list[str]           # ["1. Check leave balance", "2. Validate dates", ...]
    tools_needed: list[str]    # ["get_leave_balance", "check_overlaps"]
    reasoning: str             # why these steps


class EvalScore(TypedDict):
    """Written by the Evaluate node after response generation."""
    score: float               # 0.0 – 1.0
    relevance: float
    completeness: float
    rbac_compliant: bool
    critique: str              # natural language feedback for retry


# ── Main state ────────────────────────────────────────────────────────────────

class AgentState(TypedDict, total=False):
    """
    Flows through the entire LangGraph workflow.
    Nodes return a dict with only the keys they modify.
    """

    # ── Identity & auth ────────────────────────────────────────
    user_id:       str
    user_email:    str
    user_name:     str
    user_role:     UserRole
    department_id: str | None
    manager_id:    str | None
    preferred_lang: str

    # ── Conversation ────────────────────────────────────────────
    session_id:    str
    messages:      list[BaseMessage]   # full LangChain message history
    raw_query:     str                 # original user text (unchanged)

    # ── Routing ─────────────────────────────────────────────────
    intent:        Intent
    intent_confidence: float           # 0.0–1.0
    route_to:      RouteTo

    # ── GEPA: Plan → Execute → Evaluate ────────────────────────
    plan:          ActionPlan
    eval_score:    EvalScore
    retry_count:   int                 # incremented on each GEPA retry
    retry_critique: str                # critique passed back to Plan node

    # ── Tool execution ──────────────────────────────────────────
    tool_calls:    list[dict]          # [{name, args, result}]
    tool_error:    str | None

    # ── RAG ─────────────────────────────────────────────────────
    rag_docs:      list[dict]          # [{content, source, score}]
    rag_confidence: float              # avg cosine similarity of retrieved chunks
    web_search_triggered: bool

    # ── Human-in-loop (approval) ────────────────────────────────
    approval_required: bool
    approval_entity_type: str | None   # 'leave' | 'asset_request' | 'reimbursement'
    approval_entity_id:  str | None
    approval_decision:   str | None    # 'approved' | 'rejected'
    approval_note:       str | None

    # ── Email ────────────────────────────────────────────────────
    email_triggered:  bool
    email_recipients: list[str]
    email_subject:    str | None
    email_body:       str | None

    # ── Final response ──────────────────────────────────────────
    response:      str                 # final message shown to user
    response_type: Literal["text", "form", "table", "error"]
    metadata:      dict[str, Any]      # additional data for frontend (e.g., leave_id)

    # ── Observability ────────────────────────────────────────────
    agent_used:    str | None
    llm_model:     str | None
    latency_ms:    int | None
    error:         str | None


def initial_state(user_ctx: dict, query: str, session_id: str | None = None) -> AgentState:
    """
    Create a fresh AgentState from the enriched user context dict
    (returned by app.middleware.rbac.enrich_request).
    """
    return AgentState(
        user_id=user_ctx["user_id"],
        user_email=user_ctx["user_email"],
        user_name=user_ctx["user_name"],
        user_role=user_ctx["user_role"],
        department_id=user_ctx.get("department_id"),
        manager_id=user_ctx.get("manager_id"),
        preferred_lang=user_ctx.get("preferred_lang", "en"),
        session_id=session_id or str(uuid.uuid4()),
        messages=[],
        raw_query=query,
        intent="general.unknown",
        intent_confidence=0.0,
        route_to="unknown",
        retry_count=0,
        tool_calls=[],
        rag_docs=[],
        rag_confidence=0.0,
        web_search_triggered=False,
        approval_required=False,
        email_triggered=False,
        email_recipients=[],
        response="",
        response_type="text",
        metadata={},
    )
```

## app\agents\__init__.py

```python
from .state import AgentState, EvalScore, Intent, RouteTo, initial_state

__all__ = [
    "AgentState",
    "EvalScore",
    "Intent",
    "RouteTo",
    "initial_state",
]


```

## app\api\routes\approvals.py

```python
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any

from app.schemas.chat import ChatRequest, ChatResponse
from app.graph.workflow import run_workflow
# Assuming you have a dependency that extracts the user from a JWT/API token
# from app.middleware.rbac import get_current_user_ctx

router = APIRouter(prefix="/api/chat", tags=["Chat"])

# --- MOCK DEPENDENCY (Replace with your actual auth middleware) ---
async def get_current_user_ctx() -> Dict[str, Any]:
    """Mocks the user context that would normally come from a decoded JWT."""
    from app.models import UserRole
    return {
        "user_id": "user-uuid-1234",
        "user_email": "alice@company.com",
        "user_name": "Alice Smith",
        "user_role": UserRole.employee, # Change this to test manager/admin flows
        "department_id": "dept-uuid-hr",
    }
# ------------------------------------------------------------------

@router.post("/", response_model=ChatResponse)
async def chat_with_agent(
    request: ChatRequest, 
    user_ctx: Dict[str, Any] = Depends(get_current_user_ctx)
):
    """
    Send a message to the enterprise assistant. 
    Routes automatically to HR, IT, Finance, or RAG based on intent.
    """
    try:
        # 1. Invoke the LangGraph workflow
        final_state = await run_workflow(
            user_ctx=user_ctx, 
            query=request.query, 
            session_id=request.session_id
        )

        # 2. Return the structured response
        return ChatResponse(
            session_id=final_state.get("session_id"),
            response=final_state.get("response", "I'm sorry, I couldn't process that request."),
            intent=final_state.get("intent", "unknown"),
            approval_required=final_state.get("approval_required", False),
            metadata=final_state.get("metadata", {})
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## app\api\routes\chat.py

```python
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any

from app.schemas.chat import ChatRequest, ChatResponse
from app.graph.workflow import run_workflow
# Assuming you have a dependency that extracts the user from a JWT/API token
# from app.middleware.rbac import get_current_user_ctx

router = APIRouter(prefix="/api/chat", tags=["Chat"])

# --- MOCK DEPENDENCY (Replace with your actual auth middleware) ---
async def get_current_user_ctx() -> Dict[str, Any]:
    """Mocks the user context that would normally come from a decoded JWT."""
    from app.models import UserRole
    return {
        "user_id": "user-uuid-1234",
        "user_email": "alice@company.com",
        "user_name": "Alice Smith",
        "user_role": UserRole.employee, # Change this to test manager/admin flows
        "department_id": "dept-uuid-hr",
    }
# ------------------------------------------------------------------

@router.post("/", response_model=ChatResponse)
async def chat_with_agent(
    request: ChatRequest, 
    user_ctx: Dict[str, Any] = Depends(get_current_user_ctx)
):
    """
    Send a message to the enterprise assistant. 
    Routes automatically to HR, IT, Finance, or RAG based on intent.
    """
    try:
        # 1. Invoke the LangGraph workflow
        final_state = await run_workflow(
            user_ctx=user_ctx, 
            query=request.query, 
            session_id=request.session_id
        )

        # 2. Return the structured response
        return ChatResponse(
            session_id=final_state.get("session_id"),
            response=final_state.get("response", "I'm sorry, I couldn't process that request."),
            intent=final_state.get("intent", "unknown"),
            approval_required=final_state.get("approval_required", False),
            metadata=final_state.get("metadata", {})
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## app\api\routes\__init__.py

```python
# app/api/routes/__init__.py

```

## app\api\__init__.py

```python
# app/api/__init__.py

```

## app\config.py

```python
import os
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn, field_validator


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",          # silently skip unknown env vars (e.g. LANGSMITH_*)
    )

    # ── App ─────────────────────────────────────────────────
    APP_NAME: str = "Employee Assistant"
    APP_ENV: str = "development"             # development | staging | production
    DEBUG: bool = False
    SECRET_KEY: str                          # used for JWT signing
    ALLOWED_ORIGINS: list[str] = []

    # ── Database ─────────────────────────────────────────────
    DATABASE_URL: PostgresDsn               # postgresql+asyncpg://user:pass@host/db
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_ECHO: bool = False                   # set True to log all SQL

    # ── Redis (short-term memory / rate limiting) ─────────────
    REDIS_URL: str = "redis://localhost:6379/0"
    SESSION_TTL_SECONDS: int = 3600         # 1 hour idle timeout

    # ── LLM Providers ────────────────────────────────────────
    OPENAI_API_KEY: str = ""                 # optional — only if using OpenAI models
    ANTHROPIC_API_KEY: str = ""
    XAI_API_KEY: str = ""                    # Grok (xAI)
    GOOGLE_API_KEY: str = ""                 # Gemini
    OPENAI_BASE_URL: str | None = None
    OPENAI_VERIFY_SSL: bool = True

    # Dynamic routing: which model for which task
    
    # --- Gemini Models (Commented out) ---
    # LLM_INTENT: str = "gemini-2.5-flash"    # fast, cheap intent classification
    # LLM_HR: str = "gemini-2.5-pro"          # balanced for HR conversations
    # LLM_IT: str = "gemini-2.5-flash"        # fast for IT support
    # LLM_FINANCE: str = "gemini-2.5-pro"     # strong reasoning for calculations
    # LLM_EVALUATOR: str = "gemini-2.5-flash" # GEPA self-evaluation node
    
    # --- OpenAI Models (Active) ---
    LLM_INTENT: str = "gpt-4o-mini"
    LLM_HR: str = "gpt-4o"
    LLM_IT: str = "gpt-4o-mini"
    LLM_FINANCE: str = "gpt-4o"
    LLM_EVALUATOR: str = "gpt-4o-mini"
    
    LLM_TEMPERATURE: float = 0.1            # low temp for enterprise accuracy

    # ── LangSmith (tracing) ──────────────────────────────────
    LANGCHAIN_TRACING_V2: bool = True
    LANGCHAIN_API_KEY: str = ""
    LANGSMITH_PROJECT: str = "EmployeeAssistant"  # matches LANGSMITH_PROJECT in .env

    # ── Vector DB / RAG ──────────────────────────────────────
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    EMBEDDING_DIM: int = 1536
    RAG_TOP_K: int = 5
    RAG_SCORE_THRESHOLD: float = 0.75       # below this → trigger web search fallback
    CHUNK_SIZE: int = 512
    CHUNK_OVERLAP: int = 50

    # ── FastMCP ──────────────────────────────────────────────
    MCP_HOST: str = "0.0.0.0"
    MCP_PORT: int = 8001

    # ── Email (Power Automate trigger) ───────────────────────
    POWER_AUTOMATE_WEBHOOK_URL: str = ""

    # ── JWT ──────────────────────────────────────────────────
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 8-hour work day

    # ── Rate Limiting ─────────────────────────────────────────
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 60

    # ── GEPA (self-evaluation) ───────────────────────────────
    GEPA_EVAL_THRESHOLD: float = 0.80       # retry if quality score < this
    GEPA_MAX_RETRIES: int = 2

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def fix_asyncpg_driver(cls, v: str) -> str:
        """Ensure asyncpg driver is used."""
        if v.startswith("postgresql://"):
            return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

# Inject LangSmith settings directly into OS environment for LangChain under-the-hood tracking
if settings.LANGCHAIN_TRACING_V2 and settings.LANGCHAIN_API_KEY:
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_API_KEY"] = settings.LANGCHAIN_API_KEY
    os.environ["LANGCHAIN_PROJECT"] = settings.LANGSMITH_PROJECT
```

## app\database.py

```python
"""
app/database.py — Canonical re-export shim
==========================================
All application code imports the database layer from here:

    from app.database import AsyncSessionLocal, get_db, check_db_connection

The actual engine, session factory and Base live in `database/database.py`
(the top-level `database` package) so that Alembic env.py can import Base
without dragging in the full `app` package.

Why a shim and not a direct import everywhere?
  - Keeps all app-internal imports under the `app.*` namespace — consistent
    and IDE-friendly.
  - The underlying `database/database.py` module can evolve (e.g., switch
    to a different async driver) without touching every file in `app/`.
  - Mirrors the standard Django / SQLAlchemy project layout where a single
    `db.py` / `database.py` is the one place everything is imported from.
"""
from database.database import (  # noqa: F401  (re-exports)
    AsyncSessionLocal,
    Base,
    check_db_connection,
    engine,
    get_db,
)

__all__ = [
    "AsyncSessionLocal",
    "Base",
    "check_db_connection",
    "engine",
    "get_db",
]

```

## app\graph\workflow.py

```python
"""
LangGraph Workflow — with GEPA pattern
======================================
"""
from __future__ import annotations

import json
import time
import uuid
from typing import Literal

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.language_models import BaseChatModel
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph
from langgraph.types import interrupt

from app.agents import AgentState, EvalScore, initial_state
from app.config import settings
from app.middleware import RBACViolation, rbac_guard
from app.models import UserRole


# ── LLM instances (multi-provider: Grok, Gemini, OpenAI) ─────────────────────

def get_llm(model_key: str, temperature: float = settings.LLM_TEMPERATURE) -> BaseChatModel:
    """Create a pure Gemini LLM client based on the requested model key."""
    model_name = getattr(settings, f"LLM_{model_key.upper()}", settings.LLM_HR)

    # Keep SSL fallback logic available in case we need to pass custom clients in the future
    kwargs = {}
    verify_ssl = getattr(settings, "OPENAI_VERIFY_SSL", True)
    if not verify_ssl:
        import httpx
        kwargs["http_client"] = httpx.Client(verify=False)
        kwargs["http_async_client"] = httpx.AsyncClient(verify=False)

    # --- Gemini Setup (Commented out) ---
    # from langchain_google_genai import ChatGoogleGenerativeAI
    # return ChatGoogleGenerativeAI(
    #     model=model_name,
    #     temperature=temperature,
    #     google_api_key=settings.GOOGLE_API_KEY,
    #     transport="rest"
    # )

    # --- OpenAI Setup (Active) ---
    from langchain_openai import ChatOpenAI
    return ChatOpenAI(
        model=model_name,
        temperature=temperature,
        api_key=settings.OPENAI_API_KEY,
        **kwargs
    )


# ── Node 1: Intent detection ──────────────────────────────────────────────────

INTENT_SYSTEM = """You are an intent classifier for an enterprise HR/IT/Finance AI copilot.
Classify the user query into exactly ONE intent code. Respond ONLY with valid JSON.

Intent codes:
HR: hr.policy_query, hr.leave_apply, hr.leave_check_balance, hr.leave_view_history,
    hr.leave_cancel, hr.leave_check_status
IT: it.ticket_create, it.ticket_status, it.asset_request, it.ticket_view
Finance: finance.payslip_fetch, finance.reimbursement_submit, finance.reimbursement_status,
         finance.tax_query
Meta: general.greeting, general.unknown

Response format: {"intent": "<code>", "confidence": <0.0-1.0>}"""


async def intent_node(state: AgentState) -> AgentState:
    llm = get_llm("intent")
    result = await llm.ainvoke([
        SystemMessage(content=INTENT_SYSTEM),
        HumanMessage(content=state["raw_query"]),
    ])
    try:
        parsed = json.loads(result.content)
        return {
            "intent": parsed["intent"],
            "intent_confidence": parsed["confidence"],
            "llm_model": settings.LLM_INTENT,
        }
    except Exception:
        return {"intent": "general.unknown", "intent_confidence": 0.0}


# ── Node 2: Role / RBAC gate ──────────────────────────────────────────────────

INTENT_PERM_MAP: dict[str, str] = {
    "hr.policy_query":           "hr:policy:read",
    "hr.leave_apply":            "hr:leave:apply",
    "hr.leave_check_balance":    "hr:leave:view_own",
    "hr.leave_view_history":     "hr:leave:view_own",
    "hr.leave_cancel":           "hr:leave:apply",
    "hr.leave_check_status":     "hr:leave:view_own",
    "it.ticket_create":          "it:ticket:create",
    "it.ticket_status":          "it:ticket:view_own",
    "it.ticket_view":            "it:ticket:view_own",
    "it.asset_request":          "it:asset:request",
    "finance.payslip_fetch":     "finance:payslip:view_own",
    "finance.reimbursement_submit": "finance:claim:submit",
    "finance.reimbursement_status": "finance:claim:view_own",
    "finance.tax_query":         "finance:tax:view_own",
}

INTENT_ROUTE_MAP: dict[str, str] = {
    "hr":      "hr_agent",
    "it":      "it_agent",
    "finance": "finance_agent",
    "general": "plan_node", 
}


async def role_check_node(state: AgentState) -> AgentState:
    intent = state["intent"]
    required_perm = INTENT_PERM_MAP.get(intent)
    if required_perm:
        try:
            rbac_guard(state["user_role"], required_perm)
        except RBACViolation as e:
            return {
                "error": str(e),
                "response": "You don't have permission to perform this action.",
                "response_type": "error",
                "route_to": "respond", 
            }
            
    # Derive routing from intent prefix. Fallback to plan_node if completely unknown.
    prefix = intent.split(".")[0]
    return {"route_to": INTENT_ROUTE_MAP.get(prefix, "plan_node")}


def route_after_role_check(state: AgentState) -> str:
    if state.get("error"):
        return "respond"
        
    route = state.get("route_to", "plan_node")
    if route not in ["hr_agent", "it_agent", "finance_agent", "plan_node", "respond"]:
        return "plan_node"
        
    return route


# ── Nodes 3a/3b/3c: Department context nodes ──────────────────────────────────

async def hr_agent_node(state: AgentState) -> AgentState:
    return {
        "agent_used": "hr_agent",
        "llm_model": settings.LLM_HR,
        "metadata": {**state.get("metadata", {}), "department": "hr"},
    }


async def it_agent_node(state: AgentState) -> AgentState:
    return {
        "agent_used": "it_agent",
        "llm_model": settings.LLM_IT,
        "metadata": {**state.get("metadata", {}), "department": "it"},
    }


async def finance_agent_node(state: AgentState) -> AgentState:
    return {
        "agent_used": "finance_agent",
        "llm_model": settings.LLM_FINANCE,
        "metadata": {**state.get("metadata", {}), "department": "finance"},
    }


# ── Node 4: GEPA — Plan ───────────────────────────────────────────────────────

PLAN_SYSTEM = """You are a planning agent for an enterprise AI system. Given a user request,
write a structured resolution plan BEFORE calling any tools.

Respond ONLY with JSON:
{
  "steps": ["step 1...", "step 2...", ...],
  "tools_needed": ["tool_name_1", "tool_name_2"],
  "reasoning": "why these steps in this order"
}

If a previous attempt failed, a critique will be provided. Adjust the plan accordingly."""


async def plan_node(state: AgentState) -> AgentState:
    llm = get_llm(state.get("agent_used", "hr").split("_")[0])

    messages = [SystemMessage(content=PLAN_SYSTEM)]

    # Include critique on retry
    if state.get("retry_critique"):
        messages.append(HumanMessage(
            content=f"Previous attempt failed. Critique:\n{state['retry_critique']}\n\n"
                    f"Original request: {state['raw_query']}"
        ))
    else:
        messages.append(HumanMessage(content=state["raw_query"]))

    result = await llm.ainvoke(messages)
    try:
        plan = json.loads(result.content)
        return {"plan": plan}
    except Exception:
        return {
            "plan": {
                "steps": ["Retrieve relevant information", "Generate response"],
                "tools_needed": [],
                "reasoning": "Fallback plan",
            }
        }


# ── Node 5: Execute (tools + RAG) ─────────────────────────────────────────────

EXECUTE_SYSTEM = """You are an enterprise AI assistant. Follow the plan and call the
appropriate tools to answer the user's request accurately. If the user is just greeting you, respond politely.

User context:
- Name: {user_name}
- Role: {user_role}
- Department ID: {department_id}

Current plan:
{plan}

Be factual, cite sources when using documents, and respect the user's role permissions."""


async def execute_node(state: AgentState) -> AgentState:
    from app.tools import get_tools_for_intent

    llm = get_llm(state.get("agent_used", "hr").split("_")[0])
    tools = get_tools_for_intent(state["intent"], state["user_role"])
    llm_with_tools = llm.bind_tools(tools) if tools else llm

    plan_text = "\n".join(
        f"{i+1}. {s}" for i, s in enumerate(state.get("plan", {}).get("steps", []))
    )

    messages = [
        SystemMessage(content=EXECUTE_SYSTEM.format(
            user_name=state["user_name"],
            user_role=state["user_role"].value,
            department_id=state.get("department_id", "N/A"),
            plan=plan_text,
        )),
        *state.get("messages", []),
        HumanMessage(content=state["raw_query"]),
    ]

    start = time.time()
    result = await llm_with_tools.ainvoke(messages)
    latency = int((time.time() - start) * 1000)

    tool_calls = []
    
    approval_required = False
    approval_entity_type = None
    approval_entity_id = None
    email_triggered = False
    email_recipients = []
    email_subject = None
    email_body = None

    if hasattr(result, "tool_calls") and result.tool_calls:
        for tc in result.tool_calls:
            tool_fn = next((t for t in tools if t.name == tc["name"]), None)
            if tool_fn:
                try:
                    tool_result = await tool_fn.ainvoke(tc["args"])
                    tool_calls.append({"name": tc["name"], "args": tc["args"], "result": tool_result})
                    
                    if isinstance(tool_result, dict):
                        if tool_result.get("approval_required"):
                            approval_required = True
                            if "leave_id" in tool_result:
                                approval_entity_type = "leave"
                                approval_entity_id = str(tool_result["leave_id"])
                            elif "ticket_id" in tool_result:
                                approval_entity_type = "it_action"
                                approval_entity_id = str(tool_result["ticket_id"])
                            elif "request_id" in tool_result:
                                approval_entity_type = "asset_request"
                                approval_entity_id = str(tool_result["request_id"])
                            elif "claim_id" in tool_result:
                                approval_entity_type = "reimbursement"
                                approval_entity_id = str(tool_result["claim_id"])
                                
                        if tool_result.get("email_triggered"):
                            email_triggered = True
                            email_recipients = tool_result.get("email_recipients", [])
                            email_subject = tool_result.get("email_subject")
                            email_body = tool_result.get("email_body")

                except RBACViolation as e:
                    return {"error": str(e), "response": str(e), "response_type": "error"}

    state_update = {
        "messages": [*state.get("messages", []), HumanMessage(content=state["raw_query"]), result],
        "tool_calls": tool_calls,
        "response": result.content if isinstance(result.content, str) else str(result.content),
        "latency_ms": latency,
    }

    if approval_required:
        state_update["approval_required"] = True
        state_update["approval_entity_type"] = approval_entity_type
        state_update["approval_entity_id"] = approval_entity_id
        
    if email_triggered:
        state_update["email_triggered"] = True
        state_update["email_recipients"] = email_recipients
        state_update["email_subject"] = email_subject
        state_update["email_body"] = email_body

    return state_update


# ── Node 6: GEPA — Evaluate ───────────────────────────────────────────────────

EVAL_SYSTEM = """You are a quality evaluator for an enterprise AI system.
Score the agent's response on four dimensions (0.0–1.0 each):
  - relevance: does the response directly address the user's query?
  - completeness: does it provide all needed information?
  - rbac_compliant: does it respect the user's role and not expose unauthorized data?
  - overall: weighted average

Respond ONLY with JSON:
{
  "score": <float>,
  "relevance": <float>,
  "completeness": <float>,
  "rbac_compliant": <bool>,
  "critique": "specific feedback if score < 0.80, empty string otherwise"
}"""


async def eval_node(state: AgentState) -> AgentState:
    if state.get("error"):
        return {"eval_score": {"score": 0.0, "relevance": 0.0, "completeness": 0.0,
                               "rbac_compliant": True, "critique": ""}}

    llm = get_llm("evaluator")
    result = await llm.ainvoke([
        SystemMessage(content=EVAL_SYSTEM),
        HumanMessage(content=f"Query: {state['raw_query']}\n\nResponse: {state['response']}\n\n"
                              f"User role: {state['user_role'].value}"),
    ])
    try:
        score_data: EvalScore = json.loads(result.content)
        return {"eval_score": score_data}
    except Exception:
        return {"eval_score": {"score": 1.0, "relevance": 1.0, "completeness": 1.0,
                               "rbac_compliant": True, "critique": ""}}


def route_after_eval(state: AgentState) -> Literal["plan_node", "human_in_loop"]:
    score = state.get("eval_score", {}).get("score", 1.0)
    retry_count = state.get("retry_count", 0)

    if score < settings.GEPA_EVAL_THRESHOLD and retry_count < settings.GEPA_MAX_RETRIES:
        return "plan_node"
    return "human_in_loop"


# ── Node 7: Human-in-loop ─────────────────────────────────────────────────────

async def human_in_loop_node(state: AgentState) -> AgentState:
    if not state.get("approval_required"):
        return {}

    decision_input = interrupt({
        "message": f"Approval required for {state.get('approval_entity_type')}",
        "entity_id": state.get("approval_entity_id"),
        "requested_by": state["user_name"],
        "request_summary": state["raw_query"],
    })

    return {
        "approval_decision": decision_input.get("decision"),
        "approval_note": decision_input.get("note"),
    }


# ── Node 8: Email notification ────────────────────────────────────────────────

async def email_notify_node(state: AgentState) -> AgentState:
    if not state.get("email_triggered"):
        return {}

    from app.tools.email_tools import send_email_via_power_automate
    await send_email_via_power_automate(
        recipients=state["email_recipients"],
        subject=state.get("email_subject", ""),
        body=state.get("email_body", ""),
    )
    return {}


# ── Node 9: Save memory ───────────────────────────────────────────────────────

async def save_memory_node(state: AgentState) -> AgentState:
    from app.database import AsyncSessionLocal
    from app.models import UserMemory
    from sqlalchemy.dialects.postgresql import insert

    async with AsyncSessionLocal() as db:
        stmt = insert(UserMemory).values(
            user_id=state["user_id"],
            memory_key="last_agent_used",
            memory_value={"agent": state.get("agent_used"), "intent": state["intent"]},
            source="inferred",
        ).on_conflict_do_update(
            index_elements=["user_id", "memory_key"],
            set_={"memory_value": {"agent": state.get("agent_used"), "intent": state["intent"]},
                  "updated_at": "now()"},
        )
        await db.execute(stmt)
        await db.commit()
    return {}


# ── Node 10: Final respond ────────────────────────────────────────────────────

async def respond_node(state: AgentState) -> AgentState:
    if state.get("response"):
        return {
            "messages": [
                *state.get("messages", []),
                AIMessage(content=state["response"]),
            ]
        }
    return {}


# ── Build the graph ───────────────────────────────────────────────────────────

def build_workflow() -> StateGraph:
    graph = StateGraph(AgentState)

    graph.add_node("intent_node",       intent_node)
    graph.add_node("role_check",        role_check_node)
    graph.add_node("hr_agent",          hr_agent_node)
    graph.add_node("it_agent",          it_agent_node)
    graph.add_node("finance_agent",     finance_agent_node)
    graph.add_node("plan_node",         plan_node)
    graph.add_node("execute_node",      execute_node)
    graph.add_node("eval_node",         eval_node)
    graph.add_node("human_in_loop",     human_in_loop_node)
    graph.add_node("email_notify",      email_notify_node)
    graph.add_node("save_memory",       save_memory_node)
    graph.add_node("respond",           respond_node)

    graph.set_entry_point("intent_node")

    graph.add_edge("intent_node", "role_check")
    
    graph.add_conditional_edges("role_check", route_after_role_check, {
        "hr_agent":      "hr_agent",
        "it_agent":      "it_agent",
        "finance_agent": "finance_agent",
        "plan_node":     "plan_node",
        "respond":       "respond",
    })

    for dept in ("hr_agent", "it_agent", "finance_agent"):
        graph.add_edge(dept, "plan_node")

    graph.add_edge("plan_node",    "execute_node")
    graph.add_edge("execute_node", "eval_node")

    graph.add_conditional_edges("eval_node", route_after_eval, {
        "plan_node":     "plan_node",
        "human_in_loop": "human_in_loop",
    })

    graph.add_edge("human_in_loop", "email_notify")
    graph.add_edge("email_notify",  "save_memory")
    graph.add_edge("save_memory",   "respond")
    graph.add_edge("respond",       END)

    checkpointer = MemorySaver()
    return graph.compile(checkpointer=checkpointer, interrupt_before=["human_in_loop"])


workflow = build_workflow()


async def run_workflow(user_ctx: dict, query: str, session_id: str | None = None) -> AgentState:
    sid = session_id or str(uuid.uuid4())
    state = initial_state(user_ctx, query, session_id=sid)

    config = {"configurable": {"thread_id": sid}}
    final_state = await workflow.ainvoke(state, config=config)
    return final_state
```

## app\graph\__init__.py

```python
# app/graph/__init__.py

```

## app\main.py

```python
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import structlog

# Import your graph and database components
from app.config import settings
from app.database import AsyncSessionLocal, check_db_connection
from app.graph.workflow import run_workflow, workflow
from app.middleware import (
    RequestLoggingMiddleware, 
    RateLimitMiddleware, 
    setup_redis, 
    close_redis, 
    enrich_request, 
    load_role_permissions
)

# Set up structured logging
logger = structlog.get_logger("app.lifecycle")

# ── Lifespan (startup / shutdown) ─────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles startup and shutdown events for the FastAPI application."""
    # Startup: Load RBAC permissions (fail-open for local dev)
    try:
        async with AsyncSessionLocal() as db:
            await load_role_permissions(db)
        logger.info("rbac_loaded")
    except Exception as e:
        logger.warning("rbac_load_skipped", error=str(e), hint="RBAC permissions not loaded — admin role bypasses all checks")

    # Redis: optional for local dev (rate limiter will fail-open)
    try:
        await setup_redis()
        logger.info("redis_connected")
    except Exception as e:
        logger.warning("redis_skipped", error=str(e), hint="Rate limiting disabled — Redis not available")

    logger.info("startup_complete", app=settings.APP_NAME, env=settings.APP_ENV)
        
    yield  # The app is running
    
    # Shutdown
    try:
        await close_redis()
    except Exception:
        pass
    logger.info("shutdown_initiated", app=settings.APP_NAME)


# ── App Initialization ────────────────────────────────────────────────────────

app = FastAPI(
    title=settings.APP_NAME,
    description="LangGraph-powered AI backend for HR, IT, and Finance.",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url=None,
    lifespan=lifespan,
)

# ── Middlewares ───────────────────────────────────────────────────────────────

# CORS Middleware for frontend communication
# Normalize origins: handle both AnyHttpUrl objects and plain strings
_origins = []
for o in settings.ALLOWED_ORIGINS:
    origin_str = str(o).rstrip("/")
    _origins.append(origin_str)

# Always allow localhost:3000 in development
if settings.DEBUG:
    for dev_origin in ["http://localhost:3000", "http://127.0.0.1:3000"]:
        if dev_origin not in _origins:
            _origins.append(dev_origin)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate Limiting via Redis Token Bucket
app.add_middleware(RateLimitMiddleware)

# Structured request logging
app.add_middleware(RequestLoggingMiddleware)


# ── Schemas ───────────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    intent: str
    agent_used: str | None
    approval_required: bool
    metadata: dict

class ApprovalCallback(BaseModel):
    session_id: str
    decision: str
    note: str = ""


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/health", tags=["System"])
async def health():
    """System health check endpoint."""
    try:
        db_ok = await check_db_connection()
    except Exception:
        db_ok = False
    return {
        "status": "ok" if db_ok else "degraded",
        "db": db_ok,
        "app": settings.APP_NAME,
        "env": settings.APP_ENV,
        "debug": settings.DEBUG,
    }


@app.post("/api/v1/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(
    body: ChatRequest,
    user_ctx: dict = Depends(enrich_request),
):
    """Main conversational endpoint."""
    try:
        final_state = await run_workflow(
            user_ctx=user_ctx,
            query=body.message,
            session_id=body.session_id,
        )

        return ChatResponse(
            response=final_state.get("response", "I'm sorry, I couldn't process that request."),
            session_id=final_state["session_id"],
            intent=final_state.get("intent", "general.unknown"),
            agent_used=final_state.get("agent_used"),
            approval_required=final_state.get("approval_required", False),
            metadata=final_state.get("metadata", {}),
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        logger.error("chat_endpoint_error", error=str(e), session_id=body.session_id)
        raise HTTPException(status_code=500, detail="An error occurred while processing your request.")


@app.post("/api/v1/approve", tags=["Approvals"])
async def handle_approval(
    body: ApprovalCallback,
    user_ctx: dict = Depends(enrich_request),
):
    """Resumes a paused LangGraph workflow after a manager makes an approval decision."""
    from langgraph.types import Command
    from app.models import UserRole
    
    if user_ctx.get("user_role") not in [UserRole.manager, UserRole.admin]:
        raise HTTPException(status_code=403, detail="Only managers or admins can perform approvals.")

    try:
        config = {"configurable": {"thread_id": body.session_id}}
        
        await workflow.ainvoke(
            Command(resume={"decision": body.decision, "note": body.note}),
            config=config,
        )
        return {"status": "ok", "decision": body.decision, "session_id": body.session_id}
        
    except Exception as e:
        logger.error("approval_endpoint_error", error=str(e), session_id=body.session_id)
        raise HTTPException(status_code=500, detail="Failed to resume workflow after approval.")
```

## app\mcp\server.py

```python
"""
FastMCP Server
==============
Exposes all enterprise tools as MCP-compatible endpoints.
LangGraph agents call these tools through the MCP protocol.

Run standalone:  python -m app.mcp.server
Or mount on FastAPI: app.mount("/mcp", mcp_app)
"""
from __future__ import annotations

from datetime import date
from typing import Annotated

from fastmcp import FastMCP
from pydantic import BaseModel, Field

from app.config import settings

mcp = FastMCP(
    name="Enterprise AI Copilot Tools",
    version="1.0.0",
    instructions="Tools for HR, IT, and Finance operations. Always validate RBAC before calling.",
)


# ── Input schemas (Pydantic — FastMCP uses these for validation) ──────────────

class LeaveApplyInput(BaseModel):
    user_id:     str
    leave_type:  str   = Field(..., description="casual|sick|earned|maternity|paternity|bereavement")
    start_date:  date
    end_date:    date
    reason:      str   = ""
    is_half_day: bool  = False
    half_day_slot: str = Field("", description="morning|afternoon — only if is_half_day=True")


class LeaveBalanceInput(BaseModel):
    user_id: str
    year:    int = Field(default_factory=lambda: date.today().year)


class TicketCreateInput(BaseModel):
    user_id:     str
    category:    str   = Field(..., description="laptop|vpn|email|printer|network|software_install|hardware|access|other")
    subject:     str
    description: str
    priority:    str   = "medium"


class AssetRequestInput(BaseModel):
    user_id:       str
    asset_type:    str = Field(..., description="laptop|monitor|keyboard|mouse|vpn_token|software_license")
    justification: str


class PayslipFetchInput(BaseModel):
    user_id:   str
    pay_month: str = Field(..., description="YYYY-MM (e.g. 2024-03)")


class ReimbursementSubmitInput(BaseModel):
    user_id:      str
    category:     str   = Field(..., description="travel|internet|food|client_meeting|training")
    amount:       float
    currency:     str   = "INR"
    description:  str
    expense_date: date
    receipt_url:  str   = ""


class ApprovalInput(BaseModel):
    approval_id: str
    decision:    str  = Field(..., description="approved|rejected")
    note:        str  = ""


# ── HR Tools ──────────────────────────────────────────────────────────────────

@mcp.tool(description="Apply for leave. Validates dates, checks overlaps and holiday calendar.")
async def apply_leave(data: LeaveApplyInput) -> dict:
    from app.database import AsyncSessionLocal
    from app.models import HolidayCalendar, LeaveBalance, LeaveRequest, LeaveType, User
    from app.tools.email_tools import leave_request_email
    from sqlalchemy import and_, select
    from datetime import timedelta

    async with AsyncSessionLocal() as db:
        # ── NEW: Fetch User & Manager for Email Routing ──
        user = await db.get(User, data.user_id)
        if not user:
            return {"success": False, "error": "User not found."}
        
        manager = await db.get(User, user.manager_id) if user.manager_id else None

        # 1. Validate leave type
        try:
            ltype = LeaveType(data.leave_type)
        except ValueError:
            return {"success": False, "error": f"Invalid leave type: {data.leave_type}"}

        # 2. Check date validity
        if data.start_date < date.today():
            return {"success": False, "error": "Cannot apply leave for past dates."}
        if data.end_date < data.start_date:
            return {"success": False, "error": "end_date must be ≥ start_date."}

        # 3. Check overlapping leaves
        overlap = await db.scalar(
            select(LeaveRequest).where(
                and_(
                    LeaveRequest.user_id == data.user_id,
                    LeaveRequest.status.in_(["pending", "approved"]),
                    LeaveRequest.start_date <= data.end_date,
                    LeaveRequest.end_date   >= data.start_date,
                )
            )
        )
        if overlap:
            return {"success": False, "error": f"Overlapping leave exists ({overlap.id})."}

        # 4. Count business days (exclude weekends + holidays)
        holidays = set(
            row.holiday_date for row in (
                await db.execute(
                    select(HolidayCalendar.holiday_date).where(
                        HolidayCalendar.holiday_date.between(data.start_date, data.end_date)
                    )
                )
            ).scalars()
        )
        bdays = 0
        cur = data.start_date
        while cur <= data.end_date:
            if cur.weekday() < 5 and cur not in holidays:  # Mon–Fri, non-holiday
                bdays += 1
            cur += timedelta(days=1)
        if data.is_half_day:
            bdays = 0.5

        # 5. Check leave balance
        balance = await db.scalar(
            select(LeaveBalance).where(
                and_(
                    LeaveBalance.user_id == data.user_id,
                    LeaveBalance.year == data.start_date.year,
                    LeaveBalance.leave_type == ltype,
                )
            )
        )
        if not balance or balance.available_days < bdays:
            return {"success": False, "error": f"Insufficient {ltype.value} leave balance."}

        # 6. Create leave request
        leave = LeaveRequest(
            user_id=data.user_id,
            leave_type=ltype,
            start_date=data.start_date,
            end_date=data.end_date,
            business_days=bdays,
            reason=data.reason,
            is_half_day=data.is_half_day,
            half_day_slot=data.half_day_slot or None,
        )
        db.add(leave)
        balance.pending_days += bdays
        await db.commit()
        await db.refresh(leave)

    # ── NEW: Generate Email Payload ──
    email_data = {}
    if manager:
        # Generate an approval URL (in reality, this would point to your frontend UI)
        approve_url = f"https://copilot.internal/approve?leave_id={leave.id}"
        email_data = leave_request_email(
            employee_name=user.full_name,
            manager_email=manager.email,
            leave_type=ltype.value,
            start=str(data.start_date),
            end=str(data.end_date),
            days=float(bdays),
            leave_id=str(leave.id),
            approve_url=approve_url
        )

    return {
        "success": True,
        "leave_id": str(leave.id),
        "business_days": bdays,
        "status": "pending",
        "message": f"Leave applied successfully ({bdays} day(s)). Pending manager approval.",
        "approval_required": True,
        "email_triggered": bool(manager),
        "email_recipients": email_data.get("recipients", []),
        "email_subject": email_data.get("subject", ""),
        "email_body": email_data.get("body", ""),
    }


@mcp.tool(description="Get leave balance for a user for the current or specified year.")
async def get_leave_balance(data: LeaveBalanceInput) -> dict:
    from app.database import AsyncSessionLocal
    from app.models import LeaveBalance
    from sqlalchemy import select

    async with AsyncSessionLocal() as db:
        rows = (await db.execute(
            select(LeaveBalance).where(
                LeaveBalance.user_id == data.user_id,
                LeaveBalance.year == data.year,
            )
        )).scalars().all()

    return {
        "user_id": data.user_id,
        "year": data.year,
        "balances": [
            {
                "type": row.leave_type.value,
                "entitled": float(row.entitled_days),
                "used": float(row.used_days),
                "pending": float(row.pending_days),
                "available": float(row.available_days),
            }
            for row in rows
        ],
    }


# ── IT Tools ──────────────────────────────────────────────────────────────────

@mcp.tool(description="Create an IT support ticket. Checks for duplicates and known issues first.")
async def create_ticket(data: TicketCreateInput) -> dict:
    from app.database import AsyncSessionLocal
    from app.models import ITTicket, KnownIssue, MaintenanceSchedule, TicketCategory, TicketPriority
    from sqlalchemy import and_, select
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc)

    async with AsyncSessionLocal() as db:
        # 1. Check active maintenance
        maint = await db.scalar(
            select(MaintenanceSchedule).where(
                and_(
                    MaintenanceSchedule.starts_at <= now,
                    MaintenanceSchedule.ends_at   >= now,
                    MaintenanceSchedule.affected_system.ilike(f"%{data.category}%"),
                )
            )
        )
        if maint:
            return {
                "success": False,
                "info": f"Planned maintenance in progress: '{maint.title}'. Expected end: {maint.ends_at.isoformat()}",
                "ticket_created": False,
            }

        # 2. Check known issues
        known = await db.scalar(
            select(KnownIssue).where(
                and_(
                    KnownIssue.category == data.category,
                    KnownIssue.is_active.is_(True),
                )
            )
        )
        if known:
            return {
                "success": True,
                "info": f"Known issue: {known.title}. Workaround: {known.workaround or 'None available'}",
                "ticket_created": False,
                "message": "A known issue matches your request. No ticket raised; see workaround above.",
            }

        # 3. Check duplicate open ticket
        dupe = await db.scalar(
            select(ITTicket).where(
                and_(
                    ITTicket.user_id == data.user_id,
                    ITTicket.category == data.category,
                    ITTicket.status.in_(["open", "in_progress"]),
                )
            )
        )
        if dupe:
            return {
                "success": True,
                "info": f"You already have an open ticket ({dupe.ticket_no}) for '{data.category}'.",
                "ticket_id": str(dupe.id),
                "ticket_no": dupe.ticket_no,
                "ticket_created": False,
            }

        # 4. Create ticket
        ticket = ITTicket(
            user_id=data.user_id,
            category=TicketCategory(data.category),
            subject=data.subject,
            description=data.description,
            priority=TicketPriority(data.priority),
        )
        db.add(ticket)
        await db.commit()
        await db.refresh(ticket)

    return {
        "success": True,
        "ticket_id": str(ticket.id),
        "ticket_no": ticket.ticket_no,
        "priority": ticket.priority.value,
        "status": "open",
        "ticket_created": True,
        "message": f"Ticket {ticket.ticket_no} created. You'll receive email confirmation shortly.",
    }


@mcp.tool(description="Check inventory and submit an asset request (laptop, monitor, etc).")
async def request_asset(data: AssetRequestInput) -> dict:
    from app.database import AsyncSessionLocal
    from app.models import AssetRequest, AssetType, ITInventory
    from sqlalchemy import and_, select

    async with AsyncSessionLocal() as db:
        # Check availability
        available = await db.scalar(
            select(ITInventory).where(
                and_(
                    ITInventory.asset_type == data.asset_type,
                    ITInventory.status == "available",
                )
            )
        )

        req = AssetRequest(
            user_id=data.user_id,
            asset_type=AssetType(data.asset_type),
            justification=data.justification,
        )
        db.add(req)
        await db.commit()
        await db.refresh(req)

    return {
        "success": True,
        "request_id": str(req.id),
        "asset_type": data.asset_type,
        "inventory_available": available is not None,
        "status": "pending",
        "approval_required": True,
        "message": "Asset request submitted. Manager approval required.",
    }


# ── Finance Tools ─────────────────────────────────────────────────────────────

@mcp.tool(description="Fetch payslip details for a specific month (YYYY-MM).")
async def fetch_payslip(data: PayslipFetchInput) -> dict:
    from app.database import AsyncSessionLocal
    from app.models import PayrollRecord
    from sqlalchemy import select
    from datetime import date as dt

    year, month = map(int, data.pay_month.split("-"))
    pay_month_date = dt(year, month, 1)

    async with AsyncSessionLocal() as db:
        record = await db.scalar(
            select(PayrollRecord).where(
                PayrollRecord.user_id == data.user_id,
                PayrollRecord.pay_month == pay_month_date,
            )
        )

    if not record:
        return {"success": False, "error": f"No payslip found for {data.pay_month}."}

    return {
        "success": True,
        "pay_month": data.pay_month,
        "gross_salary": float(record.gross_salary),
        "net_salary": float(record.net_salary),
        "breakdown": {
            "basic": float(record.basic),
            "hra": float(record.hra),
            "allowances": float(record.allowances),
        },
        "deductions": {
            "pf_employee": float(record.pf_employee),
            "tds": float(record.tds),
            "professional_tax": float(record.professional_tax),
            "other": float(record.other_deductions),
        },
        "payslip_url": record.payslip_url,
    }


@mcp.tool(description="Submit a reimbursement claim with expense details and receipt URL.")
async def submit_reimbursement(data: ReimbursementSubmitInput) -> dict:
    from app.database import AsyncSessionLocal
    from app.models import Reimbursement, ReimbursementCategory
    from datetime import datetime, timezone

    async with AsyncSessionLocal() as db:
        claim = Reimbursement(
            user_id=data.user_id,
            category=ReimbursementCategory(data.category),
            amount=data.amount,
            currency=data.currency,
            description=data.description,
            expense_date=data.expense_date,
            receipt_url=data.receipt_url or None,
            status="submitted",
            submitted_at=datetime.now(timezone.utc),
        )
        db.add(claim)
        await db.commit()
        await db.refresh(claim)

    return {
        "success": True,
        "claim_id": str(claim.id),
        "claim_no": claim.claim_no,
        "amount": float(claim.amount),
        "currency": claim.currency,
        "status": "submitted",
        "approval_required": True,
        "message": f"Claim {claim.claim_no} submitted for ₹{claim.amount:.2f}. Finance team will review.",
    }


# ── Approval Tool (cross-department) ──────────────────────────────────────────

@mcp.tool(description="Record an approval decision for a leave, asset request, or reimbursement.")
async def record_approval(data: ApprovalInput) -> dict:
    from app.database import AsyncSessionLocal
    from app.models import Approval, ApprovalDecision
    from sqlalchemy import select
    from datetime import datetime, timezone

    async with AsyncSessionLocal() as db:
        approval = await db.get(Approval, data.approval_id)
        if not approval:
            return {"success": False, "error": "Approval record not found."}
        if approval.decision != ApprovalDecision.pending:
            return {"success": False, "error": f"Already decided: {approval.decision.value}"}

        approval.decision = ApprovalDecision(data.decision)
        approval.note = data.note
        approval.decided_at = datetime.now(timezone.utc)
        await db.commit()

    return {
        "success": True,
        "approval_id": data.approval_id,
        "decision": data.decision,
        "message": f"Approval {data.decision} recorded.",
    }


# ── Inventory status (IT team only) ───────────────────────────────────────────

@mcp.tool(description="View current IT inventory status and available assets. IT team only.")
async def inventory_status(asset_type: str = "") -> dict:
    from app.database import AsyncSessionLocal
    from app.models import ITInventory
    from sqlalchemy import select, func

    async with AsyncSessionLocal() as db:
        q = select(
            ITInventory.asset_type,
            ITInventory.status,
            func.count().label("count"),
        ).group_by(ITInventory.asset_type, ITInventory.status)

        if asset_type:
            q = q.where(ITInventory.asset_type == asset_type)

        rows = (await db.execute(q)).all()

    summary: dict = {}
    for row in rows:
        atype = row.asset_type.value
        summary.setdefault(atype, {})[row.status.value] = row.count

    return {"inventory": summary}


# ── Run MCP server standalone ─────────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run(host=settings.MCP_HOST, port=settings.MCP_PORT, transport="sse")
```

## app\mcp\__init__.py

```python
# app/mcp/__init__.py

```

## app\middleware\logging.py

```python
"""
Structured Request Logging Middleware
=====================================
Intercepts every HTTP request and emits a structured JSON log line with:
  - method, path, status_code, duration_ms
  - request_id (correlation ID for distributed tracing)
  - client IP

**Why structlog?**
  Standard Python `logging` emits flat strings.  structlog produces key-value
  JSON that is trivially parseable by log aggregation tools (Datadog, Loki,
  CloudWatch, ELK).  In production, structured logs let you filter dashboards
  by `status_code >= 500` or alert on `p99(duration_ms) > 800` without regex.

**Why BaseHTTPMiddleware?**
  It wraps the ASGI lifecycle at a high level, giving us access to the
  full `Request` *and* `Response` objects.  This is the simplest way to
  measure latency across all routes (including ones we don't own, like /docs).

Usage:
    # In app/main.py, *after* CORSMiddleware:
    from app.middleware.logging import RequestLoggingMiddleware
    app.add_middleware(RequestLoggingMiddleware)
"""
from __future__ import annotations

import time
import uuid

import structlog
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

# ── Configure structlog (once at module load) ─────────────────────────────────
# This pipeline turns every log event into a JSON dict with ISO-8601 timestamps.

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,          # pull vars set in other coroutines
        structlog.processors.TimeStamper(fmt="iso"),      # "timestamp": "2026-05-05T12:00:00Z"
        structlog.processors.add_log_level,               # "level": "info"
        structlog.processors.StackInfoRenderer(),         # add stack trace if requested
        structlog.processors.format_exc_info,             # format exceptions nicely
        structlog.processors.UnicodeDecoder(),            # bytes → str
        structlog.processors.JSONRenderer(),              # final output as JSON
    ],
    wrapper_class=structlog.make_filtering_bound_logger(0),  # allow all levels
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),           # writes to stdout
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger("request")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Measures wall-clock latency of every request and emits a single
    structured log line after the response is sent.

    Key design decisions:
      1. We generate a `request_id` (UUID4) and attach it as a response
         header (`X-Request-ID`).  Downstream services can propagate this
         for distributed tracing.
      2. We catch *all* unhandled exceptions so that 500s are still logged
         with the traceback attached — then we re-raise so FastAPI's
         default exception handler can return a proper error response.
      3. Health-check endpoints (/health) are logged at DEBUG to avoid
         flooding logs in environments with aggressive liveness probes.
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # ── 1. Generate correlation ID ────────────────────────────────────
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

        # ── 2. Start the clock ────────────────────────────────────────────
        start_time = time.perf_counter()

        # Bind request-scoped fields into structlog context so that any log
        # emitted inside the endpoint handler also carries them.
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            client_ip=request.client.host if request.client else "unknown",
        )

        status_code = 500  # default in case call_next explodes
        try:
            response = await call_next(request)
            status_code = response.status_code

            # Attach correlation header to response
            response.headers["X-Request-ID"] = request_id
            return response

        except Exception as exc:
            # ── 3. Log the 500 with full traceback ────────────────────────
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            logger.error(
                "unhandled_exception",
                status_code=500,
                duration_ms=duration_ms,
                exc_info=exc,
            )
            raise  # re-raise so FastAPI returns its standard 500 response

        finally:
            # ── 4. Emit the structured log line ───────────────────────────
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

            # Downgrade health-check spam to DEBUG
            log_method = logger.debug if request.url.path == "/health" else logger.info
            log_method(
                "request_completed",
                status_code=status_code,
                duration_ms=duration_ms,
            )

```

## app\middleware\rate_limit.py

```python
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import redis.asyncio as redis

from app.config import settings

# Global Redis Client
redis_client: redis.Redis | None = None

async def setup_redis():
    """Initialize Redis connection pool and verify connectivity."""
    global redis_client
    redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    # Eagerly verify connectivity so startup logs a clear warning if Redis is down
    await redis_client.ping()

async def close_redis():
    """Close Redis connection."""
    global redis_client
    if redis_client:
        await redis_client.aclose()

# Atomic Token Bucket Lua Script for Redis
TOKEN_BUCKET_LUA = """
local key = KEYS[1]
local rate = tonumber(ARGV[1])      -- tokens added per minute
local capacity = tonumber(ARGV[2])  -- max bucket size
local now = tonumber(ARGV[3])       -- current timestamp

local info = redis.call('HMGET', key, 'tokens', 'last_refresh')
local tokens = tonumber(info[1])
local last_refresh = tonumber(info[2])

-- Initialize if it's a new key
if tokens == nil then
    tokens = capacity
    last_refresh = now
end

-- Calculate token refill based on time passed
local time_passed = math.max(0, now - last_refresh)
tokens = math.min(capacity, tokens + time_passed * (rate / 60))

-- Check if we have enough tokens (1 request = 1 token)
if tokens >= 1 then
    tokens = tokens - 1
    redis.call('HMSET', key, 'tokens', tokens, 'last_refresh', now)
    redis.call('EXPIRE', key, 120) -- Keep alive for 2 mins
    return 1 -- Allowed
else
    redis.call('HMSET', key, 'tokens', tokens, 'last_refresh', now)
    redis.call('EXPIRE', key, 120)
    return 0 -- Rate limited
end
"""

class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if not redis_client:
            # Fail-open if Redis is down
            return await call_next(request)

        # Identify user by IP (or extract from Authorization token if needed)
        client_id = request.client.host if request.client else "unknown"
        bucket_key = f"rate_limit:{client_id}"
        
        try:
            # Execute the Lua script
            is_allowed = await redis_client.eval(
                TOKEN_BUCKET_LUA, 
                1, # Number of keys
                bucket_key, 
                settings.RATE_LIMIT_REQUESTS_PER_MINUTE, # Rate
                settings.RATE_LIMIT_REQUESTS_PER_MINUTE, # Capacity
                time.time() # Now
            )
            
            if not is_allowed:
                return JSONResponse(
                    status_code=429,
                    content={"error": "Too Many Requests. Rate limit exceeded."},
                    headers={"Retry-After": "60"}
                )
                
        except Exception:
            # If Redis errors out, log it but don't block the user (fail-open)
            pass

        return await call_next(request)
```

## app\middleware\rbac.py

```python
"""
RBAC Middleware
==============
Two-layer enforcement:
  Layer 1 — FastAPI dependency (HTTP): validates JWT and injects current_user
  Layer 2 — Agent-level guard (LangGraph): checked inside tool/retrieval nodes

Usage in FastAPI routes:
    @router.get("/leaves")
    async def list_leaves(user = Depends(require_permission("hr:leave:view_all"))):
        ...

Usage in LangGraph tool nodes:
    from app.middleware.rbac import rbac_guard
    rbac_guard(state["user_role"], "it:ticket:view_all")
"""
from __future__ import annotations

import time
from datetime import UTC, datetime, timedelta
from functools import lru_cache
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models import Permission, RolePermission, User, UserRole

# ── Static role → permission map (cached at startup) ─────────────────────────
# Loaded from DB once via load_role_permissions(); used for fast in-memory checks.
ROLE_PERMISSIONS: dict[UserRole, set[str]] = {}


async def load_role_permissions(db: AsyncSession) -> None:
    """Call once at FastAPI startup to cache all role permissions."""
    result = await db.execute(
        select(RolePermission.role, Permission.code)
        .join(Permission, RolePermission.perm_id == Permission.id)
    )
    for role, code in result:
        ROLE_PERMISSIONS.setdefault(role, set()).add(code)


# ── JWT helpers ───────────────────────────────────────────────────────────────

def create_access_token(user_id: str, role: str, email: str) -> str:
    expire = datetime.now(UTC) + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": user_id,
        "role": role,
        "email": email,
        "exp": expire,
        "iat": datetime.now(UTC),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


# ── FastAPI dependencies ───────────────────────────────────────────────────────

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    db: AsyncSession = Depends(get_db),
) -> User:
    """Decode JWT, load user from DB, verify active status. Supports X-Mock-Role in DEBUG mode."""
    # 1. Check for mock header in DEBUG mode
    if settings.DEBUG and "x-mock-role" in request.headers:
        role_str = request.headers.get("x-mock-role", "employee")
        try:
            role_enum = UserRole(role_str)
        except ValueError:
            role_enum = UserRole.employee
            
        import uuid
        from sqlalchemy.orm import make_transient

        mock_user = User(
            id=uuid.UUID("11111111-1111-1111-1111-111111111111") if role_enum == UserRole.manager else uuid.UUID("22222222-2222-2222-2222-222222222222"),
            employee_id=f"MOCK-{role_enum.value.upper()[:3]}-001",
            email=f"mock_{role_enum.value}@company.com",
            full_name=f"Mock {role_enum.value.capitalize()}",
            password_hash="mock_not_a_real_hash",
            role=role_enum,
            department_id=None,
            manager_id=None,
            is_active=True,
            preferred_lang="en"
        )
        # Detach from any SA session so it's never accidentally flushed to DB
        make_transient(mock_user)
        return mock_user

    # 2. Normal JWT flow
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
        
    payload = decode_access_token(credentials.credentials)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Bad token payload")

    user = await db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")
    return user


def require_permission(perm_code: str):
    """FastAPI dependency factory — raises 403 if user lacks the permission."""
    async def _check(user: User = Depends(get_current_user)) -> User:
        if not _has_permission(user.role, perm_code):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: '{perm_code}' required",
            )
        return user
    return _check


def require_role(*roles: UserRole):
    """FastAPI dependency — requires one of the given roles."""
    async def _check(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role required: one of {[r.value for r in roles]}",
            )
        return user
    return _check


# ── Agent-level guard (LangGraph nodes / tools) ───────────────────────────────

class RBACViolation(PermissionError):
    """Raised inside LangGraph tool nodes when RBAC check fails."""
    def __init__(self, role: UserRole, perm_code: str):
        super().__init__(f"Role '{role.value}' lacks permission '{perm_code}'")
        self.role = role
        self.perm_code = perm_code


def rbac_guard(role: UserRole, perm_code: str) -> None:
    """
    Raise RBACViolation if the role lacks the permission.
    Use this inside LangGraph tool nodes (not FastAPI routes).

    Example:
        async def apply_leave_tool(state: AgentState) -> AgentState:
            rbac_guard(state["user_role"], "hr:leave:apply")
            ...
    """
    if not _has_permission(role, perm_code):
        raise RBACViolation(role, perm_code)


def _has_permission(role: UserRole, perm_code: str) -> bool:
    """Check against in-memory ROLE_PERMISSIONS map. Admin always passes."""
    if role == UserRole.admin:
        return True
    return perm_code in ROLE_PERMISSIONS.get(role, set())


# ── Rate limiting middleware ───────────────────────────────────────────────────

class RateLimitMiddleware:
    """
    Simple in-process token bucket per user (not cluster-safe).
    For production, replace with Redis-backed sliding window.
    """

    def __init__(self, requests_per_minute: int = 60):
        self.rpm = requests_per_minute
        self._buckets: dict[str, tuple[int, float]] = {}  # user_id → (tokens, last_refill)

    def check(self, user_id: str) -> None:
        now = time.time()
        tokens, last_refill = self._buckets.get(user_id, (self.rpm, now))

        # Refill tokens proportional to elapsed time
        elapsed = now - last_refill
        tokens = min(self.rpm, tokens + elapsed * (self.rpm / 60))

        if tokens < 1:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please slow down.",
                headers={"Retry-After": "5"},
            )

        self._buckets[user_id] = (tokens - 1, now)


rate_limiter = RateLimitMiddleware(settings.RATE_LIMIT_REQUESTS_PER_MINUTE)


# ── Request enrichment (adds user context to every request) ──────────────────

async def enrich_request(request: Request, user: User = Depends(get_current_user)) -> dict:
    """
    Returns enriched context dict injected into the agent state.
    Attach via Depends() on chat endpoints.
    """
    rate_limiter.check(str(user.id))
    return {
        "user_id": str(user.id),
        "user_email": user.email,
        "user_name": user.full_name,
        "user_role": user.role,
        "department_id": str(user.department_id) if user.department_id else None,
        "manager_id": str(user.manager_id) if user.manager_id else None,
        "preferred_lang": user.preferred_lang,
    }
```

## app\middleware\__init__.py

```python
from .logging import RequestLoggingMiddleware
from .rate_limit import RateLimitMiddleware, setup_redis, close_redis
from .rbac import (
    RBACViolation,
    enrich_request,
    load_role_permissions,
    rbac_guard,
    require_permission,
    require_role,
)

__all__ = [
    "RequestLoggingMiddleware",
    "RateLimitMiddleware",
    "setup_redis",
    "close_redis",
    "RBACViolation",
    "enrich_request",
    "load_role_permissions",
    "rbac_guard",
    "require_permission",
    "require_role",
]
```

## app\models\__init__.py

```python
"""
SQLAlchemy ORM models — mirrors schema.sql exactly.
Import everything from here: `from app.models import User, LeaveRequest, ...`
"""
from __future__ import annotations

import enum
import uuid
from datetime import date, datetime
from typing import Any

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    ARRAY, Boolean, CheckConstraint, Column, Date, DateTime,
    Enum, ForeignKey, Index, Integer, Numeric, String, Text,
    UniqueConstraint, func,
)
from sqlalchemy.dialects.postgresql import INET, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


# ── Enums (match PostgreSQL enums in schema.sql) ──────────────────────────────

class UserRole(str, enum.Enum):
    employee     = "employee"
    manager      = "manager"
    hr_team      = "hr_team"
    it_team      = "it_team"
    finance_team = "finance_team"
    admin        = "admin"

class LeaveStatus(str, enum.Enum):
    pending   = "pending"
    approved  = "approved"
    rejected  = "rejected"
    cancelled = "cancelled"

class LeaveType(str, enum.Enum):
    casual        = "casual"
    sick          = "sick"
    earned        = "earned"
    maternity     = "maternity"
    paternity     = "paternity"
    bereavement   = "bereavement"
    compensatory  = "compensatory"
    unpaid        = "unpaid"

class TicketStatus(str, enum.Enum):
    open        = "open"
    in_progress = "in_progress"
    on_hold     = "on_hold"
    resolved    = "resolved"
    closed      = "closed"

class TicketPriority(str, enum.Enum):
    low      = "low"
    medium   = "medium"
    high     = "high"
    critical = "critical"

class TicketCategory(str, enum.Enum):
    laptop           = "laptop"
    vpn              = "vpn"
    email            = "email"
    printer          = "printer"
    network          = "network"
    software_install = "software_install"
    hardware         = "hardware"
    access           = "access"
    other            = "other"

class AssetStatus(str, enum.Enum):
    available = "available"
    assigned  = "assigned"
    in_repair = "in_repair"
    retired   = "retired"
    lost      = "lost"

class AssetType(str, enum.Enum):
    laptop           = "laptop"
    monitor          = "monitor"
    keyboard         = "keyboard"
    mouse            = "mouse"
    vpn_token        = "vpn_token"
    software_license = "software_license"
    headset          = "headset"
    docking_station  = "docking_station"
    other            = "other"

class RequestStatus(str, enum.Enum):
    pending          = "pending"
    manager_approved = "manager_approved"
    it_approved      = "it_approved"
    rejected         = "rejected"
    fulfilled        = "fulfilled"
    cancelled        = "cancelled"

class ReimbursementCategory(str, enum.Enum):
    travel          = "travel"
    internet        = "internet"
    food            = "food"
    client_meeting  = "client_meeting"
    training        = "training"
    office_supplies = "office_supplies"
    other           = "other"

class ReimbursementStatus(str, enum.Enum):
    draft        = "draft"
    submitted    = "submitted"
    under_review = "under_review"
    approved     = "approved"
    rejected     = "rejected"
    paid         = "paid"

class ApprovalEntity(str, enum.Enum):
    leave           = "leave"
    asset_request   = "asset_request"
    reimbursement   = "reimbursement"
    it_action       = "it_action"

class ApprovalDecision(str, enum.Enum):
    pending   = "pending"
    approved  = "approved"
    rejected  = "rejected"
    escalated = "escalated"

class DocDepartment(str, enum.Enum):
    hr      = "hr"
    it      = "it"
    finance = "finance"
    general = "general"


# ── Mixins ────────────────────────────────────────────────────────────────────

class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(),
        onupdate=func.now(), nullable=False
    )


# ── Core models ───────────────────────────────────────────────────────────────

class Department(TimestampMixin, Base):
    __tablename__ = "departments"

    id:        Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name:      Mapped[str]       = mapped_column(String(100), unique=True, nullable=False)
    code:      Mapped[str]       = mapped_column(String(20), unique=True, nullable=False)
    head_id:   Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", use_alter=True))
    is_active: Mapped[bool]      = mapped_column(Boolean, default=True, nullable=False)

    users: Mapped[list["User"]] = relationship("User", back_populates="department",
                                               foreign_keys="User.department_id")


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id:            Mapped[uuid.UUID]  = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id:   Mapped[str]        = mapped_column(String(20), unique=True, nullable=False)
    email:         Mapped[str]        = mapped_column(String(255), unique=True, nullable=False)
    full_name:     Mapped[str]        = mapped_column(String(200), nullable=False)
    password_hash: Mapped[str]        = mapped_column(Text, nullable=False)
    role:          Mapped[UserRole]   = mapped_column(Enum(UserRole, name="user_role"), default=UserRole.employee, nullable=False)
    department_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("departments.id"))
    manager_id:    Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    designation:   Mapped[str | None] = mapped_column(String(150))
    date_of_joining: Mapped[date | None] = mapped_column(Date)
    is_active:     Mapped[bool]       = mapped_column(Boolean, default=True, nullable=False)
    preferred_lang: Mapped[str]       = mapped_column(String(10), default="en", nullable=False)

    # Relationships
    department: Mapped["Department | None"] = relationship(
        "Department", back_populates="users", foreign_keys=[department_id]
    )
    manager:    Mapped["User | None"]       = relationship("User", remote_side="User.id",
                                                           foreign_keys=[manager_id])
    leave_requests:  Mapped[list["LeaveRequest"]]  = relationship(back_populates="user", foreign_keys="LeaveRequest.user_id")
    tickets:         Mapped[list["ITTicket"]]       = relationship(back_populates="user",
                                                                   foreign_keys="ITTicket.user_id")
    asset_requests:  Mapped[list["AssetRequest"]]  = relationship(back_populates="user", foreign_keys="AssetRequest.user_id")
    reimbursements:  Mapped[list["Reimbursement"]] = relationship(back_populates="user", foreign_keys="Reimbursement.user_id")
    memory_entries:  Mapped[list["UserMemory"]]    = relationship(back_populates="user")

    def has_permission(self, perm_code: str) -> bool:
        """Quick check — call after loading role_permissions into session context."""
        from app.middleware.rbac import ROLE_PERMISSIONS
        return perm_code in ROLE_PERMISSIONS.get(self.role, set())


class Permission(Base):
    __tablename__ = "permissions"

    id:          Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code:        Mapped[str]       = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    module:      Mapped[str]       = mapped_column(String(50), nullable=False)


class RolePermission(Base):
    __tablename__ = "role_permissions"

    role:    Mapped[UserRole]  = mapped_column(Enum(UserRole, name="user_role"), primary_key=True)
    perm_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),
                                               ForeignKey("permissions.id", ondelete="CASCADE"),
                                               primary_key=True)


# ── HR Module ─────────────────────────────────────────────────────────────────

class LeaveBalance(Base):
    __tablename__ = "leave_balances"
    __table_args__ = (UniqueConstraint("user_id", "year", "leave_type"),)

    id:            Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id:       Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    year:          Mapped[int]
    leave_type:    Mapped[LeaveType] = mapped_column(Enum(LeaveType, name="leave_type"), nullable=False)
    entitled_days: Mapped[float]     = mapped_column(Numeric(5, 1), default=0)
    used_days:     Mapped[float]     = mapped_column(Numeric(5, 1), default=0)
    pending_days:  Mapped[float]     = mapped_column(Numeric(5, 1), default=0)
    carried_over:  Mapped[float]     = mapped_column(Numeric(5, 1), default=0)
    updated_at:    Mapped[datetime]  = mapped_column(DateTime(timezone=True), server_default=func.now())

    @property
    def available_days(self) -> float:
        return self.entitled_days + self.carried_over - self.used_days - self.pending_days


class LeaveRequest(TimestampMixin, Base):
    __tablename__ = "leave_requests"
    __table_args__ = (
        CheckConstraint("end_date >= start_date", name="valid_dates"),
        CheckConstraint("business_days > 0", name="valid_business_days"),
    )

    id:            Mapped[uuid.UUID]    = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id:       Mapped[uuid.UUID]    = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    leave_type:    Mapped[LeaveType]    = mapped_column(Enum(LeaveType, name="leave_type"), nullable=False)
    start_date:    Mapped[date]         = mapped_column(Date, nullable=False)
    end_date:      Mapped[date]         = mapped_column(Date, nullable=False)
    business_days: Mapped[float]        = mapped_column(Numeric(4, 1), nullable=False)
    reason:        Mapped[str | None]   = mapped_column(Text)
    status:        Mapped[LeaveStatus]  = mapped_column(Enum(LeaveStatus, name="leave_status"), default=LeaveStatus.pending)
    applied_at:    Mapped[datetime]     = mapped_column(DateTime(timezone=True), server_default=func.now())
    reviewed_by:   Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    reviewed_at:   Mapped[datetime | None]  = mapped_column(DateTime(timezone=True))
    reviewer_note: Mapped[str | None]   = mapped_column(Text)
    is_half_day:   Mapped[bool]         = mapped_column(Boolean, default=False)
    half_day_slot: Mapped[str | None]   = mapped_column(String(10))

    user: Mapped["User"] = relationship(back_populates="leave_requests", foreign_keys=[user_id])


class HolidayCalendar(Base):
    __tablename__ = "holiday_calendar"

    id:           Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    holiday_date: Mapped[date]      = mapped_column(Date, nullable=False)
    name:         Mapped[str]       = mapped_column(String(200), nullable=False)
    is_optional:  Mapped[bool]      = mapped_column(Boolean, default=False)


# ── IT Module ─────────────────────────────────────────────────────────────────

class ITTicket(TimestampMixin, Base):
    __tablename__ = "it_tickets"

    id:             Mapped[uuid.UUID]      = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticket_no:      Mapped[str]            = mapped_column(String(20), unique=True, nullable=False)
    user_id:        Mapped[uuid.UUID]      = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    category:       Mapped[TicketCategory] = mapped_column(Enum(TicketCategory, name="ticket_category"), nullable=False)
    subject:        Mapped[str]            = mapped_column(String(500), nullable=False)
    description:    Mapped[str]            = mapped_column(Text, nullable=False)
    priority:       Mapped[TicketPriority] = mapped_column(Enum(TicketPriority, name="ticket_priority"), default=TicketPriority.medium)
    status:         Mapped[TicketStatus]   = mapped_column(Enum(TicketStatus, name="ticket_status"), default=TicketStatus.open)
    assigned_to:    Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    parent_ticket:  Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("it_tickets.id"))
    resolution:     Mapped[str | None]     = mapped_column(Text)
    is_known_issue: Mapped[bool]           = mapped_column(Boolean, default=False)
    outage_ref:     Mapped[str | None]     = mapped_column(String(100))
    resolved_at:    Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    sla_due_at:     Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    user:     Mapped["User"] = relationship(back_populates="tickets", foreign_keys=[user_id])
    comments: Mapped[list["ITTicketComment"]] = relationship(back_populates="ticket")


class ITTicketComment(Base):
    __tablename__ = "it_ticket_comments"

    id:          Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticket_id:   Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("it_tickets.id", ondelete="CASCADE"))
    author_id:   Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    comment:     Mapped[str]       = mapped_column(Text, nullable=False)
    is_internal: Mapped[bool]      = mapped_column(Boolean, default=False)
    created_at:  Mapped[datetime]  = mapped_column(DateTime(timezone=True), server_default=func.now())

    ticket: Mapped["ITTicket"] = relationship(back_populates="comments")


class MaintenanceSchedule(Base):
    __tablename__ = "maintenance_schedule"

    id:              Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title:           Mapped[str]       = mapped_column(String(300), nullable=False)
    affected_system: Mapped[str]       = mapped_column(String(200), nullable=False)
    starts_at:       Mapped[datetime]  = mapped_column(DateTime(timezone=True), nullable=False)
    ends_at:         Mapped[datetime]  = mapped_column(DateTime(timezone=True), nullable=False)
    description:     Mapped[str | None] = mapped_column(Text)
    created_by:      Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at:      Mapped[datetime]  = mapped_column(DateTime(timezone=True), server_default=func.now())


class KnownIssue(Base):
    __tablename__ = "known_issues"

    id:          Mapped[uuid.UUID]      = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title:       Mapped[str]            = mapped_column(String(300), nullable=False)
    category:    Mapped[TicketCategory] = mapped_column(Enum(TicketCategory, name="ticket_category"), nullable=False)
    description: Mapped[str]            = mapped_column(Text, nullable=False)
    workaround:  Mapped[str | None]     = mapped_column(Text)
    is_active:   Mapped[bool]           = mapped_column(Boolean, default=True)
    reported_at: Mapped[datetime]       = mapped_column(DateTime(timezone=True), server_default=func.now())
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class ITInventory(TimestampMixin, Base):
    __tablename__ = "it_inventory"

    id:            Mapped[uuid.UUID]  = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    asset_tag:     Mapped[str]        = mapped_column(String(50), unique=True, nullable=False)
    asset_type:    Mapped[AssetType]  = mapped_column(Enum(AssetType, name="asset_type"), nullable=False)
    brand:         Mapped[str | None] = mapped_column(String(100))
    model:         Mapped[str | None] = mapped_column(String(200))
    serial_no:     Mapped[str | None] = mapped_column(String(100), unique=True)
    status:        Mapped[AssetStatus] = mapped_column(Enum(AssetStatus, name="asset_status"), default=AssetStatus.available)
    assigned_to:   Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    assigned_at:   Mapped[datetime | None]  = mapped_column(DateTime(timezone=True))
    purchase_date: Mapped[date | None]      = mapped_column(Date)
    warranty_until: Mapped[date | None]     = mapped_column(Date)
    location:      Mapped[str | None]       = mapped_column(String(200))
    notes:         Mapped[str | None]       = mapped_column(Text)


class AssetRequest(TimestampMixin, Base):
    __tablename__ = "asset_requests"

    id:            Mapped[uuid.UUID]    = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id:       Mapped[uuid.UUID]    = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    asset_type:    Mapped[AssetType]    = mapped_column(Enum(AssetType, name="asset_type"), nullable=False)
    justification: Mapped[str]          = mapped_column(Text, nullable=False)
    status:        Mapped[RequestStatus] = mapped_column(Enum(RequestStatus, name="request_status"), default=RequestStatus.pending)
    manager_id:    Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    manager_action: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    manager_note:  Mapped[str | None]   = mapped_column(Text)
    it_actioned_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    it_action_at:  Mapped[datetime | None]   = mapped_column(DateTime(timezone=True))
    it_note:       Mapped[str | None]   = mapped_column(Text)
    asset_id:      Mapped[uuid.UUID | None]  = mapped_column(UUID(as_uuid=True), ForeignKey("it_inventory.id"))

    user: Mapped["User"] = relationship(back_populates="asset_requests", foreign_keys=[user_id])


# ── Finance Module ────────────────────────────────────────────────────────────

class PayrollRecord(Base):
    __tablename__ = "payroll_records"
    __table_args__ = (UniqueConstraint("user_id", "pay_month"),)

    id:               Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id:          Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    pay_month:        Mapped[date]      = mapped_column(Date, nullable=False)
    gross_salary:     Mapped[float]     = mapped_column(Numeric(12, 2), nullable=False)
    basic:            Mapped[float]     = mapped_column(Numeric(12, 2), nullable=False)
    hra:              Mapped[float]     = mapped_column(Numeric(12, 2), default=0)
    allowances:       Mapped[float]     = mapped_column(Numeric(12, 2), default=0)
    pf_employee:      Mapped[float]     = mapped_column(Numeric(12, 2), default=0)
    pf_employer:      Mapped[float]     = mapped_column(Numeric(12, 2), default=0)
    tds:              Mapped[float]     = mapped_column(Numeric(12, 2), default=0)
    professional_tax: Mapped[float]     = mapped_column(Numeric(12, 2), default=0)
    other_deductions: Mapped[float]     = mapped_column(Numeric(12, 2), default=0)
    net_salary:       Mapped[float]     = mapped_column(Numeric(12, 2), nullable=False)
    payslip_url:      Mapped[str | None] = mapped_column(Text)
    generated_at:     Mapped[datetime]  = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(foreign_keys=[user_id])


class Reimbursement(TimestampMixin, Base):
    __tablename__ = "reimbursements"
    __table_args__ = (CheckConstraint("amount > 0", name="positive_amount"),)

    id:            Mapped[uuid.UUID]             = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    claim_no:      Mapped[str]                   = mapped_column(String(20), unique=True, nullable=False)
    user_id:       Mapped[uuid.UUID]             = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    category:      Mapped[ReimbursementCategory] = mapped_column(Enum(ReimbursementCategory, name="reimbursement_category"), nullable=False)
    amount:        Mapped[float]                 = mapped_column(Numeric(10, 2), nullable=False)
    currency:      Mapped[str]                   = mapped_column(String(3), default="INR")
    description:   Mapped[str]                   = mapped_column(Text, nullable=False)
    expense_date:  Mapped[date]                  = mapped_column(Date, nullable=False)
    receipt_url:   Mapped[str | None]            = mapped_column(Text)
    status:        Mapped[ReimbursementStatus]   = mapped_column(Enum(ReimbursementStatus, name="reimbursement_status"), default=ReimbursementStatus.draft)
    submitted_at:  Mapped[datetime | None]       = mapped_column(DateTime(timezone=True))
    reviewed_by:   Mapped[uuid.UUID | None]      = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    reviewed_at:   Mapped[datetime | None]       = mapped_column(DateTime(timezone=True))
    reviewer_note: Mapped[str | None]            = mapped_column(Text)
    paid_at:       Mapped[datetime | None]       = mapped_column(DateTime(timezone=True))
    payment_ref:   Mapped[str | None]            = mapped_column(String(100))

    user: Mapped["User"] = relationship(back_populates="reimbursements", foreign_keys=[user_id])


# ── Approvals ─────────────────────────────────────────────────────────────────

class Approval(Base):
    __tablename__ = "approvals"

    id:          Mapped[uuid.UUID]      = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_type: Mapped[ApprovalEntity] = mapped_column(Enum(ApprovalEntity, name="approval_entity"), nullable=False)
    entity_id:   Mapped[uuid.UUID]      = mapped_column(UUID(as_uuid=True), nullable=False)
    approver_id: Mapped[uuid.UUID]      = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    step:        Mapped[int]            = mapped_column(Integer, default=1)
    decision:    Mapped[ApprovalDecision] = mapped_column(Enum(ApprovalDecision, name="approval_decision"), default=ApprovalDecision.pending)
    note:        Mapped[str | None]     = mapped_column(Text)
    decided_at:  Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    expires_at:  Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at:  Mapped[datetime]       = mapped_column(DateTime(timezone=True), server_default=func.now())

    approver: Mapped["User"] = relationship(foreign_keys=[approver_id])


# ── Memory & Sessions ─────────────────────────────────────────────────────────

class UserMemory(Base):
    __tablename__ = "user_memory"
    __table_args__ = (UniqueConstraint("user_id", "memory_key"),)

    id:           Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id:      Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    memory_key:   Mapped[str]       = mapped_column(String(100), nullable=False)
    memory_value: Mapped[dict]      = mapped_column(JSONB, nullable=False)
    source:       Mapped[str]       = mapped_column(String(50), default="inferred")
    updated_at:   Mapped[datetime]  = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="memory_entries")


class ConversationSession(Base):
    __tablename__ = "conversation_sessions"

    id:            Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_key:   Mapped[str]       = mapped_column(String(200), unique=True, nullable=False)
    user_id:       Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    messages:      Mapped[list]      = mapped_column(JSONB, default=list)
    agent_used:    Mapped[str | None] = mapped_column(String(50))
    started_at:    Mapped[datetime]  = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_active_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    ended_at:      Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


# ── RAG Documents ─────────────────────────────────────────────────────────────

class RAGDocument(Base):
    __tablename__ = "rag_documents"

    id:            Mapped[uuid.UUID]    = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename:      Mapped[str]          = mapped_column(String(500), nullable=False)
    department:    Mapped[DocDepartment] = mapped_column(Enum(DocDepartment, name="doc_department"), nullable=False)
    doc_type:      Mapped[str | None]   = mapped_column(String(100))
    roles_allowed: Mapped[list[UserRole]] = mapped_column(ARRAY(Enum(UserRole, name="user_role", create_constraint=False)), default=[UserRole.employee])
    file_url:      Mapped[str | None]   = mapped_column(Text)
    ingested_at:   Mapped[datetime]     = mapped_column(DateTime(timezone=True), server_default=func.now())
    is_active:     Mapped[bool]         = mapped_column(Boolean, default=True)
    chunk_count:   Mapped[int]          = mapped_column(Integer, default=0)
    metadata_:     Mapped[dict]         = mapped_column("metadata", JSONB, default=dict)

    chunks: Mapped[list["RAGChunk"]] = relationship(back_populates="document", cascade="all, delete-orphan")


class RAGChunk(Base):
    __tablename__ = "rag_chunks"
    __table_args__ = (UniqueConstraint("document_id", "chunk_index"),)

    id:          Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("rag_documents.id", ondelete="CASCADE"))
    chunk_index: Mapped[int]       = mapped_column(Integer, nullable=False)
    content:     Mapped[str]       = mapped_column(Text, nullable=False)
    embedding:   Mapped[Any]       = mapped_column(Vector(1536))       # pgvector
    token_count: Mapped[int | None] = mapped_column(Integer)
    metadata_:   Mapped[dict]      = mapped_column("metadata", JSONB, default=dict)
    created_at:  Mapped[datetime]  = mapped_column(DateTime(timezone=True), server_default=func.now())

    document: Mapped["RAGDocument"] = relationship(back_populates="chunks")


# ── Audit Log ─────────────────────────────────────────────────────────────────

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id:           Mapped[uuid.UUID]  = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id:      Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    session_id:   Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("conversation_sessions.id"))
    action:       Mapped[str]        = mapped_column(String(200), nullable=False)
    entity_type:  Mapped[str | None] = mapped_column(String(100))
    entity_id:    Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    agent_used:   Mapped[str | None] = mapped_column(String(100))
    tool_used:    Mapped[str | None] = mapped_column(String(100))
    llm_model:    Mapped[str | None] = mapped_column(String(100))
    status:       Mapped[str]        = mapped_column(String(50), default="success")
    error_message: Mapped[str | None] = mapped_column(Text)
    latency_ms:   Mapped[int | None] = mapped_column(Integer)
    token_count:  Mapped[int | None] = mapped_column(Integer)
    ip_address:   Mapped[Any]        = mapped_column(INET)
    metadata_:    Mapped[dict]       = mapped_column("metadata", JSONB, default=dict)
    created_at:   Mapped[datetime]   = mapped_column(DateTime(timezone=True), server_default=func.now())
```

## app\rag\__init__.py

```python
# app/rag/__init__.py

```

## app\schemas\chat.py

```python
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class ChatRequest(BaseModel):
    query: str = Field(..., description="The user's message.")
    session_id: Optional[str] = Field(None, description="Existing session ID for multi-turn conversations.")

class ChatResponse(BaseModel):
    session_id: str
    response: str
    intent: str
    approval_required: bool = False
    metadata: Dict[str, Any] = {}

class ApprovalDecisionRequest(BaseModel):
    decision: str = Field(..., description="Must be 'approved' or 'rejected'")
    note: Optional[str] = Field(None, description="Optional reasoning for the decision")
```

## app\schemas\__init__.py

```python
# app/schemas/__init__.py

```

## app\tools\email_tools.py

```python
"""
Email Automation — Power Automate HTTP Trigger
===============================================
LangGraph email_notify_node calls send_email_via_power_automate().
Power Automate then sends email via Office 365 / Outlook.

Setup in Power Automate:
  1. New flow → "When an HTTP request is received" trigger
  2. Copy the generated webhook URL → settings.POWER_AUTOMATE_WEBHOOK_URL
  3. Add "Send an email (V2)" action (Office 365 Outlook)
  4. Map: To=body.recipients, Subject=body.subject, Body=body.body
"""
from __future__ import annotations

import httpx
import structlog

from app.config import settings

logger = structlog.get_logger("app.email")


async def send_email_via_power_automate(
    recipients: list[str],
    subject: str,
    body: str,
    cc: list[str] | None = None,
    importance: str = "Normal",   # Low | Normal | High
) -> bool:
    """
    POST to Power Automate HTTP trigger which sends email via Outlook 365.
    Returns True on success, False on failure (non-raising — email is best-effort).
    """
    if not settings.POWER_AUTOMATE_WEBHOOK_URL:
        # Dev/test: log only (no actual send)
        logger.debug("email_mock", recipients=recipients, subject=subject)
        return True

    payload = {
        "recipients": recipients,
        "cc": cc or [],
        "subject": subject,
        "body": body,
        "importance": importance,
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.post(
                settings.POWER_AUTOMATE_WEBHOOK_URL,
                json=payload,
            )
            response.raise_for_status()
            return True
        except (httpx.HTTPStatusError, httpx.RequestError) as exc:
            logger.error("email_send_failed", exc_info=exc, recipients=recipients)
            return False


# ── Pre-built email templates ─────────────────────────────────────────────────

def leave_request_email(employee_name: str, manager_email: str,
                         leave_type: str, start: str, end: str,
                         days: float, leave_id: str, approve_url: str) -> dict:
    return {
        "recipients": [manager_email],
        "subject": f"Leave Request — {employee_name} ({days} day(s))",
        "body": f"""
Hi,

<b>{employee_name}</b> has applied for <b>{leave_type}</b> leave:
<ul>
  <li>From: {start}</li>
  <li>To: {end}</li>
  <li>Duration: {days} business day(s)</li>
</ul>

<a href="{approve_url}">Click here to approve or reject</a>

This is an automated message from the Enterprise AI Copilot.
        """,
    }


def leave_approval_email(employee_email: str, decision: str,
                          leave_type: str, start: str, end: str,
                          reviewer_note: str = "") -> dict:
    status_word = "Approved ✅" if decision == "approved" else "Rejected ❌"
    return {
        "recipients": [employee_email],
        "subject": f"Your Leave Request has been {status_word}",
        "body": f"""
Hi,

Your <b>{leave_type}</b> leave request ({start} to {end}) has been <b>{decision}</b>.

{f'Note from reviewer: {reviewer_note}' if reviewer_note else ''}

This is an automated message from the Enterprise AI Copilot.
        """,
    }


def ticket_created_email(employee_email: str, ticket_no: str,
                          subject: str, priority: str) -> dict:
    return {
        "recipients": [employee_email],
        "subject": f"IT Ticket Created — {ticket_no}",
        "body": f"""
Hi,

Your IT support ticket has been created:
<ul>
  <li>Ticket No: <b>{ticket_no}</b></li>
  <li>Subject: {subject}</li>
  <li>Priority: {priority.upper()}</li>
  <li>Status: Open</li>
</ul>

The IT team will respond based on priority SLA. You'll receive updates via email.

This is an automated message from the Enterprise AI Copilot.
        """,
    }


def reimbursement_submitted_email(employee_email: str, claim_no: str,
                                   amount: float, currency: str) -> dict:
    return {
        "recipients": [employee_email],
        "subject": f"Reimbursement Claim Submitted — {claim_no}",
        "body": f"""
Hi,

Your reimbursement claim has been submitted:
<ul>
  <li>Claim No: <b>{claim_no}</b></li>
  <li>Amount: {currency} {amount:,.2f}</li>
  <li>Status: Under Review</li>
</ul>

The Finance team will process it within 5 business days.

This is an automated message from the Enterprise AI Copilot.
        """,
    }
```

## app\tools\finance_tools.py

```python
import uuid
from datetime import date, datetime
from typing import Dict, Any
from langchain_core.tools import tool
from pydantic import BaseModel, Field

from sqlalchemy import select, and_, extract
from app.database import AsyncSessionLocal
from app.models import (
    PayrollRecord, Reimbursement, ReimbursementCategory, ReimbursementStatus
)

# ==========================================
# INPUT SCHEMAS
# ==========================================

class FetchPayslipInput(BaseModel):
    user_id: str = Field(description="The UUID of the employee requesting their payslip.")
    year: int = Field(description="The year of the requested payslip (e.g., 2023).")
    month: int = Field(description="The numeric month of the requested payslip (1-12).")

class SubmitReimbursementInput(BaseModel):
    user_id: str = Field(description="The UUID of the employee submitting the claim.")
    category: ReimbursementCategory = Field(description="The category of the expense (e.g., 'travel', 'food', 'internet').")
    amount: float = Field(description="The total amount being claimed.")
    currency: str = Field(description="The 3-letter currency code (e.g., 'USD', 'INR').", default="USD")
    description: str = Field(description="A detailed explanation of the business expense.")
    expense_date: date = Field(description="The date the expense occurred (YYYY-MM-DD).")

# ==========================================
# TOOLS
# ==========================================

@tool("fetch_payslip", args_schema=FetchPayslipInput)
async def fetch_payslip(user_id: str, year: int, month: int) -> str:
    """
    Fetch the payslip details (gross salary, net salary, deductions) for a specific month.
    Use this strictly when an employee asks for their own salary or payslip information.
    """
    try:
        async with AsyncSessionLocal() as db:
            # PostgreSQL extraction for month and year matching
            stmt = select(PayrollRecord).where(
                and_(
                    PayrollRecord.user_id == user_id,
                    extract('year', PayrollRecord.pay_month) == year,
                    extract('month', PayrollRecord.pay_month) == month
                )
            )
            result = await db.execute(stmt)
            payslip = result.scalar_one_or_none()
            
            if not payslip:
                month_name = date(year, month, 1).strftime('%B')
                return f"I couldn't find a generated payslip for {month_name} {year}. Please ensure the payroll for that month has been processed."
            
            # Format the financial data nicely
            response = f"**Payslip Summary for {payslip.pay_month.strftime('%B %Y')}**\n"
            response += f"- **Gross Salary:** {payslip.gross_salary:,.2f}\n"
            response += f"- **Basic Pay:** {payslip.basic:,.2f}\n"
            response += f"- **Allowances:** {payslip.allowances:,.2f}\n"
            response += f"- **Tax Deductions (TDS):** -{payslip.tds:,.2f}\n"
            response += f"- **Net Salary:** **{payslip.net_salary:,.2f}**\n\n"
            
            if payslip.payslip_url:
                response += f"[Click here to download your full PDF payslip]({payslip.payslip_url})"
                
            return response
            
    except Exception as e:
        return f"Error fetching payslip details: {str(e)}"

@tool("submit_reimbursement", args_schema=SubmitReimbursementInput)
async def submit_reimbursement(user_id: str, category: ReimbursementCategory, amount: float, currency: str, description: str, expense_date: date) -> Dict[str, Any]:
    """
    Submit a new expense reimbursement claim to the database.
    Use this when an employee wants to get paid back for business expenses like travel or meals.
    Requires manager and finance approval.
    """
    try:
        if amount <= 0:
            return {"error": "Reimbursement amount must be greater than zero."}

        # Generate a readable claim number
        claim_no = f"EXP-{uuid.uuid4().hex[:6].upper()}"

        async with AsyncSessionLocal() as db:
            new_claim = Reimbursement(
                claim_no=claim_no,
                user_id=user_id,
                category=category,
                amount=amount,
                currency=currency.upper(),
                description=description,
                expense_date=expense_date,
                status=ReimbursementStatus.submitted
            )
            db.add(new_claim)
            await db.commit()
            await db.refresh(new_claim)
            
            claim_id = str(new_claim.id)

        # Trigger Manager Approval Process!
        return {
            "status": "success",
            "message": f"Your reimbursement claim ({claim_no}) for {currency.upper()} {amount:,.2f} has been submitted.",
            "approval_required": True,
            "claim_id": claim_id,
            "email_triggered": True,
            "email_recipients": ["manager@company.com"], 
            "email_subject": f"Expense Approval Required: {claim_no}",
            "email_body": f"Employee {user_id} submitted a {category.value} expense for {currency.upper()} {amount:,.2f}.\n\nDescription: {description}\nDate: {expense_date}"
        }

    except Exception as e:
        return {"error": f"Failed to submit reimbursement claim: {str(e)}"}
```

## app\tools\hr_tools.py

```python
from datetime import date
from typing import Dict, Any
from langchain_core.tools import tool
from pydantic import BaseModel, Field

from sqlalchemy import select, and_
from app.database import AsyncSessionLocal
from app.models import LeaveRequest, LeaveBalance, LeaveType, LeaveStatus

# ==========================================
# INPUT SCHEMAS
# ==========================================

class LeaveBalanceInput(BaseModel):
    user_id: str = Field(description="The UUID of the employee requesting their leave balance.")
    year: int = Field(description="The current year to check the balance for.")

class ApplyLeaveInput(BaseModel):
    user_id: str = Field(description="The UUID of the employee applying for leave.")
    start_date: date = Field(description="The start date of the leave (YYYY-MM-DD).")
    end_date: date = Field(description="The end date of the leave (YYYY-MM-DD).")
    leave_type: LeaveType = Field(description="The type of leave (e.g., 'sick', 'casual', 'earned').")
    business_days: float = Field(description="The total number of working days requested.")
    reason: str = Field(description="A brief reason for the leave.")

class CancelLeaveInput(BaseModel):
    user_id: str = Field(description="The UUID of the employee canceling their leave.")
    leave_id: str = Field(description="The UUID of the leave request to cancel.")

# ==========================================
# TOOLS
# ==========================================

@tool("get_leave_balance", args_schema=LeaveBalanceInput)
async def get_leave_balance(user_id: str, year: int) -> str:
    """
    Fetch the current leave balances for an employee from the database. 
    Use this when an employee asks how many days off they have left.
    """
    try:
        async with AsyncSessionLocal() as db:
            stmt = select(LeaveBalance).where(
                and_(LeaveBalance.user_id == user_id, LeaveBalance.year == year)
            )
            result = await db.execute(stmt)
            balances = result.scalars().all()
            
            if not balances:
                return "I couldn't find any leave balance records for you in the system for this year."
            
            response = "Here are your current leave balances:\n"
            for b in balances:
                response += f"- **{b.leave_type.value.capitalize()} Leave**: {b.available_days} days available (out of {b.entitled_days} entitled).\n"
            
            return response
            
    except Exception as e:
        return f"Error fetching leave balance: {str(e)}"

@tool("apply_for_leave", args_schema=ApplyLeaveInput)
async def apply_for_leave(user_id: str, start_date: date, end_date: date, leave_type: LeaveType, business_days: float, reason: str) -> Dict[str, Any]:
    """
    Submit a new leave request for an employee to the database.
    Use this when an employee explicitly states they want to book time off.
    """
    try:
        if end_date < start_date:
            return {"error": "The end date cannot be before the start date."}

        async with AsyncSessionLocal() as db:
            new_leave = LeaveRequest(
                user_id=user_id,
                start_date=start_date,
                end_date=end_date,
                leave_type=leave_type,
                business_days=business_days,
                reason=reason,
                status=LeaveStatus.pending
            )
            db.add(new_leave)
            await db.commit()
            await db.refresh(new_leave)
            
            generated_leave_id = str(new_leave.id)

        # Trigger the LangGraph Human-in-the-loop and Email Automation!
        return {
            "status": "success",
            "message": f"Leave request for {start_date} to {end_date} has been drafted.",
            "approval_required": True,       
            "leave_id": generated_leave_id,  
            "email_triggered": True,
            "email_recipients": ["manager@company.com"], # TODO: Fetch actual manager email via graph context
            "email_subject": f"Leave Approval Required: Employee {user_id}",
            "email_body": f"Please approve {leave_type.value} leave from {start_date} to {end_date}. Reason: {reason}"
        }

    except Exception as e:
        return {"error": f"Failed to submit leave request to the database: {str(e)}"}

@tool("cancel_leave", args_schema=CancelLeaveInput)
async def cancel_leave(user_id: str, leave_id: str) -> str:
    """
    Cancel an existing pending or approved leave request in the database.
    Use this when an employee wants to revoke a previously booked holiday.
    """
    try:
        async with AsyncSessionLocal() as db:
            stmt = select(LeaveRequest).where(
                and_(LeaveRequest.id == leave_id, LeaveRequest.user_id == user_id)
            )
            result = await db.execute(stmt)
            leave_request = result.scalar_one_or_none()
            
            if not leave_request:
                return "Leave request not found or you do not have permission to cancel it."
            
            if leave_request.status in [LeaveStatus.cancelled, LeaveStatus.rejected]:
                return f"This leave request is already marked as {leave_request.status.value}."
                
            leave_request.status = LeaveStatus.cancelled
            await db.commit()
        
        return f"Leave request has been successfully canceled."
    except Exception as e:
        return f"Failed to cancel leave request: {str(e)}"
```

## app\tools\it_tools.py

```python
import uuid
from typing import Dict, Any
from langchain_core.tools import tool
from pydantic import BaseModel, Field

from sqlalchemy import select, and_
from app.database import AsyncSessionLocal
from app.models import (
    ITTicket, TicketCategory, TicketPriority, TicketStatus,
    AssetRequest, AssetType, RequestStatus
)

# ==========================================
# INPUT SCHEMAS
# ==========================================

class CreateTicketInput(BaseModel):
    user_id: str = Field(description="The UUID of the employee creating the ticket.")
    category: TicketCategory = Field(description="The category of the issue (e.g., 'laptop', 'vpn', 'access').")
    subject: str = Field(description="A brief summary of the issue.")
    description: str = Field(description="Detailed explanation of the problem.")
    priority: TicketPriority = Field(description="Urgency of the issue ('low', 'medium', 'high', 'critical').")

class GetTicketStatusInput(BaseModel):
    user_id: str = Field(description="The UUID of the employee checking the ticket.")
    ticket_no: str = Field(description="The specific ticket number (e.g., 'TKT-12345').")

class RequestAssetInput(BaseModel):
    user_id: str = Field(description="The UUID of the employee requesting the asset.")
    asset_type: AssetType = Field(description="The type of asset requested (e.g., 'laptop', 'monitor', 'software_license').")
    justification: str = Field(description="The business reason for requesting this asset.")

# ==========================================
# TOOLS
# ==========================================

@tool("create_it_ticket", args_schema=CreateTicketInput)
async def create_it_ticket(user_id: str, category: TicketCategory, subject: str, description: str, priority: TicketPriority) -> Dict[str, Any]:
    """
    Create a new IT support ticket in the database.
    Use this when an employee reports a broken device, access issue, or software bug.
    """
    try:
        # Generate a readable ticket number
        ticket_no = f"TKT-{uuid.uuid4().hex[:6].upper()}"

        async with AsyncSessionLocal() as db:
            new_ticket = ITTicket(
                ticket_no=ticket_no,
                user_id=user_id,
                category=category,
                subject=subject,
                description=description,
                priority=priority,
                status=TicketStatus.open
            )
            db.add(new_ticket)
            await db.commit()
            await db.refresh(new_ticket)
            
            ticket_id = str(new_ticket.id)

        # Trigger an email to the IT helpdesk
        return {
            "status": "success",
            "message": f"IT Ticket {ticket_no} has been successfully created.",
            "ticket_id": ticket_id,
            "ticket_no": ticket_no,
            "email_triggered": True,
            "email_recipients": ["it-support@company.com"],
            "email_subject": f"New IT Ticket [{priority.value.upper()}]: {subject}",
            "email_body": f"User {user_id} reported an issue in category {category.value}.\n\nDescription: {description}"
        }

    except Exception as e:
        return {"error": f"Failed to create IT ticket: {str(e)}"}

@tool("get_ticket_status", args_schema=GetTicketStatusInput)
async def get_ticket_status(user_id: str, ticket_no: str) -> str:
    """
    Check the current status and resolution notes of an IT ticket.
    Use this when an employee asks for an update on a ticket they submitted.
    """
    try:
        async with AsyncSessionLocal() as db:
            stmt = select(ITTicket).where(
                and_(ITTicket.ticket_no == ticket_no, ITTicket.user_id == user_id)
            )
            result = await db.execute(stmt)
            ticket = result.scalar_one_or_none()
            
            if not ticket:
                return f"I couldn't find a ticket with the number {ticket_no} associated with your account."
            
            response = f"**Ticket {ticket.ticket_no} Status Update:**\n"
            response += f"- **Status:** {ticket.status.value.replace('_', ' ').capitalize()}\n"
            response += f"- **Priority:** {ticket.priority.value.capitalize()}\n"
            
            if ticket.resolution:
                response += f"- **Resolution Notes:** {ticket.resolution}\n"
                
            return response
            
    except Exception as e:
        return f"Error fetching ticket status: {str(e)}"

@tool("request_it_asset", args_schema=RequestAssetInput)
async def request_it_asset(user_id: str, asset_type: AssetType, justification: str) -> Dict[str, Any]:
    """
    Submit a request for a new IT asset (hardware or software).
    Use this when an employee asks for a new laptop, monitor, or license.
    Requires manager approval.
    """
    try:
        async with AsyncSessionLocal() as db:
            new_request = AssetRequest(
                user_id=user_id,
                asset_type=asset_type,
                justification=justification,
                status=RequestStatus.pending
            )
            db.add(new_request)
            await db.commit()
            await db.refresh(new_request)
            
            request_id = str(new_request.id)

        # Trigger Manager Approval Process!
        return {
            "status": "success",
            "message": f"Your request for a {asset_type.value.replace('_', ' ')} has been submitted and is pending manager approval.",
            "approval_required": True,
            "request_id": request_id,
            "email_triggered": True,
            "email_recipients": ["manager@company.com"], 
            "email_subject": f"Asset Request Approval: {asset_type.value.capitalize()}",
            "email_body": f"Employee {user_id} is requesting a {asset_type.value.replace('_', ' ')}.\n\nJustification: {justification}"
        }

    except Exception as e:
        return {"error": f"Failed to submit asset request: {str(e)}"}
```

## app\tools\rag_tools.py

```python
import os
from langchain_core.tools import tool
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from pydantic import BaseModel, Field

from app.config import settings

CHROMA_PERSIST_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "database", "chroma_db"))

# Optional kwargs for disabling SSL verification
kwargs = {}
verify_ssl = getattr(settings, "OPENAI_VERIFY_SSL", True)
if not verify_ssl:
    import httpx
    kwargs["http_client"] = httpx.Client(verify=False)
    kwargs["http_async_client"] = httpx.AsyncClient(verify=False)

# Initialize connection to the Vector DB
vectorstore = Chroma(
    persist_directory=CHROMA_PERSIST_DIR,
    embedding_function=OpenAIEmbeddings(
        api_key=settings.OPENAI_API_KEY,
        **kwargs
    )
)
retriever = vectorstore.as_retriever(
    search_type="mmr", # Maximal Marginal Relevance for diversity
    search_kwargs={"k": 5, "fetch_k": 20} # Top-K=5
)

class PolicySearchInput(BaseModel):
    query: str = Field(description="The specific policy question or search query.")
    user_role: str = Field(description="The role of the user making the request (e.g., employee, manager, hr).")
    department: str = Field(description="The department to filter by (e.g., hr, it, finance).")

@tool("search_company_policies", args_schema=PolicySearchInput)
def search_company_policies(query: str, user_role: str, department: str) -> str:
    """
    Search the company knowledge base for HR, IT, or Finance policies.
    Use this tool whenever the user asks about rules, allowances, processes, or guides.
    """
    try:
        # 1. Define Metadata Filters (RBAC & Department)
        # Chroma uses simple string matching. We ensure the user's role is in the allowed string.
        search_filter = {
            "$and": [
                {"department": {"$eq": department.lower()}},
                {"roles_allowed": {"$contains": user_role.lower()}}
            ]
        }

        # 2. Execute Retrieval
        docs = vectorstore.similarity_search(
            query=query,
            k=5,
            filter=search_filter
        )

        if not docs:
            return f"No relevant {department.upper()} policies found for your query. Either the policy does not exist, or you do not have permission to view it."

        # 3. Format output with citations
        formatted_results = f"--- Retrieved {department.upper()} Policies ---\n\n"
        for i, doc in enumerate(docs, 1):
            source = doc.metadata.get("source", "Unknown Document")
            formatted_results += f"[Source {i}: {source}]\n{doc.page_content}\n\n"

        return formatted_results

    except Exception as e:
        return f"Error retrieving documents: {str(e)}"
```

## app\tools\__init__.py

```python
from typing import List
from langchain_core.tools import BaseTool
from app.models import UserRole

# Import all domain tools
from app.tools.rag_tools import search_company_policies
from app.tools.hr_tools import get_leave_balance, apply_for_leave, cancel_leave
from app.tools.it_tools import create_it_ticket, get_ticket_status, request_it_asset
from app.tools.finance_tools import fetch_payslip, submit_reimbursement

def get_tools_for_intent(intent: str, user_role: UserRole) -> List[BaseTool]:
    """
    Returns the specific list of LangChain tools available for a given intent.
    This prevents overwhelming the LLM with unnecessary tools and enforces RBAC.
    """
    tools = []
    
    # 1. RAG / Policy Tools (Available to almost everyone based on intent)
    if "policy" in intent or intent == "general.unknown":
        tools.append(search_company_policies)
        
    # 2. HR Tools
    if intent.startswith("hr.leave"):
        tools.extend([get_leave_balance, apply_for_leave, cancel_leave])
        
    # 3. IT Tools
    elif intent.startswith("it"):
        tools.extend([create_it_ticket, get_ticket_status, request_it_asset])
        
    # 4. Finance Tools
    elif intent.startswith("finance"):
        tools.extend([fetch_payslip, submit_reimbursement])
        
    return tools
```

## app\__init__.py

```python
# app/__init__.py

```

## app\agents\state.py

```python
"""
Agent State
===========
The single TypedDict that flows through every LangGraph node.
Every node reads from this state and returns a partial update.

Rule: never pass data between nodes via side channels (globals,
      module-level vars, etc.) — everything goes through AgentState.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Annotated, Any, Literal, TypedDict, Dict, Optional

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

from app.models import UserRole


# ── Intent categories ─────────────────────────────────────────────────────────

Intent = Literal[
    # HR
    "hr.policy_query",
    "hr.leave_apply",
    "hr.leave_check_balance",
    "hr.leave_view_history",
    "hr.leave_cancel",
    "hr.leave_check_status",
    # IT
    "it.ticket_create",
    "it.ticket_status",
    "it.asset_request",
    "it.ticket_view",
    # Finance
    "finance.payslip_fetch",
    "finance.reimbursement_submit",
    "finance.reimbursement_status",
    "finance.tax_query",
    # Meta
    "general.greeting",
    "general.unknown",
]

RouteTo = Literal["hr_agent", "it_agent", "finance_agent", "rag_agent", "unknown"]


# ── GEPA: planning and evaluation ─────────────────────────────────────────────

class ActionPlan(TypedDict):
    """Written by the Plan node before tool execution."""
    steps: list[str]           # ["1. Check leave balance", "2. Validate dates", ...]
    tools_needed: list[str]    # ["get_leave_balance", "check_overlaps"]
    reasoning: str             # why these steps


class EvalScore(TypedDict):
    """Written by the Evaluate node after response generation."""
    score: float               # 0.0 – 1.0
    relevance: float
    completeness: float
    rbac_compliant: bool
    critique: str              # natural language feedback for retry


# ── Main state ────────────────────────────────────────────────────────────────

class AgentState(TypedDict, total=False):
    """
    Flows through the entire LangGraph workflow.
    Nodes return a dict with only the keys they modify.
    """

    # ── Identity & auth ────────────────────────────────────────
    user_id:       str
    user_email:    str
    user_name:     str
    user_role:     UserRole
    department_id: str | None
    manager_id:    str | None
    preferred_lang: str

    # ── Conversation ────────────────────────────────────────────
    session_id:    str
    messages:      list[BaseMessage]   # full LangChain message history
    raw_query:     str                 # original user text (unchanged)

    # ── Routing ─────────────────────────────────────────────────
    intent:        Intent
    intent_confidence: float           # 0.0–1.0
    route_to:      RouteTo

    # ── GEPA: Plan → Execute → Evaluate ────────────────────────
    plan:          ActionPlan
    eval_score:    EvalScore
    retry_count:   int                 # incremented on each GEPA retry
    retry_critique: str                # critique passed back to Plan node

    # ── Tool execution ──────────────────────────────────────────
    tool_calls:    list[dict]          # [{name, args, result}]
    tool_error:    str | None

    # ── RAG ─────────────────────────────────────────────────────
    rag_docs:      list[dict]          # [{content, source, score}]
    rag_confidence: float              # avg cosine similarity of retrieved chunks
    web_search_triggered: bool

    # ── Human-in-loop (approval) ────────────────────────────────
    approval_required: bool
    approval_entity_type: str | None   # 'leave' | 'asset_request' | 'reimbursement'
    approval_entity_id:  str | None
    approval_decision:   str | None    # 'approved' | 'rejected'
    approval_note:       str | None

    # ── Email ────────────────────────────────────────────────────
    email_triggered:  bool
    email_recipients: list[str]
    email_subject:    str | None
    email_body:       str | None

    # ── Final response ──────────────────────────────────────────
    response:      str                 # final message shown to user
    response_type: Literal["text", "form", "table", "error"]
    metadata:      dict[str, Any]      # additional data for frontend (e.g., leave_id)

    # ── Observability ────────────────────────────────────────────
    agent_used:    str | None
    llm_model:     str | None
    latency_ms:    int | None
    error:         str | None


def initial_state(user_ctx: dict, query: str, session_id: str | None = None) -> AgentState:
    """
    Create a fresh AgentState from the enriched user context dict
    (returned by app.middleware.rbac.enrich_request).
    """
    return AgentState(
        user_id=user_ctx["user_id"],
        user_email=user_ctx["user_email"],
        user_name=user_ctx["user_name"],
        user_role=user_ctx["user_role"],
        department_id=user_ctx.get("department_id"),
        manager_id=user_ctx.get("manager_id"),
        preferred_lang=user_ctx.get("preferred_lang", "en"),
        session_id=session_id or str(uuid.uuid4()),
        messages=[],
        raw_query=query,
        intent="general.unknown",
        intent_confidence=0.0,
        route_to="unknown",
        retry_count=0,
        tool_calls=[],
        rag_docs=[],
        rag_confidence=0.0,
        web_search_triggered=False,
        approval_required=False,
        email_triggered=False,
        email_recipients=[],
        response="",
        response_type="text",
        metadata={},
    )
```

## app\agents\__init__.py

```python
from .state import AgentState, EvalScore, Intent, RouteTo, initial_state

__all__ = [
    "AgentState",
    "EvalScore",
    "Intent",
    "RouteTo",
    "initial_state",
]


```

## app\api\routes\approvals.py

```python
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any

from app.schemas.chat import ChatRequest, ChatResponse
from app.graph.workflow import run_workflow
# Assuming you have a dependency that extracts the user from a JWT/API token
# from app.middleware.rbac import get_current_user_ctx

router = APIRouter(prefix="/api/chat", tags=["Chat"])

# --- MOCK DEPENDENCY (Replace with your actual auth middleware) ---
async def get_current_user_ctx() -> Dict[str, Any]:
    """Mocks the user context that would normally come from a decoded JWT."""
    from app.models import UserRole
    return {
        "user_id": "user-uuid-1234",
        "user_email": "alice@company.com",
        "user_name": "Alice Smith",
        "user_role": UserRole.employee, # Change this to test manager/admin flows
        "department_id": "dept-uuid-hr",
    }
# ------------------------------------------------------------------

@router.post("/", response_model=ChatResponse)
async def chat_with_agent(
    request: ChatRequest, 
    user_ctx: Dict[str, Any] = Depends(get_current_user_ctx)
):
    """
    Send a message to the enterprise assistant. 
    Routes automatically to HR, IT, Finance, or RAG based on intent.
    """
    try:
        # 1. Invoke the LangGraph workflow
        final_state = await run_workflow(
            user_ctx=user_ctx, 
            query=request.query, 
            session_id=request.session_id
        )

        # 2. Return the structured response
        return ChatResponse(
            session_id=final_state.get("session_id"),
            response=final_state.get("response", "I'm sorry, I couldn't process that request."),
            intent=final_state.get("intent", "unknown"),
            approval_required=final_state.get("approval_required", False),
            metadata=final_state.get("metadata", {})
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## app\api\routes\chat.py

```python
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any

from app.schemas.chat import ChatRequest, ChatResponse
from app.graph.workflow import run_workflow
# Assuming you have a dependency that extracts the user from a JWT/API token
# from app.middleware.rbac import get_current_user_ctx

router = APIRouter(prefix="/api/chat", tags=["Chat"])

# --- MOCK DEPENDENCY (Replace with your actual auth middleware) ---
async def get_current_user_ctx() -> Dict[str, Any]:
    """Mocks the user context that would normally come from a decoded JWT."""
    from app.models import UserRole
    return {
        "user_id": "user-uuid-1234",
        "user_email": "alice@company.com",
        "user_name": "Alice Smith",
        "user_role": UserRole.employee, # Change this to test manager/admin flows
        "department_id": "dept-uuid-hr",
    }
# ------------------------------------------------------------------

@router.post("/", response_model=ChatResponse)
async def chat_with_agent(
    request: ChatRequest, 
    user_ctx: Dict[str, Any] = Depends(get_current_user_ctx)
):
    """
    Send a message to the enterprise assistant. 
    Routes automatically to HR, IT, Finance, or RAG based on intent.
    """
    try:
        # 1. Invoke the LangGraph workflow
        final_state = await run_workflow(
            user_ctx=user_ctx, 
            query=request.query, 
            session_id=request.session_id
        )

        # 2. Return the structured response
        return ChatResponse(
            session_id=final_state.get("session_id"),
            response=final_state.get("response", "I'm sorry, I couldn't process that request."),
            intent=final_state.get("intent", "unknown"),
            approval_required=final_state.get("approval_required", False),
            metadata=final_state.get("metadata", {})
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## app\api\routes\__init__.py

```python
# app/api/routes/__init__.py

```

## app\api\__init__.py

```python
# app/api/__init__.py

```

## app\graph\workflow.py

```python
"""
LangGraph Workflow — with GEPA pattern
======================================
"""
from __future__ import annotations

import json
import time
import uuid
from typing import Literal

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.language_models import BaseChatModel
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph
from langgraph.types import interrupt

from app.agents import AgentState, EvalScore, initial_state
from app.config import settings
from app.middleware import RBACViolation, rbac_guard
from app.models import UserRole


# ── LLM instances (multi-provider: Grok, Gemini, OpenAI) ─────────────────────

def get_llm(model_key: str, temperature: float = settings.LLM_TEMPERATURE) -> BaseChatModel:
    """Create a pure Gemini LLM client based on the requested model key."""
    model_name = getattr(settings, f"LLM_{model_key.upper()}", settings.LLM_HR)

    # Keep SSL fallback logic available in case we need to pass custom clients in the future
    kwargs = {}
    verify_ssl = getattr(settings, "OPENAI_VERIFY_SSL", True)
    if not verify_ssl:
        import httpx
        kwargs["http_client"] = httpx.Client(verify=False)
        kwargs["http_async_client"] = httpx.AsyncClient(verify=False)

    # --- Gemini Setup (Commented out) ---
    # from langchain_google_genai import ChatGoogleGenerativeAI
    # return ChatGoogleGenerativeAI(
    #     model=model_name,
    #     temperature=temperature,
    #     google_api_key=settings.GOOGLE_API_KEY,
    #     transport="rest"
    # )

    # --- OpenAI Setup (Active) ---
    from langchain_openai import ChatOpenAI
    return ChatOpenAI(
        model=model_name,
        temperature=temperature,
        api_key=settings.OPENAI_API_KEY,
        **kwargs
    )


# ── Node 1: Intent detection ──────────────────────────────────────────────────

INTENT_SYSTEM = """You are an intent classifier for an enterprise HR/IT/Finance AI copilot.
Classify the user query into exactly ONE intent code. Respond ONLY with valid JSON.

Intent codes:
HR: hr.policy_query, hr.leave_apply, hr.leave_check_balance, hr.leave_view_history,
    hr.leave_cancel, hr.leave_check_status
IT: it.ticket_create, it.ticket_status, it.asset_request, it.ticket_view
Finance: finance.payslip_fetch, finance.reimbursement_submit, finance.reimbursement_status,
         finance.tax_query
Meta: general.greeting, general.unknown

Response format: {"intent": "<code>", "confidence": <0.0-1.0>}"""


async def intent_node(state: AgentState) -> AgentState:
    llm = get_llm("intent")
    result = await llm.ainvoke([
        SystemMessage(content=INTENT_SYSTEM),
        HumanMessage(content=state["raw_query"]),
    ])
    try:
        parsed = json.loads(result.content)
        return {
            "intent": parsed["intent"],
            "intent_confidence": parsed["confidence"],
            "llm_model": settings.LLM_INTENT,
        }
    except Exception:
        return {"intent": "general.unknown", "intent_confidence": 0.0}


# ── Node 2: Role / RBAC gate ──────────────────────────────────────────────────

INTENT_PERM_MAP: dict[str, str] = {
    "hr.policy_query":           "hr:policy:read",
    "hr.leave_apply":            "hr:leave:apply",
    "hr.leave_check_balance":    "hr:leave:view_own",
    "hr.leave_view_history":     "hr:leave:view_own",
    "hr.leave_cancel":           "hr:leave:apply",
    "hr.leave_check_status":     "hr:leave:view_own",
    "it.ticket_create":          "it:ticket:create",
    "it.ticket_status":          "it:ticket:view_own",
    "it.ticket_view":            "it:ticket:view_own",
    "it.asset_request":          "it:asset:request",
    "finance.payslip_fetch":     "finance:payslip:view_own",
    "finance.reimbursement_submit": "finance:claim:submit",
    "finance.reimbursement_status": "finance:claim:view_own",
    "finance.tax_query":         "finance:tax:view_own",
}

INTENT_ROUTE_MAP: dict[str, str] = {
    "hr":      "hr_agent",
    "it":      "it_agent",
    "finance": "finance_agent",
    "general": "plan_node", 
}


async def role_check_node(state: AgentState) -> AgentState:
    intent = state["intent"]
    required_perm = INTENT_PERM_MAP.get(intent)
    if required_perm:
        try:
            rbac_guard(state["user_role"], required_perm)
        except RBACViolation as e:
            return {
                "error": str(e),
                "response": "You don't have permission to perform this action.",
                "response_type": "error",
                "route_to": "respond", 
            }
            
    # Derive routing from intent prefix. Fallback to plan_node if completely unknown.
    prefix = intent.split(".")[0]
    return {"route_to": INTENT_ROUTE_MAP.get(prefix, "plan_node")}


def route_after_role_check(state: AgentState) -> str:
    if state.get("error"):
        return "respond"
        
    route = state.get("route_to", "plan_node")
    if route not in ["hr_agent", "it_agent", "finance_agent", "plan_node", "respond"]:
        return "plan_node"
        
    return route


# ── Nodes 3a/3b/3c: Department context nodes ──────────────────────────────────

async def hr_agent_node(state: AgentState) -> AgentState:
    return {
        "agent_used": "hr_agent",
        "llm_model": settings.LLM_HR,
        "metadata": {**state.get("metadata", {}), "department": "hr"},
    }


async def it_agent_node(state: AgentState) -> AgentState:
    return {
        "agent_used": "it_agent",
        "llm_model": settings.LLM_IT,
        "metadata": {**state.get("metadata", {}), "department": "it"},
    }


async def finance_agent_node(state: AgentState) -> AgentState:
    return {
        "agent_used": "finance_agent",
        "llm_model": settings.LLM_FINANCE,
        "metadata": {**state.get("metadata", {}), "department": "finance"},
    }


# ── Node 4: GEPA — Plan ───────────────────────────────────────────────────────

PLAN_SYSTEM = """You are a planning agent for an enterprise AI system. Given a user request,
write a structured resolution plan BEFORE calling any tools.

Respond ONLY with JSON:
{
  "steps": ["step 1...", "step 2...", ...],
  "tools_needed": ["tool_name_1", "tool_name_2"],
  "reasoning": "why these steps in this order"
}

If a previous attempt failed, a critique will be provided. Adjust the plan accordingly."""


async def plan_node(state: AgentState) -> AgentState:
    llm = get_llm(state.get("agent_used", "hr").split("_")[0])

    messages = [SystemMessage(content=PLAN_SYSTEM)]

    # Include critique on retry
    if state.get("retry_critique"):
        messages.append(HumanMessage(
            content=f"Previous attempt failed. Critique:\n{state['retry_critique']}\n\n"
                    f"Original request: {state['raw_query']}"
        ))
    else:
        messages.append(HumanMessage(content=state["raw_query"]))

    result = await llm.ainvoke(messages)
    try:
        plan = json.loads(result.content)
        return {"plan": plan}
    except Exception:
        return {
            "plan": {
                "steps": ["Retrieve relevant information", "Generate response"],
                "tools_needed": [],
                "reasoning": "Fallback plan",
            }
        }


# ── Node 5: Execute (tools + RAG) ─────────────────────────────────────────────

EXECUTE_SYSTEM = """You are an enterprise AI assistant. Follow the plan and call the
appropriate tools to answer the user's request accurately. If the user is just greeting you, respond politely.

User context:
- Name: {user_name}
- Role: {user_role}
- Department ID: {department_id}

Current plan:
{plan}

Be factual, cite sources when using documents, and respect the user's role permissions."""


async def execute_node(state: AgentState) -> AgentState:
    from app.tools import get_tools_for_intent

    llm = get_llm(state.get("agent_used", "hr").split("_")[0])
    tools = get_tools_for_intent(state["intent"], state["user_role"])
    llm_with_tools = llm.bind_tools(tools) if tools else llm

    plan_text = "\n".join(
        f"{i+1}. {s}" for i, s in enumerate(state.get("plan", {}).get("steps", []))
    )

    messages = [
        SystemMessage(content=EXECUTE_SYSTEM.format(
            user_name=state["user_name"],
            user_role=state["user_role"].value,
            department_id=state.get("department_id", "N/A"),
            plan=plan_text,
        )),
        *state.get("messages", []),
        HumanMessage(content=state["raw_query"]),
    ]

    start = time.time()
    result = await llm_with_tools.ainvoke(messages)
    latency = int((time.time() - start) * 1000)

    tool_calls = []
    
    approval_required = False
    approval_entity_type = None
    approval_entity_id = None
    email_triggered = False
    email_recipients = []
    email_subject = None
    email_body = None

    if hasattr(result, "tool_calls") and result.tool_calls:
        for tc in result.tool_calls:
            tool_fn = next((t for t in tools if t.name == tc["name"]), None)
            if tool_fn:
                try:
                    tool_result = await tool_fn.ainvoke(tc["args"])
                    tool_calls.append({"name": tc["name"], "args": tc["args"], "result": tool_result})
                    
                    if isinstance(tool_result, dict):
                        if tool_result.get("approval_required"):
                            approval_required = True
                            if "leave_id" in tool_result:
                                approval_entity_type = "leave"
                                approval_entity_id = str(tool_result["leave_id"])
                            elif "ticket_id" in tool_result:
                                approval_entity_type = "it_action"
                                approval_entity_id = str(tool_result["ticket_id"])
                            elif "request_id" in tool_result:
                                approval_entity_type = "asset_request"
                                approval_entity_id = str(tool_result["request_id"])
                            elif "claim_id" in tool_result:
                                approval_entity_type = "reimbursement"
                                approval_entity_id = str(tool_result["claim_id"])
                                
                        if tool_result.get("email_triggered"):
                            email_triggered = True
                            email_recipients = tool_result.get("email_recipients", [])
                            email_subject = tool_result.get("email_subject")
                            email_body = tool_result.get("email_body")

                except RBACViolation as e:
                    return {"error": str(e), "response": str(e), "response_type": "error"}

    state_update = {
        "messages": [*state.get("messages", []), HumanMessage(content=state["raw_query"]), result],
        "tool_calls": tool_calls,
        "response": result.content if isinstance(result.content, str) else str(result.content),
        "latency_ms": latency,
    }

    if approval_required:
        state_update["approval_required"] = True
        state_update["approval_entity_type"] = approval_entity_type
        state_update["approval_entity_id"] = approval_entity_id
        
    if email_triggered:
        state_update["email_triggered"] = True
        state_update["email_recipients"] = email_recipients
        state_update["email_subject"] = email_subject
        state_update["email_body"] = email_body

    return state_update


# ── Node 6: GEPA — Evaluate ───────────────────────────────────────────────────

EVAL_SYSTEM = """You are a quality evaluator for an enterprise AI system.
Score the agent's response on four dimensions (0.0–1.0 each):
  - relevance: does the response directly address the user's query?
  - completeness: does it provide all needed information?
  - rbac_compliant: does it respect the user's role and not expose unauthorized data?
  - overall: weighted average

Respond ONLY with JSON:
{
  "score": <float>,
  "relevance": <float>,
  "completeness": <float>,
  "rbac_compliant": <bool>,
  "critique": "specific feedback if score < 0.80, empty string otherwise"
}"""


async def eval_node(state: AgentState) -> AgentState:
    if state.get("error"):
        return {"eval_score": {"score": 0.0, "relevance": 0.0, "completeness": 0.0,
                               "rbac_compliant": True, "critique": ""}}

    llm = get_llm("evaluator")
    result = await llm.ainvoke([
        SystemMessage(content=EVAL_SYSTEM),
        HumanMessage(content=f"Query: {state['raw_query']}\n\nResponse: {state['response']}\n\n"
                              f"User role: {state['user_role'].value}"),
    ])
    try:
        score_data: EvalScore = json.loads(result.content)
        return {"eval_score": score_data}
    except Exception:
        return {"eval_score": {"score": 1.0, "relevance": 1.0, "completeness": 1.0,
                               "rbac_compliant": True, "critique": ""}}


def route_after_eval(state: AgentState) -> Literal["plan_node", "human_in_loop"]:
    score = state.get("eval_score", {}).get("score", 1.0)
    retry_count = state.get("retry_count", 0)

    if score < settings.GEPA_EVAL_THRESHOLD and retry_count < settings.GEPA_MAX_RETRIES:
        return "plan_node"
    return "human_in_loop"


# ── Node 7: Human-in-loop ─────────────────────────────────────────────────────

async def human_in_loop_node(state: AgentState) -> AgentState:
    if not state.get("approval_required"):
        return {}

    decision_input = interrupt({
        "message": f"Approval required for {state.get('approval_entity_type')}",
        "entity_id": state.get("approval_entity_id"),
        "requested_by": state["user_name"],
        "request_summary": state["raw_query"],
    })

    return {
        "approval_decision": decision_input.get("decision"),
        "approval_note": decision_input.get("note"),
    }


# ── Node 8: Email notification ────────────────────────────────────────────────

async def email_notify_node(state: AgentState) -> AgentState:
    if not state.get("email_triggered"):
        return {}

    from app.tools.email_tools import send_email_via_power_automate
    await send_email_via_power_automate(
        recipients=state["email_recipients"],
        subject=state.get("email_subject", ""),
        body=state.get("email_body", ""),
    )
    return {}


# ── Node 9: Save memory ───────────────────────────────────────────────────────

async def save_memory_node(state: AgentState) -> AgentState:
    from app.database import AsyncSessionLocal
    from app.models import UserMemory
    from sqlalchemy.dialects.postgresql import insert

    async with AsyncSessionLocal() as db:
        stmt = insert(UserMemory).values(
            user_id=state["user_id"],
            memory_key="last_agent_used",
            memory_value={"agent": state.get("agent_used"), "intent": state["intent"]},
            source="inferred",
        ).on_conflict_do_update(
            index_elements=["user_id", "memory_key"],
            set_={"memory_value": {"agent": state.get("agent_used"), "intent": state["intent"]},
                  "updated_at": "now()"},
        )
        await db.execute(stmt)
        await db.commit()
    return {}


# ── Node 10: Final respond ────────────────────────────────────────────────────

async def respond_node(state: AgentState) -> AgentState:
    if state.get("response"):
        return {
            "messages": [
                *state.get("messages", []),
                AIMessage(content=state["response"]),
            ]
        }
    return {}


# ── Build the graph ───────────────────────────────────────────────────────────

def build_workflow() -> StateGraph:
    graph = StateGraph(AgentState)

    graph.add_node("intent_node",       intent_node)
    graph.add_node("role_check",        role_check_node)
    graph.add_node("hr_agent",          hr_agent_node)
    graph.add_node("it_agent",          it_agent_node)
    graph.add_node("finance_agent",     finance_agent_node)
    graph.add_node("plan_node",         plan_node)
    graph.add_node("execute_node",      execute_node)
    graph.add_node("eval_node",         eval_node)
    graph.add_node("human_in_loop",     human_in_loop_node)
    graph.add_node("email_notify",      email_notify_node)
    graph.add_node("save_memory",       save_memory_node)
    graph.add_node("respond",           respond_node)

    graph.set_entry_point("intent_node")

    graph.add_edge("intent_node", "role_check")
    
    graph.add_conditional_edges("role_check", route_after_role_check, {
        "hr_agent":      "hr_agent",
        "it_agent":      "it_agent",
        "finance_agent": "finance_agent",
        "plan_node":     "plan_node",
        "respond":       "respond",
    })

    for dept in ("hr_agent", "it_agent", "finance_agent"):
        graph.add_edge(dept, "plan_node")

    graph.add_edge("plan_node",    "execute_node")
    graph.add_edge("execute_node", "eval_node")

    graph.add_conditional_edges("eval_node", route_after_eval, {
        "plan_node":     "plan_node",
        "human_in_loop": "human_in_loop",
    })

    graph.add_edge("human_in_loop", "email_notify")
    graph.add_edge("email_notify",  "save_memory")
    graph.add_edge("save_memory",   "respond")
    graph.add_edge("respond",       END)

    checkpointer = MemorySaver()
    return graph.compile(checkpointer=checkpointer, interrupt_before=["human_in_loop"])


workflow = build_workflow()


async def run_workflow(user_ctx: dict, query: str, session_id: str | None = None) -> AgentState:
    sid = session_id or str(uuid.uuid4())
    state = initial_state(user_ctx, query, session_id=sid)

    config = {"configurable": {"thread_id": sid}}
    final_state = await workflow.ainvoke(state, config=config)
    return final_state
```

## app\graph\__init__.py

```python
# app/graph/__init__.py

```

## app\mcp\server.py

```python
"""
FastMCP Server
==============
Exposes all enterprise tools as MCP-compatible endpoints.
LangGraph agents call these tools through the MCP protocol.

Run standalone:  python -m app.mcp.server
Or mount on FastAPI: app.mount("/mcp", mcp_app)
"""
from __future__ import annotations

from datetime import date
from typing import Annotated

from fastmcp import FastMCP
from pydantic import BaseModel, Field

from app.config import settings

mcp = FastMCP(
    name="Enterprise AI Copilot Tools",
    version="1.0.0",
    instructions="Tools for HR, IT, and Finance operations. Always validate RBAC before calling.",
)


# ── Input schemas (Pydantic — FastMCP uses these for validation) ──────────────

class LeaveApplyInput(BaseModel):
    user_id:     str
    leave_type:  str   = Field(..., description="casual|sick|earned|maternity|paternity|bereavement")
    start_date:  date
    end_date:    date
    reason:      str   = ""
    is_half_day: bool  = False
    half_day_slot: str = Field("", description="morning|afternoon — only if is_half_day=True")


class LeaveBalanceInput(BaseModel):
    user_id: str
    year:    int = Field(default_factory=lambda: date.today().year)


class TicketCreateInput(BaseModel):
    user_id:     str
    category:    str   = Field(..., description="laptop|vpn|email|printer|network|software_install|hardware|access|other")
    subject:     str
    description: str
    priority:    str   = "medium"


class AssetRequestInput(BaseModel):
    user_id:       str
    asset_type:    str = Field(..., description="laptop|monitor|keyboard|mouse|vpn_token|software_license")
    justification: str


class PayslipFetchInput(BaseModel):
    user_id:   str
    pay_month: str = Field(..., description="YYYY-MM (e.g. 2024-03)")


class ReimbursementSubmitInput(BaseModel):
    user_id:      str
    category:     str   = Field(..., description="travel|internet|food|client_meeting|training")
    amount:       float
    currency:     str   = "INR"
    description:  str
    expense_date: date
    receipt_url:  str   = ""


class ApprovalInput(BaseModel):
    approval_id: str
    decision:    str  = Field(..., description="approved|rejected")
    note:        str  = ""


# ── HR Tools ──────────────────────────────────────────────────────────────────

@mcp.tool(description="Apply for leave. Validates dates, checks overlaps and holiday calendar.")
async def apply_leave(data: LeaveApplyInput) -> dict:
    from app.database import AsyncSessionLocal
    from app.models import HolidayCalendar, LeaveBalance, LeaveRequest, LeaveType, User
    from app.tools.email_tools import leave_request_email
    from sqlalchemy import and_, select
    from datetime import timedelta

    async with AsyncSessionLocal() as db:
        # ── NEW: Fetch User & Manager for Email Routing ──
        user = await db.get(User, data.user_id)
        if not user:
            return {"success": False, "error": "User not found."}
        
        manager = await db.get(User, user.manager_id) if user.manager_id else None

        # 1. Validate leave type
        try:
            ltype = LeaveType(data.leave_type)
        except ValueError:
            return {"success": False, "error": f"Invalid leave type: {data.leave_type}"}

        # 2. Check date validity
        if data.start_date < date.today():
            return {"success": False, "error": "Cannot apply leave for past dates."}
        if data.end_date < data.start_date:
            return {"success": False, "error": "end_date must be ≥ start_date."}

        # 3. Check overlapping leaves
        overlap = await db.scalar(
            select(LeaveRequest).where(
                and_(
                    LeaveRequest.user_id == data.user_id,
                    LeaveRequest.status.in_(["pending", "approved"]),
                    LeaveRequest.start_date <= data.end_date,
                    LeaveRequest.end_date   >= data.start_date,
                )
            )
        )
        if overlap:
            return {"success": False, "error": f"Overlapping leave exists ({overlap.id})."}

        # 4. Count business days (exclude weekends + holidays)
        holidays = set(
            row.holiday_date for row in (
                await db.execute(
                    select(HolidayCalendar.holiday_date).where(
                        HolidayCalendar.holiday_date.between(data.start_date, data.end_date)
                    )
                )
            ).scalars()
        )
        bdays = 0
        cur = data.start_date
        while cur <= data.end_date:
            if cur.weekday() < 5 and cur not in holidays:  # Mon–Fri, non-holiday
                bdays += 1
            cur += timedelta(days=1)
        if data.is_half_day:
            bdays = 0.5

        # 5. Check leave balance
        balance = await db.scalar(
            select(LeaveBalance).where(
                and_(
                    LeaveBalance.user_id == data.user_id,
                    LeaveBalance.year == data.start_date.year,
                    LeaveBalance.leave_type == ltype,
                )
            )
        )
        if not balance or balance.available_days < bdays:
            return {"success": False, "error": f"Insufficient {ltype.value} leave balance."}

        # 6. Create leave request
        leave = LeaveRequest(
            user_id=data.user_id,
            leave_type=ltype,
            start_date=data.start_date,
            end_date=data.end_date,
            business_days=bdays,
            reason=data.reason,
            is_half_day=data.is_half_day,
            half_day_slot=data.half_day_slot or None,
        )
        db.add(leave)
        balance.pending_days += bdays
        await db.commit()
        await db.refresh(leave)

    # ── NEW: Generate Email Payload ──
    email_data = {}
    if manager:
        # Generate an approval URL (in reality, this would point to your frontend UI)
        approve_url = f"https://copilot.internal/approve?leave_id={leave.id}"
        email_data = leave_request_email(
            employee_name=user.full_name,
            manager_email=manager.email,
            leave_type=ltype.value,
            start=str(data.start_date),
            end=str(data.end_date),
            days=float(bdays),
            leave_id=str(leave.id),
            approve_url=approve_url
        )

    return {
        "success": True,
        "leave_id": str(leave.id),
        "business_days": bdays,
        "status": "pending",
        "message": f"Leave applied successfully ({bdays} day(s)). Pending manager approval.",
        "approval_required": True,
        "email_triggered": bool(manager),
        "email_recipients": email_data.get("recipients", []),
        "email_subject": email_data.get("subject", ""),
        "email_body": email_data.get("body", ""),
    }


@mcp.tool(description="Get leave balance for a user for the current or specified year.")
async def get_leave_balance(data: LeaveBalanceInput) -> dict:
    from app.database import AsyncSessionLocal
    from app.models import LeaveBalance
    from sqlalchemy import select

    async with AsyncSessionLocal() as db:
        rows = (await db.execute(
            select(LeaveBalance).where(
                LeaveBalance.user_id == data.user_id,
                LeaveBalance.year == data.year,
            )
        )).scalars().all()

    return {
        "user_id": data.user_id,
        "year": data.year,
        "balances": [
            {
                "type": row.leave_type.value,
                "entitled": float(row.entitled_days),
                "used": float(row.used_days),
                "pending": float(row.pending_days),
                "available": float(row.available_days),
            }
            for row in rows
        ],
    }


# ── IT Tools ──────────────────────────────────────────────────────────────────

@mcp.tool(description="Create an IT support ticket. Checks for duplicates and known issues first.")
async def create_ticket(data: TicketCreateInput) -> dict:
    from app.database import AsyncSessionLocal
    from app.models import ITTicket, KnownIssue, MaintenanceSchedule, TicketCategory, TicketPriority
    from sqlalchemy import and_, select
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc)

    async with AsyncSessionLocal() as db:
        # 1. Check active maintenance
        maint = await db.scalar(
            select(MaintenanceSchedule).where(
                and_(
                    MaintenanceSchedule.starts_at <= now,
                    MaintenanceSchedule.ends_at   >= now,
                    MaintenanceSchedule.affected_system.ilike(f"%{data.category}%"),
                )
            )
        )
        if maint:
            return {
                "success": False,
                "info": f"Planned maintenance in progress: '{maint.title}'. Expected end: {maint.ends_at.isoformat()}",
                "ticket_created": False,
            }

        # 2. Check known issues
        known = await db.scalar(
            select(KnownIssue).where(
                and_(
                    KnownIssue.category == data.category,
                    KnownIssue.is_active.is_(True),
                )
            )
        )
        if known:
            return {
                "success": True,
                "info": f"Known issue: {known.title}. Workaround: {known.workaround or 'None available'}",
                "ticket_created": False,
                "message": "A known issue matches your request. No ticket raised; see workaround above.",
            }

        # 3. Check duplicate open ticket
        dupe = await db.scalar(
            select(ITTicket).where(
                and_(
                    ITTicket.user_id == data.user_id,
                    ITTicket.category == data.category,
                    ITTicket.status.in_(["open", "in_progress"]),
                )
            )
        )
        if dupe:
            return {
                "success": True,
                "info": f"You already have an open ticket ({dupe.ticket_no}) for '{data.category}'.",
                "ticket_id": str(dupe.id),
                "ticket_no": dupe.ticket_no,
                "ticket_created": False,
            }

        # 4. Create ticket
        ticket = ITTicket(
            user_id=data.user_id,
            category=TicketCategory(data.category),
            subject=data.subject,
            description=data.description,
            priority=TicketPriority(data.priority),
        )
        db.add(ticket)
        await db.commit()
        await db.refresh(ticket)

    return {
        "success": True,
        "ticket_id": str(ticket.id),
        "ticket_no": ticket.ticket_no,
        "priority": ticket.priority.value,
        "status": "open",
        "ticket_created": True,
        "message": f"Ticket {ticket.ticket_no} created. You'll receive email confirmation shortly.",
    }


@mcp.tool(description="Check inventory and submit an asset request (laptop, monitor, etc).")
async def request_asset(data: AssetRequestInput) -> dict:
    from app.database import AsyncSessionLocal
    from app.models import AssetRequest, AssetType, ITInventory
    from sqlalchemy import and_, select

    async with AsyncSessionLocal() as db:
        # Check availability
        available = await db.scalar(
            select(ITInventory).where(
                and_(
                    ITInventory.asset_type == data.asset_type,
                    ITInventory.status == "available",
                )
            )
        )

        req = AssetRequest(
            user_id=data.user_id,
            asset_type=AssetType(data.asset_type),
            justification=data.justification,
        )
        db.add(req)
        await db.commit()
        await db.refresh(req)

    return {
        "success": True,
        "request_id": str(req.id),
        "asset_type": data.asset_type,
        "inventory_available": available is not None,
        "status": "pending",
        "approval_required": True,
        "message": "Asset request submitted. Manager approval required.",
    }


# ── Finance Tools ─────────────────────────────────────────────────────────────

@mcp.tool(description="Fetch payslip details for a specific month (YYYY-MM).")
async def fetch_payslip(data: PayslipFetchInput) -> dict:
    from app.database import AsyncSessionLocal
    from app.models import PayrollRecord
    from sqlalchemy import select
    from datetime import date as dt

    year, month = map(int, data.pay_month.split("-"))
    pay_month_date = dt(year, month, 1)

    async with AsyncSessionLocal() as db:
        record = await db.scalar(
            select(PayrollRecord).where(
                PayrollRecord.user_id == data.user_id,
                PayrollRecord.pay_month == pay_month_date,
            )
        )

    if not record:
        return {"success": False, "error": f"No payslip found for {data.pay_month}."}

    return {
        "success": True,
        "pay_month": data.pay_month,
        "gross_salary": float(record.gross_salary),
        "net_salary": float(record.net_salary),
        "breakdown": {
            "basic": float(record.basic),
            "hra": float(record.hra),
            "allowances": float(record.allowances),
        },
        "deductions": {
            "pf_employee": float(record.pf_employee),
            "tds": float(record.tds),
            "professional_tax": float(record.professional_tax),
            "other": float(record.other_deductions),
        },
        "payslip_url": record.payslip_url,
    }


@mcp.tool(description="Submit a reimbursement claim with expense details and receipt URL.")
async def submit_reimbursement(data: ReimbursementSubmitInput) -> dict:
    from app.database import AsyncSessionLocal
    from app.models import Reimbursement, ReimbursementCategory
    from datetime import datetime, timezone

    async with AsyncSessionLocal() as db:
        claim = Reimbursement(
            user_id=data.user_id,
            category=ReimbursementCategory(data.category),
            amount=data.amount,
            currency=data.currency,
            description=data.description,
            expense_date=data.expense_date,
            receipt_url=data.receipt_url or None,
            status="submitted",
            submitted_at=datetime.now(timezone.utc),
        )
        db.add(claim)
        await db.commit()
        await db.refresh(claim)

    return {
        "success": True,
        "claim_id": str(claim.id),
        "claim_no": claim.claim_no,
        "amount": float(claim.amount),
        "currency": claim.currency,
        "status": "submitted",
        "approval_required": True,
        "message": f"Claim {claim.claim_no} submitted for ₹{claim.amount:.2f}. Finance team will review.",
    }


# ── Approval Tool (cross-department) ──────────────────────────────────────────

@mcp.tool(description="Record an approval decision for a leave, asset request, or reimbursement.")
async def record_approval(data: ApprovalInput) -> dict:
    from app.database import AsyncSessionLocal
    from app.models import Approval, ApprovalDecision
    from sqlalchemy import select
    from datetime import datetime, timezone

    async with AsyncSessionLocal() as db:
        approval = await db.get(Approval, data.approval_id)
        if not approval:
            return {"success": False, "error": "Approval record not found."}
        if approval.decision != ApprovalDecision.pending:
            return {"success": False, "error": f"Already decided: {approval.decision.value}"}

        approval.decision = ApprovalDecision(data.decision)
        approval.note = data.note
        approval.decided_at = datetime.now(timezone.utc)
        await db.commit()

    return {
        "success": True,
        "approval_id": data.approval_id,
        "decision": data.decision,
        "message": f"Approval {data.decision} recorded.",
    }


# ── Inventory status (IT team only) ───────────────────────────────────────────

@mcp.tool(description="View current IT inventory status and available assets. IT team only.")
async def inventory_status(asset_type: str = "") -> dict:
    from app.database import AsyncSessionLocal
    from app.models import ITInventory
    from sqlalchemy import select, func

    async with AsyncSessionLocal() as db:
        q = select(
            ITInventory.asset_type,
            ITInventory.status,
            func.count().label("count"),
        ).group_by(ITInventory.asset_type, ITInventory.status)

        if asset_type:
            q = q.where(ITInventory.asset_type == asset_type)

        rows = (await db.execute(q)).all()

    summary: dict = {}
    for row in rows:
        atype = row.asset_type.value
        summary.setdefault(atype, {})[row.status.value] = row.count

    return {"inventory": summary}


# ── Run MCP server standalone ─────────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run(host=settings.MCP_HOST, port=settings.MCP_PORT, transport="sse")
```

## app\mcp\__init__.py

```python
# app/mcp/__init__.py

```

## app\middleware\logging.py

```python
"""
Structured Request Logging Middleware
=====================================
Intercepts every HTTP request and emits a structured JSON log line with:
  - method, path, status_code, duration_ms
  - request_id (correlation ID for distributed tracing)
  - client IP

**Why structlog?**
  Standard Python `logging` emits flat strings.  structlog produces key-value
  JSON that is trivially parseable by log aggregation tools (Datadog, Loki,
  CloudWatch, ELK).  In production, structured logs let you filter dashboards
  by `status_code >= 500` or alert on `p99(duration_ms) > 800` without regex.

**Why BaseHTTPMiddleware?**
  It wraps the ASGI lifecycle at a high level, giving us access to the
  full `Request` *and* `Response` objects.  This is the simplest way to
  measure latency across all routes (including ones we don't own, like /docs).

Usage:
    # In app/main.py, *after* CORSMiddleware:
    from app.middleware.logging import RequestLoggingMiddleware
    app.add_middleware(RequestLoggingMiddleware)
"""
from __future__ import annotations

import time
import uuid

import structlog
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

# ── Configure structlog (once at module load) ─────────────────────────────────
# This pipeline turns every log event into a JSON dict with ISO-8601 timestamps.

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,          # pull vars set in other coroutines
        structlog.processors.TimeStamper(fmt="iso"),      # "timestamp": "2026-05-05T12:00:00Z"
        structlog.processors.add_log_level,               # "level": "info"
        structlog.processors.StackInfoRenderer(),         # add stack trace if requested
        structlog.processors.format_exc_info,             # format exceptions nicely
        structlog.processors.UnicodeDecoder(),            # bytes → str
        structlog.processors.JSONRenderer(),              # final output as JSON
    ],
    wrapper_class=structlog.make_filtering_bound_logger(0),  # allow all levels
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),           # writes to stdout
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger("request")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Measures wall-clock latency of every request and emits a single
    structured log line after the response is sent.

    Key design decisions:
      1. We generate a `request_id` (UUID4) and attach it as a response
         header (`X-Request-ID`).  Downstream services can propagate this
         for distributed tracing.
      2. We catch *all* unhandled exceptions so that 500s are still logged
         with the traceback attached — then we re-raise so FastAPI's
         default exception handler can return a proper error response.
      3. Health-check endpoints (/health) are logged at DEBUG to avoid
         flooding logs in environments with aggressive liveness probes.
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # ── 1. Generate correlation ID ────────────────────────────────────
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

        # ── 2. Start the clock ────────────────────────────────────────────
        start_time = time.perf_counter()

        # Bind request-scoped fields into structlog context so that any log
        # emitted inside the endpoint handler also carries them.
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            client_ip=request.client.host if request.client else "unknown",
        )

        status_code = 500  # default in case call_next explodes
        try:
            response = await call_next(request)
            status_code = response.status_code

            # Attach correlation header to response
            response.headers["X-Request-ID"] = request_id
            return response

        except Exception as exc:
            # ── 3. Log the 500 with full traceback ────────────────────────
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            logger.error(
                "unhandled_exception",
                status_code=500,
                duration_ms=duration_ms,
                exc_info=exc,
            )
            raise  # re-raise so FastAPI returns its standard 500 response

        finally:
            # ── 4. Emit the structured log line ───────────────────────────
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

            # Downgrade health-check spam to DEBUG
            log_method = logger.debug if request.url.path == "/health" else logger.info
            log_method(
                "request_completed",
                status_code=status_code,
                duration_ms=duration_ms,
            )

```

## app\middleware\rate_limit.py

```python
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import redis.asyncio as redis

from app.config import settings

# Global Redis Client
redis_client: redis.Redis | None = None

async def setup_redis():
    """Initialize Redis connection pool and verify connectivity."""
    global redis_client
    redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    # Eagerly verify connectivity so startup logs a clear warning if Redis is down
    await redis_client.ping()

async def close_redis():
    """Close Redis connection."""
    global redis_client
    if redis_client:
        await redis_client.aclose()

# Atomic Token Bucket Lua Script for Redis
TOKEN_BUCKET_LUA = """
local key = KEYS[1]
local rate = tonumber(ARGV[1])      -- tokens added per minute
local capacity = tonumber(ARGV[2])  -- max bucket size
local now = tonumber(ARGV[3])       -- current timestamp

local info = redis.call('HMGET', key, 'tokens', 'last_refresh')
local tokens = tonumber(info[1])
local last_refresh = tonumber(info[2])

-- Initialize if it's a new key
if tokens == nil then
    tokens = capacity
    last_refresh = now
end

-- Calculate token refill based on time passed
local time_passed = math.max(0, now - last_refresh)
tokens = math.min(capacity, tokens + time_passed * (rate / 60))

-- Check if we have enough tokens (1 request = 1 token)
if tokens >= 1 then
    tokens = tokens - 1
    redis.call('HMSET', key, 'tokens', tokens, 'last_refresh', now)
    redis.call('EXPIRE', key, 120) -- Keep alive for 2 mins
    return 1 -- Allowed
else
    redis.call('HMSET', key, 'tokens', tokens, 'last_refresh', now)
    redis.call('EXPIRE', key, 120)
    return 0 -- Rate limited
end
"""

class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if not redis_client:
            # Fail-open if Redis is down
            return await call_next(request)

        # Identify user by IP (or extract from Authorization token if needed)
        client_id = request.client.host if request.client else "unknown"
        bucket_key = f"rate_limit:{client_id}"
        
        try:
            # Execute the Lua script
            is_allowed = await redis_client.eval(
                TOKEN_BUCKET_LUA, 
                1, # Number of keys
                bucket_key, 
                settings.RATE_LIMIT_REQUESTS_PER_MINUTE, # Rate
                settings.RATE_LIMIT_REQUESTS_PER_MINUTE, # Capacity
                time.time() # Now
            )
            
            if not is_allowed:
                return JSONResponse(
                    status_code=429,
                    content={"error": "Too Many Requests. Rate limit exceeded."},
                    headers={"Retry-After": "60"}
                )
                
        except Exception:
            # If Redis errors out, log it but don't block the user (fail-open)
            pass

        return await call_next(request)
```

## app\middleware\rbac.py

```python
"""
RBAC Middleware
==============
Two-layer enforcement:
  Layer 1 — FastAPI dependency (HTTP): validates JWT and injects current_user
  Layer 2 — Agent-level guard (LangGraph): checked inside tool/retrieval nodes

Usage in FastAPI routes:
    @router.get("/leaves")
    async def list_leaves(user = Depends(require_permission("hr:leave:view_all"))):
        ...

Usage in LangGraph tool nodes:
    from app.middleware.rbac import rbac_guard
    rbac_guard(state["user_role"], "it:ticket:view_all")
"""
from __future__ import annotations

import time
from datetime import UTC, datetime, timedelta
from functools import lru_cache
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models import Permission, RolePermission, User, UserRole

# ── Static role → permission map (cached at startup) ─────────────────────────
# Loaded from DB once via load_role_permissions(); used for fast in-memory checks.
ROLE_PERMISSIONS: dict[UserRole, set[str]] = {}


async def load_role_permissions(db: AsyncSession) -> None:
    """Call once at FastAPI startup to cache all role permissions."""
    result = await db.execute(
        select(RolePermission.role, Permission.code)
        .join(Permission, RolePermission.perm_id == Permission.id)
    )
    for role, code in result:
        ROLE_PERMISSIONS.setdefault(role, set()).add(code)


# ── JWT helpers ───────────────────────────────────────────────────────────────

def create_access_token(user_id: str, role: str, email: str) -> str:
    expire = datetime.now(UTC) + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": user_id,
        "role": role,
        "email": email,
        "exp": expire,
        "iat": datetime.now(UTC),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


# ── FastAPI dependencies ───────────────────────────────────────────────────────

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    db: AsyncSession = Depends(get_db),
) -> User:
    """Decode JWT, load user from DB, verify active status. Supports X-Mock-Role in DEBUG mode."""
    # 1. Check for mock header in DEBUG mode
    if settings.DEBUG and "x-mock-role" in request.headers:
        role_str = request.headers.get("x-mock-role", "employee")
        try:
            role_enum = UserRole(role_str)
        except ValueError:
            role_enum = UserRole.employee
            
        import uuid
        from sqlalchemy.orm import make_transient

        mock_user = User(
            id=uuid.UUID("11111111-1111-1111-1111-111111111111") if role_enum == UserRole.manager else uuid.UUID("22222222-2222-2222-2222-222222222222"),
            employee_id=f"MOCK-{role_enum.value.upper()[:3]}-001",
            email=f"mock_{role_enum.value}@company.com",
            full_name=f"Mock {role_enum.value.capitalize()}",
            password_hash="mock_not_a_real_hash",
            role=role_enum,
            department_id=None,
            manager_id=None,
            is_active=True,
            preferred_lang="en"
        )
        # Detach from any SA session so it's never accidentally flushed to DB
        make_transient(mock_user)
        return mock_user

    # 2. Normal JWT flow
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
        
    payload = decode_access_token(credentials.credentials)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Bad token payload")

    user = await db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")
    return user


def require_permission(perm_code: str):
    """FastAPI dependency factory — raises 403 if user lacks the permission."""
    async def _check(user: User = Depends(get_current_user)) -> User:
        if not _has_permission(user.role, perm_code):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: '{perm_code}' required",
            )
        return user
    return _check


def require_role(*roles: UserRole):
    """FastAPI dependency — requires one of the given roles."""
    async def _check(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role required: one of {[r.value for r in roles]}",
            )
        return user
    return _check


# ── Agent-level guard (LangGraph nodes / tools) ───────────────────────────────

class RBACViolation(PermissionError):
    """Raised inside LangGraph tool nodes when RBAC check fails."""
    def __init__(self, role: UserRole, perm_code: str):
        super().__init__(f"Role '{role.value}' lacks permission '{perm_code}'")
        self.role = role
        self.perm_code = perm_code


def rbac_guard(role: UserRole, perm_code: str) -> None:
    """
    Raise RBACViolation if the role lacks the permission.
    Use this inside LangGraph tool nodes (not FastAPI routes).

    Example:
        async def apply_leave_tool(state: AgentState) -> AgentState:
            rbac_guard(state["user_role"], "hr:leave:apply")
            ...
    """
    if not _has_permission(role, perm_code):
        raise RBACViolation(role, perm_code)


def _has_permission(role: UserRole, perm_code: str) -> bool:
    """Check against in-memory ROLE_PERMISSIONS map. Admin always passes."""
    if role == UserRole.admin:
        return True
    return perm_code in ROLE_PERMISSIONS.get(role, set())


# ── Rate limiting middleware ───────────────────────────────────────────────────

class RateLimitMiddleware:
    """
    Simple in-process token bucket per user (not cluster-safe).
    For production, replace with Redis-backed sliding window.
    """

    def __init__(self, requests_per_minute: int = 60):
        self.rpm = requests_per_minute
        self._buckets: dict[str, tuple[int, float]] = {}  # user_id → (tokens, last_refill)

    def check(self, user_id: str) -> None:
        now = time.time()
        tokens, last_refill = self._buckets.get(user_id, (self.rpm, now))

        # Refill tokens proportional to elapsed time
        elapsed = now - last_refill
        tokens = min(self.rpm, tokens + elapsed * (self.rpm / 60))

        if tokens < 1:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please slow down.",
                headers={"Retry-After": "5"},
            )

        self._buckets[user_id] = (tokens - 1, now)


rate_limiter = RateLimitMiddleware(settings.RATE_LIMIT_REQUESTS_PER_MINUTE)


# ── Request enrichment (adds user context to every request) ──────────────────

async def enrich_request(request: Request, user: User = Depends(get_current_user)) -> dict:
    """
    Returns enriched context dict injected into the agent state.
    Attach via Depends() on chat endpoints.
    """
    rate_limiter.check(str(user.id))
    return {
        "user_id": str(user.id),
        "user_email": user.email,
        "user_name": user.full_name,
        "user_role": user.role,
        "department_id": str(user.department_id) if user.department_id else None,
        "manager_id": str(user.manager_id) if user.manager_id else None,
        "preferred_lang": user.preferred_lang,
    }
```

## app\middleware\__init__.py

```python
from .logging import RequestLoggingMiddleware
from .rate_limit import RateLimitMiddleware, setup_redis, close_redis
from .rbac import (
    RBACViolation,
    enrich_request,
    load_role_permissions,
    rbac_guard,
    require_permission,
    require_role,
)

__all__ = [
    "RequestLoggingMiddleware",
    "RateLimitMiddleware",
    "setup_redis",
    "close_redis",
    "RBACViolation",
    "enrich_request",
    "load_role_permissions",
    "rbac_guard",
    "require_permission",
    "require_role",
]
```

## app\models\__init__.py

```python
"""
SQLAlchemy ORM models — mirrors schema.sql exactly.
Import everything from here: `from app.models import User, LeaveRequest, ...`
"""
from __future__ import annotations

import enum
import uuid
from datetime import date, datetime
from typing import Any

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    ARRAY, Boolean, CheckConstraint, Column, Date, DateTime,
    Enum, ForeignKey, Index, Integer, Numeric, String, Text,
    UniqueConstraint, func,
)
from sqlalchemy.dialects.postgresql import INET, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


# ── Enums (match PostgreSQL enums in schema.sql) ──────────────────────────────

class UserRole(str, enum.Enum):
    employee     = "employee"
    manager      = "manager"
    hr_team      = "hr_team"
    it_team      = "it_team"
    finance_team = "finance_team"
    admin        = "admin"

class LeaveStatus(str, enum.Enum):
    pending   = "pending"
    approved  = "approved"
    rejected  = "rejected"
    cancelled = "cancelled"

class LeaveType(str, enum.Enum):
    casual        = "casual"
    sick          = "sick"
    earned        = "earned"
    maternity     = "maternity"
    paternity     = "paternity"
    bereavement   = "bereavement"
    compensatory  = "compensatory"
    unpaid        = "unpaid"

class TicketStatus(str, enum.Enum):
    open        = "open"
    in_progress = "in_progress"
    on_hold     = "on_hold"
    resolved    = "resolved"
    closed      = "closed"

class TicketPriority(str, enum.Enum):
    low      = "low"
    medium   = "medium"
    high     = "high"
    critical = "critical"

class TicketCategory(str, enum.Enum):
    laptop           = "laptop"
    vpn              = "vpn"
    email            = "email"
    printer          = "printer"
    network          = "network"
    software_install = "software_install"
    hardware         = "hardware"
    access           = "access"
    other            = "other"

class AssetStatus(str, enum.Enum):
    available = "available"
    assigned  = "assigned"
    in_repair = "in_repair"
    retired   = "retired"
    lost      = "lost"

class AssetType(str, enum.Enum):
    laptop           = "laptop"
    monitor          = "monitor"
    keyboard         = "keyboard"
    mouse            = "mouse"
    vpn_token        = "vpn_token"
    software_license = "software_license"
    headset          = "headset"
    docking_station  = "docking_station"
    other            = "other"

class RequestStatus(str, enum.Enum):
    pending          = "pending"
    manager_approved = "manager_approved"
    it_approved      = "it_approved"
    rejected         = "rejected"
    fulfilled        = "fulfilled"
    cancelled        = "cancelled"

class ReimbursementCategory(str, enum.Enum):
    travel          = "travel"
    internet        = "internet"
    food            = "food"
    client_meeting  = "client_meeting"
    training        = "training"
    office_supplies = "office_supplies"
    other           = "other"

class ReimbursementStatus(str, enum.Enum):
    draft        = "draft"
    submitted    = "submitted"
    under_review = "under_review"
    approved     = "approved"
    rejected     = "rejected"
    paid         = "paid"

class ApprovalEntity(str, enum.Enum):
    leave           = "leave"
    asset_request   = "asset_request"
    reimbursement   = "reimbursement"
    it_action       = "it_action"

class ApprovalDecision(str, enum.Enum):
    pending   = "pending"
    approved  = "approved"
    rejected  = "rejected"
    escalated = "escalated"

class DocDepartment(str, enum.Enum):
    hr      = "hr"
    it      = "it"
    finance = "finance"
    general = "general"


# ── Mixins ────────────────────────────────────────────────────────────────────

class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(),
        onupdate=func.now(), nullable=False
    )


# ── Core models ───────────────────────────────────────────────────────────────

class Department(TimestampMixin, Base):
    __tablename__ = "departments"

    id:        Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name:      Mapped[str]       = mapped_column(String(100), unique=True, nullable=False)
    code:      Mapped[str]       = mapped_column(String(20), unique=True, nullable=False)
    head_id:   Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", use_alter=True))
    is_active: Mapped[bool]      = mapped_column(Boolean, default=True, nullable=False)

    users: Mapped[list["User"]] = relationship("User", back_populates="department",
                                               foreign_keys="User.department_id")


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id:            Mapped[uuid.UUID]  = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id:   Mapped[str]        = mapped_column(String(20), unique=True, nullable=False)
    email:         Mapped[str]        = mapped_column(String(255), unique=True, nullable=False)
    full_name:     Mapped[str]        = mapped_column(String(200), nullable=False)
    password_hash: Mapped[str]        = mapped_column(Text, nullable=False)
    role:          Mapped[UserRole]   = mapped_column(Enum(UserRole, name="user_role"), default=UserRole.employee, nullable=False)
    department_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("departments.id"))
    manager_id:    Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    designation:   Mapped[str | None] = mapped_column(String(150))
    date_of_joining: Mapped[date | None] = mapped_column(Date)
    is_active:     Mapped[bool]       = mapped_column(Boolean, default=True, nullable=False)
    preferred_lang: Mapped[str]       = mapped_column(String(10), default="en", nullable=False)

    # Relationships
    department: Mapped["Department | None"] = relationship(
        "Department", back_populates="users", foreign_keys=[department_id]
    )
    manager:    Mapped["User | None"]       = relationship("User", remote_side="User.id",
                                                           foreign_keys=[manager_id])
    leave_requests:  Mapped[list["LeaveRequest"]]  = relationship(back_populates="user", foreign_keys="LeaveRequest.user_id")
    tickets:         Mapped[list["ITTicket"]]       = relationship(back_populates="user",
                                                                   foreign_keys="ITTicket.user_id")
    asset_requests:  Mapped[list["AssetRequest"]]  = relationship(back_populates="user", foreign_keys="AssetRequest.user_id")
    reimbursements:  Mapped[list["Reimbursement"]] = relationship(back_populates="user", foreign_keys="Reimbursement.user_id")
    memory_entries:  Mapped[list["UserMemory"]]    = relationship(back_populates="user")

    def has_permission(self, perm_code: str) -> bool:
        """Quick check — call after loading role_permissions into session context."""
        from app.middleware.rbac import ROLE_PERMISSIONS
        return perm_code in ROLE_PERMISSIONS.get(self.role, set())


class Permission(Base):
    __tablename__ = "permissions"

    id:          Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code:        Mapped[str]       = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    module:      Mapped[str]       = mapped_column(String(50), nullable=False)


class RolePermission(Base):
    __tablename__ = "role_permissions"

    role:    Mapped[UserRole]  = mapped_column(Enum(UserRole, name="user_role"), primary_key=True)
    perm_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),
                                               ForeignKey("permissions.id", ondelete="CASCADE"),
                                               primary_key=True)


# ── HR Module ─────────────────────────────────────────────────────────────────

class LeaveBalance(Base):
    __tablename__ = "leave_balances"
    __table_args__ = (UniqueConstraint("user_id", "year", "leave_type"),)

    id:            Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id:       Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    year:          Mapped[int]
    leave_type:    Mapped[LeaveType] = mapped_column(Enum(LeaveType, name="leave_type"), nullable=False)
    entitled_days: Mapped[float]     = mapped_column(Numeric(5, 1), default=0)
    used_days:     Mapped[float]     = mapped_column(Numeric(5, 1), default=0)
    pending_days:  Mapped[float]     = mapped_column(Numeric(5, 1), default=0)
    carried_over:  Mapped[float]     = mapped_column(Numeric(5, 1), default=0)
    updated_at:    Mapped[datetime]  = mapped_column(DateTime(timezone=True), server_default=func.now())

    @property
    def available_days(self) -> float:
        return self.entitled_days + self.carried_over - self.used_days - self.pending_days


class LeaveRequest(TimestampMixin, Base):
    __tablename__ = "leave_requests"
    __table_args__ = (
        CheckConstraint("end_date >= start_date", name="valid_dates"),
        CheckConstraint("business_days > 0", name="valid_business_days"),
    )

    id:            Mapped[uuid.UUID]    = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id:       Mapped[uuid.UUID]    = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    leave_type:    Mapped[LeaveType]    = mapped_column(Enum(LeaveType, name="leave_type"), nullable=False)
    start_date:    Mapped[date]         = mapped_column(Date, nullable=False)
    end_date:      Mapped[date]         = mapped_column(Date, nullable=False)
    business_days: Mapped[float]        = mapped_column(Numeric(4, 1), nullable=False)
    reason:        Mapped[str | None]   = mapped_column(Text)
    status:        Mapped[LeaveStatus]  = mapped_column(Enum(LeaveStatus, name="leave_status"), default=LeaveStatus.pending)
    applied_at:    Mapped[datetime]     = mapped_column(DateTime(timezone=True), server_default=func.now())
    reviewed_by:   Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    reviewed_at:   Mapped[datetime | None]  = mapped_column(DateTime(timezone=True))
    reviewer_note: Mapped[str | None]   = mapped_column(Text)
    is_half_day:   Mapped[bool]         = mapped_column(Boolean, default=False)
    half_day_slot: Mapped[str | None]   = mapped_column(String(10))

    user: Mapped["User"] = relationship(back_populates="leave_requests", foreign_keys=[user_id])


class HolidayCalendar(Base):
    __tablename__ = "holiday_calendar"

    id:           Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    holiday_date: Mapped[date]      = mapped_column(Date, nullable=False)
    name:         Mapped[str]       = mapped_column(String(200), nullable=False)
    is_optional:  Mapped[bool]      = mapped_column(Boolean, default=False)


# ── IT Module ─────────────────────────────────────────────────────────────────

class ITTicket(TimestampMixin, Base):
    __tablename__ = "it_tickets"

    id:             Mapped[uuid.UUID]      = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticket_no:      Mapped[str]            = mapped_column(String(20), unique=True, nullable=False)
    user_id:        Mapped[uuid.UUID]      = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    category:       Mapped[TicketCategory] = mapped_column(Enum(TicketCategory, name="ticket_category"), nullable=False)
    subject:        Mapped[str]            = mapped_column(String(500), nullable=False)
    description:    Mapped[str]            = mapped_column(Text, nullable=False)
    priority:       Mapped[TicketPriority] = mapped_column(Enum(TicketPriority, name="ticket_priority"), default=TicketPriority.medium)
    status:         Mapped[TicketStatus]   = mapped_column(Enum(TicketStatus, name="ticket_status"), default=TicketStatus.open)
    assigned_to:    Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    parent_ticket:  Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("it_tickets.id"))
    resolution:     Mapped[str | None]     = mapped_column(Text)
    is_known_issue: Mapped[bool]           = mapped_column(Boolean, default=False)
    outage_ref:     Mapped[str | None]     = mapped_column(String(100))
    resolved_at:    Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    sla_due_at:     Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    user:     Mapped["User"] = relationship(back_populates="tickets", foreign_keys=[user_id])
    comments: Mapped[list["ITTicketComment"]] = relationship(back_populates="ticket")


class ITTicketComment(Base):
    __tablename__ = "it_ticket_comments"

    id:          Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticket_id:   Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("it_tickets.id", ondelete="CASCADE"))
    author_id:   Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    comment:     Mapped[str]       = mapped_column(Text, nullable=False)
    is_internal: Mapped[bool]      = mapped_column(Boolean, default=False)
    created_at:  Mapped[datetime]  = mapped_column(DateTime(timezone=True), server_default=func.now())

    ticket: Mapped["ITTicket"] = relationship(back_populates="comments")


class MaintenanceSchedule(Base):
    __tablename__ = "maintenance_schedule"

    id:              Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title:           Mapped[str]       = mapped_column(String(300), nullable=False)
    affected_system: Mapped[str]       = mapped_column(String(200), nullable=False)
    starts_at:       Mapped[datetime]  = mapped_column(DateTime(timezone=True), nullable=False)
    ends_at:         Mapped[datetime]  = mapped_column(DateTime(timezone=True), nullable=False)
    description:     Mapped[str | None] = mapped_column(Text)
    created_by:      Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at:      Mapped[datetime]  = mapped_column(DateTime(timezone=True), server_default=func.now())


class KnownIssue(Base):
    __tablename__ = "known_issues"

    id:          Mapped[uuid.UUID]      = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title:       Mapped[str]            = mapped_column(String(300), nullable=False)
    category:    Mapped[TicketCategory] = mapped_column(Enum(TicketCategory, name="ticket_category"), nullable=False)
    description: Mapped[str]            = mapped_column(Text, nullable=False)
    workaround:  Mapped[str | None]     = mapped_column(Text)
    is_active:   Mapped[bool]           = mapped_column(Boolean, default=True)
    reported_at: Mapped[datetime]       = mapped_column(DateTime(timezone=True), server_default=func.now())
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class ITInventory(TimestampMixin, Base):
    __tablename__ = "it_inventory"

    id:            Mapped[uuid.UUID]  = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    asset_tag:     Mapped[str]        = mapped_column(String(50), unique=True, nullable=False)
    asset_type:    Mapped[AssetType]  = mapped_column(Enum(AssetType, name="asset_type"), nullable=False)
    brand:         Mapped[str | None] = mapped_column(String(100))
    model:         Mapped[str | None] = mapped_column(String(200))
    serial_no:     Mapped[str | None] = mapped_column(String(100), unique=True)
    status:        Mapped[AssetStatus] = mapped_column(Enum(AssetStatus, name="asset_status"), default=AssetStatus.available)
    assigned_to:   Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    assigned_at:   Mapped[datetime | None]  = mapped_column(DateTime(timezone=True))
    purchase_date: Mapped[date | None]      = mapped_column(Date)
    warranty_until: Mapped[date | None]     = mapped_column(Date)
    location:      Mapped[str | None]       = mapped_column(String(200))
    notes:         Mapped[str | None]       = mapped_column(Text)


class AssetRequest(TimestampMixin, Base):
    __tablename__ = "asset_requests"

    id:            Mapped[uuid.UUID]    = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id:       Mapped[uuid.UUID]    = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    asset_type:    Mapped[AssetType]    = mapped_column(Enum(AssetType, name="asset_type"), nullable=False)
    justification: Mapped[str]          = mapped_column(Text, nullable=False)
    status:        Mapped[RequestStatus] = mapped_column(Enum(RequestStatus, name="request_status"), default=RequestStatus.pending)
    manager_id:    Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    manager_action: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    manager_note:  Mapped[str | None]   = mapped_column(Text)
    it_actioned_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    it_action_at:  Mapped[datetime | None]   = mapped_column(DateTime(timezone=True))
    it_note:       Mapped[str | None]   = mapped_column(Text)
    asset_id:      Mapped[uuid.UUID | None]  = mapped_column(UUID(as_uuid=True), ForeignKey("it_inventory.id"))

    user: Mapped["User"] = relationship(back_populates="asset_requests", foreign_keys=[user_id])


# ── Finance Module ────────────────────────────────────────────────────────────

class PayrollRecord(Base):
    __tablename__ = "payroll_records"
    __table_args__ = (UniqueConstraint("user_id", "pay_month"),)

    id:               Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id:          Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    pay_month:        Mapped[date]      = mapped_column(Date, nullable=False)
    gross_salary:     Mapped[float]     = mapped_column(Numeric(12, 2), nullable=False)
    basic:            Mapped[float]     = mapped_column(Numeric(12, 2), nullable=False)
    hra:              Mapped[float]     = mapped_column(Numeric(12, 2), default=0)
    allowances:       Mapped[float]     = mapped_column(Numeric(12, 2), default=0)
    pf_employee:      Mapped[float]     = mapped_column(Numeric(12, 2), default=0)
    pf_employer:      Mapped[float]     = mapped_column(Numeric(12, 2), default=0)
    tds:              Mapped[float]     = mapped_column(Numeric(12, 2), default=0)
    professional_tax: Mapped[float]     = mapped_column(Numeric(12, 2), default=0)
    other_deductions: Mapped[float]     = mapped_column(Numeric(12, 2), default=0)
    net_salary:       Mapped[float]     = mapped_column(Numeric(12, 2), nullable=False)
    payslip_url:      Mapped[str | None] = mapped_column(Text)
    generated_at:     Mapped[datetime]  = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(foreign_keys=[user_id])


class Reimbursement(TimestampMixin, Base):
    __tablename__ = "reimbursements"
    __table_args__ = (CheckConstraint("amount > 0", name="positive_amount"),)

    id:            Mapped[uuid.UUID]             = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    claim_no:      Mapped[str]                   = mapped_column(String(20), unique=True, nullable=False)
    user_id:       Mapped[uuid.UUID]             = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    category:      Mapped[ReimbursementCategory] = mapped_column(Enum(ReimbursementCategory, name="reimbursement_category"), nullable=False)
    amount:        Mapped[float]                 = mapped_column(Numeric(10, 2), nullable=False)
    currency:      Mapped[str]                   = mapped_column(String(3), default="INR")
    description:   Mapped[str]                   = mapped_column(Text, nullable=False)
    expense_date:  Mapped[date]                  = mapped_column(Date, nullable=False)
    receipt_url:   Mapped[str | None]            = mapped_column(Text)
    status:        Mapped[ReimbursementStatus]   = mapped_column(Enum(ReimbursementStatus, name="reimbursement_status"), default=ReimbursementStatus.draft)
    submitted_at:  Mapped[datetime | None]       = mapped_column(DateTime(timezone=True))
    reviewed_by:   Mapped[uuid.UUID | None]      = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    reviewed_at:   Mapped[datetime | None]       = mapped_column(DateTime(timezone=True))
    reviewer_note: Mapped[str | None]            = mapped_column(Text)
    paid_at:       Mapped[datetime | None]       = mapped_column(DateTime(timezone=True))
    payment_ref:   Mapped[str | None]            = mapped_column(String(100))

    user: Mapped["User"] = relationship(back_populates="reimbursements", foreign_keys=[user_id])


# ── Approvals ─────────────────────────────────────────────────────────────────

class Approval(Base):
    __tablename__ = "approvals"

    id:          Mapped[uuid.UUID]      = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_type: Mapped[ApprovalEntity] = mapped_column(Enum(ApprovalEntity, name="approval_entity"), nullable=False)
    entity_id:   Mapped[uuid.UUID]      = mapped_column(UUID(as_uuid=True), nullable=False)
    approver_id: Mapped[uuid.UUID]      = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    step:        Mapped[int]            = mapped_column(Integer, default=1)
    decision:    Mapped[ApprovalDecision] = mapped_column(Enum(ApprovalDecision, name="approval_decision"), default=ApprovalDecision.pending)
    note:        Mapped[str | None]     = mapped_column(Text)
    decided_at:  Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    expires_at:  Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at:  Mapped[datetime]       = mapped_column(DateTime(timezone=True), server_default=func.now())

    approver: Mapped["User"] = relationship(foreign_keys=[approver_id])


# ── Memory & Sessions ─────────────────────────────────────────────────────────

class UserMemory(Base):
    __tablename__ = "user_memory"
    __table_args__ = (UniqueConstraint("user_id", "memory_key"),)

    id:           Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id:      Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    memory_key:   Mapped[str]       = mapped_column(String(100), nullable=False)
    memory_value: Mapped[dict]      = mapped_column(JSONB, nullable=False)
    source:       Mapped[str]       = mapped_column(String(50), default="inferred")
    updated_at:   Mapped[datetime]  = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="memory_entries")


class ConversationSession(Base):
    __tablename__ = "conversation_sessions"

    id:            Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_key:   Mapped[str]       = mapped_column(String(200), unique=True, nullable=False)
    user_id:       Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    messages:      Mapped[list]      = mapped_column(JSONB, default=list)
    agent_used:    Mapped[str | None] = mapped_column(String(50))
    started_at:    Mapped[datetime]  = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_active_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    ended_at:      Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


# ── RAG Documents ─────────────────────────────────────────────────────────────

class RAGDocument(Base):
    __tablename__ = "rag_documents"

    id:            Mapped[uuid.UUID]    = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename:      Mapped[str]          = mapped_column(String(500), nullable=False)
    department:    Mapped[DocDepartment] = mapped_column(Enum(DocDepartment, name="doc_department"), nullable=False)
    doc_type:      Mapped[str | None]   = mapped_column(String(100))
    roles_allowed: Mapped[list[UserRole]] = mapped_column(ARRAY(Enum(UserRole, name="user_role", create_constraint=False)), default=[UserRole.employee])
    file_url:      Mapped[str | None]   = mapped_column(Text)
    ingested_at:   Mapped[datetime]     = mapped_column(DateTime(timezone=True), server_default=func.now())
    is_active:     Mapped[bool]         = mapped_column(Boolean, default=True)
    chunk_count:   Mapped[int]          = mapped_column(Integer, default=0)
    metadata_:     Mapped[dict]         = mapped_column("metadata", JSONB, default=dict)

    chunks: Mapped[list["RAGChunk"]] = relationship(back_populates="document", cascade="all, delete-orphan")


class RAGChunk(Base):
    __tablename__ = "rag_chunks"
    __table_args__ = (UniqueConstraint("document_id", "chunk_index"),)

    id:          Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("rag_documents.id", ondelete="CASCADE"))
    chunk_index: Mapped[int]       = mapped_column(Integer, nullable=False)
    content:     Mapped[str]       = mapped_column(Text, nullable=False)
    embedding:   Mapped[Any]       = mapped_column(Vector(1536))       # pgvector
    token_count: Mapped[int | None] = mapped_column(Integer)
    metadata_:   Mapped[dict]      = mapped_column("metadata", JSONB, default=dict)
    created_at:  Mapped[datetime]  = mapped_column(DateTime(timezone=True), server_default=func.now())

    document: Mapped["RAGDocument"] = relationship(back_populates="chunks")


# ── Audit Log ─────────────────────────────────────────────────────────────────

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id:           Mapped[uuid.UUID]  = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id:      Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    session_id:   Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("conversation_sessions.id"))
    action:       Mapped[str]        = mapped_column(String(200), nullable=False)
    entity_type:  Mapped[str | None] = mapped_column(String(100))
    entity_id:    Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    agent_used:   Mapped[str | None] = mapped_column(String(100))
    tool_used:    Mapped[str | None] = mapped_column(String(100))
    llm_model:    Mapped[str | None] = mapped_column(String(100))
    status:       Mapped[str]        = mapped_column(String(50), default="success")
    error_message: Mapped[str | None] = mapped_column(Text)
    latency_ms:   Mapped[int | None] = mapped_column(Integer)
    token_count:  Mapped[int | None] = mapped_column(Integer)
    ip_address:   Mapped[Any]        = mapped_column(INET)
    metadata_:    Mapped[dict]       = mapped_column("metadata", JSONB, default=dict)
    created_at:   Mapped[datetime]   = mapped_column(DateTime(timezone=True), server_default=func.now())
```

## app\rag\__init__.py

```python
# app/rag/__init__.py

```

## app\schemas\chat.py

```python
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class ChatRequest(BaseModel):
    query: str = Field(..., description="The user's message.")
    session_id: Optional[str] = Field(None, description="Existing session ID for multi-turn conversations.")

class ChatResponse(BaseModel):
    session_id: str
    response: str
    intent: str
    approval_required: bool = False
    metadata: Dict[str, Any] = {}

class ApprovalDecisionRequest(BaseModel):
    decision: str = Field(..., description="Must be 'approved' or 'rejected'")
    note: Optional[str] = Field(None, description="Optional reasoning for the decision")
```

## app\schemas\__init__.py

```python
# app/schemas/__init__.py

```

## app\tools\email_tools.py

```python
"""
Email Automation — Power Automate HTTP Trigger
===============================================
LangGraph email_notify_node calls send_email_via_power_automate().
Power Automate then sends email via Office 365 / Outlook.

Setup in Power Automate:
  1. New flow → "When an HTTP request is received" trigger
  2. Copy the generated webhook URL → settings.POWER_AUTOMATE_WEBHOOK_URL
  3. Add "Send an email (V2)" action (Office 365 Outlook)
  4. Map: To=body.recipients, Subject=body.subject, Body=body.body
"""
from __future__ import annotations

import httpx
import structlog

from app.config import settings

logger = structlog.get_logger("app.email")


async def send_email_via_power_automate(
    recipients: list[str],
    subject: str,
    body: str,
    cc: list[str] | None = None,
    importance: str = "Normal",   # Low | Normal | High
) -> bool:
    """
    POST to Power Automate HTTP trigger which sends email via Outlook 365.
    Returns True on success, False on failure (non-raising — email is best-effort).
    """
    if not settings.POWER_AUTOMATE_WEBHOOK_URL:
        # Dev/test: log only (no actual send)
        logger.debug("email_mock", recipients=recipients, subject=subject)
        return True

    payload = {
        "recipients": recipients,
        "cc": cc or [],
        "subject": subject,
        "body": body,
        "importance": importance,
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.post(
                settings.POWER_AUTOMATE_WEBHOOK_URL,
                json=payload,
            )
            response.raise_for_status()
            return True
        except (httpx.HTTPStatusError, httpx.RequestError) as exc:
            logger.error("email_send_failed", exc_info=exc, recipients=recipients)
            return False


# ── Pre-built email templates ─────────────────────────────────────────────────

def leave_request_email(employee_name: str, manager_email: str,
                         leave_type: str, start: str, end: str,
                         days: float, leave_id: str, approve_url: str) -> dict:
    return {
        "recipients": [manager_email],
        "subject": f"Leave Request — {employee_name} ({days} day(s))",
        "body": f"""
Hi,

<b>{employee_name}</b> has applied for <b>{leave_type}</b> leave:
<ul>
  <li>From: {start}</li>
  <li>To: {end}</li>
  <li>Duration: {days} business day(s)</li>
</ul>

<a href="{approve_url}">Click here to approve or reject</a>

This is an automated message from the Enterprise AI Copilot.
        """,
    }


def leave_approval_email(employee_email: str, decision: str,
                          leave_type: str, start: str, end: str,
                          reviewer_note: str = "") -> dict:
    status_word = "Approved ✅" if decision == "approved" else "Rejected ❌"
    return {
        "recipients": [employee_email],
        "subject": f"Your Leave Request has been {status_word}",
        "body": f"""
Hi,

Your <b>{leave_type}</b> leave request ({start} to {end}) has been <b>{decision}</b>.

{f'Note from reviewer: {reviewer_note}' if reviewer_note else ''}

This is an automated message from the Enterprise AI Copilot.
        """,
    }


def ticket_created_email(employee_email: str, ticket_no: str,
                          subject: str, priority: str) -> dict:
    return {
        "recipients": [employee_email],
        "subject": f"IT Ticket Created — {ticket_no}",
        "body": f"""
Hi,

Your IT support ticket has been created:
<ul>
  <li>Ticket No: <b>{ticket_no}</b></li>
  <li>Subject: {subject}</li>
  <li>Priority: {priority.upper()}</li>
  <li>Status: Open</li>
</ul>

The IT team will respond based on priority SLA. You'll receive updates via email.

This is an automated message from the Enterprise AI Copilot.
        """,
    }


def reimbursement_submitted_email(employee_email: str, claim_no: str,
                                   amount: float, currency: str) -> dict:
    return {
        "recipients": [employee_email],
        "subject": f"Reimbursement Claim Submitted — {claim_no}",
        "body": f"""
Hi,

Your reimbursement claim has been submitted:
<ul>
  <li>Claim No: <b>{claim_no}</b></li>
  <li>Amount: {currency} {amount:,.2f}</li>
  <li>Status: Under Review</li>
</ul>

The Finance team will process it within 5 business days.

This is an automated message from the Enterprise AI Copilot.
        """,
    }
```

## app\tools\finance_tools.py

```python
import uuid
from datetime import date, datetime
from typing import Dict, Any
from langchain_core.tools import tool
from pydantic import BaseModel, Field

from sqlalchemy import select, and_, extract
from app.database import AsyncSessionLocal
from app.models import (
    PayrollRecord, Reimbursement, ReimbursementCategory, ReimbursementStatus
)

# ==========================================
# INPUT SCHEMAS
# ==========================================

class FetchPayslipInput(BaseModel):
    user_id: str = Field(description="The UUID of the employee requesting their payslip.")
    year: int = Field(description="The year of the requested payslip (e.g., 2023).")
    month: int = Field(description="The numeric month of the requested payslip (1-12).")

class SubmitReimbursementInput(BaseModel):
    user_id: str = Field(description="The UUID of the employee submitting the claim.")
    category: ReimbursementCategory = Field(description="The category of the expense (e.g., 'travel', 'food', 'internet').")
    amount: float = Field(description="The total amount being claimed.")
    currency: str = Field(description="The 3-letter currency code (e.g., 'USD', 'INR').", default="USD")
    description: str = Field(description="A detailed explanation of the business expense.")
    expense_date: date = Field(description="The date the expense occurred (YYYY-MM-DD).")

# ==========================================
# TOOLS
# ==========================================

@tool("fetch_payslip", args_schema=FetchPayslipInput)
async def fetch_payslip(user_id: str, year: int, month: int) -> str:
    """
    Fetch the payslip details (gross salary, net salary, deductions) for a specific month.
    Use this strictly when an employee asks for their own salary or payslip information.
    """
    try:
        async with AsyncSessionLocal() as db:
            # PostgreSQL extraction for month and year matching
            stmt = select(PayrollRecord).where(
                and_(
                    PayrollRecord.user_id == user_id,
                    extract('year', PayrollRecord.pay_month) == year,
                    extract('month', PayrollRecord.pay_month) == month
                )
            )
            result = await db.execute(stmt)
            payslip = result.scalar_one_or_none()
            
            if not payslip:
                month_name = date(year, month, 1).strftime('%B')
                return f"I couldn't find a generated payslip for {month_name} {year}. Please ensure the payroll for that month has been processed."
            
            # Format the financial data nicely
            response = f"**Payslip Summary for {payslip.pay_month.strftime('%B %Y')}**\n"
            response += f"- **Gross Salary:** {payslip.gross_salary:,.2f}\n"
            response += f"- **Basic Pay:** {payslip.basic:,.2f}\n"
            response += f"- **Allowances:** {payslip.allowances:,.2f}\n"
            response += f"- **Tax Deductions (TDS):** -{payslip.tds:,.2f}\n"
            response += f"- **Net Salary:** **{payslip.net_salary:,.2f}**\n\n"
            
            if payslip.payslip_url:
                response += f"[Click here to download your full PDF payslip]({payslip.payslip_url})"
                
            return response
            
    except Exception as e:
        return f"Error fetching payslip details: {str(e)}"

@tool("submit_reimbursement", args_schema=SubmitReimbursementInput)
async def submit_reimbursement(user_id: str, category: ReimbursementCategory, amount: float, currency: str, description: str, expense_date: date) -> Dict[str, Any]:
    """
    Submit a new expense reimbursement claim to the database.
    Use this when an employee wants to get paid back for business expenses like travel or meals.
    Requires manager and finance approval.
    """
    try:
        if amount <= 0:
            return {"error": "Reimbursement amount must be greater than zero."}

        # Generate a readable claim number
        claim_no = f"EXP-{uuid.uuid4().hex[:6].upper()}"

        async with AsyncSessionLocal() as db:
            new_claim = Reimbursement(
                claim_no=claim_no,
                user_id=user_id,
                category=category,
                amount=amount,
                currency=currency.upper(),
                description=description,
                expense_date=expense_date,
                status=ReimbursementStatus.submitted
            )
            db.add(new_claim)
            await db.commit()
            await db.refresh(new_claim)
            
            claim_id = str(new_claim.id)

        # Trigger Manager Approval Process!
        return {
            "status": "success",
            "message": f"Your reimbursement claim ({claim_no}) for {currency.upper()} {amount:,.2f} has been submitted.",
            "approval_required": True,
            "claim_id": claim_id,
            "email_triggered": True,
            "email_recipients": ["manager@company.com"], 
            "email_subject": f"Expense Approval Required: {claim_no}",
            "email_body": f"Employee {user_id} submitted a {category.value} expense for {currency.upper()} {amount:,.2f}.\n\nDescription: {description}\nDate: {expense_date}"
        }

    except Exception as e:
        return {"error": f"Failed to submit reimbursement claim: {str(e)}"}
```

## app\tools\hr_tools.py

```python
from datetime import date
from typing import Dict, Any
from langchain_core.tools import tool
from pydantic import BaseModel, Field

from sqlalchemy import select, and_
from app.database import AsyncSessionLocal
from app.models import LeaveRequest, LeaveBalance, LeaveType, LeaveStatus

# ==========================================
# INPUT SCHEMAS
# ==========================================

class LeaveBalanceInput(BaseModel):
    user_id: str = Field(description="The UUID of the employee requesting their leave balance.")
    year: int = Field(description="The current year to check the balance for.")

class ApplyLeaveInput(BaseModel):
    user_id: str = Field(description="The UUID of the employee applying for leave.")
    start_date: date = Field(description="The start date of the leave (YYYY-MM-DD).")
    end_date: date = Field(description="The end date of the leave (YYYY-MM-DD).")
    leave_type: LeaveType = Field(description="The type of leave (e.g., 'sick', 'casual', 'earned').")
    business_days: float = Field(description="The total number of working days requested.")
    reason: str = Field(description="A brief reason for the leave.")

class CancelLeaveInput(BaseModel):
    user_id: str = Field(description="The UUID of the employee canceling their leave.")
    leave_id: str = Field(description="The UUID of the leave request to cancel.")

# ==========================================
# TOOLS
# ==========================================

@tool("get_leave_balance", args_schema=LeaveBalanceInput)
async def get_leave_balance(user_id: str, year: int) -> str:
    """
    Fetch the current leave balances for an employee from the database. 
    Use this when an employee asks how many days off they have left.
    """
    try:
        async with AsyncSessionLocal() as db:
            stmt = select(LeaveBalance).where(
                and_(LeaveBalance.user_id == user_id, LeaveBalance.year == year)
            )
            result = await db.execute(stmt)
            balances = result.scalars().all()
            
            if not balances:
                return "I couldn't find any leave balance records for you in the system for this year."
            
            response = "Here are your current leave balances:\n"
            for b in balances:
                response += f"- **{b.leave_type.value.capitalize()} Leave**: {b.available_days} days available (out of {b.entitled_days} entitled).\n"
            
            return response
            
    except Exception as e:
        return f"Error fetching leave balance: {str(e)}"

@tool("apply_for_leave", args_schema=ApplyLeaveInput)
async def apply_for_leave(user_id: str, start_date: date, end_date: date, leave_type: LeaveType, business_days: float, reason: str) -> Dict[str, Any]:
    """
    Submit a new leave request for an employee to the database.
    Use this when an employee explicitly states they want to book time off.
    """
    try:
        if end_date < start_date:
            return {"error": "The end date cannot be before the start date."}

        async with AsyncSessionLocal() as db:
            new_leave = LeaveRequest(
                user_id=user_id,
                start_date=start_date,
                end_date=end_date,
                leave_type=leave_type,
                business_days=business_days,
                reason=reason,
                status=LeaveStatus.pending
            )
            db.add(new_leave)
            await db.commit()
            await db.refresh(new_leave)
            
            generated_leave_id = str(new_leave.id)

        # Trigger the LangGraph Human-in-the-loop and Email Automation!
        return {
            "status": "success",
            "message": f"Leave request for {start_date} to {end_date} has been drafted.",
            "approval_required": True,       
            "leave_id": generated_leave_id,  
            "email_triggered": True,
            "email_recipients": ["manager@company.com"], # TODO: Fetch actual manager email via graph context
            "email_subject": f"Leave Approval Required: Employee {user_id}",
            "email_body": f"Please approve {leave_type.value} leave from {start_date} to {end_date}. Reason: {reason}"
        }

    except Exception as e:
        return {"error": f"Failed to submit leave request to the database: {str(e)}"}

@tool("cancel_leave", args_schema=CancelLeaveInput)
async def cancel_leave(user_id: str, leave_id: str) -> str:
    """
    Cancel an existing pending or approved leave request in the database.
    Use this when an employee wants to revoke a previously booked holiday.
    """
    try:
        async with AsyncSessionLocal() as db:
            stmt = select(LeaveRequest).where(
                and_(LeaveRequest.id == leave_id, LeaveRequest.user_id == user_id)
            )
            result = await db.execute(stmt)
            leave_request = result.scalar_one_or_none()
            
            if not leave_request:
                return "Leave request not found or you do not have permission to cancel it."
            
            if leave_request.status in [LeaveStatus.cancelled, LeaveStatus.rejected]:
                return f"This leave request is already marked as {leave_request.status.value}."
                
            leave_request.status = LeaveStatus.cancelled
            await db.commit()
        
        return f"Leave request has been successfully canceled."
    except Exception as e:
        return f"Failed to cancel leave request: {str(e)}"
```

## app\tools\it_tools.py

```python
import uuid
from typing import Dict, Any
from langchain_core.tools import tool
from pydantic import BaseModel, Field

from sqlalchemy import select, and_
from app.database import AsyncSessionLocal
from app.models import (
    ITTicket, TicketCategory, TicketPriority, TicketStatus,
    AssetRequest, AssetType, RequestStatus
)

# ==========================================
# INPUT SCHEMAS
# ==========================================

class CreateTicketInput(BaseModel):
    user_id: str = Field(description="The UUID of the employee creating the ticket.")
    category: TicketCategory = Field(description="The category of the issue (e.g., 'laptop', 'vpn', 'access').")
    subject: str = Field(description="A brief summary of the issue.")
    description: str = Field(description="Detailed explanation of the problem.")
    priority: TicketPriority = Field(description="Urgency of the issue ('low', 'medium', 'high', 'critical').")

class GetTicketStatusInput(BaseModel):
    user_id: str = Field(description="The UUID of the employee checking the ticket.")
    ticket_no: str = Field(description="The specific ticket number (e.g., 'TKT-12345').")

class RequestAssetInput(BaseModel):
    user_id: str = Field(description="The UUID of the employee requesting the asset.")
    asset_type: AssetType = Field(description="The type of asset requested (e.g., 'laptop', 'monitor', 'software_license').")
    justification: str = Field(description="The business reason for requesting this asset.")

# ==========================================
# TOOLS
# ==========================================

@tool("create_it_ticket", args_schema=CreateTicketInput)
async def create_it_ticket(user_id: str, category: TicketCategory, subject: str, description: str, priority: TicketPriority) -> Dict[str, Any]:
    """
    Create a new IT support ticket in the database.
    Use this when an employee reports a broken device, access issue, or software bug.
    """
    try:
        # Generate a readable ticket number
        ticket_no = f"TKT-{uuid.uuid4().hex[:6].upper()}"

        async with AsyncSessionLocal() as db:
            new_ticket = ITTicket(
                ticket_no=ticket_no,
                user_id=user_id,
                category=category,
                subject=subject,
                description=description,
                priority=priority,
                status=TicketStatus.open
            )
            db.add(new_ticket)
            await db.commit()
            await db.refresh(new_ticket)
            
            ticket_id = str(new_ticket.id)

        # Trigger an email to the IT helpdesk
        return {
            "status": "success",
            "message": f"IT Ticket {ticket_no} has been successfully created.",
            "ticket_id": ticket_id,
            "ticket_no": ticket_no,
            "email_triggered": True,
            "email_recipients": ["it-support@company.com"],
            "email_subject": f"New IT Ticket [{priority.value.upper()}]: {subject}",
            "email_body": f"User {user_id} reported an issue in category {category.value}.\n\nDescription: {description}"
        }

    except Exception as e:
        return {"error": f"Failed to create IT ticket: {str(e)}"}

@tool("get_ticket_status", args_schema=GetTicketStatusInput)
async def get_ticket_status(user_id: str, ticket_no: str) -> str:
    """
    Check the current status and resolution notes of an IT ticket.
    Use this when an employee asks for an update on a ticket they submitted.
    """
    try:
        async with AsyncSessionLocal() as db:
            stmt = select(ITTicket).where(
                and_(ITTicket.ticket_no == ticket_no, ITTicket.user_id == user_id)
            )
            result = await db.execute(stmt)
            ticket = result.scalar_one_or_none()
            
            if not ticket:
                return f"I couldn't find a ticket with the number {ticket_no} associated with your account."
            
            response = f"**Ticket {ticket.ticket_no} Status Update:**\n"
            response += f"- **Status:** {ticket.status.value.replace('_', ' ').capitalize()}\n"
            response += f"- **Priority:** {ticket.priority.value.capitalize()}\n"
            
            if ticket.resolution:
                response += f"- **Resolution Notes:** {ticket.resolution}\n"
                
            return response
            
    except Exception as e:
        return f"Error fetching ticket status: {str(e)}"

@tool("request_it_asset", args_schema=RequestAssetInput)
async def request_it_asset(user_id: str, asset_type: AssetType, justification: str) -> Dict[str, Any]:
    """
    Submit a request for a new IT asset (hardware or software).
    Use this when an employee asks for a new laptop, monitor, or license.
    Requires manager approval.
    """
    try:
        async with AsyncSessionLocal() as db:
            new_request = AssetRequest(
                user_id=user_id,
                asset_type=asset_type,
                justification=justification,
                status=RequestStatus.pending
            )
            db.add(new_request)
            await db.commit()
            await db.refresh(new_request)
            
            request_id = str(new_request.id)

        # Trigger Manager Approval Process!
        return {
            "status": "success",
            "message": f"Your request for a {asset_type.value.replace('_', ' ')} has been submitted and is pending manager approval.",
            "approval_required": True,
            "request_id": request_id,
            "email_triggered": True,
            "email_recipients": ["manager@company.com"], 
            "email_subject": f"Asset Request Approval: {asset_type.value.capitalize()}",
            "email_body": f"Employee {user_id} is requesting a {asset_type.value.replace('_', ' ')}.\n\nJustification: {justification}"
        }

    except Exception as e:
        return {"error": f"Failed to submit asset request: {str(e)}"}
```

## app\tools\rag_tools.py

```python
import os
from langchain_core.tools import tool
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from pydantic import BaseModel, Field

from app.config import settings

CHROMA_PERSIST_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "database", "chroma_db"))

# Optional kwargs for disabling SSL verification
kwargs = {}
verify_ssl = getattr(settings, "OPENAI_VERIFY_SSL", True)
if not verify_ssl:
    import httpx
    kwargs["http_client"] = httpx.Client(verify=False)
    kwargs["http_async_client"] = httpx.AsyncClient(verify=False)

# Initialize connection to the Vector DB
vectorstore = Chroma(
    persist_directory=CHROMA_PERSIST_DIR,
    embedding_function=OpenAIEmbeddings(
        api_key=settings.OPENAI_API_KEY,
        **kwargs
    )
)
retriever = vectorstore.as_retriever(
    search_type="mmr", # Maximal Marginal Relevance for diversity
    search_kwargs={"k": 5, "fetch_k": 20} # Top-K=5
)

class PolicySearchInput(BaseModel):
    query: str = Field(description="The specific policy question or search query.")
    user_role: str = Field(description="The role of the user making the request (e.g., employee, manager, hr).")
    department: str = Field(description="The department to filter by (e.g., hr, it, finance).")

@tool("search_company_policies", args_schema=PolicySearchInput)
def search_company_policies(query: str, user_role: str, department: str) -> str:
    """
    Search the company knowledge base for HR, IT, or Finance policies.
    Use this tool whenever the user asks about rules, allowances, processes, or guides.
    """
    try:
        # 1. Define Metadata Filters (RBAC & Department)
        # Chroma uses simple string matching. We ensure the user's role is in the allowed string.
        search_filter = {
            "$and": [
                {"department": {"$eq": department.lower()}},
                {"roles_allowed": {"$contains": user_role.lower()}}
            ]
        }

        # 2. Execute Retrieval
        docs = vectorstore.similarity_search(
            query=query,
            k=5,
            filter=search_filter
        )

        if not docs:
            return f"No relevant {department.upper()} policies found for your query. Either the policy does not exist, or you do not have permission to view it."

        # 3. Format output with citations
        formatted_results = f"--- Retrieved {department.upper()} Policies ---\n\n"
        for i, doc in enumerate(docs, 1):
            source = doc.metadata.get("source", "Unknown Document")
            formatted_results += f"[Source {i}: {source}]\n{doc.page_content}\n\n"

        return formatted_results

    except Exception as e:
        return f"Error retrieving documents: {str(e)}"
```

## app\tools\__init__.py

```python
from typing import List
from langchain_core.tools import BaseTool
from app.models import UserRole

# Import all domain tools
from app.tools.rag_tools import search_company_policies
from app.tools.hr_tools import get_leave_balance, apply_for_leave, cancel_leave
from app.tools.it_tools import create_it_ticket, get_ticket_status, request_it_asset
from app.tools.finance_tools import fetch_payslip, submit_reimbursement

def get_tools_for_intent(intent: str, user_role: UserRole) -> List[BaseTool]:
    """
    Returns the specific list of LangChain tools available for a given intent.
    This prevents overwhelming the LLM with unnecessary tools and enforces RBAC.
    """
    tools = []
    
    # 1. RAG / Policy Tools (Available to almost everyone based on intent)
    if "policy" in intent or intent == "general.unknown":
        tools.append(search_company_policies)
        
    # 2. HR Tools
    if intent.startswith("hr.leave"):
        tools.extend([get_leave_balance, apply_for_leave, cancel_leave])
        
    # 3. IT Tools
    elif intent.startswith("it"):
        tools.extend([create_it_ticket, get_ticket_status, request_it_asset])
        
    # 4. Finance Tools
    elif intent.startswith("finance"):
        tools.extend([fetch_payslip, submit_reimbursement])
        
    return tools
```

## app\__init__.py

```python
# app/__init__.py

```

## app\config.py

```python
import os
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn, field_validator


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",          # silently skip unknown env vars (e.g. LANGSMITH_*)
    )

    # ── App ─────────────────────────────────────────────────
    APP_NAME: str = "Employee Assistant"
    APP_ENV: str = "development"             # development | staging | production
    DEBUG: bool = False
    SECRET_KEY: str                          # used for JWT signing
    ALLOWED_ORIGINS: list[str] = []

    # ── Database ─────────────────────────────────────────────
    DATABASE_URL: PostgresDsn               # postgresql+asyncpg://user:pass@host/db
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_ECHO: bool = False                   # set True to log all SQL

    # ── Redis (short-term memory / rate limiting) ─────────────
    REDIS_URL: str = "redis://localhost:6379/0"
    SESSION_TTL_SECONDS: int = 3600         # 1 hour idle timeout

    # ── LLM Providers ────────────────────────────────────────
    OPENAI_API_KEY: str = ""                 # optional — only if using OpenAI models
    ANTHROPIC_API_KEY: str = ""
    XAI_API_KEY: str = ""                    # Grok (xAI)
    GOOGLE_API_KEY: str = ""                 # Gemini
    OPENAI_BASE_URL: str | None = None
    OPENAI_VERIFY_SSL: bool = True

    # Dynamic routing: which model for which task
    
    # --- Gemini Models (Commented out) ---
    # LLM_INTENT: str = "gemini-2.5-flash"    # fast, cheap intent classification
    # LLM_HR: str = "gemini-2.5-pro"          # balanced for HR conversations
    # LLM_IT: str = "gemini-2.5-flash"        # fast for IT support
    # LLM_FINANCE: str = "gemini-2.5-pro"     # strong reasoning for calculations
    # LLM_EVALUATOR: str = "gemini-2.5-flash" # GEPA self-evaluation node
    
    # --- OpenAI Models (Active) ---
    LLM_INTENT: str = "gpt-4o-mini"
    LLM_HR: str = "gpt-4o"
    LLM_IT: str = "gpt-4o-mini"
    LLM_FINANCE: str = "gpt-4o"
    LLM_EVALUATOR: str = "gpt-4o-mini"
    
    LLM_TEMPERATURE: float = 0.1            # low temp for enterprise accuracy

    # ── LangSmith (tracing) ──────────────────────────────────
    LANGCHAIN_TRACING_V2: bool = True
    LANGCHAIN_API_KEY: str = ""
    LANGSMITH_PROJECT: str = "EmployeeAssistant"  # matches LANGSMITH_PROJECT in .env

    # ── Vector DB / RAG ──────────────────────────────────────
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    EMBEDDING_DIM: int = 1536
    RAG_TOP_K: int = 5
    RAG_SCORE_THRESHOLD: float = 0.75       # below this → trigger web search fallback
    CHUNK_SIZE: int = 512
    CHUNK_OVERLAP: int = 50

    # ── FastMCP ──────────────────────────────────────────────
    MCP_HOST: str = "0.0.0.0"
    MCP_PORT: int = 8001

    # ── Email (Power Automate trigger) ───────────────────────
    POWER_AUTOMATE_WEBHOOK_URL: str = ""

    # ── JWT ──────────────────────────────────────────────────
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 8-hour work day

    # ── Rate Limiting ─────────────────────────────────────────
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 60

    # ── GEPA (self-evaluation) ───────────────────────────────
    GEPA_EVAL_THRESHOLD: float = 0.80       # retry if quality score < this
    GEPA_MAX_RETRIES: int = 2

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def fix_asyncpg_driver(cls, v: str) -> str:
        """Ensure asyncpg driver is used."""
        if v.startswith("postgresql://"):
            return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

# Inject LangSmith settings directly into OS environment for LangChain under-the-hood tracking
if settings.LANGCHAIN_TRACING_V2 and settings.LANGCHAIN_API_KEY:
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_API_KEY"] = settings.LANGCHAIN_API_KEY
    os.environ["LANGCHAIN_PROJECT"] = settings.LANGSMITH_PROJECT
```

## app\database.py

```python
"""
app/database.py — Canonical re-export shim
==========================================
All application code imports the database layer from here:

    from app.database import AsyncSessionLocal, get_db, check_db_connection

The actual engine, session factory and Base live in `database/database.py`
(the top-level `database` package) so that Alembic env.py can import Base
without dragging in the full `app` package.

Why a shim and not a direct import everywhere?
  - Keeps all app-internal imports under the `app.*` namespace — consistent
    and IDE-friendly.
  - The underlying `database/database.py` module can evolve (e.g., switch
    to a different async driver) without touching every file in `app/`.
  - Mirrors the standard Django / SQLAlchemy project layout where a single
    `db.py` / `database.py` is the one place everything is imported from.
"""
from database.database import (  # noqa: F401  (re-exports)
    AsyncSessionLocal,
    Base,
    check_db_connection,
    engine,
    get_db,
)

__all__ = [
    "AsyncSessionLocal",
    "Base",
    "check_db_connection",
    "engine",
    "get_db",
]

```

## app\main.py

```python
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import structlog

# Import your graph and database components
from app.config import settings
from app.database import AsyncSessionLocal, check_db_connection
from app.graph.workflow import run_workflow, workflow
from app.middleware import (
    RequestLoggingMiddleware, 
    RateLimitMiddleware, 
    setup_redis, 
    close_redis, 
    enrich_request, 
    load_role_permissions
)

# Set up structured logging
logger = structlog.get_logger("app.lifecycle")

# ── Lifespan (startup / shutdown) ─────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles startup and shutdown events for the FastAPI application."""
    # Startup: Load RBAC permissions (fail-open for local dev)
    try:
        async with AsyncSessionLocal() as db:
            await load_role_permissions(db)
        logger.info("rbac_loaded")
    except Exception as e:
        logger.warning("rbac_load_skipped", error=str(e), hint="RBAC permissions not loaded — admin role bypasses all checks")

    # Redis: optional for local dev (rate limiter will fail-open)
    try:
        await setup_redis()
        logger.info("redis_connected")
    except Exception as e:
        logger.warning("redis_skipped", error=str(e), hint="Rate limiting disabled — Redis not available")

    logger.info("startup_complete", app=settings.APP_NAME, env=settings.APP_ENV)
        
    yield  # The app is running
    
    # Shutdown
    try:
        await close_redis()
    except Exception:
        pass
    logger.info("shutdown_initiated", app=settings.APP_NAME)


# ── App Initialization ────────────────────────────────────────────────────────

app = FastAPI(
    title=settings.APP_NAME,
    description="LangGraph-powered AI backend for HR, IT, and Finance.",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url=None,
    lifespan=lifespan,
)

# ── Middlewares ───────────────────────────────────────────────────────────────

# CORS Middleware for frontend communication
# Normalize origins: handle both AnyHttpUrl objects and plain strings
_origins = []
for o in settings.ALLOWED_ORIGINS:
    origin_str = str(o).rstrip("/")
    _origins.append(origin_str)

# Always allow localhost:3000 in development
if settings.DEBUG:
    for dev_origin in ["http://localhost:3000", "http://127.0.0.1:3000"]:
        if dev_origin not in _origins:
            _origins.append(dev_origin)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate Limiting via Redis Token Bucket
app.add_middleware(RateLimitMiddleware)

# Structured request logging
app.add_middleware(RequestLoggingMiddleware)


# ── Schemas ───────────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    intent: str
    agent_used: str | None
    approval_required: bool
    metadata: dict

class ApprovalCallback(BaseModel):
    session_id: str
    decision: str
    note: str = ""


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/health", tags=["System"])
async def health():
    """System health check endpoint."""
    try:
        db_ok = await check_db_connection()
    except Exception:
        db_ok = False
    return {
        "status": "ok" if db_ok else "degraded",
        "db": db_ok,
        "app": settings.APP_NAME,
        "env": settings.APP_ENV,
        "debug": settings.DEBUG,
    }


@app.post("/api/v1/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(
    body: ChatRequest,
    user_ctx: dict = Depends(enrich_request),
):
    """Main conversational endpoint."""
    try:
        final_state = await run_workflow(
            user_ctx=user_ctx,
            query=body.message,
            session_id=body.session_id,
        )

        return ChatResponse(
            response=final_state.get("response", "I'm sorry, I couldn't process that request."),
            session_id=final_state["session_id"],
            intent=final_state.get("intent", "general.unknown"),
            agent_used=final_state.get("agent_used"),
            approval_required=final_state.get("approval_required", False),
            metadata=final_state.get("metadata", {}),
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        logger.error("chat_endpoint_error", error=str(e), session_id=body.session_id)
        raise HTTPException(status_code=500, detail="An error occurred while processing your request.")


@app.post("/api/v1/approve", tags=["Approvals"])
async def handle_approval(
    body: ApprovalCallback,
    user_ctx: dict = Depends(enrich_request),
):
    """Resumes a paused LangGraph workflow after a manager makes an approval decision."""
    from langgraph.types import Command
    from app.models import UserRole
    
    if user_ctx.get("user_role") not in [UserRole.manager, UserRole.admin]:
        raise HTTPException(status_code=403, detail="Only managers or admins can perform approvals.")

    try:
        config = {"configurable": {"thread_id": body.session_id}}
        
        await workflow.ainvoke(
            Command(resume={"decision": body.decision, "note": body.note}),
            config=config,
        )
        return {"status": "ok", "decision": body.decision, "session_id": body.session_id}
        
    except Exception as e:
        logger.error("approval_endpoint_error", error=str(e), session_id=body.session_id)
        raise HTTPException(status_code=500, detail="Failed to resume workflow after approval.")
```

## database\database.py

```python
from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, MappedColumn
from sqlalchemy import DateTime, func, text
from app.config import settings


# ── Engine ────────────────────────────────────────────────────────────────────

engine = create_async_engine(
    str(settings.DATABASE_URL),
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    echo=settings.DB_ECHO,
    pool_pre_ping=True,                     # auto-recover stale connections
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,                 # keep objects usable after commit
)


# ── Base model ────────────────────────────────────────────────────────────────

class Base(DeclarativeBase):
    """All SQLAlchemy models inherit from this."""
    pass


# ── Dependency (FastAPI) ──────────────────────────────────────────────────────

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency — yields an async DB session per request."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# ── Health check ──────────────────────────────────────────────────────────────

async def check_db_connection() -> bool:
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
```

## database\schema.sql

```sql
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
```

## database\__init__.py

```python
# database/__init__.py
# Makes the top-level `database` directory a proper Python package.
# Alembic env.py imports `from database.database import Base` — this file
# ensures that import resolves correctly under all Python path configurations.

```

## frontend\AGENTS.md

```markdown
<!-- BEGIN:nextjs-agent-rules -->
# This is NOT the Next.js you know

This version has breaking changes — APIs, conventions, and file structure may all differ from your training data. Read the relevant guide in `node_modules/next/dist/docs/` before writing any code. Heed deprecation notices.
<!-- END:nextjs-agent-rules -->

```

## frontend\app\approvals\page.tsx

```tsx
// app/approvals/page.tsx
"use client";

import { useState } from "react";
import { useAuth } from "@/lib/AuthContext";
import { api } from "@/lib/api";
import { useRouter } from "next/navigation";
import { ShieldCheck, Check, X, AlertCircle, Hash, Search } from "lucide-react";
import { motion } from "framer-motion";

export default function ApprovalsPage() {
  const { user } = useAuth();
  const router = useRouter();
  
  const [sessionId, setSessionId] = useState("");
  const [note, setNote] = useState("");
  const [status, setStatus] = useState<{ type: "success" | "error"; msg: string } | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // Security redirect
  if (user && user.role === "employee") {
    router.push("/chat");
    return null;
  }

  const handleDecision = async (decision: "approved" | "rejected") => {
    if (!sessionId.trim()) {
      setStatus({ type: "error", msg: "Please enter a valid Session ID." });
      return;
    }

    setIsLoading(true);
    setStatus(null);

    try {
      const result = await api.approve(sessionId, decision, note, user!.role);
      setStatus({ 
        type: "success", 
        msg: `Success! The workflow was ${decision}. Final response: "${result.final_response}"` 
      });
      setSessionId("");
      setNote("");
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : "Unknown error";
      setStatus({ type: "error", msg: `Failed: ${errorMsg}` });
    } finally {
      setIsLoading(false);
    }
  };

  if (!user) return null;

  return (
    <div className="flex min-h-screen flex-col bg-zinc-950/50 p-8 md:p-12 relative">
      <div className="max-w-3xl mx-auto w-full relative z-10">
        
        <div className="mb-10 flex items-center gap-4">
          <div className="h-12 w-12 bg-emerald-500/20 rounded-2xl flex items-center justify-center border border-emerald-500/30 shadow-lg shadow-emerald-500/10">
            <ShieldCheck className="h-6 w-6 text-emerald-400" />
          </div>
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-white mb-1">Pending Approvals</h1>
            <p className="text-sm text-zinc-400 font-medium">
              Review and manage paused workflow requests from your team.
            </p>
          </div>
        </div>

        <motion.div 
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-zinc-900/60 backdrop-blur-xl p-8 rounded-3xl shadow-2xl border border-zinc-800/50"
        >
          <div className="space-y-6">
            <div>
              <label className="flex items-center gap-2 text-sm font-semibold text-zinc-300 mb-2">
                <Hash className="h-4 w-4 text-zinc-500" /> Workflow Session ID
              </label>
              <div className="relative">
                <input
                  type="text"
                  value={sessionId}
                  onChange={(e) => setSessionId(e.target.value)}
                  placeholder="e.g., 550e8400-e29b-41d4-a716-446655440000"
                  className="w-full rounded-xl bg-zinc-950 border border-zinc-800 p-4 pl-12 focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/50 text-zinc-100 placeholder-zinc-600 transition-all font-mono text-sm"
                />
                <Search className="absolute left-4 top-4 h-5 w-5 text-zinc-500" />
              </div>
              <p className="text-xs text-zinc-500 mt-2 font-medium">Find this in the chat UI or automated alert email.</p>
            </div>

            <div>
              <label className="block text-sm font-semibold text-zinc-300 mb-2">
                Manager Notes (Optional)
              </label>
              <textarea
                value={note}
                onChange={(e) => setNote(e.target.value)}
                placeholder="Add reasoning for your decision (will be sent back to the workflow)..."
                className="w-full rounded-xl bg-zinc-950 border border-zinc-800 p-4 focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/50 text-zinc-100 placeholder-zinc-600 transition-all min-h-[120px] resize-none"
              />
            </div>

            {status && (
              <motion.div 
                initial={{ opacity: 0, scale: 0.98 }}
                animate={{ opacity: 1, scale: 1 }}
                className={`p-4 rounded-xl text-sm font-medium flex items-start gap-3 ${
                  status.type === "success" 
                    ? "bg-emerald-500/10 text-emerald-200 border border-emerald-500/30" 
                    : "bg-red-500/10 text-red-200 border border-red-500/30"
                }`}
              >
                {status.type === "success" ? (
                  <Check className="h-5 w-5 text-emerald-400 flex-shrink-0" />
                ) : (
                  <AlertCircle className="h-5 w-5 text-red-400 flex-shrink-0" />
                )}
                <div>{status.msg}</div>
              </motion.div>
            )}

            <div className="flex gap-4 pt-6 border-t border-zinc-800/50">
              <button
                onClick={() => handleDecision("approved")}
                disabled={isLoading || !sessionId.trim()}
                className="flex-1 flex items-center justify-center gap-2 bg-emerald-600/90 text-white py-3.5 rounded-xl font-semibold hover:bg-emerald-500 disabled:opacity-50 disabled:hover:bg-emerald-600/90 transition-all shadow-lg shadow-emerald-900/20 active:scale-[0.98]"
              >
                <Check className="h-5 w-5" />
                {isLoading ? "Processing..." : "Approve Request"}
              </button>
              <button
                onClick={() => handleDecision("rejected")}
                disabled={isLoading || !sessionId.trim()}
                className="flex-1 flex items-center justify-center gap-2 bg-zinc-800 text-white py-3.5 rounded-xl font-semibold hover:bg-red-600/90 disabled:opacity-50 disabled:hover:bg-zinc-800 transition-all active:scale-[0.98] border border-zinc-700/50 hover:border-red-500/50"
              >
                <X className="h-5 w-5" />
                {isLoading ? "Processing..." : "Reject Request"}
              </button>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
```

## frontend\app\chat\page.tsx

```tsx
"use client";

import { useState, useRef, useEffect } from "react";
import { useAuth } from "@/lib/AuthContext";
import { api } from "@/lib/api";
import ChatBubble from "@/components/ChatBubble";
import { Send, Hash, Sparkles } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
  isApprovalRequired?: boolean;
};

export default function ChatPage() {
  const { user } = useAuth();
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      role: "assistant",
      content: "Hello! I am Aura, your Enterprise Intelligence. I can help you check leave balances, submit IT tickets, fetch payslips, and more. How can I assist you today?",
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  const handleSend = async (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!input.trim() || !user || isLoading) return;

    const userMessage: Message = { id: Date.now().toString(), role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const data = await api.chat(userMessage.content, sessionId, user.role);
      
      if (!sessionId) setSessionId(data.session_id);

      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: data.response,
        isApprovalRequired: data.approval_required,
      };

      setMessages((prev) => [...prev, aiMessage]);
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : "Unknown error occurred.";
      setMessages((prev) => [
        ...prev,
        { id: "error-" + Date.now(), role: "assistant", content: `⚠️ ${errorMsg}` },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  if (!user) return null;

  return (
    <div className="flex h-full flex-col bg-zinc-950/50 backdrop-blur-3xl relative">
      <header className="bg-zinc-900/40 border-b border-zinc-800/50 px-8 py-5 flex justify-between items-center backdrop-blur-md z-10 sticky top-0">
        <div className="flex items-center gap-3">
          <h1 className="text-xl font-bold text-zinc-100 flex items-center gap-2">
            Aura Chat <Sparkles className="h-4 w-4 text-indigo-400" />
          </h1>
        </div>
        {sessionId && (
          <div className="flex items-center gap-2 bg-zinc-800/50 px-3 py-1.5 rounded-full border border-zinc-700/50">
            <Hash className="h-3 w-3 text-zinc-500" />
            <span className="text-xs text-zinc-400 font-mono font-medium">{sessionId.slice(0, 8)}</span>
          </div>
        )}
      </header>

      <div className="flex-1 overflow-y-auto p-6 scroll-smooth">
        <div className="mx-auto max-w-4xl pt-4 pb-10">
          {messages.map((msg) => (
            <ChatBubble key={msg.id} {...msg} />
          ))}
          
          <AnimatePresence>
            {isLoading && (
              <motion.div 
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.9 }}
                className="flex items-center gap-3 ml-12 text-zinc-400 text-sm font-medium"
              >
                <div className="flex gap-1">
                  <span className="animate-bounce delay-75 w-1.5 h-1.5 bg-indigo-500 rounded-full block"></span>
                  <span className="animate-bounce delay-150 w-1.5 h-1.5 bg-indigo-500 rounded-full block"></span>
                  <span className="animate-bounce delay-300 w-1.5 h-1.5 bg-indigo-500 rounded-full block"></span>
                </div>
                Aura is thinking...
              </motion.div>
            )}
          </AnimatePresence>
          <div ref={messagesEndRef} className="h-4" />
        </div>
      </div>

      <div className="p-6 bg-gradient-to-t from-zinc-950 via-zinc-950 to-transparent sticky bottom-0">
        <div className="mx-auto max-w-4xl relative">
          <div className="absolute -inset-1 bg-gradient-to-r from-indigo-500/20 to-purple-500/20 rounded-3xl blur-md"></div>
          <form 
            onSubmit={handleSend} 
            className="relative flex items-end bg-zinc-900 border border-zinc-700/50 rounded-3xl overflow-hidden shadow-2xl transition-all focus-within:border-indigo-500/50 focus-within:ring-1 focus-within:ring-indigo-500/50"
          >
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask about policies, submit requests, or search knowledge..."
              className="w-full bg-transparent px-6 py-5 text-zinc-100 placeholder-zinc-500 focus:outline-none resize-none max-h-40 min-h-[64px]"
              rows={1}
              disabled={isLoading}
            />
            <div className="px-4 py-3 pb-4">
              <button
                type="submit"
                disabled={isLoading || !input.trim()}
                className="flex h-10 w-10 items-center justify-center rounded-2xl bg-indigo-600 text-white shadow-md shadow-indigo-600/20 transition-all hover:bg-indigo-500 hover:scale-105 active:scale-95 disabled:opacity-50 disabled:hover:scale-100 disabled:hover:bg-indigo-600"
              >
                <Send className="h-4 w-4 ml-0.5" />
              </button>
            </div>
          </form>
          <div className="text-center mt-3 text-[10px] text-zinc-600 font-medium">
            Aura can make mistakes. Consider verifying important information.
          </div>
        </div>
      </div>
    </div>
  );
}
```

## frontend\app\favicon.ico

```ico
[Binary file content not included]
```

## frontend\app\globals.css

```css
@import "tailwindcss";

:root {
  --background: #ffffff;
  --foreground: #09090b;
}

@theme inline {
  --color-background: var(--background);
  --color-foreground: var(--foreground);
  --font-sans: var(--font-inter), ui-sans-serif, system-ui, sans-serif;
  --font-mono: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
}

@media (prefers-color-scheme: dark) {
  :root {
    --background: #09090b; /* zinc-950 */
    --foreground: #fafafa; /* zinc-50 */
  }
}

body {
  background: var(--background);
  color: var(--foreground);
  font-family: var(--font-sans);
}

/* Custom Scrollbar for a premium feel */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: #3f3f46; /* zinc-700 */
  border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {
  background: #52525b; /* zinc-600 */
}

/* Tailwind utility class for hiding scrollbars but keeping functionality */
@layer utilities {
  .scrollbar-hide::-webkit-scrollbar {
    display: none;
  }
  .scrollbar-hide {
    -ms-overflow-style: none;
    scrollbar-width: none;
  }
}

```

## frontend\app\layout.tsx

```tsx
import type { Metadata } from "next";
import { Inter, Outfit } from "next/font/google";
import "./globals.css";
import { AuthProvider } from "@/lib/AuthContext";
import AppLayout from "@/components/AppLayout";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

const outfit = Outfit({
  variable: "--font-outfit",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "NoviBot - Employee Assistant",
  description: "Intelligent HR, IT, and Finance Assistant",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${inter.variable} ${outfit.variable} h-full antialiased dark`}
    >
      <body className="min-h-full flex flex-col bg-zinc-950 text-zinc-100 font-sans">
        <AuthProvider>
          <AppLayout>{children}</AppLayout>
        </AuthProvider>
      </body>
    </html>
  );
}

```

## frontend\app\login\page.tsx

```tsx
"use client";

import { useAuth } from "@/lib/AuthContext";
import { UserCircle, ShieldAlert, Sparkles, Activity, CheckCircle2 } from "lucide-react";
import { motion } from "framer-motion";

export default function LoginPage() {
  const { login } = useAuth();

  return (
    <div className="flex min-h-screen items-center justify-center bg-zinc-950 font-sans text-zinc-100 overflow-hidden relative selection:bg-indigo-500/30">
      
      {/* Background gradients */}
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-indigo-600/20 blur-[120px] rounded-full pointer-events-none" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-purple-600/20 blur-[120px] rounded-full pointer-events-none" />

      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
        className="w-full max-w-md relative z-10"
      >
        <div className="bg-zinc-900/60 backdrop-blur-xl border border-zinc-800/50 rounded-3xl p-10 shadow-2xl">
          <div className="flex justify-center mb-6">
            <div className="h-16 w-16 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-2xl flex items-center justify-center shadow-lg shadow-indigo-500/20">
              <Sparkles className="text-white h-8 w-8" />
            </div>
          </div>
          
          <div className="text-center mb-10">
            <h2 className="text-3xl font-bold tracking-tight bg-gradient-to-br from-white to-zinc-400 bg-clip-text text-transparent">
              Aura Copilot
            </h2>
            <p className="mt-3 text-sm text-zinc-400 font-medium">
              Enterprise Agentic Intelligence
            </p>
          </div>

          <div className="space-y-4">
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => login("employee")}
              className="group relative w-full overflow-hidden rounded-xl bg-zinc-800/50 border border-zinc-700/50 p-4 transition-all hover:bg-indigo-500/10 hover:border-indigo-500/50"
            >
              <div className="flex items-center gap-4">
                <div className="bg-indigo-500/20 p-2 rounded-lg group-hover:bg-indigo-500 transition-colors">
                  <UserCircle className="h-6 w-6 text-indigo-400 group-hover:text-white transition-colors" />
                </div>
                <div className="text-left">
                  <div className="text-sm font-semibold text-zinc-200">Continue as Employee</div>
                  <div className="text-xs text-zinc-500">Access HR, IT, and personal tools</div>
                </div>
              </div>
            </motion.button>

            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => login("manager")}
              className="group relative w-full overflow-hidden rounded-xl bg-zinc-800/50 border border-zinc-700/50 p-4 transition-all hover:bg-emerald-500/10 hover:border-emerald-500/50"
            >
              <div className="flex items-center gap-4">
                <div className="bg-emerald-500/20 p-2 rounded-lg group-hover:bg-emerald-500 transition-colors">
                  <ShieldAlert className="h-6 w-6 text-emerald-400 group-hover:text-white transition-colors" />
                </div>
                <div className="text-left">
                  <div className="text-sm font-semibold text-zinc-200">Continue as Manager</div>
                  <div className="text-xs text-zinc-500">Review approvals and team insights</div>
                </div>
              </div>
            </motion.button>
          </div>
          
          <div className="mt-8 flex items-center justify-center gap-6 text-xs text-zinc-600 font-medium">
            <div className="flex items-center gap-1.5"><Activity className="h-3.5 w-3.5" /> All systems operational</div>
            <div className="flex items-center gap-1.5"><CheckCircle2 className="h-3.5 w-3.5" /> End-to-end encrypted</div>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
```

## frontend\app\page.tsx

```tsx
import { redirect } from "next/navigation";

export default function Home() {
  redirect("/chat");
}

```

## frontend\CLAUDE.md

```markdown
@AGENTS.md

```

## frontend\components\AppLayout.tsx

```tsx
"use client";

import { useAuth } from "@/lib/AuthContext";
import Sidebar from "./Sidebar";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const { user } = useAuth();
  const pathname = usePathname();
  const router = useRouter();
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  useEffect(() => {
    if (isMounted && !user && pathname !== "/login") {
      router.push("/login");
    }
  }, [user, pathname, router, isMounted]);

  // Don't render until mounted to avoid hydration mismatch
  if (!isMounted) return <div className="min-h-screen bg-zinc-950 flex items-center justify-center">Loading...</div>;

  if (!user || pathname === "/login") {
    return <main className="flex-1">{children}</main>;
  }

  return (
    <div className="flex h-screen overflow-hidden bg-zinc-950 text-zinc-100 font-sans selection:bg-indigo-500/30">
      <Sidebar />
      <main className="flex-1 flex flex-col overflow-hidden relative">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-indigo-900/20 via-zinc-950 to-zinc-950 z-0"></div>
        <div className="relative z-10 flex flex-col h-full">{children}</div>
      </main>
    </div>
  );
}

```

## frontend\components\ChatBubble.tsx

```tsx
// components/ChatBubble.tsx
import React from "react";
import { User, Bot, Clock } from "lucide-react";
import { motion } from "framer-motion";

type MessageProps = {
  role: "user" | "assistant";
  content: string;
  isApprovalRequired?: boolean;
};

export default function ChatBubble({ role, content, isApprovalRequired }: MessageProps) {
  const isUser = role === "user";

  return (
    <motion.div 
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`flex w-full ${isUser ? "justify-end" : "justify-start"} mb-6 group`}
    >
      {!isUser && (
        <div className="flex-shrink-0 mr-4 mt-1">
          <div className="h-8 w-8 rounded-full bg-indigo-500/20 flex items-center justify-center border border-indigo-500/30">
            <Bot className="h-4 w-4 text-indigo-400" />
          </div>
        </div>
      )}

      <div
        className={`max-w-[75%] rounded-2xl px-5 py-3.5 shadow-sm relative ${
          isUser
            ? "bg-indigo-600 text-white rounded-tr-sm"
            : "bg-zinc-800/80 backdrop-blur-sm border border-zinc-700/50 text-zinc-100 rounded-tl-sm shadow-black/20"
        }`}
      >
        <div className="whitespace-pre-wrap text-[15px] leading-relaxed">
          {content}
        </div>
        
        {/* Special UI if the graph paused for approval */}
        {isApprovalRequired && !isUser && (
          <div className="mt-4 rounded-xl border border-amber-500/30 bg-amber-500/10 p-3.5 text-xs text-amber-200/90 flex items-start gap-3">
            <Clock className="h-4 w-4 text-amber-400 flex-shrink-0 mt-0.5" />
            <div>
              <span className="font-semibold text-amber-300 block mb-0.5">Approval Required</span>
              This request has been paused and sent to your manager for approval. 
              You will be notified once a decision is made.
            </div>
          </div>
        )}
      </div>

      {isUser && (
        <div className="flex-shrink-0 ml-4 mt-1">
          <div className="h-8 w-8 rounded-full bg-zinc-700 flex items-center justify-center border border-zinc-600">
            <User className="h-4 w-4 text-zinc-300" />
          </div>
        </div>
      )}
    </motion.div>
  );
}
```

## frontend\components\Sidebar.tsx

```tsx
"use client";

import Link from "next/link";
import { useAuth } from "@/lib/AuthContext";
import { usePathname } from "next/navigation";
import { MessageSquare, CheckSquare, LogOut, Sparkles, User, Settings } from "lucide-react";
import { motion } from "framer-motion";

export default function Sidebar() {
  const { user, logout } = useAuth();
  const pathname = usePathname();

  if (!user) return null;

  const isManager = ["manager", "admin"].includes(user.role);

  return (
    <div className="flex h-screen w-72 flex-col border-r border-zinc-800/50 bg-zinc-950/80 backdrop-blur-xl px-4 py-6 z-20">
      <div className="mb-8 px-3 flex items-center gap-3">
        <div className="h-10 w-10 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg shadow-indigo-500/20">
          <Sparkles className="text-white h-5 w-5" />
        </div>
        <div>
          <h1 className="text-lg font-bold tracking-tight bg-gradient-to-br from-white to-zinc-400 bg-clip-text text-transparent">
            Aura
          </h1>
          <p className="text-[10px] uppercase tracking-widest text-zinc-500 font-semibold">Workspace</p>
        </div>
      </div>

      <nav className="flex-1 space-y-1.5 px-1">
        <div className="text-xs font-semibold text-zinc-500 uppercase tracking-wider mb-3 px-3">Menu</div>
        
        <Link href="/chat">
          <div className={`group relative flex items-center gap-3 rounded-xl px-3 py-2.5 transition-all duration-200 ${
            pathname === "/chat" 
              ? "bg-indigo-500/10 text-indigo-300 font-medium" 
              : "text-zinc-400 hover:bg-zinc-800/50 hover:text-zinc-200"
          }`}>
            {pathname === "/chat" && (
              <motion.div layoutId="sidebar-active" className="absolute left-0 w-1 h-6 bg-indigo-500 rounded-r-full" />
            )}
            <MessageSquare className={`h-5 w-5 ${pathname === "/chat" ? "text-indigo-400" : "text-zinc-500 group-hover:text-zinc-300"}`} />
            Copilot Chat
          </div>
        </Link>

        {isManager && (
          <Link href="/approvals">
            <div className={`group relative flex items-center justify-between rounded-xl px-3 py-2.5 transition-all duration-200 ${
              pathname === "/approvals" 
                ? "bg-emerald-500/10 text-emerald-300 font-medium" 
                : "text-zinc-400 hover:bg-zinc-800/50 hover:text-zinc-200"
            }`}>
              {pathname === "/approvals" && (
                <motion.div layoutId="sidebar-active" className="absolute left-0 w-1 h-6 bg-emerald-500 rounded-r-full" />
              )}
              <div className="flex items-center gap-3">
                <CheckSquare className={`h-5 w-5 ${pathname === "/approvals" ? "text-emerald-400" : "text-zinc-500 group-hover:text-zinc-300"}`} />
                Approvals
              </div>
              <span className="flex h-5 w-5 items-center justify-center rounded-full bg-emerald-500/20 text-[10px] font-bold text-emerald-400">
                2
              </span>
            </div>
          </Link>
        )}
        
        <div className="pt-4 mt-2 border-t border-zinc-800/50">
          <div className="text-xs font-semibold text-zinc-500 uppercase tracking-wider mb-3 px-3">Support</div>
          <button className="w-full flex items-center gap-3 rounded-xl px-3 py-2.5 text-zinc-400 hover:bg-zinc-800/50 hover:text-zinc-200 transition-colors">
            <Settings className="h-5 w-5 text-zinc-500" />
            Settings
          </button>
        </div>
      </nav>

      <div className="mt-auto border border-zinc-800/80 bg-zinc-900/50 rounded-2xl p-3">
        <div className="flex items-center gap-3 mb-3">
          <div className="h-9 w-9 bg-zinc-800 rounded-full flex items-center justify-center border border-zinc-700">
            <User className="h-4 w-4 text-zinc-400" />
          </div>
          <div className="flex-1 overflow-hidden">
            <div className="text-sm font-semibold text-zinc-200 truncate">{user.name}</div>
            <div className="text-xs text-zinc-500 truncate capitalize">{user.role}</div>
          </div>
        </div>
        <button
          onClick={logout}
          className="w-full flex items-center justify-center gap-2 rounded-xl bg-zinc-800/80 py-2 text-xs font-medium text-zinc-300 hover:bg-red-500/10 hover:text-red-400 transition-colors border border-transparent hover:border-red-500/20"
        >
          <LogOut className="h-3.5 w-3.5" />
          Sign Out
        </button>
      </div>
    </div>
  );
}
```

## frontend\eslint.config.mjs

```mjs
import { defineConfig, globalIgnores } from "eslint/config";
import nextVitals from "eslint-config-next/core-web-vitals";
import nextTs from "eslint-config-next/typescript";

const eslintConfig = defineConfig([
  ...nextVitals,
  ...nextTs,
  // Override default ignores of eslint-config-next.
  globalIgnores([
    // Default ignores of eslint-config-next:
    ".next/**",
    "out/**",
    "build/**",
    "next-env.d.ts",
  ]),
]);

export default eslintConfig;

```

## frontend\lib\api.ts

```typescript
// lib/api.ts — Frontend API client for the FastAPI backend

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "/api/v1";

// Derive the root URL for health checks.
// If the base URL is relative (/api/v1), health is at /health.
// If absolute (http://localhost:8000/api/v1), strip the path.
const API_ROOT_URL = API_BASE_URL.startsWith("http")
  ? API_BASE_URL.replace(/\/api\/v1\/?$/, "")
  : "";

/**
 * Helper to build auth headers.
 * In DEBUG mode the backend reads `X-Mock-Role` to synthesise a mock user.
 * In production, replace with a real Bearer token.
 */
const getHeaders = (role: string): Record<string, string> => ({
  "Content-Type": "application/json",
  "X-Mock-Role": role,
});

/**
 * Shared fetch wrapper with better error messages.
 */
async function apiFetch<T>(
  url: string,
  options: RequestInit
): Promise<T> {
  let response: Response;
  try {
    response = await fetch(url, options);
  } catch (networkError) {
    throw new Error(
      "Cannot reach the backend server. Make sure the FastAPI backend is running on " +
        API_ROOT_URL
    );
  }

  if (!response.ok) {
    let detail = response.statusText;
    try {
      const body = await response.json();
      detail = body.detail || JSON.stringify(body);
    } catch {
      // response wasn't JSON — use statusText
    }
    throw new Error(`API Error (${response.status}): ${detail}`);
  }

  return response.json() as Promise<T>;
}

// ── Type definitions matching the backend Pydantic models ────────────────────

export type ChatApiResponse = {
  response: string;
  session_id: string;
  intent: string;
  agent_used: string | null;
  approval_required: boolean;
  metadata: Record<string, unknown>;
};

export type ApprovalApiResponse = {
  status: string;
  decision: string;
  session_id: string;
};

export type HealthResponse = {
  status: string;
  db: boolean;
  app?: string;
  env?: string;
  debug?: boolean;
};

// ── API methods ──────────────────────────────────────────────────────────────

export const api = {
  /**
   * Quick check that the backend is reachable.
   */
  health: async (): Promise<HealthResponse> => {
    return apiFetch<HealthResponse>(`${API_ROOT_URL}/health`, {
      method: "GET",
    });
  },

  /**
   * Send a chat message to the LangGraph workflow.
   */
  chat: async (
    message: string,
    sessionId: string | null,
    role: string
  ): Promise<ChatApiResponse> => {
    return apiFetch<ChatApiResponse>(`${API_BASE_URL}/chat`, {
      method: "POST",
      headers: getHeaders(role),
      body: JSON.stringify({
        message,
        session_id: sessionId,
      }),
    });
  },

  /**
   * Submit a manager's approval/rejection decision for a paused workflow.
   */
  approve: async (
    sessionId: string,
    decision: "approved" | "rejected",
    note: string,
    role: string
  ): Promise<ApprovalApiResponse> => {
    return apiFetch<ApprovalApiResponse>(`${API_BASE_URL}/approve`, {
      method: "POST",
      headers: getHeaders(role),
      body: JSON.stringify({
        session_id: sessionId,
        decision,
        note,
      }),
    });
  },
};
```

## frontend\lib\AuthContext.tsx

```tsx
"use client";

import { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { useRouter } from "next/navigation";

type User = {
  id: string;
  name: string;
  role: "employee" | "manager" | "admin";
};

type AuthContextType = {
  user: User | null;
  login: (role: "employee" | "manager") => void;
  logout: () => void;
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const router = useRouter();

  // Load user from local storage on mount
  useEffect(() => {
    const stored = localStorage.getItem("assistant_user");
    if (stored) setUser(JSON.parse(stored));
  }, []);

  const login = (role: "employee" | "manager") => {
    const mockUser: User = {
      id: role === "manager" ? "manager-123" : "emp-456",
      name: role === "manager" ? "Alice (Manager)" : "Bob (Employee)",
      role: role,
    };
    setUser(mockUser);
    localStorage.setItem("assistant_user", JSON.stringify(mockUser));
    router.push("/chat");
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem("assistant_user");
    router.push("/login");
  };

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used within an AuthProvider");
  return context;
};
```

## frontend\next-env.d.ts

```typescript
/// <reference types="next" />
/// <reference types="next/image-types/global" />
import "./.next/dev/types/routes.d.ts";

// NOTE: This file should not be edited
// see https://nextjs.org/docs/app/api-reference/config/typescript for more information.

```

## frontend\next.config.ts

```typescript
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Proxy API requests to the FastAPI backend during development.
  // This avoids CORS issues entirely: the browser only ever talks to
  // localhost:3000, and Next.js forwards /api/v1/* to localhost:8000.
  async rewrites() {
    return [
      {
        source: "/api/v1/:path*",
        destination: "http://localhost:8000/api/v1/:path*",
      },
      {
        source: "/health",
        destination: "http://localhost:8000/health",
      },
    ];
  },
};

export default nextConfig;

```

## frontend\package-lock.json

```json
{
  "name": "frontend",
  "version": "0.1.0",
  "lockfileVersion": 3,
  "requires": true,
  "packages": {
    "": {
      "name": "frontend",
      "version": "0.1.0",
      "dependencies": {
        "framer-motion": "^12.38.0",
        "lucide-react": "^1.14.0",
        "next": "16.2.4",
        "react": "19.2.4",
        "react-dom": "19.2.4"
      },
      "devDependencies": {
        "@tailwindcss/postcss": "^4",
        "@types/node": "^20",
        "@types/react": "^19",
        "@types/react-dom": "^19",
        "eslint": "^9",
        "eslint-config-next": "16.2.4",
        "tailwindcss": "^4",
        "typescript": "^5"
      }
    },
    "node_modules/@alloc/quick-lru": {
      "version": "5.2.0",
      "resolved": "https://registry.npmjs.org/@alloc/quick-lru/-/quick-lru-5.2.0.tgz",
      "integrity": "sha512-UrcABB+4bUrFABwbluTIBErXwvbsU/V7TZWfmbgJfbkwiBuziS9gxdODUyuiecfdGQ85jglMW6juS3+z5TsKLw==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=10"
      },
      "funding": {
        "url": "https://github.com/sponsors/sindresorhus"
      }
    },
    "node_modules/@babel/code-frame": {
      "version": "7.29.0",
      "resolved": "https://registry.npmjs.org/@babel/code-frame/-/code-frame-7.29.0.tgz",
      "integrity": "sha512-9NhCeYjq9+3uxgdtp20LSiJXJvN0FeCtNGpJxuMFZ1Kv3cWUNb6DOhJwUvcVCzKGR66cw4njwM6hrJLqgOwbcw==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "@babel/helper-validator-identifier": "^7.28.5",
        "js-tokens": "^4.0.0",
        "picocolors": "^1.1.1"
      },
      "engines": {
        "node": ">=6.9.0"
      }
    },
    "node_modules/@babel/compat-data": {
      "version": "7.29.3",
      "resolved": "https://registry.npmjs.org/@babel/compat-data/-/compat-data-7.29.3.tgz",
      "integrity": "sha512-LIVqM46zQWZhj17qA8wb4nW/ixr2y1Nw+r1etiAWgRM6U1IqP+LNhL1yg440jYZR72jCWcWbLWzIosH+uP1fqg==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=6.9.0"
      }
    },
    "node_modules/@babel/core": {
      "version": "7.29.0",
      "resolved": "https://registry.npmjs.org/@babel/core/-/core-7.29.0.tgz",
      "integrity": "sha512-CGOfOJqWjg2qW/Mb6zNsDm+u5vFQ8DxXfbM09z69p5Z6+mE1ikP2jUXw+j42Pf1XTYED2Rni5f95npYeuwMDQA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "@babel/code-frame": "^7.29.0",
        "@babel/generator": "^7.29.0",
        "@babel/helper-compilation-targets": "^7.28.6",
        "@babel/helper-module-transforms": "^7.28.6",
        "@babel/helpers": "^7.28.6",
        "@babel/parser": "^7.29.0",
        "@babel/template": "^7.28.6",
        "@babel/traverse": "^7.29.0",
        "@babel/types": "^7.29.0",
        "@jridgewell/remapping": "^2.3.5",
        "convert-source-map": "^2.0.0",
        "debug": "^4.1.0",
        "gensync": "^1.0.0-beta.2",
        "json5": "^2.2.3",
        "semver": "^6.3.1"
      },
      "engines": {
        "node": ">=6.9.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/babel"
      }
    },
    "node_modules/@babel/generator": {
      "version": "7.29.1",
      "resolved": "https://registry.npmjs.org/@babel/generator/-/generator-7.29.1.tgz",
      "integrity": "sha512-qsaF+9Qcm2Qv8SRIMMscAvG4O3lJ0F1GuMo5HR/Bp02LopNgnZBC/EkbevHFeGs4ls/oPz9v+Bsmzbkbe+0dUw==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "@babel/parser": "^7.29.0",
        "@babel/types": "^7.29.0",
        "@jridgewell/gen-mapping": "^0.3.12",
        "@jridgewell/trace-mapping": "^0.3.28",
        "jsesc": "^3.0.2"
      },
      "engines": {
        "node": ">=6.9.0"
      }
    },
    "node_modules/@babel/helper-compilation-targets": {
      "version": "7.28.6",
      "resolved": "https://registry.npmjs.org/@babel/helper-compilation-targets/-/helper-compilation-targets-7.28.6.tgz",
      "integrity": "sha512-JYtls3hqi15fcx5GaSNL7SCTJ2MNmjrkHXg4FSpOA/grxK8KwyZ5bubHsCq8FXCkua6xhuaaBit+3b7+VZRfcA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "@babel/compat-data": "^7.28.6",
        "@babel/helper-validator-option": "^7.27.1",
        "browserslist": "^4.24.0",
        "lru-cache": "^5.1.1",
        "semver": "^6.3.1"
      },
      "engines": {
        "node": ">=6.9.0"
      }
    },
    "node_modules/@babel/helper-globals": {
      "version": "7.28.0",
      "resolved": "https://registry.npmjs.org/@babel/helper-globals/-/helper-globals-7.28.0.tgz",
      "integrity": "sha512-+W6cISkXFa1jXsDEdYA8HeevQT/FULhxzR99pxphltZcVaugps53THCeiWA8SguxxpSp3gKPiuYfSWopkLQ4hw==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=6.9.0"
      }
    },
    "node_modules/@babel/helper-module-imports": {
      "version": "7.28.6",
      "resolved": "https://registry.npmjs.org/@babel/helper-module-imports/-/helper-module-imports-7.28.6.tgz",
      "integrity": "sha512-l5XkZK7r7wa9LucGw9LwZyyCUscb4x37JWTPz7swwFE/0FMQAGpiWUZn8u9DzkSBWEcK25jmvubfpw2dnAMdbw==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "@babel/traverse": "^7.28.6",
        "@babel/types": "^7.28.6"
      },
      "engines": {
        "node": ">=6.9.0"
      }
    },
    "node_modules/@babel/helper-module-transforms": {
      "version": "7.28.6",
      "resolved": "https://registry.npmjs.org/@babel/helper-module-transforms/-/helper-module-transforms-7.28.6.tgz",
      "integrity": "sha512-67oXFAYr2cDLDVGLXTEABjdBJZ6drElUSI7WKp70NrpyISso3plG9SAGEF6y7zbha/wOzUByWWTJvEDVNIUGcA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "@babel/helper-module-imports": "^7.28.6",
        "@babel/helper-validator-identifier": "^7.28.5",
        "@babel/traverse": "^7.28.6"
      },
      "engines": {
        "node": ">=6.9.0"
      },
      "peerDependencies": {
        "@babel/core": "^7.0.0"
      }
    },
    "node_modules/@babel/helper-string-parser": {
      "version": "7.27.1",
      "resolved": "https://registry.npmjs.org/@babel/helper-string-parser/-/helper-string-parser-7.27.1.tgz",
      "integrity": "sha512-qMlSxKbpRlAridDExk92nSobyDdpPijUq2DW6oDnUqd0iOGxmQjyqhMIihI9+zv4LPyZdRje2cavWPbCbWm3eA==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=6.9.0"
      }
    },
    "node_modules/@babel/helper-validator-identifier": {
      "version": "7.28.5",
      "resolved": "https://registry.npmjs.org/@babel/helper-validator-identifier/-/helper-validator-identifier-7.28.5.tgz",
      "integrity": "sha512-qSs4ifwzKJSV39ucNjsvc6WVHs6b7S03sOh2OcHF9UHfVPqWWALUsNUVzhSBiItjRZoLHx7nIarVjqKVusUZ1Q==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=6.9.0"
      }
    },
    "node_modules/@babel/helper-validator-option": {
      "version": "7.27.1",
      "resolved": "https://registry.npmjs.org/@babel/helper-validator-option/-/helper-validator-option-7.27.1.tgz",
      "integrity": "sha512-YvjJow9FxbhFFKDSuFnVCe2WxXk1zWc22fFePVNEaWJEu8IrZVlda6N0uHwzZrUM1il7NC9Mlp4MaJYbYd9JSg==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=6.9.0"
      }
    },
    "node_modules/@babel/helpers": {
      "version": "7.29.2",
      "resolved": "https://registry.npmjs.org/@babel/helpers/-/helpers-7.29.2.tgz",
      "integrity": "sha512-HoGuUs4sCZNezVEKdVcwqmZN8GoHirLUcLaYVNBK2J0DadGtdcqgr3BCbvH8+XUo4NGjNl3VOtSjEKNzqfFgKw==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "@babel/template": "^7.28.6",
        "@babel/types": "^7.29.0"
      },
      "engines": {
        "node": ">=6.9.0"
      }
    },
    "node_modules/@babel/parser": {
      "version": "7.29.3",
      "resolved": "https://registry.npmjs.org/@babel/parser/-/parser-7.29.3.tgz",
      "integrity": "sha512-b3ctpQwp+PROvU/cttc4OYl4MzfJUWy6FZg+PMXfzmt/+39iHVF0sDfqay8TQM3JA2EUOyKcFZt75jWriQijsA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "@babel/types": "^7.29.0"
      },
      "bin": {
        "parser": "bin/babel-parser.js"
      },
      "engines": {
        "node": ">=6.0.0"
      }
    },
    "node_modules/@babel/template": {
      "version": "7.28.6",
      "resolved": "https://registry.npmjs.org/@babel/template/-/template-7.28.6.tgz",
      "integrity": "sha512-YA6Ma2KsCdGb+WC6UpBVFJGXL58MDA6oyONbjyF/+5sBgxY/dwkhLogbMT2GXXyU84/IhRw/2D1Os1B/giz+BQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "@babel/code-frame": "^7.28.6",
        "@babel/parser": "^7.28.6",
        "@babel/types": "^7.28.6"
      },
      "engines": {
        "node": ">=6.9.0"
      }
    },
    "node_modules/@babel/traverse": {
      "version": "7.29.0",
      "resolved": "https://registry.npmjs.org/@babel/traverse/-/traverse-7.29.0.tgz",
      "integrity": "sha512-4HPiQr0X7+waHfyXPZpWPfWL/J7dcN1mx9gL6WdQVMbPnF3+ZhSMs8tCxN7oHddJE9fhNE7+lxdnlyemKfJRuA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "@babel/code-frame": "^7.29.0",
        "@babel/generator": "^7.29.0",
        "@babel/helper-globals": "^7.28.0",
        "@babel/parser": "^7.29.0",
        "@babel/template": "^7.28.6",
        "@babel/types": "^7.29.0",
        "debug": "^4.3.1"
      },
      "engines": {
        "node": ">=6.9.0"
      }
    },
    "node_modules/@babel/types": {
      "version": "7.29.0",
      "resolved": "https://registry.npmjs.org/@babel/types/-/types-7.29.0.tgz",
      "integrity": "sha512-LwdZHpScM4Qz8Xw2iKSzS+cfglZzJGvofQICy7W7v4caru4EaAmyUuO6BGrbyQ2mYV11W0U8j5mBhd14dd3B0A==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "@babel/helper-string-parser": "^7.27.1",
        "@babel/helper-validator-identifier": "^7.28.5"
      },
      "engines": {
        "node": ">=6.9.0"
      }
    },
    "node_modules/@emnapi/core": {
      "version": "1.10.0",
      "resolved": "https://registry.npmjs.org/@emnapi/core/-/core-1.10.0.tgz",
      "integrity": "sha512-yq6OkJ4p82CAfPl0u9mQebQHKPJkY7WrIuk205cTYnYe+k2Z8YBh11FrbRG/H6ihirqcacOgl2BIO8oyMQLeXw==",
      "dev": true,
      "license": "MIT",
      "optional": true,
      "dependencies": {
        "@emnapi/wasi-threads": "1.2.1",
        "tslib": "^2.4.0"
      }
    },
    "node_modules/@emnapi/runtime": {
      "version": "1.10.0",
      "resolved": "https://registry.npmjs.org/@emnapi/runtime/-/runtime-1.10.0.tgz",
      "integrity": "sha512-ewvYlk86xUoGI0zQRNq/mC+16R1QeDlKQy21Ki3oSYXNgLb45GV1P6A0M+/s6nyCuNDqe5VpaY84BzXGwVbwFA==",
      "license": "MIT",
      "optional": true,
      "dependencies": {
        "tslib": "^2.4.0"
      }
    },
    "node_modules/@emnapi/wasi-threads": {
      "version": "1.2.1",
      "resolved": "https://registry.npmjs.org/@emnapi/wasi-threads/-/wasi-threads-1.2.1.tgz",
      "integrity": "sha512-uTII7OYF+/Mes/MrcIOYp5yOtSMLBWSIoLPpcgwipoiKbli6k322tcoFsxoIIxPDqW01SQGAgko4EzZi2BNv2w==",
      "dev": true,
      "license": "MIT",
      "optional": true,
      "dependencies": {
        "tslib": "^2.4.0"
      }
    },
    "node_modules/@eslint-community/eslint-utils": {
      "version": "4.9.1",
      "resolved": "https://registry.npmjs.org/@eslint-community/eslint-utils/-/eslint-utils-4.9.1.tgz",
      "integrity": "sha512-phrYmNiYppR7znFEdqgfWHXR6NCkZEK7hwWDHZUjit/2/U0r6XvkDl0SYnoM51Hq7FhCGdLDT6zxCCOY1hexsQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "eslint-visitor-keys": "^3.4.3"
      },
      "engines": {
        "node": "^12.22.0 || ^14.17.0 || >=16.0.0"
      },
      "funding": {
        "url": "https://opencollective.com/eslint"
      },
      "peerDependencies": {
        "eslint": "^6.0.0 || ^7.0.0 || >=8.0.0"
      }
    },
    "node_modules/@eslint-community/eslint-utils/node_modules/eslint-visitor-keys": {
      "version": "3.4.3",
      "resolved": "https://registry.npmjs.org/eslint-visitor-keys/-/eslint-visitor-keys-3.4.3.tgz",
      "integrity": "sha512-wpc+LXeiyiisxPlEkUzU6svyS1frIO3Mgxj1fdy7Pm8Ygzguax2N3Fa/D/ag1WqbOprdI+uY6wMUl8/a2G+iag==",
      "dev": true,
      "license": "Apache-2.0",
      "engines": {
        "node": "^12.22.0 || ^14.17.0 || >=16.0.0"
      },
      "funding": {
        "url": "https://opencollective.com/eslint"
      }
    },
    "node_modules/@eslint-community/regexpp": {
      "version": "4.12.2",
      "resolved": "https://registry.npmjs.org/@eslint-community/regexpp/-/regexpp-4.12.2.tgz",
      "integrity": "sha512-EriSTlt5OC9/7SXkRSCAhfSxxoSUgBm33OH+IkwbdpgoqsSsUg7y3uh+IICI/Qg4BBWr3U2i39RpmycbxMq4ew==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": "^12.0.0 || ^14.0.0 || >=16.0.0"
      }
    },
    "node_modules/@eslint/config-array": {
      "version": "0.21.2",
      "resolved": "https://registry.npmjs.org/@eslint/config-array/-/config-array-0.21.2.tgz",
      "integrity": "sha512-nJl2KGTlrf9GjLimgIru+V/mzgSK0ABCDQRvxw5BjURL7WfH5uoWmizbH7QB6MmnMBd8cIC9uceWnezL1VZWWw==",
      "dev": true,
      "license": "Apache-2.0",
      "dependencies": {
        "@eslint/object-schema": "^2.1.7",
        "debug": "^4.3.1",
        "minimatch": "^3.1.5"
      },
      "engines": {
        "node": "^18.18.0 || ^20.9.0 || >=21.1.0"
      }
    },
    "node_modules/@eslint/config-helpers": {
      "version": "0.4.2",
      "resolved": "https://registry.npmjs.org/@eslint/config-helpers/-/config-helpers-0.4.2.tgz",
      "integrity": "sha512-gBrxN88gOIf3R7ja5K9slwNayVcZgK6SOUORm2uBzTeIEfeVaIhOpCtTox3P6R7o2jLFwLFTLnC7kU/RGcYEgw==",
      "dev": true,
      "license": "Apache-2.0",
      "dependencies": {
        "@eslint/core": "^0.17.0"
      },
      "engines": {
        "node": "^18.18.0 || ^20.9.0 || >=21.1.0"
      }
    },
    "node_modules/@eslint/core": {
      "version": "0.17.0",
      "resolved": "https://registry.npmjs.org/@eslint/core/-/core-0.17.0.tgz",
      "integrity": "sha512-yL/sLrpmtDaFEiUj1osRP4TI2MDz1AddJL+jZ7KSqvBuliN4xqYY54IfdN8qD8Toa6g1iloph1fxQNkjOxrrpQ==",
      "dev": true,
      "license": "Apache-2.0",
      "dependencies": {
        "@types/json-schema": "^7.0.15"
      },
      "engines": {
        "node": "^18.18.0 || ^20.9.0 || >=21.1.0"
      }
    },
    "node_modules/@eslint/eslintrc": {
      "version": "3.3.5",
      "resolved": "https://registry.npmjs.org/@eslint/eslintrc/-/eslintrc-3.3.5.tgz",
      "integrity": "sha512-4IlJx0X0qftVsN5E+/vGujTRIFtwuLbNsVUe7TO6zYPDR1O6nFwvwhIKEKSrl6dZchmYBITazxKoUYOjdtjlRg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "ajv": "^6.14.0",
        "debug": "^4.3.2",
        "espree": "^10.0.1",
        "globals": "^14.0.0",
        "ignore": "^5.2.0",
        "import-fresh": "^3.2.1",
        "js-yaml": "^4.1.1",
        "minimatch": "^3.1.5",
        "strip-json-comments": "^3.1.1"
      },
      "engines": {
        "node": "^18.18.0 || ^20.9.0 || >=21.1.0"
      },
      "funding": {
        "url": "https://opencollective.com/eslint"
      }
    },
    "node_modules/@eslint/js": {
      "version": "9.39.4",
      "resolved": "https://registry.npmjs.org/@eslint/js/-/js-9.39.4.tgz",
      "integrity": "sha512-nE7DEIchvtiFTwBw4Lfbu59PG+kCofhjsKaCWzxTpt4lfRjRMqG6uMBzKXuEcyXhOHoUp9riAm7/aWYGhXZ9cw==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": "^18.18.0 || ^20.9.0 || >=21.1.0"
      },
      "funding": {
        "url": "https://eslint.org/donate"
      }
    },
    "node_modules/@eslint/object-schema": {
      "version": "2.1.7",
      "resolved": "https://registry.npmjs.org/@eslint/object-schema/-/object-schema-2.1.7.tgz",
      "integrity": "sha512-VtAOaymWVfZcmZbp6E2mympDIHvyjXs/12LqWYjVw6qjrfF+VK+fyG33kChz3nnK+SU5/NeHOqrTEHS8sXO3OA==",
      "dev": true,
      "license": "Apache-2.0",
      "engines": {
        "node": "^18.18.0 || ^20.9.0 || >=21.1.0"
      }
    },
    "node_modules/@eslint/plugin-kit": {
      "version": "0.4.1",
      "resolved": "https://registry.npmjs.org/@eslint/plugin-kit/-/plugin-kit-0.4.1.tgz",
      "integrity": "sha512-43/qtrDUokr7LJqoF2c3+RInu/t4zfrpYdoSDfYyhg52rwLV6TnOvdG4fXm7IkSB3wErkcmJS9iEhjVtOSEjjA==",
      "dev": true,
      "license": "Apache-2.0",
      "dependencies": {
        "@eslint/core": "^0.17.0",
        "levn": "^0.4.1"
      },
      "engines": {
        "node": "^18.18.0 || ^20.9.0 || >=21.1.0"
      }
    },
    "node_modules/@humanfs/core": {
      "version": "0.19.2",
      "resolved": "https://registry.npmjs.org/@humanfs/core/-/core-0.19.2.tgz",
      "integrity": "sha512-UhXNm+CFMWcbChXywFwkmhqjs3PRCmcSa/hfBgLIb7oQ5HNb1wS0icWsGtSAUNgefHeI+eBrA8I1fxmbHsGdvA==",
      "dev": true,
      "license": "Apache-2.0",
      "dependencies": {
        "@humanfs/types": "^0.15.0"
      },
      "engines": {
        "node": ">=18.18.0"
      }
    },
    "node_modules/@humanfs/node": {
      "version": "0.16.8",
      "resolved": "https://registry.npmjs.org/@humanfs/node/-/node-0.16.8.tgz",
      "integrity": "sha512-gE1eQNZ3R++kTzFUpdGlpmy8kDZD/MLyHqDwqjkVQI0JMdI1D51sy1H958PNXYkM2rAac7e5/CnIKZrHtPh3BQ==",
      "dev": true,
      "license": "Apache-2.0",
      "dependencies": {
        "@humanfs/core": "^0.19.2",
        "@humanfs/types": "^0.15.0",
        "@humanwhocodes/retry": "^0.4.0"
      },
      "engines": {
        "node": ">=18.18.0"
      }
    },
    "node_modules/@humanfs/types": {
      "version": "0.15.0",
      "resolved": "https://registry.npmjs.org/@humanfs/types/-/types-0.15.0.tgz",
      "integrity": "sha512-ZZ1w0aoQkwuUuC7Yf+7sdeaNfqQiiLcSRbfI08oAxqLtpXQr9AIVX7Ay7HLDuiLYAaFPu8oBYNq/QIi9URHJ3Q==",
      "dev": true,
      "license": "Apache-2.0",
      "engines": {
        "node": ">=18.18.0"
      }
    },
    "node_modules/@humanwhocodes/module-importer": {
      "version": "1.0.1",
      "resolved": "https://registry.npmjs.org/@humanwhocodes/module-importer/-/module-importer-1.0.1.tgz",
      "integrity": "sha512-bxveV4V8v5Yb4ncFTT3rPSgZBOpCkjfK0y4oVVVJwIuDVBRMDXrPyXRL988i5ap9m9bnyEEjWfm5WkBmtffLfA==",
      "dev": true,
      "license": "Apache-2.0",
      "engines": {
        "node": ">=12.22"
      },
      "funding": {
        "type": "github",
        "url": "https://github.com/sponsors/nzakas"
      }
    },
    "node_modules/@humanwhocodes/retry": {
      "version": "0.4.3",
      "resolved": "https://registry.npmjs.org/@humanwhocodes/retry/-/retry-0.4.3.tgz",
      "integrity": "sha512-bV0Tgo9K4hfPCek+aMAn81RppFKv2ySDQeMoSZuvTASywNTnVJCArCZE2FWqpvIatKu7VMRLWlR1EazvVhDyhQ==",
      "dev": true,
      "license": "Apache-2.0",
      "engines": {
        "node": ">=18.18"
      },
      "funding": {
        "type": "github",
        "url": "https://github.com/sponsors/nzakas"
      }
    },
    "node_modules/@img/colour": {
      "version": "1.1.0",
      "resolved": "https://registry.npmjs.org/@img/colour/-/colour-1.1.0.tgz",
      "integrity": "sha512-Td76q7j57o/tLVdgS746cYARfSyxk8iEfRxewL9h4OMzYhbW4TAcppl0mT4eyqXddh6L/jwoM75mo7ixa/pCeQ==",
      "license": "MIT",
      "optional": true,
      "engines": {
        "node": ">=18"
      }
    },
    "node_modules/@img/sharp-darwin-arm64": {
      "version": "0.34.5",
      "resolved": "https://registry.npmjs.org/@img/sharp-darwin-arm64/-/sharp-darwin-arm64-0.34.5.tgz",
      "integrity": "sha512-imtQ3WMJXbMY4fxb/Ndp6HBTNVtWCUI0WdobyheGf5+ad6xX8VIDO8u2xE4qc/fr08CKG/7dDseFtn6M6g/r3w==",
      "cpu": [
        "arm64"
      ],
      "license": "Apache-2.0",
      "optional": true,
      "os": [
        "darwin"
      ],
      "engines": {
        "node": "^18.17.0 || ^20.3.0 || >=21.0.0"
      },
      "funding": {
        "url": "https://opencollective.com/libvips"
      },
      "optionalDependencies": {
        "@img/sharp-libvips-darwin-arm64": "1.2.4"
      }
    },
    "node_modules/@img/sharp-darwin-x64": {
      "version": "0.34.5",
      "resolved": "https://registry.npmjs.org/@img/sharp-darwin-x64/-/sharp-darwin-x64-0.34.5.tgz",
      "integrity": "sha512-YNEFAF/4KQ/PeW0N+r+aVVsoIY0/qxxikF2SWdp+NRkmMB7y9LBZAVqQ4yhGCm/H3H270OSykqmQMKLBhBJDEw==",
      "cpu": [
        "x64"
      ],
      "license": "Apache-2.0",
      "optional": true,
      "os": [
        "darwin"
      ],
      "engines": {
        "node": "^18.17.0 || ^20.3.0 || >=21.0.0"
      },
      "funding": {
        "url": "https://opencollective.com/libvips"
      },
      "optionalDependencies": {
        "@img/sharp-libvips-darwin-x64": "1.2.4"
      }
    },
    "node_modules/@img/sharp-libvips-darwin-arm64": {
      "version": "1.2.4",
      "resolved": "https://registry.npmjs.org/@img/sharp-libvips-darwin-arm64/-/sharp-libvips-darwin-arm64-1.2.4.tgz",
      "integrity": "sha512-zqjjo7RatFfFoP0MkQ51jfuFZBnVE2pRiaydKJ1G/rHZvnsrHAOcQALIi9sA5co5xenQdTugCvtb1cuf78Vf4g==",
      "cpu": [
        "arm64"
      ],
      "license": "LGPL-3.0-or-later",
      "optional": true,
      "os": [
        "darwin"
      ],
      "funding": {
        "url": "https://opencollective.com/libvips"
      }
    },
    "node_modules/@img/sharp-libvips-darwin-x64": {
      "version": "1.2.4",
      "resolved": "https://registry.npmjs.org/@img/sharp-libvips-darwin-x64/-/sharp-libvips-darwin-x64-1.2.4.tgz",
      "integrity": "sha512-1IOd5xfVhlGwX+zXv2N93k0yMONvUlANylbJw1eTah8K/Jtpi15KC+WSiaX/nBmbm2HxRM1gZ0nSdjSsrZbGKg==",
      "cpu": [
        "x64"
      ],
      "license": "LGPL-3.0-or-later",
      "optional": true,
      "os": [
        "darwin"
      ],
      "funding": {
        "url": "https://opencollective.com/libvips"
      }
    },
    "node_modules/@img/sharp-libvips-linux-arm": {
      "version": "1.2.4",
      "resolved": "https://registry.npmjs.org/@img/sharp-libvips-linux-arm/-/sharp-libvips-linux-arm-1.2.4.tgz",
      "integrity": "sha512-bFI7xcKFELdiNCVov8e44Ia4u2byA+l3XtsAj+Q8tfCwO6BQ8iDojYdvoPMqsKDkuoOo+X6HZA0s0q11ANMQ8A==",
      "cpu": [
        "arm"
      ],
      "license": "LGPL-3.0-or-later",
      "optional": true,
      "os": [
        "linux"
      ],
      "funding": {
        "url": "https://opencollective.com/libvips"
      }
    },
    "node_modules/@img/sharp-libvips-linux-arm64": {
      "version": "1.2.4",
      "resolved": "https://registry.npmjs.org/@img/sharp-libvips-linux-arm64/-/sharp-libvips-linux-arm64-1.2.4.tgz",
      "integrity": "sha512-excjX8DfsIcJ10x1Kzr4RcWe1edC9PquDRRPx3YVCvQv+U5p7Yin2s32ftzikXojb1PIFc/9Mt28/y+iRklkrw==",
      "cpu": [
        "arm64"
      ],
      "license": "LGPL-3.0-or-later",
      "optional": true,
      "os": [
        "linux"
      ],
      "funding": {
        "url": "https://opencollective.com/libvips"
      }
    },
    "node_modules/@img/sharp-libvips-linux-ppc64": {
      "version": "1.2.4",
      "resolved": "https://registry.npmjs.org/@img/sharp-libvips-linux-ppc64/-/sharp-libvips-linux-ppc64-1.2.4.tgz",
      "integrity": "sha512-FMuvGijLDYG6lW+b/UvyilUWu5Ayu+3r2d1S8notiGCIyYU/76eig1UfMmkZ7vwgOrzKzlQbFSuQfgm7GYUPpA==",
      "cpu": [
        "ppc64"
      ],
      "license": "LGPL-3.0-or-later",
      "optional": true,
      "os": [
        "linux"
      ],
      "funding": {
        "url": "https://opencollective.com/libvips"
      }
    },
    "node_modules/@img/sharp-libvips-linux-riscv64": {
      "version": "1.2.4",
      "resolved": "https://registry.npmjs.org/@img/sharp-libvips-linux-riscv64/-/sharp-libvips-linux-riscv64-1.2.4.tgz",
      "integrity": "sha512-oVDbcR4zUC0ce82teubSm+x6ETixtKZBh/qbREIOcI3cULzDyb18Sr/Wcyx7NRQeQzOiHTNbZFF1UwPS2scyGA==",
      "cpu": [
        "riscv64"
      ],
      "license": "LGPL-3.0-or-later",
      "optional": true,
      "os": [
        "linux"
      ],
      "funding": {
        "url": "https://opencollective.com/libvips"
      }
    },
    "node_modules/@img/sharp-libvips-linux-s390x": {
      "version": "1.2.4",
      "resolved": "https://registry.npmjs.org/@img/sharp-libvips-linux-s390x/-/sharp-libvips-linux-s390x-1.2.4.tgz",
      "integrity": "sha512-qmp9VrzgPgMoGZyPvrQHqk02uyjA0/QrTO26Tqk6l4ZV0MPWIW6LTkqOIov+J1yEu7MbFQaDpwdwJKhbJvuRxQ==",
      "cpu": [
        "s390x"
      ],
      "license": "LGPL-3.0-or-later",
      "optional": true,
      "os": [
        "linux"
      ],
      "funding": {
        "url": "https://opencollective.com/libvips"
      }
    },
    "node_modules/@img/sharp-libvips-linux-x64": {
      "version": "1.2.4",
      "resolved": "https://registry.npmjs.org/@img/sharp-libvips-linux-x64/-/sharp-libvips-linux-x64-1.2.4.tgz",
      "integrity": "sha512-tJxiiLsmHc9Ax1bz3oaOYBURTXGIRDODBqhveVHonrHJ9/+k89qbLl0bcJns+e4t4rvaNBxaEZsFtSfAdquPrw==",
      "cpu": [
        "x64"
      ],
      "license": "LGPL-3.0-or-later",
      "optional": true,
      "os": [
        "linux"
      ],
      "funding": {
        "url": "https://opencollective.com/libvips"
      }
    },
    "node_modules/@img/sharp-libvips-linuxmusl-arm64": {
      "version": "1.2.4",
      "resolved": "https://registry.npmjs.org/@img/sharp-libvips-linuxmusl-arm64/-/sharp-libvips-linuxmusl-arm64-1.2.4.tgz",
      "integrity": "sha512-FVQHuwx1IIuNow9QAbYUzJ+En8KcVm9Lk5+uGUQJHaZmMECZmOlix9HnH7n1TRkXMS0pGxIJokIVB9SuqZGGXw==",
      "cpu": [
        "arm64"
      ],
      "license": "LGPL-3.0-or-later",
      "optional": true,
      "os": [
        "linux"
      ],
      "funding": {
        "url": "https://opencollective.com/libvips"
      }
    },
    "node_modules/@img/sharp-libvips-linuxmusl-x64": {
      "version": "1.2.4",
      "resolved": "https://registry.npmjs.org/@img/sharp-libvips-linuxmusl-x64/-/sharp-libvips-linuxmusl-x64-1.2.4.tgz",
      "integrity": "sha512-+LpyBk7L44ZIXwz/VYfglaX/okxezESc6UxDSoyo2Ks6Jxc4Y7sGjpgU9s4PMgqgjj1gZCylTieNamqA1MF7Dg==",
      "cpu": [
        "x64"
      ],
      "license": "LGPL-3.0-or-later",
      "optional": true,
      "os": [
        "linux"
      ],
      "funding": {
        "url": "https://opencollective.com/libvips"
      }
    },
    "node_modules/@img/sharp-linux-arm": {
      "version": "0.34.5",
      "resolved": "https://registry.npmjs.org/@img/sharp-linux-arm/-/sharp-linux-arm-0.34.5.tgz",
      "integrity": "sha512-9dLqsvwtg1uuXBGZKsxem9595+ujv0sJ6Vi8wcTANSFpwV/GONat5eCkzQo/1O6zRIkh0m/8+5BjrRr7jDUSZw==",
      "cpu": [
        "arm"
      ],
      "license": "Apache-2.0",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": "^18.17.0 || ^20.3.0 || >=21.0.0"
      },
      "funding": {
        "url": "https://opencollective.com/libvips"
      },
      "optionalDependencies": {
        "@img/sharp-libvips-linux-arm": "1.2.4"
      }
    },
    "node_modules/@img/sharp-linux-arm64": {
      "version": "0.34.5",
      "resolved": "https://registry.npmjs.org/@img/sharp-linux-arm64/-/sharp-linux-arm64-0.34.5.tgz",
      "integrity": "sha512-bKQzaJRY/bkPOXyKx5EVup7qkaojECG6NLYswgktOZjaXecSAeCWiZwwiFf3/Y+O1HrauiE3FVsGxFg8c24rZg==",
      "cpu": [
        "arm64"
      ],
      "license": "Apache-2.0",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": "^18.17.0 || ^20.3.0 || >=21.0.0"
      },
      "funding": {
        "url": "https://opencollective.com/libvips"
      },
      "optionalDependencies": {
        "@img/sharp-libvips-linux-arm64": "1.2.4"
      }
    },
    "node_modules/@img/sharp-linux-ppc64": {
      "version": "0.34.5",
      "resolved": "https://registry.npmjs.org/@img/sharp-linux-ppc64/-/sharp-linux-ppc64-0.34.5.tgz",
      "integrity": "sha512-7zznwNaqW6YtsfrGGDA6BRkISKAAE1Jo0QdpNYXNMHu2+0dTrPflTLNkpc8l7MUP5M16ZJcUvysVWWrMefZquA==",
      "cpu": [
        "ppc64"
      ],
      "license": "Apache-2.0",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": "^18.17.0 || ^20.3.0 || >=21.0.0"
      },
      "funding": {
        "url": "https://opencollective.com/libvips"
      },
      "optionalDependencies": {
        "@img/sharp-libvips-linux-ppc64": "1.2.4"
      }
    },
    "node_modules/@img/sharp-linux-riscv64": {
      "version": "0.34.5",
      "resolved": "https://registry.npmjs.org/@img/sharp-linux-riscv64/-/sharp-linux-riscv64-0.34.5.tgz",
      "integrity": "sha512-51gJuLPTKa7piYPaVs8GmByo7/U7/7TZOq+cnXJIHZKavIRHAP77e3N2HEl3dgiqdD/w0yUfiJnII77PuDDFdw==",
      "cpu": [
        "riscv64"
      ],
      "license": "Apache-2.0",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": "^18.17.0 || ^20.3.0 || >=21.0.0"
      },
      "funding": {
        "url": "https://opencollective.com/libvips"
      },
      "optionalDependencies": {
        "@img/sharp-libvips-linux-riscv64": "1.2.4"
      }
    },
    "node_modules/@img/sharp-linux-s390x": {
      "version": "0.34.5",
      "resolved": "https://registry.npmjs.org/@img/sharp-linux-s390x/-/sharp-linux-s390x-0.34.5.tgz",
      "integrity": "sha512-nQtCk0PdKfho3eC5MrbQoigJ2gd1CgddUMkabUj+rBevs8tZ2cULOx46E7oyX+04WGfABgIwmMC0VqieTiR4jg==",
      "cpu": [
        "s390x"
      ],
      "license": "Apache-2.0",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": "^18.17.0 || ^20.3.0 || >=21.0.0"
      },
      "funding": {
        "url": "https://opencollective.com/libvips"
      },
      "optionalDependencies": {
        "@img/sharp-libvips-linux-s390x": "1.2.4"
      }
    },
    "node_modules/@img/sharp-linux-x64": {
      "version": "0.34.5",
      "resolved": "https://registry.npmjs.org/@img/sharp-linux-x64/-/sharp-linux-x64-0.34.5.tgz",
      "integrity": "sha512-MEzd8HPKxVxVenwAa+JRPwEC7QFjoPWuS5NZnBt6B3pu7EG2Ge0id1oLHZpPJdn3OQK+BQDiw9zStiHBTJQQQQ==",
      "cpu": [
        "x64"
      ],
      "license": "Apache-2.0",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": "^18.17.0 || ^20.3.0 || >=21.0.0"
      },
      "funding": {
        "url": "https://opencollective.com/libvips"
      },
      "optionalDependencies": {
        "@img/sharp-libvips-linux-x64": "1.2.4"
      }
    },
    "node_modules/@img/sharp-linuxmusl-arm64": {
      "version": "0.34.5",
      "resolved": "https://registry.npmjs.org/@img/sharp-linuxmusl-arm64/-/sharp-linuxmusl-arm64-0.34.5.tgz",
      "integrity": "sha512-fprJR6GtRsMt6Kyfq44IsChVZeGN97gTD331weR1ex1c1rypDEABN6Tm2xa1wE6lYb5DdEnk03NZPqA7Id21yg==",
      "cpu": [
        "arm64"
      ],
      "license": "Apache-2.0",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": "^18.17.0 || ^20.3.0 || >=21.0.0"
      },
      "funding": {
        "url": "https://opencollective.com/libvips"
      },
      "optionalDependencies": {
        "@img/sharp-libvips-linuxmusl-arm64": "1.2.4"
      }
    },
    "node_modules/@img/sharp-linuxmusl-x64": {
      "version": "0.34.5",
      "resolved": "https://registry.npmjs.org/@img/sharp-linuxmusl-x64/-/sharp-linuxmusl-x64-0.34.5.tgz",
      "integrity": "sha512-Jg8wNT1MUzIvhBFxViqrEhWDGzqymo3sV7z7ZsaWbZNDLXRJZoRGrjulp60YYtV4wfY8VIKcWidjojlLcWrd8Q==",
      "cpu": [
        "x64"
      ],
      "license": "Apache-2.0",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": "^18.17.0 || ^20.3.0 || >=21.0.0"
      },
      "funding": {
        "url": "https://opencollective.com/libvips"
      },
      "optionalDependencies": {
        "@img/sharp-libvips-linuxmusl-x64": "1.2.4"
      }
    },
    "node_modules/@img/sharp-wasm32": {
      "version": "0.34.5",
      "resolved": "https://registry.npmjs.org/@img/sharp-wasm32/-/sharp-wasm32-0.34.5.tgz",
      "integrity": "sha512-OdWTEiVkY2PHwqkbBI8frFxQQFekHaSSkUIJkwzclWZe64O1X4UlUjqqqLaPbUpMOQk6FBu/HtlGXNblIs0huw==",
      "cpu": [
        "wasm32"
      ],
      "license": "Apache-2.0 AND LGPL-3.0-or-later AND MIT",
      "optional": true,
      "dependencies": {
        "@emnapi/runtime": "^1.7.0"
      },
      "engines": {
        "node": "^18.17.0 || ^20.3.0 || >=21.0.0"
      },
      "funding": {
        "url": "https://opencollective.com/libvips"
      }
    },
    "node_modules/@img/sharp-win32-arm64": {
      "version": "0.34.5",
      "resolved": "https://registry.npmjs.org/@img/sharp-win32-arm64/-/sharp-win32-arm64-0.34.5.tgz",
      "integrity": "sha512-WQ3AgWCWYSb2yt+IG8mnC6Jdk9Whs7O0gxphblsLvdhSpSTtmu69ZG1Gkb6NuvxsNACwiPV6cNSZNzt0KPsw7g==",
      "cpu": [
        "arm64"
      ],
      "license": "Apache-2.0 AND LGPL-3.0-or-later",
      "optional": true,
      "os": [
        "win32"
      ],
      "engines": {
        "node": "^18.17.0 || ^20.3.0 || >=21.0.0"
      },
      "funding": {
        "url": "https://opencollective.com/libvips"
      }
    },
    "node_modules/@img/sharp-win32-ia32": {
      "version": "0.34.5",
      "resolved": "https://registry.npmjs.org/@img/sharp-win32-ia32/-/sharp-win32-ia32-0.34.5.tgz",
      "integrity": "sha512-FV9m/7NmeCmSHDD5j4+4pNI8Cp3aW+JvLoXcTUo0IqyjSfAZJ8dIUmijx1qaJsIiU+Hosw6xM5KijAWRJCSgNg==",
      "cpu": [
        "ia32"
      ],
      "license": "Apache-2.0 AND LGPL-3.0-or-later",
      "optional": true,
      "os": [
        "win32"
      ],
      "engines": {
        "node": "^18.17.0 || ^20.3.0 || >=21.0.0"
      },
      "funding": {
        "url": "https://opencollective.com/libvips"
      }
    },
    "node_modules/@img/sharp-win32-x64": {
      "version": "0.34.5",
      "resolved": "https://registry.npmjs.org/@img/sharp-win32-x64/-/sharp-win32-x64-0.34.5.tgz",
      "integrity": "sha512-+29YMsqY2/9eFEiW93eqWnuLcWcufowXewwSNIT6UwZdUUCrM3oFjMWH/Z6/TMmb4hlFenmfAVbpWeup2jryCw==",
      "cpu": [
        "x64"
      ],
      "license": "Apache-2.0 AND LGPL-3.0-or-later",
      "optional": true,
      "os": [
        "win32"
      ],
      "engines": {
        "node": "^18.17.0 || ^20.3.0 || >=21.0.0"
      },
      "funding": {
        "url": "https://opencollective.com/libvips"
      }
    },
    "node_modules/@jridgewell/gen-mapping": {
      "version": "0.3.13",
      "resolved": "https://registry.npmjs.org/@jridgewell/gen-mapping/-/gen-mapping-0.3.13.tgz",
      "integrity": "sha512-2kkt/7niJ6MgEPxF0bYdQ6etZaA+fQvDcLKckhy1yIQOzaoKjBBjSj63/aLVjYE3qhRt5dvM+uUyfCg6UKCBbA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "@jridgewell/sourcemap-codec": "^1.5.0",
        "@jridgewell/trace-mapping": "^0.3.24"
      }
    },
    "node_modules/@jridgewell/remapping": {
      "version": "2.3.5",
      "resolved": "https://registry.npmjs.org/@jridgewell/remapping/-/remapping-2.3.5.tgz",
      "integrity": "sha512-LI9u/+laYG4Ds1TDKSJW2YPrIlcVYOwi2fUC6xB43lueCjgxV4lffOCZCtYFiH6TNOX+tQKXx97T4IKHbhyHEQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "@jridgewell/gen-mapping": "^0.3.5",
        "@jridgewell/trace-mapping": "^0.3.24"
      }
    },
    "node_modules/@jridgewell/resolve-uri": {
      "version": "3.1.2",
      "resolved": "https://registry.npmjs.org/@jridgewell/resolve-uri/-/resolve-uri-3.1.2.tgz",
      "integrity": "sha512-bRISgCIjP20/tbWSPWMEi54QVPRZExkuD9lJL+UIxUKtwVJA8wW1Trb1jMs1RFXo1CBTNZ/5hpC9QvmKWdopKw==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=6.0.0"
      }
    },
    "node_modules/@jridgewell/sourcemap-codec": {
      "version": "1.5.5",
      "resolved": "https://registry.npmjs.org/@jridgewell/sourcemap-codec/-/sourcemap-codec-1.5.5.tgz",
      "integrity": "sha512-cYQ9310grqxueWbl+WuIUIaiUaDcj7WOq5fVhEljNVgRfOUhY9fy2zTvfoqWsnebh8Sl70VScFbICvJnLKB0Og==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/@jridgewell/trace-mapping": {
      "version": "0.3.31",
      "resolved": "https://registry.npmjs.org/@jridgewell/trace-mapping/-/trace-mapping-0.3.31.tgz",
      "integrity": "sha512-zzNR+SdQSDJzc8joaeP8QQoCQr8NuYx2dIIytl1QeBEZHJ9uW6hebsrYgbz8hJwUQao3TWCMtmfV8Nu1twOLAw==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "@jridgewell/resolve-uri": "^3.1.0",
        "@jridgewell/sourcemap-codec": "^1.4.14"
      }
    },
    "node_modules/@napi-rs/wasm-runtime": {
      "version": "0.2.12",
      "resolved": "https://registry.npmjs.org/@napi-rs/wasm-runtime/-/wasm-runtime-0.2.12.tgz",
      "integrity": "sha512-ZVWUcfwY4E/yPitQJl481FjFo3K22D6qF0DuFH6Y/nbnE11GY5uguDxZMGXPQ8WQ0128MXQD7TnfHyK4oWoIJQ==",
      "dev": true,
      "license": "MIT",
      "optional": true,
      "dependencies": {
        "@emnapi/core": "^1.4.3",
        "@emnapi/runtime": "^1.4.3",
        "@tybys/wasm-util": "^0.10.0"
      }
    },
    "node_modules/@next/env": {
      "version": "16.2.4",
      "resolved": "https://registry.npmjs.org/@next/env/-/env-16.2.4.tgz",
      "integrity": "sha512-dKkkOzOSwFYe5RX6y26fZgkSpVAlIOJKQHIiydQcrWH6y/97+RceSOAdjZ14Qa3zLduVUy0TXcn+EiM6t4rPgw==",
      "license": "MIT"
    },
    "node_modules/@next/eslint-plugin-next": {
      "version": "16.2.4",
      "resolved": "https://registry.npmjs.org/@next/eslint-plugin-next/-/eslint-plugin-next-16.2.4.tgz",
      "integrity": "sha512-tOX826JJ96gYK/go18sPUgMq9FK1tqxBFfUCEufJb5XIkWFFmpgU7mahJANKGkHs7F41ir3tReJ3Lv5La0RvhA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "fast-glob": "3.3.1"
      }
    },
    "node_modules/@next/swc-darwin-arm64": {
      "version": "16.2.4",
      "resolved": "https://registry.npmjs.org/@next/swc-darwin-arm64/-/swc-darwin-arm64-16.2.4.tgz",
      "integrity": "sha512-OXTFFox5EKN1Ym08vfrz+OXxmCcEjT4SFMbNRsWZE99dMqt2Kcusl5MqPXcW232RYkMLQTy0hqgAMEsfEd/l2A==",
      "cpu": [
        "arm64"
      ],
      "license": "MIT",
      "optional": true,
      "os": [
        "darwin"
      ],
      "engines": {
        "node": ">= 10"
      }
    },
    "node_modules/@next/swc-darwin-x64": {
      "version": "16.2.4",
      "resolved": "https://registry.npmjs.org/@next/swc-darwin-x64/-/swc-darwin-x64-16.2.4.tgz",
      "integrity": "sha512-XhpVnUfmYWvD3YrXu55XdcAkQtOnvaI6wtQa8fuF5fGoKoxIUZ0kWPtcOfqJEWngFF/lOS9l3+O9CcownhiQxQ==",
      "cpu": [
        "x64"
      ],
      "license": "MIT",
      "optional": true,
      "os": [
        "darwin"
      ],
      "engines": {
        "node": ">= 10"
      }
    },
    "node_modules/@next/swc-linux-arm64-gnu": {
      "version": "16.2.4",
      "resolved": "https://registry.npmjs.org/@next/swc-linux-arm64-gnu/-/swc-linux-arm64-gnu-16.2.4.tgz",
      "integrity": "sha512-Mx/tjlNA3G8kg14QvuGAJ4xBwPk1tUHq56JxZ8CXnZwz1Etz714soCEzGQQzVMz4bEnGPowzkV6Xrp6wAkEWOQ==",
      "cpu": [
        "arm64"
      ],
      "license": "MIT",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": ">= 10"
      }
    },
    "node_modules/@next/swc-linux-arm64-musl": {
      "version": "16.2.4",
      "resolved": "https://registry.npmjs.org/@next/swc-linux-arm64-musl/-/swc-linux-arm64-musl-16.2.4.tgz",
      "integrity": "sha512-iVMMp14514u7Nup2umQS03nT/bN9HurK8ufylC3FZNykrwjtx7V1A7+4kvhbDSCeonTVqV3Txnv0Lu+m2oDXNg==",
      "cpu": [
        "arm64"
      ],
      "license": "MIT",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": ">= 10"
      }
    },
    "node_modules/@next/swc-linux-x64-gnu": {
      "version": "16.2.4",
      "resolved": "https://registry.npmjs.org/@next/swc-linux-x64-gnu/-/swc-linux-x64-gnu-16.2.4.tgz",
      "integrity": "sha512-EZOvm1aQWgnI/N/xcWOlnS3RQBk0VtVav5Zo7n4p0A7UKyTDx047k8opDbXgBpHl4CulRqRfbw3QrX2w5UOXMQ==",
      "cpu": [
        "x64"
      ],
      "license": "MIT",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": ">= 10"
      }
    },
    "node_modules/@next/swc-linux-x64-musl": {
      "version": "16.2.4",
      "resolved": "https://registry.npmjs.org/@next/swc-linux-x64-musl/-/swc-linux-x64-musl-16.2.4.tgz",
      "integrity": "sha512-h9FxsngCm9cTBf71AR4fGznDEDx1hS7+kSEiIRjq5kO1oXWm07DxVGZjCvk0SGx7TSjlUqhI8oOyz7NfwAdPoA==",
      "cpu": [
        "x64"
      ],
      "license": "MIT",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": ">= 10"
      }
    },
    "node_modules/@next/swc-win32-arm64-msvc": {
      "version": "16.2.4",
      "resolved": "https://registry.npmjs.org/@next/swc-win32-arm64-msvc/-/swc-win32-arm64-msvc-16.2.4.tgz",
      "integrity": "sha512-3NdJV5OXMSOeJYijX+bjaLge3mJBlh4ybydbT4GFoB/2hAojWHtMhl3CYlYoMrjPuodp0nzFVi4Tj2+WaMg+Ow==",
      "cpu": [
        "arm64"
      ],
      "license": "MIT",
      "optional": true,
      "os": [
        "win32"
      ],
      "engines": {
        "node": ">= 10"
      }
    },
    "node_modules/@next/swc-win32-x64-msvc": {
      "version": "16.2.4",
      "resolved": "https://registry.npmjs.org/@next/swc-win32-x64-msvc/-/swc-win32-x64-msvc-16.2.4.tgz",
      "integrity": "sha512-kMVGgsqhO5YTYODD9IPGGhA6iprWidQckK3LmPeW08PIFENRmgfb4MjXHO+p//d+ts2rpjvK5gXWzXSMrPl9cw==",
      "cpu": [
        "x64"
      ],
      "license": "MIT",
      "optional": true,
      "os": [
        "win32"
      ],
      "engines": {
        "node": ">= 10"
      }
    },
    "node_modules/@nodelib/fs.scandir": {
      "version": "2.1.5",
      "resolved": "https://registry.npmjs.org/@nodelib/fs.scandir/-/fs.scandir-2.1.5.tgz",
      "integrity": "sha512-vq24Bq3ym5HEQm2NKCr3yXDwjc7vTsEThRDnkp2DK9p1uqLR+DHurm/NOTo0KG7HYHU7eppKZj3MyqYuMBf62g==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "@nodelib/fs.stat": "2.0.5",
        "run-parallel": "^1.1.9"
      },
      "engines": {
        "node": ">= 8"
      }
    },
    "node_modules/@nodelib/fs.stat": {
      "version": "2.0.5",
      "resolved": "https://registry.npmjs.org/@nodelib/fs.stat/-/fs.stat-2.0.5.tgz",
      "integrity": "sha512-RkhPPp2zrqDAQA/2jNhnztcPAlv64XdhIp7a7454A5ovI7Bukxgt7MX7udwAu3zg1DcpPU0rz3VV1SeaqvY4+A==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">= 8"
      }
    },
    "node_modules/@nodelib/fs.walk": {
      "version": "1.2.8",
      "resolved": "https://registry.npmjs.org/@nodelib/fs.walk/-/fs.walk-1.2.8.tgz",
      "integrity": "sha512-oGB+UxlgWcgQkgwo8GcEGwemoTFt3FIO9ababBmaGwXIoBKZ+GTy0pP185beGg7Llih/NSHSV2XAs1lnznocSg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "@nodelib/fs.scandir": "2.1.5",
        "fastq": "^1.6.0"
      },
      "engines": {
        "node": ">= 8"
      }
    },
    "node_modules/@nolyfill/is-core-module": {
      "version": "1.0.39",
      "resolved": "https://registry.npmjs.org/@nolyfill/is-core-module/-/is-core-module-1.0.39.tgz",
      "integrity": "sha512-nn5ozdjYQpUCZlWGuxcJY/KpxkWQs4DcbMCmKojjyrYDEAGy4Ce19NN4v5MduafTwJlbKc99UA8YhSVqq9yPZA==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=12.4.0"
      }
    },
    "node_modules/@rtsao/scc": {
      "version": "1.1.0",
      "resolved": "https://registry.npmjs.org/@rtsao/scc/-/scc-1.1.0.tgz",
      "integrity": "sha512-zt6OdqaDoOnJ1ZYsCYGt9YmWzDXl4vQdKTyJev62gFhRGKdx7mcT54V9KIjg+d2wi9EXsPvAPKe7i7WjfVWB8g==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/@swc/helpers": {
      "version": "0.5.15",
      "resolved": "https://registry.npmjs.org/@swc/helpers/-/helpers-0.5.15.tgz",
      "integrity": "sha512-JQ5TuMi45Owi4/BIMAJBoSQoOJu12oOk/gADqlcUL9JEdHB8vyjUSsxqeNXnmXHjYKMi2WcYtezGEEhqUI/E2g==",
      "license": "Apache-2.0",
      "dependencies": {
        "tslib": "^2.8.0"
      }
    },
    "node_modules/@tailwindcss/node": {
      "version": "4.2.4",
      "resolved": "https://registry.npmjs.org/@tailwindcss/node/-/node-4.2.4.tgz",
      "integrity": "sha512-Ai7+yQPxz3ddrDQzFfBKdHEVBg0w3Zl83jnjuwxnZOsnH9pGn93QHQtpU0p/8rYWxvbFZHneni6p1BSLK4DkGA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "@jridgewell/remapping": "^2.3.5",
        "enhanced-resolve": "^5.19.0",
        "jiti": "^2.6.1",
        "lightningcss": "1.32.0",
        "magic-string": "^0.30.21",
        "source-map-js": "^1.2.1",
        "tailwindcss": "4.2.4"
      }
    },
    "node_modules/@tailwindcss/oxide": {
      "version": "4.2.4",
      "resolved": "https://registry.npmjs.org/@tailwindcss/oxide/-/oxide-4.2.4.tgz",
      "integrity": "sha512-9El/iI069DKDSXwTvB9J4BwdO5JhRrOweGaK25taBAvBXyXqJAX+Jqdvs8r8gKpsI/1m0LeJLyQYTf/WLrBT1Q==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">= 20"
      },
      "optionalDependencies": {
        "@tailwindcss/oxide-android-arm64": "4.2.4",
        "@tailwindcss/oxide-darwin-arm64": "4.2.4",
        "@tailwindcss/oxide-darwin-x64": "4.2.4",
        "@tailwindcss/oxide-freebsd-x64": "4.2.4",
        "@tailwindcss/oxide-linux-arm-gnueabihf": "4.2.4",
        "@tailwindcss/oxide-linux-arm64-gnu": "4.2.4",
        "@tailwindcss/oxide-linux-arm64-musl": "4.2.4",
        "@tailwindcss/oxide-linux-x64-gnu": "4.2.4",
        "@tailwindcss/oxide-linux-x64-musl": "4.2.4",
        "@tailwindcss/oxide-wasm32-wasi": "4.2.4",
        "@tailwindcss/oxide-win32-arm64-msvc": "4.2.4",
        "@tailwindcss/oxide-win32-x64-msvc": "4.2.4"
      }
    },
    "node_modules/@tailwindcss/oxide-android-arm64": {
      "version": "4.2.4",
      "resolved": "https://registry.npmjs.org/@tailwindcss/oxide-android-arm64/-/oxide-android-arm64-4.2.4.tgz",
      "integrity": "sha512-e7MOr1SAn9U8KlZzPi1ZXGZHeC5anY36qjNwmZv9pOJ8E4Q6jmD1vyEHkQFmNOIN7twGPEMXRHmitN4zCMN03g==",
      "cpu": [
        "arm64"
      ],
      "dev": true,
      "license": "MIT",
      "optional": true,
      "os": [
        "android"
      ],
      "engines": {
        "node": ">= 20"
      }
    },
    "node_modules/@tailwindcss/oxide-darwin-arm64": {
      "version": "4.2.4",
      "resolved": "https://registry.npmjs.org/@tailwindcss/oxide-darwin-arm64/-/oxide-darwin-arm64-4.2.4.tgz",
      "integrity": "sha512-tSC/Kbqpz/5/o/C2sG7QvOxAKqyd10bq+ypZNf+9Fi2TvbVbv1zNpcEptcsU7DPROaSbVgUXmrzKhurFvo5eDg==",
      "cpu": [
        "arm64"
      ],
      "dev": true,
      "license": "MIT",
      "optional": true,
      "os": [
        "darwin"
      ],
      "engines": {
        "node": ">= 20"
      }
    },
    "node_modules/@tailwindcss/oxide-darwin-x64": {
      "version": "4.2.4",
      "resolved": "https://registry.npmjs.org/@tailwindcss/oxide-darwin-x64/-/oxide-darwin-x64-4.2.4.tgz",
      "integrity": "sha512-yPyUXn3yO/ufR6+Kzv0t4fCg2qNr90jxXc5QqBpjlPNd0NqyDXcmQb/6weunH/MEDXW5dhyEi+agTDiqa3WsGg==",
      "cpu": [
        "x64"
      ],
      "dev": true,
      "license": "MIT",
      "optional": true,
      "os": [
        "darwin"
      ],
      "engines": {
        "node": ">= 20"
      }
    },
    "node_modules/@tailwindcss/oxide-freebsd-x64": {
      "version": "4.2.4",
      "resolved": "https://registry.npmjs.org/@tailwindcss/oxide-freebsd-x64/-/oxide-freebsd-x64-4.2.4.tgz",
      "integrity": "sha512-BoMIB4vMQtZsXdGLVc2z+P9DbETkiopogfWZKbWwM8b/1Vinbs4YcUwo+kM/KeLkX3Ygrf4/PsRndKaYhS8Eiw==",
      "cpu": [
        "x64"
      ],
      "dev": true,
      "license": "MIT",
      "optional": true,
      "os": [
        "freebsd"
      ],
      "engines": {
        "node": ">= 20"
      }
    },
    "node_modules/@tailwindcss/oxide-linux-arm-gnueabihf": {
      "version": "4.2.4",
      "resolved": "https://registry.npmjs.org/@tailwindcss/oxide-linux-arm-gnueabihf/-/oxide-linux-arm-gnueabihf-4.2.4.tgz",
      "integrity": "sha512-7pIHBLTHYRAlS7V22JNuTh33yLH4VElwKtB3bwchK/UaKUPpQ0lPQiOWcbm4V3WP2I6fNIJ23vABIvoy2izdwA==",
      "cpu": [
        "arm"
      ],
      "dev": true,
      "license": "MIT",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": ">= 20"
      }
    },
    "node_modules/@tailwindcss/oxide-linux-arm64-gnu": {
      "version": "4.2.4",
      "resolved": "https://registry.npmjs.org/@tailwindcss/oxide-linux-arm64-gnu/-/oxide-linux-arm64-gnu-4.2.4.tgz",
      "integrity": "sha512-+E4wxJ0ZGOzSH325reXTWB48l42i93kQqMvDyz5gqfRzRZ7faNhnmvlV4EPGJU3QJM/3Ab5jhJ5pCRUsKn6OQw==",
      "cpu": [
        "arm64"
      ],
      "dev": true,
      "license": "MIT",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": ">= 20"
      }
    },
    "node_modules/@tailwindcss/oxide-linux-arm64-musl": {
      "version": "4.2.4",
      "resolved": "https://registry.npmjs.org/@tailwindcss/oxide-linux-arm64-musl/-/oxide-linux-arm64-musl-4.2.4.tgz",
      "integrity": "sha512-bBADEGAbo4ASnppIziaQJelekCxdMaxisrk+fB7Thit72IBnALp9K6ffA2G4ruj90G9XRS2VQ6q2bCKbfFV82g==",
      "cpu": [
        "arm64"
      ],
      "dev": true,
      "license": "MIT",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": ">= 20"
      }
    },
    "node_modules/@tailwindcss/oxide-linux-x64-gnu": {
      "version": "4.2.4",
      "resolved": "https://registry.npmjs.org/@tailwindcss/oxide-linux-x64-gnu/-/oxide-linux-x64-gnu-4.2.4.tgz",
      "integrity": "sha512-7Mx25E4WTfnht0TVRTyC00j3i0M+EeFe7wguMDTlX4mRxafznw0CA8WJkFjWYH5BlgELd1kSjuU2JiPnNZbJDA==",
      "cpu": [
        "x64"
      ],
      "dev": true,
      "license": "MIT",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": ">= 20"
      }
    },
    "node_modules/@tailwindcss/oxide-linux-x64-musl": {
      "version": "4.2.4",
      "resolved": "https://registry.npmjs.org/@tailwindcss/oxide-linux-x64-musl/-/oxide-linux-x64-musl-4.2.4.tgz",
      "integrity": "sha512-2wwJRF7nyhOR0hhHoChc04xngV3iS+akccHTGtz965FwF0up4b2lOdo6kI1EbDaEXKgvcrFBYcYQQ/rrnWFVfA==",
      "cpu": [
        "x64"
      ],
      "dev": true,
      "license": "MIT",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": ">= 20"
      }
    },
    "node_modules/@tailwindcss/oxide-wasm32-wasi": {
      "version": "4.2.4",
      "resolved": "https://registry.npmjs.org/@tailwindcss/oxide-wasm32-wasi/-/oxide-wasm32-wasi-4.2.4.tgz",
      "integrity": "sha512-FQsqApeor8Fo6gUEklzmaa9994orJZZDBAlQpK2Mq+DslRKFJeD6AjHpBQ0kZFQohVr8o85PPh8eOy86VlSCmw==",
      "bundleDependencies": [
        "@napi-rs/wasm-runtime",
        "@emnapi/core",
        "@emnapi/runtime",
        "@tybys/wasm-util",
        "@emnapi/wasi-threads",
        "tslib"
      ],
      "cpu": [
        "wasm32"
      ],
      "dev": true,
      "license": "MIT",
      "optional": true,
      "dependencies": {
        "@emnapi/core": "^1.8.1",
        "@emnapi/runtime": "^1.8.1",
        "@emnapi/wasi-threads": "^1.1.0",
        "@napi-rs/wasm-runtime": "^1.1.1",
        "@tybys/wasm-util": "^0.10.1",
        "tslib": "^2.8.1"
      },
      "engines": {
        "node": ">=14.0.0"
      }
    },
    "node_modules/@tailwindcss/oxide-win32-arm64-msvc": {
      "version": "4.2.4",
      "resolved": "https://registry.npmjs.org/@tailwindcss/oxide-win32-arm64-msvc/-/oxide-win32-arm64-msvc-4.2.4.tgz",
      "integrity": "sha512-L9BXqxC4ToVgwMFqj3pmZRqyHEztulpUJzCxUtLjobMCzTPsGt1Fa9enKbOpY2iIyVtaHNeNvAK8ERP/64sqGQ==",
      "cpu": [
        "arm64"
      ],
      "dev": true,
      "license": "MIT",
      "optional": true,
      "os": [
        "win32"
      ],
      "engines": {
        "node": ">= 20"
      }
    },
    "node_modules/@tailwindcss/oxide-win32-x64-msvc": {
      "version": "4.2.4",
      "resolved": "https://registry.npmjs.org/@tailwindcss/oxide-win32-x64-msvc/-/oxide-win32-x64-msvc-4.2.4.tgz",
      "integrity": "sha512-ESlKG0EpVJQwRjXDDa9rLvhEAh0mhP1sF7sap9dNZT0yyl9SAG6T7gdP09EH0vIv0UNTlo6jPWyujD6559fZvw==",
      "cpu": [
        "x64"
      ],
      "dev": true,
      "license": "MIT",
      "optional": true,
      "os": [
        "win32"
      ],
      "engines": {
        "node": ">= 20"
      }
    },
    "node_modules/@tailwindcss/postcss": {
      "version": "4.2.4",
      "resolved": "https://registry.npmjs.org/@tailwindcss/postcss/-/postcss-4.2.4.tgz",
      "integrity": "sha512-wgAVj6nUWAolAu8YFvzT2cTBIElWHkjZwFYovF+xsqKsW2ADxM/X2opxj5NsF/qVccAOjRNe8X2IdPzMsWyHTg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "@alloc/quick-lru": "^5.2.0",
        "@tailwindcss/node": "4.2.4",
        "@tailwindcss/oxide": "4.2.4",
        "postcss": "^8.5.6",
        "tailwindcss": "4.2.4"
      }
    },
    "node_modules/@tybys/wasm-util": {
      "version": "0.10.2",
      "resolved": "https://registry.npmjs.org/@tybys/wasm-util/-/wasm-util-0.10.2.tgz",
      "integrity": "sha512-RoBvJ2X0wuKlWFIjrwffGw1IqZHKQqzIchKaadZZfnNpsAYp2mM0h36JtPCjNDAHGgYez/15uMBpfGwchhiMgg==",
      "dev": true,
      "license": "MIT",
      "optional": true,
      "dependencies": {
        "tslib": "^2.4.0"
      }
    },
    "node_modules/@types/estree": {
      "version": "1.0.8",
      "resolved": "https://registry.npmjs.org/@types/estree/-/estree-1.0.8.tgz",
      "integrity": "sha512-dWHzHa2WqEXI/O1E9OjrocMTKJl2mSrEolh1Iomrv6U+JuNwaHXsXx9bLu5gG7BUWFIN0skIQJQ/L1rIex4X6w==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/@types/json-schema": {
      "version": "7.0.15",
      "resolved": "https://registry.npmjs.org/@types/json-schema/-/json-schema-7.0.15.tgz",
      "integrity": "sha512-5+fP8P8MFNC+AyZCDxrB2pkZFPGzqQWUzpSeuuVLvm8VMcorNYavBqoFcxK8bQz4Qsbn4oUEEem4wDLfcysGHA==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/@types/json5": {
      "version": "0.0.29",
      "resolved": "https://registry.npmjs.org/@types/json5/-/json5-0.0.29.tgz",
      "integrity": "sha512-dRLjCWHYg4oaA77cxO64oO+7JwCwnIzkZPdrrC71jQmQtlhM556pwKo5bUzqvZndkVbeFLIIi+9TC40JNF5hNQ==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/@types/node": {
      "version": "20.19.39",
      "resolved": "https://registry.npmjs.org/@types/node/-/node-20.19.39.tgz",
      "integrity": "sha512-orrrD74MBUyK8jOAD/r0+lfa1I2MO6I+vAkmAWzMYbCcgrN4lCrmK52gRFQq/JRxfYPfonkr4b0jcY7Olqdqbw==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "undici-types": "~6.21.0"
      }
    },
    "node_modules/@types/react": {
      "version": "19.2.14",
      "resolved": "https://registry.npmjs.org/@types/react/-/react-19.2.14.tgz",
      "integrity": "sha512-ilcTH/UniCkMdtexkoCN0bI7pMcJDvmQFPvuPvmEaYA/NSfFTAgdUSLAoVjaRJm7+6PvcM+q1zYOwS4wTYMF9w==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "csstype": "^3.2.2"
      }
    },
    "node_modules/@types/react-dom": {
      "version": "19.2.3",
      "resolved": "https://registry.npmjs.org/@types/react-dom/-/react-dom-19.2.3.tgz",
      "integrity": "sha512-jp2L/eY6fn+KgVVQAOqYItbF0VY/YApe5Mz2F0aykSO8gx31bYCZyvSeYxCHKvzHG5eZjc+zyaS5BrBWya2+kQ==",
      "dev": true,
      "license": "MIT",
      "peerDependencies": {
        "@types/react": "^19.2.0"
      }
    },
    "node_modules/@typescript-eslint/eslint-plugin": {
      "version": "8.59.2",
      "resolved": "https://registry.npmjs.org/@typescript-eslint/eslint-plugin/-/eslint-plugin-8.59.2.tgz",
      "integrity": "sha512-j/bwmkBvHUtPNxzuWe5z6BEk3q54YRyGlBXkSsmfoih7zNrBvl5A9A98anlp/7JbyZcWIJ8KXo/3Tq/DjFLtuQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "@eslint-community/regexpp": "^4.12.2",
        "@typescript-eslint/scope-manager": "8.59.2",
        "@typescript-eslint/type-utils": "8.59.2",
        "@typescript-eslint/utils": "8.59.2",
        "@typescript-eslint/visitor-keys": "8.59.2",
        "ignore": "^7.0.5",
        "natural-compare": "^1.4.0",
        "ts-api-utils": "^2.5.0"
      },
      "engines": {
        "node": "^18.18.0 || ^20.9.0 || >=21.1.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/typescript-eslint"
      },
      "peerDependencies": {
        "@typescript-eslint/parser": "^8.59.2",
        "eslint": "^8.57.0 || ^9.0.0 || ^10.0.0",
        "typescript": ">=4.8.4 <6.1.0"
      }
    },
    "node_modules/@typescript-eslint/eslint-plugin/node_modules/ignore": {
      "version": "7.0.5",
      "resolved": "https://registry.npmjs.org/ignore/-/ignore-7.0.5.tgz",
      "integrity": "sha512-Hs59xBNfUIunMFgWAbGX5cq6893IbWg4KnrjbYwX3tx0ztorVgTDA6B2sxf8ejHJ4wz8BqGUMYlnzNBer5NvGg==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">= 4"
      }
    },
    "node_modules/@typescript-eslint/parser": {
      "version": "8.59.2",
      "resolved": "https://registry.npmjs.org/@typescript-eslint/parser/-/parser-8.59.2.tgz",
      "integrity": "sha512-plR3pp6D+SSUn1HM7xvSkx12/DhoHInI2YF35KAcVFNZvlC0gtrWqx7Qq1oH2Ssgi0vlFRCTbP+DZc7B9+TtsQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "@typescript-eslint/scope-manager": "8.59.2",
        "@typescript-eslint/types": "8.59.2",
        "@typescript-eslint/typescript-estree": "8.59.2",
        "@typescript-eslint/visitor-keys": "8.59.2",
        "debug": "^4.4.3"
      },
      "engines": {
        "node": "^18.18.0 || ^20.9.0 || >=21.1.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/typescript-eslint"
      },
      "peerDependencies": {
        "eslint": "^8.57.0 || ^9.0.0 || ^10.0.0",
        "typescript": ">=4.8.4 <6.1.0"
      }
    },
    "node_modules/@typescript-eslint/project-service": {
      "version": "8.59.2",
      "resolved": "https://registry.npmjs.org/@typescript-eslint/project-service/-/project-service-8.59.2.tgz",
      "integrity": "sha512-+2hqvEkeyf/0FBor67duF0Ll7Ot8jyKzDQOSrxazF/danillRq2DwR9dLptsXpoZQqxE1UisSmoZewrlPas9Vw==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "@typescript-eslint/tsconfig-utils": "^8.59.2",
        "@typescript-eslint/types": "^8.59.2",
        "debug": "^4.4.3"
      },
      "engines": {
        "node": "^18.18.0 || ^20.9.0 || >=21.1.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/typescript-eslint"
      },
      "peerDependencies": {
        "typescript": ">=4.8.4 <6.1.0"
      }
    },
    "node_modules/@typescript-eslint/scope-manager": {
      "version": "8.59.2",
      "resolved": "https://registry.npmjs.org/@typescript-eslint/scope-manager/-/scope-manager-8.59.2.tgz",
      "integrity": "sha512-JzfyEpEtOU89CcFSwyNS3mu4MLvLSXqnmX05+aKBDM+TdR5jzcGOEBwxwGNxrEQ7p/z6kK2WyioCGBf2zZBnvg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "@typescript-eslint/types": "8.59.2",
        "@typescript-eslint/visitor-keys": "8.59.2"
      },
      "engines": {
        "node": "^18.18.0 || ^20.9.0 || >=21.1.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/typescript-eslint"
      }
    },
    "node_modules/@typescript-eslint/tsconfig-utils": {
      "version": "8.59.2",
      "resolved": "https://registry.npmjs.org/@typescript-eslint/tsconfig-utils/-/tsconfig-utils-8.59.2.tgz",
      "integrity": "sha512-BKK4alN7oi4C/zv4VqHQ+uRU+lTa6JGIZ7s1juw7b3RHo9OfKB+bKX3u0iVZetdsUCBBkSbdWbarJbmN0fTeSw==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": "^18.18.0 || ^20.9.0 || >=21.1.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/typescript-eslint"
      },
      "peerDependencies": {
        "typescript": ">=4.8.4 <6.1.0"
      }
    },
    "node_modules/@typescript-eslint/type-utils": {
      "version": "8.59.2",
      "resolved": "https://registry.npmjs.org/@typescript-eslint/type-utils/-/type-utils-8.59.2.tgz",
      "integrity": "sha512-nhqaj1nmTdVVl/BP5omXNRGO38jn5iosis2vbdmupF2txCf8ylWT8lx+JlvMYYVqzGVKtjojUFoQ3JRWK+mfzQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "@typescript-eslint/types": "8.59.2",
        "@typescript-eslint/typescript-estree": "8.59.2",
        "@typescript-eslint/utils": "8.59.2",
        "debug": "^4.4.3",
        "ts-api-utils": "^2.5.0"
      },
      "engines": {
        "node": "^18.18.0 || ^20.9.0 || >=21.1.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/typescript-eslint"
      },
      "peerDependencies": {
        "eslint": "^8.57.0 || ^9.0.0 || ^10.0.0",
        "typescript": ">=4.8.4 <6.1.0"
      }
    },
    "node_modules/@typescript-eslint/types": {
      "version": "8.59.2",
      "resolved": "https://registry.npmjs.org/@typescript-eslint/types/-/types-8.59.2.tgz",
      "integrity": "sha512-e82GVOE8Ps3E++Egvb6Y3Dw0S10u8NkQ9KXmtRhCWJJ8kDhOJTvtMAWnFL16kB1583goCWXsr0NieKCZMs2/0Q==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": "^18.18.0 || ^20.9.0 || >=21.1.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/typescript-eslint"
      }
    },
    "node_modules/@typescript-eslint/typescript-estree": {
      "version": "8.59.2",
      "resolved": "https://registry.npmjs.org/@typescript-eslint/typescript-estree/-/typescript-estree-8.59.2.tgz",
      "integrity": "sha512-o0XPGNwcWw+FIwStOWn+BwBuEmL6QXP0rsvAFg7ET1dey1Nr6Wb1ac8p5HEsK0ygO/6mUxlk+YWQD9xcb/nnXg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "@typescript-eslint/project-service": "8.59.2",
        "@typescript-eslint/tsconfig-utils": "8.59.2",
        "@typescript-eslint/types": "8.59.2",
        "@typescript-eslint/visitor-keys": "8.59.2",
        "debug": "^4.4.3",
        "minimatch": "^10.2.2",
        "semver": "^7.7.3",
        "tinyglobby": "^0.2.15",
        "ts-api-utils": "^2.5.0"
      },
      "engines": {
        "node": "^18.18.0 || ^20.9.0 || >=21.1.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/typescript-eslint"
      },
      "peerDependencies": {
        "typescript": ">=4.8.4 <6.1.0"
      }
    },
    "node_modules/@typescript-eslint/typescript-estree/node_modules/balanced-match": {
      "version": "4.0.4",
      "resolved": "https://registry.npmjs.org/balanced-match/-/balanced-match-4.0.4.tgz",
      "integrity": "sha512-BLrgEcRTwX2o6gGxGOCNyMvGSp35YofuYzw9h1IMTRmKqttAZZVU67bdb9Pr2vUHA8+j3i2tJfjO6C6+4myGTA==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": "18 || 20 || >=22"
      }
    },
    "node_modules/@typescript-eslint/typescript-estree/node_modules/brace-expansion": {
      "version": "5.0.5",
      "resolved": "https://registry.npmjs.org/brace-expansion/-/brace-expansion-5.0.5.tgz",
      "integrity": "sha512-VZznLgtwhn+Mact9tfiwx64fA9erHH/MCXEUfB/0bX/6Fz6ny5EGTXYltMocqg4xFAQZtnO3DHWWXi8RiuN7cQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "balanced-match": "^4.0.2"
      },
      "engines": {
        "node": "18 || 20 || >=22"
      }
    },
    "node_modules/@typescript-eslint/typescript-estree/node_modules/minimatch": {
      "version": "10.2.5",
      "resolved": "https://registry.npmjs.org/minimatch/-/minimatch-10.2.5.tgz",
      "integrity": "sha512-MULkVLfKGYDFYejP07QOurDLLQpcjk7Fw+7jXS2R2czRQzR56yHRveU5NDJEOviH+hETZKSkIk5c+T23GjFUMg==",
      "dev": true,
      "license": "BlueOak-1.0.0",
      "dependencies": {
        "brace-expansion": "^5.0.5"
      },
      "engines": {
        "node": "18 || 20 || >=22"
      },
      "funding": {
        "url": "https://github.com/sponsors/isaacs"
      }
    },
    "node_modules/@typescript-eslint/typescript-estree/node_modules/semver": {
      "version": "7.7.4",
      "resolved": "https://registry.npmjs.org/semver/-/semver-7.7.4.tgz",
      "integrity": "sha512-vFKC2IEtQnVhpT78h1Yp8wzwrf8CM+MzKMHGJZfBtzhZNycRFnXsHk6E5TxIkkMsgNS7mdX3AGB7x2QM2di4lA==",
      "dev": true,
      "license": "ISC",
      "bin": {
        "semver": "bin/semver.js"
      },
      "engines": {
        "node": ">=10"
      }
    },
    "node_modules/@typescript-eslint/utils": {
      "version": "8.59.2",
      "resolved": "https://registry.npmjs.org/@typescript-eslint/utils/-/utils-8.59.2.tgz",
      "integrity": "sha512-Juw3EinkXqjaffxz6roowvV7GZT/kET5vSKKZT6upl5TXdWkLkYmNPXwDDL2Vkt2DPn0nODIS4egC/0AGxKo/Q==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "@eslint-community/eslint-utils": "^4.9.1",
        "@typescript-eslint/scope-manager": "8.59.2",
        "@typescript-eslint/types": "8.59.2",
        "@typescript-eslint/typescript-estree": "8.59.2"
      },
      "engines": {
        "node": "^18.18.0 || ^20.9.0 || >=21.1.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/typescript-eslint"
      },
      "peerDependencies": {
        "eslint": "^8.57.0 || ^9.0.0 || ^10.0.0",
        "typescript": ">=4.8.4 <6.1.0"
      }
    },
    "node_modules/@typescript-eslint/visitor-keys": {
      "version": "8.59.2",
      "resolved": "https://registry.npmjs.org/@typescript-eslint/visitor-keys/-/visitor-keys-8.59.2.tgz",
      "integrity": "sha512-NwjLUnGy8/Zfx23fl50tRC8rYaYnM52xNRYFAXvmiil9yh1+K6aRVQMnzW6gQB/1DLgWt977lYQn7C+wtgXZiA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "@typescript-eslint/types": "8.59.2",
        "eslint-visitor-keys": "^5.0.0"
      },
      "engines": {
        "node": "^18.18.0 || ^20.9.0 || >=21.1.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/typescript-eslint"
      }
    },
    "node_modules/@typescript-eslint/visitor-keys/node_modules/eslint-visitor-keys": {
      "version": "5.0.1",
      "resolved": "https://registry.npmjs.org/eslint-visitor-keys/-/eslint-visitor-keys-5.0.1.tgz",
      "integrity": "sha512-tD40eHxA35h0PEIZNeIjkHoDR4YjjJp34biM0mDvplBe//mB+IHCqHDGV7pxF+7MklTvighcCPPZC7ynWyjdTA==",
      "dev": true,
      "license": "Apache-2.0",
      "engines": {
        "node": "^20.19.0 || ^22.13.0 || >=24"
      },
      "funding": {
        "url": "https://opencollective.com/eslint"
      }
    },
    "node_modules/@unrs/resolver-binding-android-arm-eabi": {
      "version": "1.11.1",
      "resolved": "https://registry.npmjs.org/@unrs/resolver-binding-android-arm-eabi/-/resolver-binding-android-arm-eabi-1.11.1.tgz",
      "integrity": "sha512-ppLRUgHVaGRWUx0R0Ut06Mjo9gBaBkg3v/8AxusGLhsIotbBLuRk51rAzqLC8gq6NyyAojEXglNjzf6R948DNw==",
      "cpu": [
        "arm"
      ],
      "dev": true,
      "license": "MIT",
      "optional": true,
      "os": [
        "android"
      ]
    },
    "node_modules/@unrs/resolver-binding-android-arm64": {
      "version": "1.11.1",
      "resolved": "https://registry.npmjs.org/@unrs/resolver-binding-android-arm64/-/resolver-binding-android-arm64-1.11.1.tgz",
      "integrity": "sha512-lCxkVtb4wp1v+EoN+HjIG9cIIzPkX5OtM03pQYkG+U5O/wL53LC4QbIeazgiKqluGeVEeBlZahHalCaBvU1a2g==",
      "cpu": [
        "arm64"
      ],
      "dev": true,
      "license": "MIT",
      "optional": true,
      "os": [
        "android"
      ]
    },
    "node_modules/@unrs/resolver-binding-darwin-arm64": {
      "version": "1.11.1",
      "resolved": "https://registry.npmjs.org/@unrs/resolver-binding-darwin-arm64/-/resolver-binding-darwin-arm64-1.11.1.tgz",
      "integrity": "sha512-gPVA1UjRu1Y/IsB/dQEsp2V1pm44Of6+LWvbLc9SDk1c2KhhDRDBUkQCYVWe6f26uJb3fOK8saWMgtX8IrMk3g==",
      "cpu": [
        "arm64"
      ],
      "dev": true,
      "license": "MIT",
      "optional": true,
      "os": [
        "darwin"
      ]
    },
    "node_modules/@unrs/resolver-binding-darwin-x64": {
      "version": "1.11.1",
      "resolved": "https://registry.npmjs.org/@unrs/resolver-binding-darwin-x64/-/resolver-binding-darwin-x64-1.11.1.tgz",
      "integrity": "sha512-cFzP7rWKd3lZaCsDze07QX1SC24lO8mPty9vdP+YVa3MGdVgPmFc59317b2ioXtgCMKGiCLxJ4HQs62oz6GfRQ==",
      "cpu": [
        "x64"
      ],
      "dev": true,
      "license": "MIT",
      "optional": true,
      "os": [
        "darwin"
      ]
    },
    "node_modules/@unrs/resolver-binding-freebsd-x64": {
      "version": "1.11.1",
      "resolved": "https://registry.npmjs.org/@unrs/resolver-binding-freebsd-x64/-/resolver-binding-freebsd-x64-1.11.1.tgz",
      "integrity": "sha512-fqtGgak3zX4DCB6PFpsH5+Kmt/8CIi4Bry4rb1ho6Av2QHTREM+47y282Uqiu3ZRF5IQioJQ5qWRV6jduA+iGw==",
      "cpu": [
        "x64"
      ],
      "dev": true,
      "license": "MIT",
      "optional": true,
      "os": [
        "freebsd"
      ]
    },
    "node_modules/@unrs/resolver-binding-linux-arm-gnueabihf": {
      "version": "1.11.1",
      "resolved": "https://registry.npmjs.org/@unrs/resolver-binding-linux-arm-gnueabihf/-/resolver-binding-linux-arm-gnueabihf-1.11.1.tgz",
      "integrity": "sha512-u92mvlcYtp9MRKmP+ZvMmtPN34+/3lMHlyMj7wXJDeXxuM0Vgzz0+PPJNsro1m3IZPYChIkn944wW8TYgGKFHw==",
      "cpu": [
        "arm"
      ],
      "dev": true,
      "license": "MIT",
      "optional": true,
      "os": [
        "linux"
      ]
    },
    "node_modules/@unrs/resolver-binding-linux-arm-musleabihf": {
      "version": "1.11.1",
      "resolved": "https://registry.npmjs.org/@unrs/resolver-binding-linux-arm-musleabihf/-/resolver-binding-linux-arm-musleabihf-1.11.1.tgz",
      "integrity": "sha512-cINaoY2z7LVCrfHkIcmvj7osTOtm6VVT16b5oQdS4beibX2SYBwgYLmqhBjA1t51CarSaBuX5YNsWLjsqfW5Cw==",
      "cpu": [
        "arm"
      ],
      "dev": true,
      "license": "MIT",
      "optional": true,
      "os": [
        "linux"
      ]
    },
    "node_modules/@unrs/resolver-binding-linux-arm64-gnu": {
      "version": "1.11.1",
      "resolved": "https://registry.npmjs.org/@unrs/resolver-binding-linux-arm64-gnu/-/resolver-binding-linux-arm64-gnu-1.11.1.tgz",
      "integrity": "sha512-34gw7PjDGB9JgePJEmhEqBhWvCiiWCuXsL9hYphDF7crW7UgI05gyBAi6MF58uGcMOiOqSJ2ybEeCvHcq0BCmQ==",
      "cpu": [
        "arm64"
      ],
      "dev": true,
      "license": "MIT",
      "optional": true,
      "os": [
        "linux"
      ]
    },
    "node_modules/@unrs/resolver-binding-linux-arm64-musl": {
      "version": "1.11.1",
      "resolved": "https://registry.npmjs.org/@unrs/resolver-binding-linux-arm64-musl/-/resolver-binding-linux-arm64-musl-1.11.1.tgz",
      "integrity": "sha512-RyMIx6Uf53hhOtJDIamSbTskA99sPHS96wxVE/bJtePJJtpdKGXO1wY90oRdXuYOGOTuqjT8ACccMc4K6QmT3w==",
      "cpu": [
        "arm64"
      ],
      "dev": true,
      "license": "MIT",
      "optional": true,
      "os": [
        "linux"
      ]
    },
    "node_modules/@unrs/resolver-binding-linux-ppc64-gnu": {
      "version": "1.11.1",
      "resolved": "https://registry.npmjs.org/@unrs/resolver-binding-linux-ppc64-gnu/-/resolver-binding-linux-ppc64-gnu-1.11.1.tgz",
      "integrity": "sha512-D8Vae74A4/a+mZH0FbOkFJL9DSK2R6TFPC9M+jCWYia/q2einCubX10pecpDiTmkJVUH+y8K3BZClycD8nCShA==",
      "cpu": [
        "ppc64"
      ],
      "dev": true,
      "license": "MIT",
      "optional": true,
      "os": [
        "linux"
      ]
    },
    "node_modules/@unrs/resolver-binding-linux-riscv64-gnu": {
      "version": "1.11.1",
      "resolved": "https://registry.npmjs.org/@unrs/resolver-binding-linux-riscv64-gnu/-/resolver-binding-linux-riscv64-gnu-1.11.1.tgz",
      "integrity": "sha512-frxL4OrzOWVVsOc96+V3aqTIQl1O2TjgExV4EKgRY09AJ9leZpEg8Ak9phadbuX0BA4k8U5qtvMSQQGGmaJqcQ==",
      "cpu": [
        "riscv64"
      ],
      "dev": true,
      "license": "MIT",
      "optional": true,
      "os": [
        "linux"
      ]
    },
    "node_modules/@unrs/resolver-binding-linux-riscv64-musl": {
      "version": "1.11.1",
      "resolved": "https://registry.npmjs.org/@unrs/resolver-binding-linux-riscv64-musl/-/resolver-binding-linux-riscv64-musl-1.11.1.tgz",
      "integrity": "sha512-mJ5vuDaIZ+l/acv01sHoXfpnyrNKOk/3aDoEdLO/Xtn9HuZlDD6jKxHlkN8ZhWyLJsRBxfv9GYM2utQ1SChKew==",
      "cpu": [
        "riscv64"
      ],
      "dev": true,
      "license": "MIT",
      "optional": true,
      "os": [
        "linux"
      ]
    },
    "node_modules/@unrs/resolver-binding-linux-s390x-gnu": {
      "version": "1.11.1",
      "resolved": "https://registry.npmjs.org/@unrs/resolver-binding-linux-s390x-gnu/-/resolver-binding-linux-s390x-gnu-1.11.1.tgz",
      "integrity": "sha512-kELo8ebBVtb9sA7rMe1Cph4QHreByhaZ2QEADd9NzIQsYNQpt9UkM9iqr2lhGr5afh885d/cB5QeTXSbZHTYPg==",
      "cpu": [
        "s390x"
      ],
      "dev": true,
      "license": "MIT",
      "optional": true,
      "os": [
        "linux"
      ]
    },
    "node_modules/@unrs/resolver-binding-linux-x64-gnu": {
      "version": "1.11.1",
      "resolved": "https://registry.npmjs.org/@unrs/resolver-binding-linux-x64-gnu/-/resolver-binding-linux-x64-gnu-1.11.1.tgz",
      "integrity": "sha512-C3ZAHugKgovV5YvAMsxhq0gtXuwESUKc5MhEtjBpLoHPLYM+iuwSj3lflFwK3DPm68660rZ7G8BMcwSro7hD5w==",
      "cpu": [
        "x64"
      ],
      "dev": true,
      "license": "MIT",
      "optional": true,
      "os": [
        "linux"
      ]
    },
    "node_modules/@unrs/resolver-binding-linux-x64-musl": {
      "version": "1.11.1",
      "resolved": "https://registry.npmjs.org/@unrs/resolver-binding-linux-x64-musl/-/resolver-binding-linux-x64-musl-1.11.1.tgz",
      "integrity": "sha512-rV0YSoyhK2nZ4vEswT/QwqzqQXw5I6CjoaYMOX0TqBlWhojUf8P94mvI7nuJTeaCkkds3QE4+zS8Ko+GdXuZtA==",
      "cpu": [
        "x64"
      ],
      "dev": true,
      "license": "MIT",
      "optional": true,
      "os": [
        "linux"
      ]
    },
    "node_modules/@unrs/resolver-binding-wasm32-wasi": {
      "version": "1.11.1",
      "resolved": "https://registry.npmjs.org/@unrs/resolver-binding-wasm32-wasi/-/resolver-binding-wasm32-wasi-1.11.1.tgz",
      "integrity": "sha512-5u4RkfxJm+Ng7IWgkzi3qrFOvLvQYnPBmjmZQ8+szTK/b31fQCnleNl1GgEt7nIsZRIf5PLhPwT0WM+q45x/UQ==",
      "cpu": [
        "wasm32"
      ],
      "dev": true,
      "license": "MIT",
      "optional": true,
      "dependencies": {
        "@napi-rs/wasm-runtime": "^0.2.11"
      },
      "engines": {
        "node": ">=14.0.0"
      }
    },
    "node_modules/@unrs/resolver-binding-win32-arm64-msvc": {
      "version": "1.11.1",
      "resolved": "https://registry.npmjs.org/@unrs/resolver-binding-win32-arm64-msvc/-/resolver-binding-win32-arm64-msvc-1.11.1.tgz",
      "integrity": "sha512-nRcz5Il4ln0kMhfL8S3hLkxI85BXs3o8EYoattsJNdsX4YUU89iOkVn7g0VHSRxFuVMdM4Q1jEpIId1Ihim/Uw==",
      "cpu": [
        "arm64"
      ],
      "dev": true,
      "license": "MIT",
      "optional": true,
      "os": [
        "win32"
      ]
    },
    "node_modules/@unrs/resolver-binding-win32-ia32-msvc": {
      "version": "1.11.1",
      "resolved": "https://registry.npmjs.org/@unrs/resolver-binding-win32-ia32-msvc/-/resolver-binding-win32-ia32-msvc-1.11.1.tgz",
      "integrity": "sha512-DCEI6t5i1NmAZp6pFonpD5m7i6aFrpofcp4LA2i8IIq60Jyo28hamKBxNrZcyOwVOZkgsRp9O2sXWBWP8MnvIQ==",
      "cpu": [
        "ia32"
      ],
      "dev": true,
      "license": "MIT",
      "optional": true,
      "os": [
        "win32"
      ]
    },
    "node_modules/@unrs/resolver-binding-win32-x64-msvc": {
      "version": "1.11.1",
      "resolved": "https://registry.npmjs.org/@unrs/resolver-binding-win32-x64-msvc/-/resolver-binding-win32-x64-msvc-1.11.1.tgz",
      "integrity": "sha512-lrW200hZdbfRtztbygyaq/6jP6AKE8qQN2KvPcJ+x7wiD038YtnYtZ82IMNJ69GJibV7bwL3y9FgK+5w/pYt6g==",
      "cpu": [
        "x64"
      ],
      "dev": true,
      "license": "MIT",
      "optional": true,
      "os": [
        "win32"
      ]
    },
    "node_modules/acorn": {
      "version": "8.16.0",
      "resolved": "https://registry.npmjs.org/acorn/-/acorn-8.16.0.tgz",
      "integrity": "sha512-UVJyE9MttOsBQIDKw1skb9nAwQuR5wuGD3+82K6JgJlm/Y+KI92oNsMNGZCYdDsVtRHSak0pcV5Dno5+4jh9sw==",
      "dev": true,
      "license": "MIT",
      "bin": {
        "acorn": "bin/acorn"
      },
      "engines": {
        "node": ">=0.4.0"
      }
    },
    "node_modules/acorn-jsx": {
      "version": "5.3.2",
      "resolved": "https://registry.npmjs.org/acorn-jsx/-/acorn-jsx-5.3.2.tgz",
      "integrity": "sha512-rq9s+JNhf0IChjtDXxllJ7g41oZk5SlXtp0LHwyA5cejwn7vKmKp4pPri6YEePv2PU65sAsegbXtIinmDFDXgQ==",
      "dev": true,
      "license": "MIT",
      "peerDependencies": {
        "acorn": "^6.0.0 || ^7.0.0 || ^8.0.0"
      }
    },
    "node_modules/ajv": {
      "version": "6.15.0",
      "resolved": "https://registry.npmjs.org/ajv/-/ajv-6.15.0.tgz",
      "integrity": "sha512-fgFx7Hfoq60ytK2c7DhnF8jIvzYgOMxfugjLOSMHjLIPgenqa7S7oaagATUq99mV6IYvN2tRmC0wnTYX6iPbMw==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "fast-deep-equal": "^3.1.1",
        "fast-json-stable-stringify": "^2.0.0",
        "json-schema-traverse": "^0.4.1",
        "uri-js": "^4.2.2"
      },
      "funding": {
        "type": "github",
        "url": "https://github.com/sponsors/epoberezkin"
      }
    },
    "node_modules/ansi-styles": {
      "version": "4.3.0",
      "resolved": "https://registry.npmjs.org/ansi-styles/-/ansi-styles-4.3.0.tgz",
      "integrity": "sha512-zbB9rCJAT1rbjiVDb2hqKFHNYLxgtk8NURxZ3IZwD3F6NtxbXZQCnnSi1Lkx+IDohdPlFp222wVALIheZJQSEg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "color-convert": "^2.0.1"
      },
      "engines": {
        "node": ">=8"
      },
      "funding": {
        "url": "https://github.com/chalk/ansi-styles?sponsor=1"
      }
    },
    "node_modules/argparse": {
      "version": "2.0.1",
      "resolved": "https://registry.npmjs.org/argparse/-/argparse-2.0.1.tgz",
      "integrity": "sha512-8+9WqebbFzpX9OR+Wa6O29asIogeRMzcGtAINdpMHHyAg10f05aSFVBbcEqGf/PXw1EjAZ+q2/bEBg3DvurK3Q==",
      "dev": true,
      "license": "Python-2.0"
    },
    "node_modules/aria-query": {
      "version": "5.3.2",
      "resolved": "https://registry.npmjs.org/aria-query/-/aria-query-5.3.2.tgz",
      "integrity": "sha512-COROpnaoap1E2F000S62r6A60uHZnmlvomhfyT2DlTcrY1OrBKn2UhH7qn5wTC9zMvD0AY7csdPSNwKP+7WiQw==",
      "dev": true,
      "license": "Apache-2.0",
      "engines": {
        "node": ">= 0.4"
      }
    },
    "node_modules/array-buffer-byte-length": {
      "version": "1.0.2",
      "resolved": "https://registry.npmjs.org/array-buffer-byte-length/-/array-buffer-byte-length-1.0.2.tgz",
      "integrity": "sha512-LHE+8BuR7RYGDKvnrmcuSq3tDcKv9OFEXQt/HpbZhY7V6h0zlUXutnAD82GiFx9rdieCMjkvtcsPqBwgUl1Iiw==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bound": "^1.0.3",
        "is-array-buffer": "^3.0.5"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/array-includes": {
      "version": "3.1.9",
      "resolved": "https://registry.npmjs.org/array-includes/-/array-includes-3.1.9.tgz",
      "integrity": "sha512-FmeCCAenzH0KH381SPT5FZmiA/TmpndpcaShhfgEN9eCVjnFBqq3l1xrI42y8+PPLI6hypzou4GXw00WHmPBLQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bind": "^1.0.8",
        "call-bound": "^1.0.4",
        "define-properties": "^1.2.1",
        "es-abstract": "^1.24.0",
        "es-object-atoms": "^1.1.1",
        "get-intrinsic": "^1.3.0",
        "is-string": "^1.1.1",
        "math-intrinsics": "^1.1.0"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/array.prototype.findlast": {
      "version": "1.2.5",
      "resolved": "https://registry.npmjs.org/array.prototype.findlast/-/array.prototype.findlast-1.2.5.tgz",
      "integrity": "sha512-CVvd6FHg1Z3POpBLxO6E6zr+rSKEQ9L6rZHAaY7lLfhKsWYUBBOuMs0e9o24oopj6H+geRCX0YJ+TJLBK2eHyQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bind": "^1.0.7",
        "define-properties": "^1.2.1",
        "es-abstract": "^1.23.2",
        "es-errors": "^1.3.0",
        "es-object-atoms": "^1.0.0",
        "es-shim-unscopables": "^1.0.2"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/array.prototype.findlastindex": {
      "version": "1.2.6",
      "resolved": "https://registry.npmjs.org/array.prototype.findlastindex/-/array.prototype.findlastindex-1.2.6.tgz",
      "integrity": "sha512-F/TKATkzseUExPlfvmwQKGITM3DGTK+vkAsCZoDc5daVygbJBnjEUCbgkAvVFsgfXfX4YIqZ/27G3k3tdXrTxQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bind": "^1.0.8",
        "call-bound": "^1.0.4",
        "define-properties": "^1.2.1",
        "es-abstract": "^1.23.9",
        "es-errors": "^1.3.0",
        "es-object-atoms": "^1.1.1",
        "es-shim-unscopables": "^1.1.0"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/array.prototype.flat": {
      "version": "1.3.3",
      "resolved": "https://registry.npmjs.org/array.prototype.flat/-/array.prototype.flat-1.3.3.tgz",
      "integrity": "sha512-rwG/ja1neyLqCuGZ5YYrznA62D4mZXg0i1cIskIUKSiqF3Cje9/wXAls9B9s1Wa2fomMsIv8czB8jZcPmxCXFg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bind": "^1.0.8",
        "define-properties": "^1.2.1",
        "es-abstract": "^1.23.5",
        "es-shim-unscopables": "^1.0.2"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/array.prototype.flatmap": {
      "version": "1.3.3",
      "resolved": "https://registry.npmjs.org/array.prototype.flatmap/-/array.prototype.flatmap-1.3.3.tgz",
      "integrity": "sha512-Y7Wt51eKJSyi80hFrJCePGGNo5ktJCslFuboqJsbf57CCPcm5zztluPlc4/aD8sWsKvlwatezpV4U1efk8kpjg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bind": "^1.0.8",
        "define-properties": "^1.2.1",
        "es-abstract": "^1.23.5",
        "es-shim-unscopables": "^1.0.2"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/array.prototype.tosorted": {
      "version": "1.1.4",
      "resolved": "https://registry.npmjs.org/array.prototype.tosorted/-/array.prototype.tosorted-1.1.4.tgz",
      "integrity": "sha512-p6Fx8B7b7ZhL/gmUsAy0D15WhvDccw3mnGNbZpi3pmeJdxtWsj2jEaI4Y6oo3XiHfzuSgPwKc04MYt6KgvC/wA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bind": "^1.0.7",
        "define-properties": "^1.2.1",
        "es-abstract": "^1.23.3",
        "es-errors": "^1.3.0",
        "es-shim-unscopables": "^1.0.2"
      },
      "engines": {
        "node": ">= 0.4"
      }
    },
    "node_modules/arraybuffer.prototype.slice": {
      "version": "1.0.4",
      "resolved": "https://registry.npmjs.org/arraybuffer.prototype.slice/-/arraybuffer.prototype.slice-1.0.4.tgz",
      "integrity": "sha512-BNoCY6SXXPQ7gF2opIP4GBE+Xw7U+pHMYKuzjgCN3GwiaIR09UUeKfheyIry77QtrCBlC0KK0q5/TER/tYh3PQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "array-buffer-byte-length": "^1.0.1",
        "call-bind": "^1.0.8",
        "define-properties": "^1.2.1",
        "es-abstract": "^1.23.5",
        "es-errors": "^1.3.0",
        "get-intrinsic": "^1.2.6",
        "is-array-buffer": "^3.0.4"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/ast-types-flow": {
      "version": "0.0.8",
      "resolved": "https://registry.npmjs.org/ast-types-flow/-/ast-types-flow-0.0.8.tgz",
      "integrity": "sha512-OH/2E5Fg20h2aPrbe+QL8JZQFko0YZaF+j4mnQ7BGhfavO7OpSLa8a0y9sBwomHdSbkhTS8TQNayBfnW5DwbvQ==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/async-function": {
      "version": "1.0.0",
      "resolved": "https://registry.npmjs.org/async-function/-/async-function-1.0.0.tgz",
      "integrity": "sha512-hsU18Ae8CDTR6Kgu9DYf0EbCr/a5iGL0rytQDobUcdpYOKokk8LEjVphnXkDkgpi0wYVsqrXuP0bZxJaTqdgoA==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">= 0.4"
      }
    },
    "node_modules/available-typed-arrays": {
      "version": "1.0.7",
      "resolved": "https://registry.npmjs.org/available-typed-arrays/-/available-typed-arrays-1.0.7.tgz",
      "integrity": "sha512-wvUjBtSGN7+7SjNpq/9M2Tg350UZD3q62IFZLbRAR1bSMlCo1ZaeW+BJ+D090e4hIIZLBcTDWe4Mh4jvUDajzQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "possible-typed-array-names": "^1.0.0"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/axe-core": {
      "version": "4.11.4",
      "resolved": "https://registry.npmjs.org/axe-core/-/axe-core-4.11.4.tgz",
      "integrity": "sha512-KunSNx+TVpkAw/6ULfhnx+HWRecjqZGTOyquAoWHYLRSdK1tB5Ihce1ZW+UY3fj33bYAFWPu7W/GRSmmrCGuxA==",
      "dev": true,
      "license": "MPL-2.0",
      "engines": {
        "node": ">=4"
      }
    },
    "node_modules/axobject-query": {
      "version": "4.1.0",
      "resolved": "https://registry.npmjs.org/axobject-query/-/axobject-query-4.1.0.tgz",
      "integrity": "sha512-qIj0G9wZbMGNLjLmg1PT6v2mE9AH2zlnADJD/2tC6E00hgmhUOfEB6greHPAfLRSufHqROIUTkw6E+M3lH0PTQ==",
      "dev": true,
      "license": "Apache-2.0",
      "engines": {
        "node": ">= 0.4"
      }
    },
    "node_modules/balanced-match": {
      "version": "1.0.2",
      "resolved": "https://registry.npmjs.org/balanced-match/-/balanced-match-1.0.2.tgz",
      "integrity": "sha512-3oSeUO0TMV67hN1AmbXsK4yaqU7tjiHlbxRDZOpH0KW9+CeX4bRAaX0Anxt0tx2MrpRpWwQaPwIlISEJhYU5Pw==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/baseline-browser-mapping": {
      "version": "2.10.27",
      "resolved": "https://registry.npmjs.org/baseline-browser-mapping/-/baseline-browser-mapping-2.10.27.tgz",
      "integrity": "sha512-zEs/ufmZoUd7WftKpKyXaT6RFxpQ5Qm9xytKRHvJfxFV9DFJkZph9RvJ1LcOUi0Z1ZVijMte65JbILeV+8QQEA==",
      "license": "Apache-2.0",
      "bin": {
        "baseline-browser-mapping": "dist/cli.cjs"
      },
      "engines": {
        "node": ">=6.0.0"
      }
    },
    "node_modules/brace-expansion": {
      "version": "1.1.14",
      "resolved": "https://registry.npmjs.org/brace-expansion/-/brace-expansion-1.1.14.tgz",
      "integrity": "sha512-MWPGfDxnyzKU7rNOW9SP/c50vi3xrmrua/+6hfPbCS2ABNWfx24vPidzvC7krjU/RTo235sV776ymlsMtGKj8g==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "balanced-match": "^1.0.0",
        "concat-map": "0.0.1"
      }
    },
    "node_modules/braces": {
      "version": "3.0.3",
      "resolved": "https://registry.npmjs.org/braces/-/braces-3.0.3.tgz",
      "integrity": "sha512-yQbXgO/OSZVD2IsiLlro+7Hf6Q18EJrKSEsdoMzKePKXct3gvD8oLcOQdIzGupr5Fj+EDe8gO/lxc1BzfMpxvA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "fill-range": "^7.1.1"
      },
      "engines": {
        "node": ">=8"
      }
    },
    "node_modules/browserslist": {
      "version": "4.28.2",
      "resolved": "https://registry.npmjs.org/browserslist/-/browserslist-4.28.2.tgz",
      "integrity": "sha512-48xSriZYYg+8qXna9kwqjIVzuQxi+KYWp2+5nCYnYKPTr0LvD89Jqk2Or5ogxz0NUMfIjhh2lIUX/LyX9B4oIg==",
      "dev": true,
      "funding": [
        {
          "type": "opencollective",
          "url": "https://opencollective.com/browserslist"
        },
        {
          "type": "tidelift",
          "url": "https://tidelift.com/funding/github/npm/browserslist"
        },
        {
          "type": "github",
          "url": "https://github.com/sponsors/ai"
        }
      ],
      "license": "MIT",
      "dependencies": {
        "baseline-browser-mapping": "^2.10.12",
        "caniuse-lite": "^1.0.30001782",
        "electron-to-chromium": "^1.5.328",
        "node-releases": "^2.0.36",
        "update-browserslist-db": "^1.2.3"
      },
      "bin": {
        "browserslist": "cli.js"
      },
      "engines": {
        "node": "^6 || ^7 || ^8 || ^9 || ^10 || ^11 || ^12 || >=13.7"
      }
    },
    "node_modules/call-bind": {
      "version": "1.0.9",
      "resolved": "https://registry.npmjs.org/call-bind/-/call-bind-1.0.9.tgz",
      "integrity": "sha512-a/hy+pNsFUTR+Iz8TCJvXudKVLAnz/DyeSUo10I5yvFDQJBFU2s9uqQpoSrJlroHUKoKqzg+epxyP9lqFdzfBQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bind-apply-helpers": "^1.0.2",
        "es-define-property": "^1.0.1",
        "get-intrinsic": "^1.3.0",
        "set-function-length": "^1.2.2"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/call-bind-apply-helpers": {
      "version": "1.0.2",
      "resolved": "https://registry.npmjs.org/call-bind-apply-helpers/-/call-bind-apply-helpers-1.0.2.tgz",
      "integrity": "sha512-Sp1ablJ0ivDkSzjcaJdxEunN5/XvksFJ2sMBFfq6x0ryhQV/2b/KwFe21cMpmHtPOSij8K99/wSfoEuTObmuMQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "es-errors": "^1.3.0",
        "function-bind": "^1.1.2"
      },
      "engines": {
        "node": ">= 0.4"
      }
    },
    "node_modules/call-bound": {
      "version": "1.0.4",
      "resolved": "https://registry.npmjs.org/call-bound/-/call-bound-1.0.4.tgz",
      "integrity": "sha512-+ys997U96po4Kx/ABpBCqhA9EuxJaQWDQg7295H4hBphv3IZg0boBKuwYpt4YXp6MZ5AmZQnU/tyMTlRpaSejg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bind-apply-helpers": "^1.0.2",
        "get-intrinsic": "^1.3.0"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/callsites": {
      "version": "3.1.0",
      "resolved": "https://registry.npmjs.org/callsites/-/callsites-3.1.0.tgz",
      "integrity": "sha512-P8BjAsXvZS+VIDUI11hHCQEv74YT67YUi5JJFNWIqL235sBmjX4+qx9Muvls5ivyNENctx46xQLQ3aTuE7ssaQ==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=6"
      }
    },
    "node_modules/caniuse-lite": {
      "version": "1.0.30001791",
      "resolved": "https://registry.npmjs.org/caniuse-lite/-/caniuse-lite-1.0.30001791.tgz",
      "integrity": "sha512-yk0l/YSrOnFZk3UROpDLQD9+kC1l4meK/wed583AXrzoarMGJcbRi2Q4RaUYbKxYAsZ8sWmaSa/DsLmdBeI1vQ==",
      "funding": [
        {
          "type": "opencollective",
          "url": "https://opencollective.com/browserslist"
        },
        {
          "type": "tidelift",
          "url": "https://tidelift.com/funding/github/npm/caniuse-lite"
        },
        {
          "type": "github",
          "url": "https://github.com/sponsors/ai"
        }
      ],
      "license": "CC-BY-4.0"
    },
    "node_modules/chalk": {
      "version": "4.1.2",
      "resolved": "https://registry.npmjs.org/chalk/-/chalk-4.1.2.tgz",
      "integrity": "sha512-oKnbhFyRIXpUuez8iBMmyEa4nbj4IOQyuhc/wy9kY7/WVPcwIO9VA668Pu8RkO7+0G76SLROeyw9CpQ061i4mA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "ansi-styles": "^4.1.0",
        "supports-color": "^7.1.0"
      },
      "engines": {
        "node": ">=10"
      },
      "funding": {
        "url": "https://github.com/chalk/chalk?sponsor=1"
      }
    },
    "node_modules/client-only": {
      "version": "0.0.1",
      "resolved": "https://registry.npmjs.org/client-only/-/client-only-0.0.1.tgz",
      "integrity": "sha512-IV3Ou0jSMzZrd3pZ48nLkT9DA7Ag1pnPzaiQhpW7c3RbcqqzvzzVu+L8gfqMp/8IM2MQtSiqaCxrrcfu8I8rMA==",
      "license": "MIT"
    },
    "node_modules/color-convert": {
      "version": "2.0.1",
      "resolved": "https://registry.npmjs.org/color-convert/-/color-convert-2.0.1.tgz",
      "integrity": "sha512-RRECPsj7iu/xb5oKYcsFHSppFNnsj/52OVTRKb4zP5onXwVF3zVmmToNcOfGC+CRDpfK/U584fMg38ZHCaElKQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "color-name": "~1.1.4"
      },
      "engines": {
        "node": ">=7.0.0"
      }
    },
    "node_modules/color-name": {
      "version": "1.1.4",
      "resolved": "https://registry.npmjs.org/color-name/-/color-name-1.1.4.tgz",
      "integrity": "sha512-dOy+3AuW3a2wNbZHIuMZpTcgjGuLU/uBL/ubcZF9OXbDo8ff4O8yVp5Bf0efS8uEoYo5q4Fx7dY9OgQGXgAsQA==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/concat-map": {
      "version": "0.0.1",
      "resolved": "https://registry.npmjs.org/concat-map/-/concat-map-0.0.1.tgz",
      "integrity": "sha512-/Srv4dswyQNBfohGpz9o6Yb3Gz3SrUDqBH5rTuhGR7ahtlbYKnVxw2bCFMRljaA7EXHaXZ8wsHdodFvbkhKmqg==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/convert-source-map": {
      "version": "2.0.0",
      "resolved": "https://registry.npmjs.org/convert-source-map/-/convert-source-map-2.0.0.tgz",
      "integrity": "sha512-Kvp459HrV2FEJ1CAsi1Ku+MY3kasH19TFykTz2xWmMeq6bk2NU3XXvfJ+Q61m0xktWwt+1HSYf3JZsTms3aRJg==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/cross-spawn": {
      "version": "7.0.6",
      "resolved": "https://registry.npmjs.org/cross-spawn/-/cross-spawn-7.0.6.tgz",
      "integrity": "sha512-uV2QOWP2nWzsy2aMp8aRibhi9dlzF5Hgh5SHaB9OiTGEyDTiJJyx0uy51QXdyWbtAHNua4XJzUKca3OzKUd3vA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "path-key": "^3.1.0",
        "shebang-command": "^2.0.0",
        "which": "^2.0.1"
      },
      "engines": {
        "node": ">= 8"
      }
    },
    "node_modules/csstype": {
      "version": "3.2.3",
      "resolved": "https://registry.npmjs.org/csstype/-/csstype-3.2.3.tgz",
      "integrity": "sha512-z1HGKcYy2xA8AGQfwrn0PAy+PB7X/GSj3UVJW9qKyn43xWa+gl5nXmU4qqLMRzWVLFC8KusUX8T/0kCiOYpAIQ==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/damerau-levenshtein": {
      "version": "1.0.8",
      "resolved": "https://registry.npmjs.org/damerau-levenshtein/-/damerau-levenshtein-1.0.8.tgz",
      "integrity": "sha512-sdQSFB7+llfUcQHUQO3+B8ERRj0Oa4w9POWMI/puGtuf7gFywGmkaLCElnudfTiKZV+NvHqL0ifzdrI8Ro7ESA==",
      "dev": true,
      "license": "BSD-2-Clause"
    },
    "node_modules/data-view-buffer": {
      "version": "1.0.2",
      "resolved": "https://registry.npmjs.org/data-view-buffer/-/data-view-buffer-1.0.2.tgz",
      "integrity": "sha512-EmKO5V3OLXh1rtK2wgXRansaK1/mtVdTUEiEI0W8RkvgT05kfxaH29PliLnpLP73yYO6142Q72QNa8Wx/A5CqQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bound": "^1.0.3",
        "es-errors": "^1.3.0",
        "is-data-view": "^1.0.2"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/data-view-byte-length": {
      "version": "1.0.2",
      "resolved": "https://registry.npmjs.org/data-view-byte-length/-/data-view-byte-length-1.0.2.tgz",
      "integrity": "sha512-tuhGbE6CfTM9+5ANGf+oQb72Ky/0+s3xKUpHvShfiz2RxMFgFPjsXuRLBVMtvMs15awe45SRb83D6wH4ew6wlQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bound": "^1.0.3",
        "es-errors": "^1.3.0",
        "is-data-view": "^1.0.2"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/inspect-js"
      }
    },
    "node_modules/data-view-byte-offset": {
      "version": "1.0.1",
      "resolved": "https://registry.npmjs.org/data-view-byte-offset/-/data-view-byte-offset-1.0.1.tgz",
      "integrity": "sha512-BS8PfmtDGnrgYdOonGZQdLZslWIeCGFP9tpan0hi1Co2Zr2NKADsvGYA8XxuG/4UWgJ6Cjtv+YJnB6MM69QGlQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bound": "^1.0.2",
        "es-errors": "^1.3.0",
        "is-data-view": "^1.0.1"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/debug": {
      "version": "4.4.3",
      "resolved": "https://registry.npmjs.org/debug/-/debug-4.4.3.tgz",
      "integrity": "sha512-RGwwWnwQvkVfavKVt22FGLw+xYSdzARwm0ru6DhTVA3umU5hZc28V3kO4stgYryrTlLpuvgI9GiijltAjNbcqA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "ms": "^2.1.3"
      },
      "engines": {
        "node": ">=6.0"
      },
      "peerDependenciesMeta": {
        "supports-color": {
          "optional": true
        }
      }
    },
    "node_modules/deep-is": {
      "version": "0.1.4",
      "resolved": "https://registry.npmjs.org/deep-is/-/deep-is-0.1.4.tgz",
      "integrity": "sha512-oIPzksmTg4/MriiaYGO+okXDT7ztn/w3Eptv/+gSIdMdKsJo0u4CfYNFJPy+4SKMuCqGw2wxnA+URMg3t8a/bQ==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/define-data-property": {
      "version": "1.1.4",
      "resolved": "https://registry.npmjs.org/define-data-property/-/define-data-property-1.1.4.tgz",
      "integrity": "sha512-rBMvIzlpA8v6E+SJZoo++HAYqsLrkg7MSfIinMPFhmkorw7X+dOXVJQs+QT69zGkzMyfDnIMN2Wid1+NbL3T+A==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "es-define-property": "^1.0.0",
        "es-errors": "^1.3.0",
        "gopd": "^1.0.1"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/define-properties": {
      "version": "1.2.1",
      "resolved": "https://registry.npmjs.org/define-properties/-/define-properties-1.2.1.tgz",
      "integrity": "sha512-8QmQKqEASLd5nx0U1B1okLElbUuuttJ/AnYmRXbbbGDWh6uS208EjD4Xqq/I9wK7u0v6O08XhTWnt5XtEbR6Dg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "define-data-property": "^1.0.1",
        "has-property-descriptors": "^1.0.0",
        "object-keys": "^1.1.1"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/detect-libc": {
      "version": "2.1.2",
      "resolved": "https://registry.npmjs.org/detect-libc/-/detect-libc-2.1.2.tgz",
      "integrity": "sha512-Btj2BOOO83o3WyH59e8MgXsxEQVcarkUOpEYrubB0urwnN10yQ364rsiByU11nZlqWYZm05i/of7io4mzihBtQ==",
      "devOptional": true,
      "license": "Apache-2.0",
      "engines": {
        "node": ">=8"
      }
    },
    "node_modules/doctrine": {
      "version": "2.1.0",
      "resolved": "https://registry.npmjs.org/doctrine/-/doctrine-2.1.0.tgz",
      "integrity": "sha512-35mSku4ZXK0vfCuHEDAwt55dg2jNajHZ1odvF+8SSr82EsZY4QmXfuWso8oEd8zRhVObSN18aM0CjSdoBX7zIw==",
      "dev": true,
      "license": "Apache-2.0",
      "dependencies": {
        "esutils": "^2.0.2"
      },
      "engines": {
        "node": ">=0.10.0"
      }
    },
    "node_modules/dunder-proto": {
      "version": "1.0.1",
      "resolved": "https://registry.npmjs.org/dunder-proto/-/dunder-proto-1.0.1.tgz",
      "integrity": "sha512-KIN/nDJBQRcXw0MLVhZE9iQHmG68qAVIBg9CqmUYjmQIhgij9U5MFvrqkUL5FbtyyzZuOeOt0zdeRe4UY7ct+A==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bind-apply-helpers": "^1.0.1",
        "es-errors": "^1.3.0",
        "gopd": "^1.2.0"
      },
      "engines": {
        "node": ">= 0.4"
      }
    },
    "node_modules/electron-to-chromium": {
      "version": "1.5.351",
      "resolved": "https://registry.npmjs.org/electron-to-chromium/-/electron-to-chromium-1.5.351.tgz",
      "integrity": "sha512-9D7Iqx8RImSvCnOsj86rCH6eQjZFQoM04Jn6HnZVM0Nu/G58/gmKYQ1d12MZTbjQbQSTGI8nwEy07ErsA2slLA==",
      "dev": true,
      "license": "ISC"
    },
    "node_modules/emoji-regex": {
      "version": "9.2.2",
      "resolved": "https://registry.npmjs.org/emoji-regex/-/emoji-regex-9.2.2.tgz",
      "integrity": "sha512-L18DaJsXSUk2+42pv8mLs5jJT2hqFkFE4j21wOmgbUqsZ2hL72NsUU785g9RXgo3s0ZNgVl42TiHp3ZtOv/Vyg==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/enhanced-resolve": {
      "version": "5.21.0",
      "resolved": "https://registry.npmjs.org/enhanced-resolve/-/enhanced-resolve-5.21.0.tgz",
      "integrity": "sha512-otxSQPw4lkOZWkHpB3zaEQs6gWYEsmX4xQF68ElXC/TWvGxGMSGOvoNbaLXm6/cS/fSfHtsEdw90y20PCd+sCA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "graceful-fs": "^4.2.4",
        "tapable": "^2.3.3"
      },
      "engines": {
        "node": ">=10.13.0"
      }
    },
    "node_modules/es-abstract": {
      "version": "1.24.2",
      "resolved": "https://registry.npmjs.org/es-abstract/-/es-abstract-1.24.2.tgz",
      "integrity": "sha512-2FpH9Q5i2RRwyEP1AylXe6nYLR5OhaJTZwmlcP0dL/+JCbgg7yyEo/sEK6HeGZRf3dFpWwThaRHVApXSkW3xeg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "array-buffer-byte-length": "^1.0.2",
        "arraybuffer.prototype.slice": "^1.0.4",
        "available-typed-arrays": "^1.0.7",
        "call-bind": "^1.0.8",
        "call-bound": "^1.0.4",
        "data-view-buffer": "^1.0.2",
        "data-view-byte-length": "^1.0.2",
        "data-view-byte-offset": "^1.0.1",
        "es-define-property": "^1.0.1",
        "es-errors": "^1.3.0",
        "es-object-atoms": "^1.1.1",
        "es-set-tostringtag": "^2.1.0",
        "es-to-primitive": "^1.3.0",
        "function.prototype.name": "^1.1.8",
        "get-intrinsic": "^1.3.0",
        "get-proto": "^1.0.1",
        "get-symbol-description": "^1.1.0",
        "globalthis": "^1.0.4",
        "gopd": "^1.2.0",
        "has-property-descriptors": "^1.0.2",
        "has-proto": "^1.2.0",
        "has-symbols": "^1.1.0",
        "hasown": "^2.0.2",
        "internal-slot": "^1.1.0",
        "is-array-buffer": "^3.0.5",
        "is-callable": "^1.2.7",
        "is-data-view": "^1.0.2",
        "is-negative-zero": "^2.0.3",
        "is-regex": "^1.2.1",
        "is-set": "^2.0.3",
        "is-shared-array-buffer": "^1.0.4",
        "is-string": "^1.1.1",
        "is-typed-array": "^1.1.15",
        "is-weakref": "^1.1.1",
        "math-intrinsics": "^1.1.0",
        "object-inspect": "^1.13.4",
        "object-keys": "^1.1.1",
        "object.assign": "^4.1.7",
        "own-keys": "^1.0.1",
        "regexp.prototype.flags": "^1.5.4",
        "safe-array-concat": "^1.1.3",
        "safe-push-apply": "^1.0.0",
        "safe-regex-test": "^1.1.0",
        "set-proto": "^1.0.0",
        "stop-iteration-iterator": "^1.1.0",
        "string.prototype.trim": "^1.2.10",
        "string.prototype.trimend": "^1.0.9",
        "string.prototype.trimstart": "^1.0.8",
        "typed-array-buffer": "^1.0.3",
        "typed-array-byte-length": "^1.0.3",
        "typed-array-byte-offset": "^1.0.4",
        "typed-array-length": "^1.0.7",
        "unbox-primitive": "^1.1.0",
        "which-typed-array": "^1.1.19"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/es-define-property": {
      "version": "1.0.1",
      "resolved": "https://registry.npmjs.org/es-define-property/-/es-define-property-1.0.1.tgz",
      "integrity": "sha512-e3nRfgfUZ4rNGL232gUgX06QNyyez04KdjFrF+LTRoOXmrOgFKDg4BCdsjW8EnT69eqdYGmRpJwiPVYNrCaW3g==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">= 0.4"
      }
    },
    "node_modules/es-errors": {
      "version": "1.3.0",
      "resolved": "https://registry.npmjs.org/es-errors/-/es-errors-1.3.0.tgz",
      "integrity": "sha512-Zf5H2Kxt2xjTvbJvP2ZWLEICxA6j+hAmMzIlypy4xcBg1vKVnx89Wy0GbS+kf5cwCVFFzdCFh2XSCFNULS6csw==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">= 0.4"
      }
    },
    "node_modules/es-iterator-helpers": {
      "version": "1.3.2",
      "resolved": "https://registry.npmjs.org/es-iterator-helpers/-/es-iterator-helpers-1.3.2.tgz",
      "integrity": "sha512-HVLACW1TppGYjJ8H6/jqH/pqOtKRw6wMlrB23xfExmFWxFquAIWCmwoLsOyN96K4a5KbmOf5At9ZUO3GZbetAw==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bind": "^1.0.9",
        "call-bound": "^1.0.4",
        "define-properties": "^1.2.1",
        "es-abstract": "^1.24.2",
        "es-errors": "^1.3.0",
        "es-set-tostringtag": "^2.1.0",
        "function-bind": "^1.1.2",
        "get-intrinsic": "^1.3.0",
        "globalthis": "^1.0.4",
        "gopd": "^1.2.0",
        "has-property-descriptors": "^1.0.2",
        "has-proto": "^1.2.0",
        "has-symbols": "^1.1.0",
        "internal-slot": "^1.1.0",
        "iterator.prototype": "^1.1.5",
        "math-intrinsics": "^1.1.0"
      },
      "engines": {
        "node": ">= 0.4"
      }
    },
    "node_modules/es-object-atoms": {
      "version": "1.1.1",
      "resolved": "https://registry.npmjs.org/es-object-atoms/-/es-object-atoms-1.1.1.tgz",
      "integrity": "sha512-FGgH2h8zKNim9ljj7dankFPcICIK9Cp5bm+c2gQSYePhpaG5+esrLODihIorn+Pe6FGJzWhXQotPv73jTaldXA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "es-errors": "^1.3.0"
      },
      "engines": {
        "node": ">= 0.4"
      }
    },
    "node_modules/es-set-tostringtag": {
      "version": "2.1.0",
      "resolved": "https://registry.npmjs.org/es-set-tostringtag/-/es-set-tostringtag-2.1.0.tgz",
      "integrity": "sha512-j6vWzfrGVfyXxge+O0x5sh6cvxAog0a/4Rdd2K36zCMV5eJ+/+tOAngRO8cODMNWbVRdVlmGZQL2YS3yR8bIUA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "es-errors": "^1.3.0",
        "get-intrinsic": "^1.2.6",
        "has-tostringtag": "^1.0.2",
        "hasown": "^2.0.2"
      },
      "engines": {
        "node": ">= 0.4"
      }
    },
    "node_modules/es-shim-unscopables": {
      "version": "1.1.0",
      "resolved": "https://registry.npmjs.org/es-shim-unscopables/-/es-shim-unscopables-1.1.0.tgz",
      "integrity": "sha512-d9T8ucsEhh8Bi1woXCf+TIKDIROLG5WCkxg8geBCbvk22kzwC5G2OnXVMO6FUsvQlgUUXQ2itephWDLqDzbeCw==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "hasown": "^2.0.2"
      },
      "engines": {
        "node": ">= 0.4"
      }
    },
    "node_modules/es-to-primitive": {
      "version": "1.3.0",
      "resolved": "https://registry.npmjs.org/es-to-primitive/-/es-to-primitive-1.3.0.tgz",
      "integrity": "sha512-w+5mJ3GuFL+NjVtJlvydShqE1eN3h3PbI7/5LAsYJP/2qtuMXjfL2LpHSRqo4b4eSF5K/DH1JXKUAHSB2UW50g==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "is-callable": "^1.2.7",
        "is-date-object": "^1.0.5",
        "is-symbol": "^1.0.4"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/escalade": {
      "version": "3.2.0",
      "resolved": "https://registry.npmjs.org/escalade/-/escalade-3.2.0.tgz",
      "integrity": "sha512-WUj2qlxaQtO4g6Pq5c29GTcWGDyd8itL8zTlipgECz3JesAiiOKotd8JU6otB3PACgG6xkJUyVhboMS+bje/jA==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=6"
      }
    },
    "node_modules/escape-string-regexp": {
      "version": "4.0.0",
      "resolved": "https://registry.npmjs.org/escape-string-regexp/-/escape-string-regexp-4.0.0.tgz",
      "integrity": "sha512-TtpcNJ3XAzx3Gq8sWRzJaVajRs0uVxA2YAkdb1jm2YkPz4G6egUFAyA3n5vtEIZefPk5Wa4UXbKuS5fKkJWdgA==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=10"
      },
      "funding": {
        "url": "https://github.com/sponsors/sindresorhus"
      }
    },
    "node_modules/eslint": {
      "version": "9.39.4",
      "resolved": "https://registry.npmjs.org/eslint/-/eslint-9.39.4.tgz",
      "integrity": "sha512-XoMjdBOwe/esVgEvLmNsD3IRHkm7fbKIUGvrleloJXUZgDHig2IPWNniv+GwjyJXzuNqVjlr5+4yVUZjycJwfQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "@eslint-community/eslint-utils": "^4.8.0",
        "@eslint-community/regexpp": "^4.12.1",
        "@eslint/config-array": "^0.21.2",
        "@eslint/config-helpers": "^0.4.2",
        "@eslint/core": "^0.17.0",
        "@eslint/eslintrc": "^3.3.5",
        "@eslint/js": "9.39.4",
        "@eslint/plugin-kit": "^0.4.1",
        "@humanfs/node": "^0.16.6",
        "@humanwhocodes/module-importer": "^1.0.1",
        "@humanwhocodes/retry": "^0.4.2",
        "@types/estree": "^1.0.6",
        "ajv": "^6.14.0",
        "chalk": "^4.0.0",
        "cross-spawn": "^7.0.6",
        "debug": "^4.3.2",
        "escape-string-regexp": "^4.0.0",
        "eslint-scope": "^8.4.0",
        "eslint-visitor-keys": "^4.2.1",
        "espree": "^10.4.0",
        "esquery": "^1.5.0",
        "esutils": "^2.0.2",
        "fast-deep-equal": "^3.1.3",
        "file-entry-cache": "^8.0.0",
        "find-up": "^5.0.0",
        "glob-parent": "^6.0.2",
        "ignore": "^5.2.0",
        "imurmurhash": "^0.1.4",
        "is-glob": "^4.0.0",
        "json-stable-stringify-without-jsonify": "^1.0.1",
        "lodash.merge": "^4.6.2",
        "minimatch": "^3.1.5",
        "natural-compare": "^1.4.0",
        "optionator": "^0.9.3"
      },
      "bin": {
        "eslint": "bin/eslint.js"
      },
      "engines": {
        "node": "^18.18.0 || ^20.9.0 || >=21.1.0"
      },
      "funding": {
        "url": "https://eslint.org/donate"
      },
      "peerDependencies": {
        "jiti": "*"
      },
      "peerDependenciesMeta": {
        "jiti": {
          "optional": true
        }
      }
    },
    "node_modules/eslint-config-next": {
      "version": "16.2.4",
      "resolved": "https://registry.npmjs.org/eslint-config-next/-/eslint-config-next-16.2.4.tgz",
      "integrity": "sha512-A6ekXYFj/YQxBPMl45g3e+U8zJo+X2+ZQwcz34pPKjpc/3S4roBA2Rd9xWB4FKuSxhofo1/95WjzmUY+wHrOhg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "@next/eslint-plugin-next": "16.2.4",
        "eslint-import-resolver-node": "^0.3.6",
        "eslint-import-resolver-typescript": "^3.5.2",
        "eslint-plugin-import": "^2.32.0",
        "eslint-plugin-jsx-a11y": "^6.10.0",
        "eslint-plugin-react": "^7.37.0",
        "eslint-plugin-react-hooks": "^7.0.0",
        "globals": "16.4.0",
        "typescript-eslint": "^8.46.0"
      },
      "peerDependencies": {
        "eslint": ">=9.0.0",
        "typescript": ">=3.3.1"
      },
      "peerDependenciesMeta": {
        "typescript": {
          "optional": true
        }
      }
    },
    "node_modules/eslint-config-next/node_modules/globals": {
      "version": "16.4.0",
      "resolved": "https://registry.npmjs.org/globals/-/globals-16.4.0.tgz",
      "integrity": "sha512-ob/2LcVVaVGCYN+r14cnwnoDPUufjiYgSqRhiFD0Q1iI4Odora5RE8Iv1D24hAz5oMophRGkGz+yuvQmmUMnMw==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=18"
      },
      "funding": {
        "url": "https://github.com/sponsors/sindresorhus"
      }
    },
    "node_modules/eslint-import-resolver-node": {
      "version": "0.3.10",
      "resolved": "https://registry.npmjs.org/eslint-import-resolver-node/-/eslint-import-resolver-node-0.3.10.tgz",
      "integrity": "sha512-tRrKqFyCaKict5hOd244sL6EQFNycnMQnBe+j8uqGNXYzsImGbGUU4ibtoaBmv5FLwJwcFJNeg1GeVjQfbMrDQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "debug": "^3.2.7",
        "is-core-module": "^2.16.1",
        "resolve": "^2.0.0-next.6"
      }
    },
    "node_modules/eslint-import-resolver-node/node_modules/debug": {
      "version": "3.2.7",
      "resolved": "https://registry.npmjs.org/debug/-/debug-3.2.7.tgz",
      "integrity": "sha512-CFjzYYAi4ThfiQvizrFQevTTXHtnCqWfe7x1AhgEscTz6ZbLbfoLRLPugTQyBth6f8ZERVUSyWHFD/7Wu4t1XQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "ms": "^2.1.1"
      }
    },
    "node_modules/eslint-import-resolver-typescript": {
      "version": "3.10.1",
      "resolved": "https://registry.npmjs.org/eslint-import-resolver-typescript/-/eslint-import-resolver-typescript-3.10.1.tgz",
      "integrity": "sha512-A1rHYb06zjMGAxdLSkN2fXPBwuSaQ0iO5M/hdyS0Ajj1VBaRp0sPD3dn1FhME3c/JluGFbwSxyCfqdSbtQLAHQ==",
      "dev": true,
      "license": "ISC",
      "dependencies": {
        "@nolyfill/is-core-module": "1.0.39",
        "debug": "^4.4.0",
        "get-tsconfig": "^4.10.0",
        "is-bun-module": "^2.0.0",
        "stable-hash": "^0.0.5",
        "tinyglobby": "^0.2.13",
        "unrs-resolver": "^1.6.2"
      },
      "engines": {
        "node": "^14.18.0 || >=16.0.0"
      },
      "funding": {
        "url": "https://opencollective.com/eslint-import-resolver-typescript"
      },
      "peerDependencies": {
        "eslint": "*",
        "eslint-plugin-import": "*",
        "eslint-plugin-import-x": "*"
      },
      "peerDependenciesMeta": {
        "eslint-plugin-import": {
          "optional": true
        },
        "eslint-plugin-import-x": {
          "optional": true
        }
      }
    },
    "node_modules/eslint-module-utils": {
      "version": "2.12.1",
      "resolved": "https://registry.npmjs.org/eslint-module-utils/-/eslint-module-utils-2.12.1.tgz",
      "integrity": "sha512-L8jSWTze7K2mTg0vos/RuLRS5soomksDPoJLXIslC7c8Wmut3bx7CPpJijDcBZtxQ5lrbUdM+s0OlNbz0DCDNw==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "debug": "^3.2.7"
      },
      "engines": {
        "node": ">=4"
      },
      "peerDependenciesMeta": {
        "eslint": {
          "optional": true
        }
      }
    },
    "node_modules/eslint-module-utils/node_modules/debug": {
      "version": "3.2.7",
      "resolved": "https://registry.npmjs.org/debug/-/debug-3.2.7.tgz",
      "integrity": "sha512-CFjzYYAi4ThfiQvizrFQevTTXHtnCqWfe7x1AhgEscTz6ZbLbfoLRLPugTQyBth6f8ZERVUSyWHFD/7Wu4t1XQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "ms": "^2.1.1"
      }
    },
    "node_modules/eslint-plugin-import": {
      "version": "2.32.0",
      "resolved": "https://registry.npmjs.org/eslint-plugin-import/-/eslint-plugin-import-2.32.0.tgz",
      "integrity": "sha512-whOE1HFo/qJDyX4SnXzP4N6zOWn79WhnCUY/iDR0mPfQZO8wcYE4JClzI2oZrhBnnMUCBCHZhO6VQyoBU95mZA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "@rtsao/scc": "^1.1.0",
        "array-includes": "^3.1.9",
        "array.prototype.findlastindex": "^1.2.6",
        "array.prototype.flat": "^1.3.3",
        "array.prototype.flatmap": "^1.3.3",
        "debug": "^3.2.7",
        "doctrine": "^2.1.0",
        "eslint-import-resolver-node": "^0.3.9",
        "eslint-module-utils": "^2.12.1",
        "hasown": "^2.0.2",
        "is-core-module": "^2.16.1",
        "is-glob": "^4.0.3",
        "minimatch": "^3.1.2",
        "object.fromentries": "^2.0.8",
        "object.groupby": "^1.0.3",
        "object.values": "^1.2.1",
        "semver": "^6.3.1",
        "string.prototype.trimend": "^1.0.9",
        "tsconfig-paths": "^3.15.0"
      },
      "engines": {
        "node": ">=4"
      },
      "peerDependencies": {
        "eslint": "^2 || ^3 || ^4 || ^5 || ^6 || ^7.2.0 || ^8 || ^9"
      }
    },
    "node_modules/eslint-plugin-import/node_modules/debug": {
      "version": "3.2.7",
      "resolved": "https://registry.npmjs.org/debug/-/debug-3.2.7.tgz",
      "integrity": "sha512-CFjzYYAi4ThfiQvizrFQevTTXHtnCqWfe7x1AhgEscTz6ZbLbfoLRLPugTQyBth6f8ZERVUSyWHFD/7Wu4t1XQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "ms": "^2.1.1"
      }
    },
    "node_modules/eslint-plugin-jsx-a11y": {
      "version": "6.10.2",
      "resolved": "https://registry.npmjs.org/eslint-plugin-jsx-a11y/-/eslint-plugin-jsx-a11y-6.10.2.tgz",
      "integrity": "sha512-scB3nz4WmG75pV8+3eRUQOHZlNSUhFNq37xnpgRkCCELU3XMvXAxLk1eqWWyE22Ki4Q01Fnsw9BA3cJHDPgn2Q==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "aria-query": "^5.3.2",
        "array-includes": "^3.1.8",
        "array.prototype.flatmap": "^1.3.2",
        "ast-types-flow": "^0.0.8",
        "axe-core": "^4.10.0",
        "axobject-query": "^4.1.0",
        "damerau-levenshtein": "^1.0.8",
        "emoji-regex": "^9.2.2",
        "hasown": "^2.0.2",
        "jsx-ast-utils": "^3.3.5",
        "language-tags": "^1.0.9",
        "minimatch": "^3.1.2",
        "object.fromentries": "^2.0.8",
        "safe-regex-test": "^1.0.3",
        "string.prototype.includes": "^2.0.1"
      },
      "engines": {
        "node": ">=4.0"
      },
      "peerDependencies": {
        "eslint": "^3 || ^4 || ^5 || ^6 || ^7 || ^8 || ^9"
      }
    },
    "node_modules/eslint-plugin-react": {
      "version": "7.37.5",
      "resolved": "https://registry.npmjs.org/eslint-plugin-react/-/eslint-plugin-react-7.37.5.tgz",
      "integrity": "sha512-Qteup0SqU15kdocexFNAJMvCJEfa2xUKNV4CC1xsVMrIIqEy3SQ/rqyxCWNzfrd3/ldy6HMlD2e0JDVpDg2qIA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "array-includes": "^3.1.8",
        "array.prototype.findlast": "^1.2.5",
        "array.prototype.flatmap": "^1.3.3",
        "array.prototype.tosorted": "^1.1.4",
        "doctrine": "^2.1.0",
        "es-iterator-helpers": "^1.2.1",
        "estraverse": "^5.3.0",
        "hasown": "^2.0.2",
        "jsx-ast-utils": "^2.4.1 || ^3.0.0",
        "minimatch": "^3.1.2",
        "object.entries": "^1.1.9",
        "object.fromentries": "^2.0.8",
        "object.values": "^1.2.1",
        "prop-types": "^15.8.1",
        "resolve": "^2.0.0-next.5",
        "semver": "^6.3.1",
        "string.prototype.matchall": "^4.0.12",
        "string.prototype.repeat": "^1.0.0"
      },
      "engines": {
        "node": ">=4"
      },
      "peerDependencies": {
        "eslint": "^3 || ^4 || ^5 || ^6 || ^7 || ^8 || ^9.7"
      }
    },
    "node_modules/eslint-plugin-react-hooks": {
      "version": "7.1.1",
      "resolved": "https://registry.npmjs.org/eslint-plugin-react-hooks/-/eslint-plugin-react-hooks-7.1.1.tgz",
      "integrity": "sha512-f2I7Gw6JbvCexzIInuSbZpfdQ44D7iqdWX01FKLvrPgqxoE7oMj8clOfto8U6vYiz4yd5oKu39rRSVOe1zRu0g==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "@babel/core": "^7.24.4",
        "@babel/parser": "^7.24.4",
        "hermes-parser": "^0.25.1",
        "zod": "^3.25.0 || ^4.0.0",
        "zod-validation-error": "^3.5.0 || ^4.0.0"
      },
      "engines": {
        "node": ">=18"
      },
      "peerDependencies": {
        "eslint": "^3.0.0 || ^4.0.0 || ^5.0.0 || ^6.0.0 || ^7.0.0 || ^8.0.0-0 || ^9.0.0 || ^10.0.0"
      }
    },
    "node_modules/eslint-scope": {
      "version": "8.4.0",
      "resolved": "https://registry.npmjs.org/eslint-scope/-/eslint-scope-8.4.0.tgz",
      "integrity": "sha512-sNXOfKCn74rt8RICKMvJS7XKV/Xk9kA7DyJr8mJik3S7Cwgy3qlkkmyS2uQB3jiJg6VNdZd/pDBJu0nvG2NlTg==",
      "dev": true,
      "license": "BSD-2-Clause",
      "dependencies": {
        "esrecurse": "^4.3.0",
        "estraverse": "^5.2.0"
      },
      "engines": {
        "node": "^18.18.0 || ^20.9.0 || >=21.1.0"
      },
      "funding": {
        "url": "https://opencollective.com/eslint"
      }
    },
    "node_modules/eslint-visitor-keys": {
      "version": "4.2.1",
      "resolved": "https://registry.npmjs.org/eslint-visitor-keys/-/eslint-visitor-keys-4.2.1.tgz",
      "integrity": "sha512-Uhdk5sfqcee/9H/rCOJikYz67o0a2Tw2hGRPOG2Y1R2dg7brRe1uG0yaNQDHu+TO/uQPF/5eCapvYSmHUjt7JQ==",
      "dev": true,
      "license": "Apache-2.0",
      "engines": {
        "node": "^18.18.0 || ^20.9.0 || >=21.1.0"
      },
      "funding": {
        "url": "https://opencollective.com/eslint"
      }
    },
    "node_modules/espree": {
      "version": "10.4.0",
      "resolved": "https://registry.npmjs.org/espree/-/espree-10.4.0.tgz",
      "integrity": "sha512-j6PAQ2uUr79PZhBjP5C5fhl8e39FmRnOjsD5lGnWrFU8i2G776tBK7+nP8KuQUTTyAZUwfQqXAgrVH5MbH9CYQ==",
      "dev": true,
      "license": "BSD-2-Clause",
      "dependencies": {
        "acorn": "^8.15.0",
        "acorn-jsx": "^5.3.2",
        "eslint-visitor-keys": "^4.2.1"
      },
      "engines": {
        "node": "^18.18.0 || ^20.9.0 || >=21.1.0"
      },
      "funding": {
        "url": "https://opencollective.com/eslint"
      }
    },
    "node_modules/esquery": {
      "version": "1.7.0",
      "resolved": "https://registry.npmjs.org/esquery/-/esquery-1.7.0.tgz",
      "integrity": "sha512-Ap6G0WQwcU/LHsvLwON1fAQX9Zp0A2Y6Y/cJBl9r/JbW90Zyg4/zbG6zzKa2OTALELarYHmKu0GhpM5EO+7T0g==",
      "dev": true,
      "license": "BSD-3-Clause",
      "dependencies": {
        "estraverse": "^5.1.0"
      },
      "engines": {
        "node": ">=0.10"
      }
    },
    "node_modules/esrecurse": {
      "version": "4.3.0",
      "resolved": "https://registry.npmjs.org/esrecurse/-/esrecurse-4.3.0.tgz",
      "integrity": "sha512-KmfKL3b6G+RXvP8N1vr3Tq1kL/oCFgn2NYXEtqP8/L3pKapUA4G8cFVaoF3SU323CD4XypR/ffioHmkti6/Tag==",
      "dev": true,
      "license": "BSD-2-Clause",
      "dependencies": {
        "estraverse": "^5.2.0"
      },
      "engines": {
        "node": ">=4.0"
      }
    },
    "node_modules/estraverse": {
      "version": "5.3.0",
      "resolved": "https://registry.npmjs.org/estraverse/-/estraverse-5.3.0.tgz",
      "integrity": "sha512-MMdARuVEQziNTeJD8DgMqmhwR11BRQ/cBP+pLtYdSTnf3MIO8fFeiINEbX36ZdNlfU/7A9f3gUw49B3oQsvwBA==",
      "dev": true,
      "license": "BSD-2-Clause",
      "engines": {
        "node": ">=4.0"
      }
    },
    "node_modules/esutils": {
      "version": "2.0.3",
      "resolved": "https://registry.npmjs.org/esutils/-/esutils-2.0.3.tgz",
      "integrity": "sha512-kVscqXk4OCp68SZ0dkgEKVi6/8ij300KBWTJq32P/dYeWTSwK41WyTxalN1eRmA5Z9UU/LX9D7FWSmV9SAYx6g==",
      "dev": true,
      "license": "BSD-2-Clause",
      "engines": {
        "node": ">=0.10.0"
      }
    },
    "node_modules/fast-deep-equal": {
      "version": "3.1.3",
      "resolved": "https://registry.npmjs.org/fast-deep-equal/-/fast-deep-equal-3.1.3.tgz",
      "integrity": "sha512-f3qQ9oQy9j2AhBe/H9VC91wLmKBCCU/gDOnKNAYG5hswO7BLKj09Hc5HYNz9cGI++xlpDCIgDaitVs03ATR84Q==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/fast-glob": {
      "version": "3.3.1",
      "resolved": "https://registry.npmjs.org/fast-glob/-/fast-glob-3.3.1.tgz",
      "integrity": "sha512-kNFPyjhh5cKjrUltxs+wFx+ZkbRaxxmZ+X0ZU31SOsxCEtP9VPgtq2teZw1DebupL5GmDaNQ6yKMMVcM41iqDg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "@nodelib/fs.stat": "^2.0.2",
        "@nodelib/fs.walk": "^1.2.3",
        "glob-parent": "^5.1.2",
        "merge2": "^1.3.0",
        "micromatch": "^4.0.4"
      },
      "engines": {
        "node": ">=8.6.0"
      }
    },
    "node_modules/fast-glob/node_modules/glob-parent": {
      "version": "5.1.2",
      "resolved": "https://registry.npmjs.org/glob-parent/-/glob-parent-5.1.2.tgz",
      "integrity": "sha512-AOIgSQCepiJYwP3ARnGx+5VnTu2HBYdzbGP45eLw1vr3zB3vZLeyed1sC9hnbcOc9/SrMyM5RPQrkGz4aS9Zow==",
      "dev": true,
      "license": "ISC",
      "dependencies": {
        "is-glob": "^4.0.1"
      },
      "engines": {
        "node": ">= 6"
      }
    },
    "node_modules/fast-json-stable-stringify": {
      "version": "2.1.0",
      "resolved": "https://registry.npmjs.org/fast-json-stable-stringify/-/fast-json-stable-stringify-2.1.0.tgz",
      "integrity": "sha512-lhd/wF+Lk98HZoTCtlVraHtfh5XYijIjalXck7saUtuanSDyLMxnHhSXEDJqHxD7msR8D0uCmqlkwjCV8xvwHw==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/fast-levenshtein": {
      "version": "2.0.6",
      "resolved": "https://registry.npmjs.org/fast-levenshtein/-/fast-levenshtein-2.0.6.tgz",
      "integrity": "sha512-DCXu6Ifhqcks7TZKY3Hxp3y6qphY5SJZmrWMDrKcERSOXWQdMhU9Ig/PYrzyw/ul9jOIyh0N4M0tbC5hodg8dw==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/fastq": {
      "version": "1.20.1",
      "resolved": "https://registry.npmjs.org/fastq/-/fastq-1.20.1.tgz",
      "integrity": "sha512-GGToxJ/w1x32s/D2EKND7kTil4n8OVk/9mycTc4VDza13lOvpUZTGX3mFSCtV9ksdGBVzvsyAVLM6mHFThxXxw==",
      "dev": true,
      "license": "ISC",
      "dependencies": {
        "reusify": "^1.0.4"
      }
    },
    "node_modules/file-entry-cache": {
      "version": "8.0.0",
      "resolved": "https://registry.npmjs.org/file-entry-cache/-/file-entry-cache-8.0.0.tgz",
      "integrity": "sha512-XXTUwCvisa5oacNGRP9SfNtYBNAMi+RPwBFmblZEF7N7swHYQS6/Zfk7SRwx4D5j3CH211YNRco1DEMNVfZCnQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "flat-cache": "^4.0.0"
      },
      "engines": {
        "node": ">=16.0.0"
      }
    },
    "node_modules/fill-range": {
      "version": "7.1.1",
      "resolved": "https://registry.npmjs.org/fill-range/-/fill-range-7.1.1.tgz",
      "integrity": "sha512-YsGpe3WHLK8ZYi4tWDg2Jy3ebRz2rXowDxnld4bkQB00cc/1Zw9AWnC0i9ztDJitivtQvaI9KaLyKrc+hBW0yg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "to-regex-range": "^5.0.1"
      },
      "engines": {
        "node": ">=8"
      }
    },
    "node_modules/find-up": {
      "version": "5.0.0",
      "resolved": "https://registry.npmjs.org/find-up/-/find-up-5.0.0.tgz",
      "integrity": "sha512-78/PXT1wlLLDgTzDs7sjq9hzz0vXD+zn+7wypEe4fXQxCmdmqfGsEPQxmiCSQI3ajFV91bVSsvNtrJRiW6nGng==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "locate-path": "^6.0.0",
        "path-exists": "^4.0.0"
      },
      "engines": {
        "node": ">=10"
      },
      "funding": {
        "url": "https://github.com/sponsors/sindresorhus"
      }
    },
    "node_modules/flat-cache": {
      "version": "4.0.1",
      "resolved": "https://registry.npmjs.org/flat-cache/-/flat-cache-4.0.1.tgz",
      "integrity": "sha512-f7ccFPK3SXFHpx15UIGyRJ/FJQctuKZ0zVuN3frBo4HnK3cay9VEW0R6yPYFHC0AgqhukPzKjq22t5DmAyqGyw==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "flatted": "^3.2.9",
        "keyv": "^4.5.4"
      },
      "engines": {
        "node": ">=16"
      }
    },
    "node_modules/flatted": {
      "version": "3.4.2",
      "resolved": "https://registry.npmjs.org/flatted/-/flatted-3.4.2.tgz",
      "integrity": "sha512-PjDse7RzhcPkIJwy5t7KPWQSZ9cAbzQXcafsetQoD7sOJRQlGikNbx7yZp2OotDnJyrDcbyRq3Ttb18iYOqkxA==",
      "dev": true,
      "license": "ISC"
    },
    "node_modules/for-each": {
      "version": "0.3.5",
      "resolved": "https://registry.npmjs.org/for-each/-/for-each-0.3.5.tgz",
      "integrity": "sha512-dKx12eRCVIzqCxFGplyFKJMPvLEWgmNtUrpTiJIR5u97zEhRG8ySrtboPHZXx7daLxQVrl643cTzbab2tkQjxg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "is-callable": "^1.2.7"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/framer-motion": {
      "version": "12.38.0",
      "resolved": "https://registry.npmjs.org/framer-motion/-/framer-motion-12.38.0.tgz",
      "integrity": "sha512-rFYkY/pigbcswl1XQSb7q424kSTQ8q6eAC+YUsSKooHQYuLdzdHjrt6uxUC+PRAO++q5IS7+TamgIw1AphxR+g==",
      "license": "MIT",
      "dependencies": {
        "motion-dom": "^12.38.0",
        "motion-utils": "^12.36.0",
        "tslib": "^2.4.0"
      },
      "peerDependencies": {
        "@emotion/is-prop-valid": "*",
        "react": "^18.0.0 || ^19.0.0",
        "react-dom": "^18.0.0 || ^19.0.0"
      },
      "peerDependenciesMeta": {
        "@emotion/is-prop-valid": {
          "optional": true
        },
        "react": {
          "optional": true
        },
        "react-dom": {
          "optional": true
        }
      }
    },
    "node_modules/function-bind": {
      "version": "1.1.2",
      "resolved": "https://registry.npmjs.org/function-bind/-/function-bind-1.1.2.tgz",
      "integrity": "sha512-7XHNxH7qX9xG5mIwxkhumTox/MIRNcOgDrxWsMt2pAr23WHp6MrRlN7FBSFpCpr+oVO0F744iUgR82nJMfG2SA==",
      "dev": true,
      "license": "MIT",
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/function.prototype.name": {
      "version": "1.1.8",
      "resolved": "https://registry.npmjs.org/function.prototype.name/-/function.prototype.name-1.1.8.tgz",
      "integrity": "sha512-e5iwyodOHhbMr/yNrc7fDYG4qlbIvI5gajyzPnb5TCwyhjApznQh1BMFou9b30SevY43gCJKXycoCBjMbsuW0Q==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bind": "^1.0.8",
        "call-bound": "^1.0.3",
        "define-properties": "^1.2.1",
        "functions-have-names": "^1.2.3",
        "hasown": "^2.0.2",
        "is-callable": "^1.2.7"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/functions-have-names": {
      "version": "1.2.3",
      "resolved": "https://registry.npmjs.org/functions-have-names/-/functions-have-names-1.2.3.tgz",
      "integrity": "sha512-xckBUXyTIqT97tq2x2AMb+g163b5JFysYk0x4qxNFwbfQkmNZoiRHb6sPzI9/QV33WeuvVYBUIiD4NzNIyqaRQ==",
      "dev": true,
      "license": "MIT",
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/generator-function": {
      "version": "2.0.1",
      "resolved": "https://registry.npmjs.org/generator-function/-/generator-function-2.0.1.tgz",
      "integrity": "sha512-SFdFmIJi+ybC0vjlHN0ZGVGHc3lgE0DxPAT0djjVg+kjOnSqclqmj0KQ7ykTOLP6YxoqOvuAODGdcHJn+43q3g==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">= 0.4"
      }
    },
    "node_modules/gensync": {
      "version": "1.0.0-beta.2",
      "resolved": "https://registry.npmjs.org/gensync/-/gensync-1.0.0-beta.2.tgz",
      "integrity": "sha512-3hN7NaskYvMDLQY55gnW3NQ+mesEAepTqlg+VEbj7zzqEMBVNhzcGYYeqFo/TlYz6eQiFcp1HcsCZO+nGgS8zg==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=6.9.0"
      }
    },
    "node_modules/get-intrinsic": {
      "version": "1.3.0",
      "resolved": "https://registry.npmjs.org/get-intrinsic/-/get-intrinsic-1.3.0.tgz",
      "integrity": "sha512-9fSjSaos/fRIVIp+xSJlE6lfwhES7LNtKaCBIamHsjr2na1BiABJPo0mOjjz8GJDURarmCPGqaiVg5mfjb98CQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bind-apply-helpers": "^1.0.2",
        "es-define-property": "^1.0.1",
        "es-errors": "^1.3.0",
        "es-object-atoms": "^1.1.1",
        "function-bind": "^1.1.2",
        "get-proto": "^1.0.1",
        "gopd": "^1.2.0",
        "has-symbols": "^1.1.0",
        "hasown": "^2.0.2",
        "math-intrinsics": "^1.1.0"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/get-proto": {
      "version": "1.0.1",
      "resolved": "https://registry.npmjs.org/get-proto/-/get-proto-1.0.1.tgz",
      "integrity": "sha512-sTSfBjoXBp89JvIKIefqw7U2CCebsc74kiY6awiGogKtoSGbgjYE/G/+l9sF3MWFPNc9IcoOC4ODfKHfxFmp0g==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "dunder-proto": "^1.0.1",
        "es-object-atoms": "^1.0.0"
      },
      "engines": {
        "node": ">= 0.4"
      }
    },
    "node_modules/get-symbol-description": {
      "version": "1.1.0",
      "resolved": "https://registry.npmjs.org/get-symbol-description/-/get-symbol-description-1.1.0.tgz",
      "integrity": "sha512-w9UMqWwJxHNOvoNzSJ2oPF5wvYcvP7jUvYzhp67yEhTi17ZDBBC1z9pTdGuzjD+EFIqLSYRweZjqfiPzQ06Ebg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bound": "^1.0.3",
        "es-errors": "^1.3.0",
        "get-intrinsic": "^1.2.6"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/get-tsconfig": {
      "version": "4.14.0",
      "resolved": "https://registry.npmjs.org/get-tsconfig/-/get-tsconfig-4.14.0.tgz",
      "integrity": "sha512-yTb+8DXzDREzgvYmh6s9vHsSVCHeC0G3PI5bEXNBHtmshPnO+S5O7qgLEOn0I5QvMy6kpZN8K1NKGyilLb93wA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "resolve-pkg-maps": "^1.0.0"
      },
      "funding": {
        "url": "https://github.com/privatenumber/get-tsconfig?sponsor=1"
      }
    },
    "node_modules/glob-parent": {
      "version": "6.0.2",
      "resolved": "https://registry.npmjs.org/glob-parent/-/glob-parent-6.0.2.tgz",
      "integrity": "sha512-XxwI8EOhVQgWp6iDL+3b0r86f4d6AX6zSU55HfB4ydCEuXLXc5FcYeOu+nnGftS4TEju/11rt4KJPTMgbfmv4A==",
      "dev": true,
      "license": "ISC",
      "dependencies": {
        "is-glob": "^4.0.3"
      },
      "engines": {
        "node": ">=10.13.0"
      }
    },
    "node_modules/globals": {
      "version": "14.0.0",
      "resolved": "https://registry.npmjs.org/globals/-/globals-14.0.0.tgz",
      "integrity": "sha512-oahGvuMGQlPw/ivIYBjVSrWAfWLBeku5tpPE2fOPLi+WHffIWbuh2tCjhyQhTBPMf5E9jDEH4FOmTYgYwbKwtQ==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=18"
      },
      "funding": {
        "url": "https://github.com/sponsors/sindresorhus"
      }
    },
    "node_modules/globalthis": {
      "version": "1.0.4",
      "resolved": "https://registry.npmjs.org/globalthis/-/globalthis-1.0.4.tgz",
      "integrity": "sha512-DpLKbNU4WylpxJykQujfCcwYWiV/Jhm50Goo0wrVILAv5jOr9d+H+UR3PhSCD2rCCEIg0uc+G+muBTwD54JhDQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "define-properties": "^1.2.1",
        "gopd": "^1.0.1"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/gopd": {
      "version": "1.2.0",
      "resolved": "https://registry.npmjs.org/gopd/-/gopd-1.2.0.tgz",
      "integrity": "sha512-ZUKRh6/kUFoAiTAtTYPZJ3hw9wNxx+BIBOijnlG9PnrJsCcSjs1wyyD6vJpaYtgnzDrKYRSqf3OO6Rfa93xsRg==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/graceful-fs": {
      "version": "4.2.11",
      "resolved": "https://registry.npmjs.org/graceful-fs/-/graceful-fs-4.2.11.tgz",
      "integrity": "sha512-RbJ5/jmFcNNCcDV5o9eTnBLJ/HszWV0P73bc+Ff4nS/rJj+YaS6IGyiOL0VoBYX+l1Wrl3k63h/KrH+nhJ0XvQ==",
      "dev": true,
      "license": "ISC"
    },
    "node_modules/has-bigints": {
      "version": "1.1.0",
      "resolved": "https://registry.npmjs.org/has-bigints/-/has-bigints-1.1.0.tgz",
      "integrity": "sha512-R3pbpkcIqv2Pm3dUwgjclDRVmWpTJW2DcMzcIhEXEx1oh/CEMObMm3KLmRJOdvhM7o4uQBnwr8pzRK2sJWIqfg==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/has-flag": {
      "version": "4.0.0",
      "resolved": "https://registry.npmjs.org/has-flag/-/has-flag-4.0.0.tgz",
      "integrity": "sha512-EykJT/Q1KjTWctppgIAgfSO0tKVuZUjhgMr17kqTumMl6Afv3EISleU7qZUzoXDFTAHTDC4NOoG/ZxU3EvlMPQ==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=8"
      }
    },
    "node_modules/has-property-descriptors": {
      "version": "1.0.2",
      "resolved": "https://registry.npmjs.org/has-property-descriptors/-/has-property-descriptors-1.0.2.tgz",
      "integrity": "sha512-55JNKuIW+vq4Ke1BjOTjM2YctQIvCT7GFzHwmfZPGo5wnrgkid0YQtnAleFSqumZm4az3n2BS+erby5ipJdgrg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "es-define-property": "^1.0.0"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/has-proto": {
      "version": "1.2.0",
      "resolved": "https://registry.npmjs.org/has-proto/-/has-proto-1.2.0.tgz",
      "integrity": "sha512-KIL7eQPfHQRC8+XluaIw7BHUwwqL19bQn4hzNgdr+1wXoU0KKj6rufu47lhY7KbJR2C6T6+PfyN0Ea7wkSS+qQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "dunder-proto": "^1.0.0"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/has-symbols": {
      "version": "1.1.0",
      "resolved": "https://registry.npmjs.org/has-symbols/-/has-symbols-1.1.0.tgz",
      "integrity": "sha512-1cDNdwJ2Jaohmb3sg4OmKaMBwuC48sYni5HUw2DvsC8LjGTLK9h+eb1X6RyuOHe4hT0ULCW68iomhjUoKUqlPQ==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/has-tostringtag": {
      "version": "1.0.2",
      "resolved": "https://registry.npmjs.org/has-tostringtag/-/has-tostringtag-1.0.2.tgz",
      "integrity": "sha512-NqADB8VjPFLM2V0VvHUewwwsw0ZWBaIdgo+ieHtK3hasLz4qeCRjYcqfB6AQrBggRKppKF8L52/VqdVsO47Dlw==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "has-symbols": "^1.0.3"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/hasown": {
      "version": "2.0.3",
      "resolved": "https://registry.npmjs.org/hasown/-/hasown-2.0.3.tgz",
      "integrity": "sha512-ej4AhfhfL2Q2zpMmLo7U1Uv9+PyhIZpgQLGT1F9miIGmiCJIoCgSmczFdrc97mWT4kVY72KA+WnnhJ5pghSvSg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "function-bind": "^1.1.2"
      },
      "engines": {
        "node": ">= 0.4"
      }
    },
    "node_modules/hermes-estree": {
      "version": "0.25.1",
      "resolved": "https://registry.npmjs.org/hermes-estree/-/hermes-estree-0.25.1.tgz",
      "integrity": "sha512-0wUoCcLp+5Ev5pDW2OriHC2MJCbwLwuRx+gAqMTOkGKJJiBCLjtrvy4PWUGn6MIVefecRpzoOZ/UV6iGdOr+Cw==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/hermes-parser": {
      "version": "0.25.1",
      "resolved": "https://registry.npmjs.org/hermes-parser/-/hermes-parser-0.25.1.tgz",
      "integrity": "sha512-6pEjquH3rqaI6cYAXYPcz9MS4rY6R4ngRgrgfDshRptUZIc3lw0MCIJIGDj9++mfySOuPTHB4nrSW99BCvOPIA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "hermes-estree": "0.25.1"
      }
    },
    "node_modules/ignore": {
      "version": "5.3.2",
      "resolved": "https://registry.npmjs.org/ignore/-/ignore-5.3.2.tgz",
      "integrity": "sha512-hsBTNUqQTDwkWtcdYI2i06Y/nUBEsNEDJKjWdigLvegy8kDuJAS8uRlpkkcQpyEXL0Z/pjDy5HBmMjRCJ2gq+g==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">= 4"
      }
    },
    "node_modules/import-fresh": {
      "version": "3.3.1",
      "resolved": "https://registry.npmjs.org/import-fresh/-/import-fresh-3.3.1.tgz",
      "integrity": "sha512-TR3KfrTZTYLPB6jUjfx6MF9WcWrHL9su5TObK4ZkYgBdWKPOFoSoQIdEuTuR82pmtxH2spWG9h6etwfr1pLBqQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "parent-module": "^1.0.0",
        "resolve-from": "^4.0.0"
      },
      "engines": {
        "node": ">=6"
      },
      "funding": {
        "url": "https://github.com/sponsors/sindresorhus"
      }
    },
    "node_modules/imurmurhash": {
      "version": "0.1.4",
      "resolved": "https://registry.npmjs.org/imurmurhash/-/imurmurhash-0.1.4.tgz",
      "integrity": "sha512-JmXMZ6wuvDmLiHEml9ykzqO6lwFbof0GG4IkcGaENdCRDDmMVnny7s5HsIgHCbaq0w2MyPhDqkhTUgS2LU2PHA==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=0.8.19"
      }
    },
    "node_modules/internal-slot": {
      "version": "1.1.0",
      "resolved": "https://registry.npmjs.org/internal-slot/-/internal-slot-1.1.0.tgz",
      "integrity": "sha512-4gd7VpWNQNB4UKKCFFVcp1AVv+FMOgs9NKzjHKusc8jTMhd5eL1NqQqOpE0KzMds804/yHlglp3uxgluOqAPLw==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "es-errors": "^1.3.0",
        "hasown": "^2.0.2",
        "side-channel": "^1.1.0"
      },
      "engines": {
        "node": ">= 0.4"
      }
    },
    "node_modules/is-array-buffer": {
      "version": "3.0.5",
      "resolved": "https://registry.npmjs.org/is-array-buffer/-/is-array-buffer-3.0.5.tgz",
      "integrity": "sha512-DDfANUiiG2wC1qawP66qlTugJeL5HyzMpfr8lLK+jMQirGzNod0B12cFB/9q838Ru27sBwfw78/rdoU7RERz6A==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bind": "^1.0.8",
        "call-bound": "^1.0.3",
        "get-intrinsic": "^1.2.6"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/is-async-function": {
      "version": "2.1.1",
      "resolved": "https://registry.npmjs.org/is-async-function/-/is-async-function-2.1.1.tgz",
      "integrity": "sha512-9dgM/cZBnNvjzaMYHVoxxfPj2QXt22Ev7SuuPrs+xav0ukGB0S6d4ydZdEiM48kLx5kDV+QBPrpVnFyefL8kkQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "async-function": "^1.0.0",
        "call-bound": "^1.0.3",
        "get-proto": "^1.0.1",
        "has-tostringtag": "^1.0.2",
        "safe-regex-test": "^1.1.0"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/is-bigint": {
      "version": "1.1.0",
      "resolved": "https://registry.npmjs.org/is-bigint/-/is-bigint-1.1.0.tgz",
      "integrity": "sha512-n4ZT37wG78iz03xPRKJrHTdZbe3IicyucEtdRsV5yglwc3GyUfbAfpSeD0FJ41NbUNSt5wbhqfp1fS+BgnvDFQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "has-bigints": "^1.0.2"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/is-boolean-object": {
      "version": "1.2.2",
      "resolved": "https://registry.npmjs.org/is-boolean-object/-/is-boolean-object-1.2.2.tgz",
      "integrity": "sha512-wa56o2/ElJMYqjCjGkXri7it5FbebW5usLw/nPmCMs5DeZ7eziSYZhSmPRn0txqeW4LnAmQQU7FgqLpsEFKM4A==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bound": "^1.0.3",
        "has-tostringtag": "^1.0.2"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/is-bun-module": {
      "version": "2.0.0",
      "resolved": "https://registry.npmjs.org/is-bun-module/-/is-bun-module-2.0.0.tgz",
      "integrity": "sha512-gNCGbnnnnFAUGKeZ9PdbyeGYJqewpmc2aKHUEMO5nQPWU9lOmv7jcmQIv+qHD8fXW6W7qfuCwX4rY9LNRjXrkQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "semver": "^7.7.1"
      }
    },
    "node_modules/is-bun-module/node_modules/semver": {
      "version": "7.7.4",
      "resolved": "https://registry.npmjs.org/semver/-/semver-7.7.4.tgz",
      "integrity": "sha512-vFKC2IEtQnVhpT78h1Yp8wzwrf8CM+MzKMHGJZfBtzhZNycRFnXsHk6E5TxIkkMsgNS7mdX3AGB7x2QM2di4lA==",
      "dev": true,
      "license": "ISC",
      "bin": {
        "semver": "bin/semver.js"
      },
      "engines": {
        "node": ">=10"
      }
    },
    "node_modules/is-callable": {
      "version": "1.2.7",
      "resolved": "https://registry.npmjs.org/is-callable/-/is-callable-1.2.7.tgz",
      "integrity": "sha512-1BC0BVFhS/p0qtw6enp8e+8OD0UrK0oFLztSjNzhcKA3WDuJxxAPXzPuPtKkjEY9UUoEWlX/8fgKeu2S8i9JTA==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/is-core-module": {
      "version": "2.16.2",
      "resolved": "https://registry.npmjs.org/is-core-module/-/is-core-module-2.16.2.tgz",
      "integrity": "sha512-evOr8xfXKxE6qSR0hSXL2r3sd7ALj8+7jQEUvPYcm5sgZFdJ+AYzT6yNmJenvIYQBgIGwfwz08sL8zoL7yq2BA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "hasown": "^2.0.3"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/is-data-view": {
      "version": "1.0.2",
      "resolved": "https://registry.npmjs.org/is-data-view/-/is-data-view-1.0.2.tgz",
      "integrity": "sha512-RKtWF8pGmS87i2D6gqQu/l7EYRlVdfzemCJN/P3UOs//x1QE7mfhvzHIApBTRf7axvT6DMGwSwBXYCT0nfB9xw==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bound": "^1.0.2",
        "get-intrinsic": "^1.2.6",
        "is-typed-array": "^1.1.13"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/is-date-object": {
      "version": "1.1.0",
      "resolved": "https://registry.npmjs.org/is-date-object/-/is-date-object-1.1.0.tgz",
      "integrity": "sha512-PwwhEakHVKTdRNVOw+/Gyh0+MzlCl4R6qKvkhuvLtPMggI1WAHt9sOwZxQLSGpUaDnrdyDsomoRgNnCfKNSXXg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bound": "^1.0.2",
        "has-tostringtag": "^1.0.2"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/is-extglob": {
      "version": "2.1.1",
      "resolved": "https://registry.npmjs.org/is-extglob/-/is-extglob-2.1.1.tgz",
      "integrity": "sha512-SbKbANkN603Vi4jEZv49LeVJMn4yGwsbzZworEoyEiutsN3nJYdbO36zfhGJ6QEDpOZIFkDtnq5JRxmvl3jsoQ==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=0.10.0"
      }
    },
    "node_modules/is-finalizationregistry": {
      "version": "1.1.1",
      "resolved": "https://registry.npmjs.org/is-finalizationregistry/-/is-finalizationregistry-1.1.1.tgz",
      "integrity": "sha512-1pC6N8qWJbWoPtEjgcL2xyhQOP491EQjeUo3qTKcmV8YSDDJrOepfG8pcC7h/QgnQHYSv0mJ3Z/ZWxmatVrysg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bound": "^1.0.3"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/is-generator-function": {
      "version": "1.1.2",
      "resolved": "https://registry.npmjs.org/is-generator-function/-/is-generator-function-1.1.2.tgz",
      "integrity": "sha512-upqt1SkGkODW9tsGNG5mtXTXtECizwtS2kA161M+gJPc1xdb/Ax629af6YrTwcOeQHbewrPNlE5Dx7kzvXTizA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bound": "^1.0.4",
        "generator-function": "^2.0.0",
        "get-proto": "^1.0.1",
        "has-tostringtag": "^1.0.2",
        "safe-regex-test": "^1.1.0"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/is-glob": {
      "version": "4.0.3",
      "resolved": "https://registry.npmjs.org/is-glob/-/is-glob-4.0.3.tgz",
      "integrity": "sha512-xelSayHH36ZgE7ZWhli7pW34hNbNl8Ojv5KVmkJD4hBdD3th8Tfk9vYasLM+mXWOZhFkgZfxhLSnrwRr4elSSg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "is-extglob": "^2.1.1"
      },
      "engines": {
        "node": ">=0.10.0"
      }
    },
    "node_modules/is-map": {
      "version": "2.0.3",
      "resolved": "https://registry.npmjs.org/is-map/-/is-map-2.0.3.tgz",
      "integrity": "sha512-1Qed0/Hr2m+YqxnM09CjA2d/i6YZNfF6R2oRAOj36eUdS6qIV/huPJNSEpKbupewFs+ZsJlxsjjPbc0/afW6Lw==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/is-negative-zero": {
      "version": "2.0.3",
      "resolved": "https://registry.npmjs.org/is-negative-zero/-/is-negative-zero-2.0.3.tgz",
      "integrity": "sha512-5KoIu2Ngpyek75jXodFvnafB6DJgr3u8uuK0LEZJjrU19DrMD3EVERaR8sjz8CCGgpZvxPl9SuE1GMVPFHx1mw==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/is-number": {
      "version": "7.0.0",
      "resolved": "https://registry.npmjs.org/is-number/-/is-number-7.0.0.tgz",
      "integrity": "sha512-41Cifkg6e8TylSpdtTpeLVMqvSBEVzTttHvERD741+pnZ8ANv0004MRL43QKPDlK9cGvNp6NZWZUBlbGXYxxng==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=0.12.0"
      }
    },
    "node_modules/is-number-object": {
      "version": "1.1.1",
      "resolved": "https://registry.npmjs.org/is-number-object/-/is-number-object-1.1.1.tgz",
      "integrity": "sha512-lZhclumE1G6VYD8VHe35wFaIif+CTy5SJIi5+3y4psDgWu4wPDoBhF8NxUOinEc7pHgiTsT6MaBb92rKhhD+Xw==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bound": "^1.0.3",
        "has-tostringtag": "^1.0.2"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/is-regex": {
      "version": "1.2.1",
      "resolved": "https://registry.npmjs.org/is-regex/-/is-regex-1.2.1.tgz",
      "integrity": "sha512-MjYsKHO5O7mCsmRGxWcLWheFqN9DJ/2TmngvjKXihe6efViPqc274+Fx/4fYj/r03+ESvBdTXK0V6tA3rgez1g==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bound": "^1.0.2",
        "gopd": "^1.2.0",
        "has-tostringtag": "^1.0.2",
        "hasown": "^2.0.2"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/is-set": {
      "version": "2.0.3",
      "resolved": "https://registry.npmjs.org/is-set/-/is-set-2.0.3.tgz",
      "integrity": "sha512-iPAjerrse27/ygGLxw+EBR9agv9Y6uLeYVJMu+QNCoouJ1/1ri0mGrcWpfCqFZuzzx3WjtwxG098X+n4OuRkPg==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/is-shared-array-buffer": {
      "version": "1.0.4",
      "resolved": "https://registry.npmjs.org/is-shared-array-buffer/-/is-shared-array-buffer-1.0.4.tgz",
      "integrity": "sha512-ISWac8drv4ZGfwKl5slpHG9OwPNty4jOWPRIhBpxOoD+hqITiwuipOQ2bNthAzwA3B4fIjO4Nln74N0S9byq8A==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bound": "^1.0.3"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/is-string": {
      "version": "1.1.1",
      "resolved": "https://registry.npmjs.org/is-string/-/is-string-1.1.1.tgz",
      "integrity": "sha512-BtEeSsoaQjlSPBemMQIrY1MY0uM6vnS1g5fmufYOtnxLGUZM2178PKbhsk7Ffv58IX+ZtcvoGwccYsh0PglkAA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bound": "^1.0.3",
        "has-tostringtag": "^1.0.2"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/is-symbol": {
      "version": "1.1.1",
      "resolved": "https://registry.npmjs.org/is-symbol/-/is-symbol-1.1.1.tgz",
      "integrity": "sha512-9gGx6GTtCQM73BgmHQXfDmLtfjjTUDSyoxTCbp5WtoixAhfgsDirWIcVQ/IHpvI5Vgd5i/J5F7B9cN/WlVbC/w==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bound": "^1.0.2",
        "has-symbols": "^1.1.0",
        "safe-regex-test": "^1.1.0"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/is-typed-array": {
      "version": "1.1.15",
      "resolved": "https://registry.npmjs.org/is-typed-array/-/is-typed-array-1.1.15.tgz",
      "integrity": "sha512-p3EcsicXjit7SaskXHs1hA91QxgTw46Fv6EFKKGS5DRFLD8yKnohjF3hxoju94b/OcMZoQukzpPpBE9uLVKzgQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "which-typed-array": "^1.1.16"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/is-weakmap": {
      "version": "2.0.2",
      "resolved": "https://registry.npmjs.org/is-weakmap/-/is-weakmap-2.0.2.tgz",
      "integrity": "sha512-K5pXYOm9wqY1RgjpL3YTkF39tni1XajUIkawTLUo9EZEVUFga5gSQJF8nNS7ZwJQ02y+1YCNYcMh+HIf1ZqE+w==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/is-weakref": {
      "version": "1.1.1",
      "resolved": "https://registry.npmjs.org/is-weakref/-/is-weakref-1.1.1.tgz",
      "integrity": "sha512-6i9mGWSlqzNMEqpCp93KwRS1uUOodk2OJ6b+sq7ZPDSy2WuI5NFIxp/254TytR8ftefexkWn5xNiHUNpPOfSew==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bound": "^1.0.3"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/is-weakset": {
      "version": "2.0.4",
      "resolved": "https://registry.npmjs.org/is-weakset/-/is-weakset-2.0.4.tgz",
      "integrity": "sha512-mfcwb6IzQyOKTs84CQMrOwW4gQcaTOAWJ0zzJCl2WSPDrWk/OzDaImWFH3djXhb24g4eudZfLRozAvPGw4d9hQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bound": "^1.0.3",
        "get-intrinsic": "^1.2.6"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/isarray": {
      "version": "2.0.5",
      "resolved": "https://registry.npmjs.org/isarray/-/isarray-2.0.5.tgz",
      "integrity": "sha512-xHjhDr3cNBK0BzdUJSPXZntQUx/mwMS5Rw4A7lPJ90XGAO6ISP/ePDNuo0vhqOZU+UD5JoodwCAAoZQd3FeAKw==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/isexe": {
      "version": "2.0.0",
      "resolved": "https://registry.npmjs.org/isexe/-/isexe-2.0.0.tgz",
      "integrity": "sha512-RHxMLp9lnKHGHRng9QFhRCMbYAcVpn69smSGcq3f36xjgVVWThj4qqLbTLlq7Ssj8B+fIQ1EuCEGI2lKsyQeIw==",
      "dev": true,
      "license": "ISC"
    },
    "node_modules/iterator.prototype": {
      "version": "1.1.5",
      "resolved": "https://registry.npmjs.org/iterator.prototype/-/iterator.prototype-1.1.5.tgz",
      "integrity": "sha512-H0dkQoCa3b2VEeKQBOxFph+JAbcrQdE7KC0UkqwpLmv2EC4P41QXP+rqo9wYodACiG5/WM5s9oDApTU8utwj9g==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "define-data-property": "^1.1.4",
        "es-object-atoms": "^1.0.0",
        "get-intrinsic": "^1.2.6",
        "get-proto": "^1.0.0",
        "has-symbols": "^1.1.0",
        "set-function-name": "^2.0.2"
      },
      "engines": {
        "node": ">= 0.4"
      }
    },
    "node_modules/jiti": {
      "version": "2.7.0",
      "resolved": "https://registry.npmjs.org/jiti/-/jiti-2.7.0.tgz",
      "integrity": "sha512-AC/7JofJvZGrrneWNaEnJeOLUx+JlGt7tNa0wZiRPT4MY1wmfKjt2+6O2p2uz2+skll8OZZmJMNqeke7kKbNgQ==",
      "dev": true,
      "license": "MIT",
      "bin": {
        "jiti": "lib/jiti-cli.mjs"
      }
    },
    "node_modules/js-tokens": {
      "version": "4.0.0",
      "resolved": "https://registry.npmjs.org/js-tokens/-/js-tokens-4.0.0.tgz",
      "integrity": "sha512-RdJUflcE3cUzKiMqQgsCu06FPu9UdIJO0beYbPhHN4k6apgJtifcoCtT9bcxOpYBtpD2kCM6Sbzg4CausW/PKQ==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/js-yaml": {
      "version": "4.1.1",
      "resolved": "https://registry.npmjs.org/js-yaml/-/js-yaml-4.1.1.tgz",
      "integrity": "sha512-qQKT4zQxXl8lLwBtHMWwaTcGfFOZviOJet3Oy/xmGk2gZH677CJM9EvtfdSkgWcATZhj/55JZ0rmy3myCT5lsA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "argparse": "^2.0.1"
      },
      "bin": {
        "js-yaml": "bin/js-yaml.js"
      }
    },
    "node_modules/jsesc": {
      "version": "3.1.0",
      "resolved": "https://registry.npmjs.org/jsesc/-/jsesc-3.1.0.tgz",
      "integrity": "sha512-/sM3dO2FOzXjKQhJuo0Q173wf2KOo8t4I8vHy6lF9poUp7bKT0/NHE8fPX23PwfhnykfqnC2xRxOnVw5XuGIaA==",
      "dev": true,
      "license": "MIT",
      "bin": {
        "jsesc": "bin/jsesc"
      },
      "engines": {
        "node": ">=6"
      }
    },
    "node_modules/json-buffer": {
      "version": "3.0.1",
      "resolved": "https://registry.npmjs.org/json-buffer/-/json-buffer-3.0.1.tgz",
      "integrity": "sha512-4bV5BfR2mqfQTJm+V5tPPdf+ZpuhiIvTuAB5g8kcrXOZpTT/QwwVRWBywX1ozr6lEuPdbHxwaJlm9G6mI2sfSQ==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/json-schema-traverse": {
      "version": "0.4.1",
      "resolved": "https://registry.npmjs.org/json-schema-traverse/-/json-schema-traverse-0.4.1.tgz",
      "integrity": "sha512-xbbCH5dCYU5T8LcEhhuh7HJ88HXuW3qsI3Y0zOZFKfZEHcpWiHU/Jxzk629Brsab/mMiHQti9wMP+845RPe3Vg==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/json-stable-stringify-without-jsonify": {
      "version": "1.0.1",
      "resolved": "https://registry.npmjs.org/json-stable-stringify-without-jsonify/-/json-stable-stringify-without-jsonify-1.0.1.tgz",
      "integrity": "sha512-Bdboy+l7tA3OGW6FjyFHWkP5LuByj1Tk33Ljyq0axyzdk9//JSi2u3fP1QSmd1KNwq6VOKYGlAu87CisVir6Pw==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/json5": {
      "version": "2.2.3",
      "resolved": "https://registry.npmjs.org/json5/-/json5-2.2.3.tgz",
      "integrity": "sha512-XmOWe7eyHYH14cLdVPoyg+GOH3rYX++KpzrylJwSW98t3Nk+U8XOl8FWKOgwtzdb8lXGf6zYwDUzeHMWfxasyg==",
      "dev": true,
      "license": "MIT",
      "bin": {
        "json5": "lib/cli.js"
      },
      "engines": {
        "node": ">=6"
      }
    },
    "node_modules/jsx-ast-utils": {
      "version": "3.3.5",
      "resolved": "https://registry.npmjs.org/jsx-ast-utils/-/jsx-ast-utils-3.3.5.tgz",
      "integrity": "sha512-ZZow9HBI5O6EPgSJLUb8n2NKgmVWTwCvHGwFuJlMjvLFqlGG6pjirPhtdsseaLZjSibD8eegzmYpUZwoIlj2cQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "array-includes": "^3.1.6",
        "array.prototype.flat": "^1.3.1",
        "object.assign": "^4.1.4",
        "object.values": "^1.1.6"
      },
      "engines": {
        "node": ">=4.0"
      }
    },
    "node_modules/keyv": {
      "version": "4.5.4",
      "resolved": "https://registry.npmjs.org/keyv/-/keyv-4.5.4.tgz",
      "integrity": "sha512-oxVHkHR/EJf2CNXnWxRLW6mg7JyCCUcG0DtEGmL2ctUo1PNTin1PUil+r/+4r5MpVgC/fn1kjsx7mjSujKqIpw==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "json-buffer": "3.0.1"
      }
    },
    "node_modules/language-subtag-registry": {
      "version": "0.3.23",
      "resolved": "https://registry.npmjs.org/language-subtag-registry/-/language-subtag-registry-0.3.23.tgz",
      "integrity": "sha512-0K65Lea881pHotoGEa5gDlMxt3pctLi2RplBb7Ezh4rRdLEOtgi7n4EwK9lamnUCkKBqaeKRVebTq6BAxSkpXQ==",
      "dev": true,
      "license": "CC0-1.0"
    },
    "node_modules/language-tags": {
      "version": "1.0.9",
      "resolved": "https://registry.npmjs.org/language-tags/-/language-tags-1.0.9.tgz",
      "integrity": "sha512-MbjN408fEndfiQXbFQ1vnd+1NoLDsnQW41410oQBXiyXDMYH5z505juWa4KUE1LqxRC7DgOgZDbKLxHIwm27hA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "language-subtag-registry": "^0.3.20"
      },
      "engines": {
        "node": ">=0.10"
      }
    },
    "node_modules/levn": {
      "version": "0.4.1",
      "resolved": "https://registry.npmjs.org/levn/-/levn-0.4.1.tgz",
      "integrity": "sha512-+bT2uH4E5LGE7h/n3evcS/sQlJXCpIp6ym8OWJ5eV6+67Dsql/LaaT7qJBAt2rzfoa/5QBGBhxDix1dMt2kQKQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "prelude-ls": "^1.2.1",
        "type-check": "~0.4.0"
      },
      "engines": {
        "node": ">= 0.8.0"
      }
    },
    "node_modules/lightningcss": {
      "version": "1.32.0",
      "resolved": "https://registry.npmjs.org/lightningcss/-/lightningcss-1.32.0.tgz",
      "integrity": "sha512-NXYBzinNrblfraPGyrbPoD19C1h9lfI/1mzgWYvXUTe414Gz/X1FD2XBZSZM7rRTrMA8JL3OtAaGifrIKhQ5yQ==",
      "dev": true,
      "license": "MPL-2.0",
      "dependencies": {
        "detect-libc": "^2.0.3"
      },
      "engines": {
        "node": ">= 12.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/parcel"
      },
      "optionalDependencies": {
        "lightningcss-android-arm64": "1.32.0",
        "lightningcss-darwin-arm64": "1.32.0",
        "lightningcss-darwin-x64": "1.32.0",
        "lightningcss-freebsd-x64": "1.32.0",
        "lightningcss-linux-arm-gnueabihf": "1.32.0",
        "lightningcss-linux-arm64-gnu": "1.32.0",
        "lightningcss-linux-arm64-musl": "1.32.0",
        "lightningcss-linux-x64-gnu": "1.32.0",
        "lightningcss-linux-x64-musl": "1.32.0",
        "lightningcss-win32-arm64-msvc": "1.32.0",
        "lightningcss-win32-x64-msvc": "1.32.0"
      }
    },
    "node_modules/lightningcss-android-arm64": {
      "version": "1.32.0",
      "resolved": "https://registry.npmjs.org/lightningcss-android-arm64/-/lightningcss-android-arm64-1.32.0.tgz",
      "integrity": "sha512-YK7/ClTt4kAK0vo6w3X+Pnm0D2cf2vPHbhOXdoNti1Ga0al1P4TBZhwjATvjNwLEBCnKvjJc2jQgHXH0NEwlAg==",
      "cpu": [
        "arm64"
      ],
      "dev": true,
      "license": "MPL-2.0",
      "optional": true,
      "os": [
        "android"
      ],
      "engines": {
        "node": ">= 12.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/parcel"
      }
    },
    "node_modules/lightningcss-darwin-arm64": {
      "version": "1.32.0",
      "resolved": "https://registry.npmjs.org/lightningcss-darwin-arm64/-/lightningcss-darwin-arm64-1.32.0.tgz",
      "integrity": "sha512-RzeG9Ju5bag2Bv1/lwlVJvBE3q6TtXskdZLLCyfg5pt+HLz9BqlICO7LZM7VHNTTn/5PRhHFBSjk5lc4cmscPQ==",
      "cpu": [
        "arm64"
      ],
      "dev": true,
      "license": "MPL-2.0",
      "optional": true,
      "os": [
        "darwin"
      ],
      "engines": {
        "node": ">= 12.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/parcel"
      }
    },
    "node_modules/lightningcss-darwin-x64": {
      "version": "1.32.0",
      "resolved": "https://registry.npmjs.org/lightningcss-darwin-x64/-/lightningcss-darwin-x64-1.32.0.tgz",
      "integrity": "sha512-U+QsBp2m/s2wqpUYT/6wnlagdZbtZdndSmut/NJqlCcMLTWp5muCrID+K5UJ6jqD2BFshejCYXniPDbNh73V8w==",
      "cpu": [
        "x64"
      ],
      "dev": true,
      "license": "MPL-2.0",
      "optional": true,
      "os": [
        "darwin"
      ],
      "engines": {
        "node": ">= 12.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/parcel"
      }
    },
    "node_modules/lightningcss-freebsd-x64": {
      "version": "1.32.0",
      "resolved": "https://registry.npmjs.org/lightningcss-freebsd-x64/-/lightningcss-freebsd-x64-1.32.0.tgz",
      "integrity": "sha512-JCTigedEksZk3tHTTthnMdVfGf61Fky8Ji2E4YjUTEQX14xiy/lTzXnu1vwiZe3bYe0q+SpsSH/CTeDXK6WHig==",
      "cpu": [
        "x64"
      ],
      "dev": true,
      "license": "MPL-2.0",
      "optional": true,
      "os": [
        "freebsd"
      ],
      "engines": {
        "node": ">= 12.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/parcel"
      }
    },
    "node_modules/lightningcss-linux-arm-gnueabihf": {
      "version": "1.32.0",
      "resolved": "https://registry.npmjs.org/lightningcss-linux-arm-gnueabihf/-/lightningcss-linux-arm-gnueabihf-1.32.0.tgz",
      "integrity": "sha512-x6rnnpRa2GL0zQOkt6rts3YDPzduLpWvwAF6EMhXFVZXD4tPrBkEFqzGowzCsIWsPjqSK+tyNEODUBXeeVHSkw==",
      "cpu": [
        "arm"
      ],
      "dev": true,
      "license": "MPL-2.0",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": ">= 12.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/parcel"
      }
    },
    "node_modules/lightningcss-linux-arm64-gnu": {
      "version": "1.32.0",
      "resolved": "https://registry.npmjs.org/lightningcss-linux-arm64-gnu/-/lightningcss-linux-arm64-gnu-1.32.0.tgz",
      "integrity": "sha512-0nnMyoyOLRJXfbMOilaSRcLH3Jw5z9HDNGfT/gwCPgaDjnx0i8w7vBzFLFR1f6CMLKF8gVbebmkUN3fa/kQJpQ==",
      "cpu": [
        "arm64"
      ],
      "dev": true,
      "license": "MPL-2.0",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": ">= 12.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/parcel"
      }
    },
    "node_modules/lightningcss-linux-arm64-musl": {
      "version": "1.32.0",
      "resolved": "https://registry.npmjs.org/lightningcss-linux-arm64-musl/-/lightningcss-linux-arm64-musl-1.32.0.tgz",
      "integrity": "sha512-UpQkoenr4UJEzgVIYpI80lDFvRmPVg6oqboNHfoH4CQIfNA+HOrZ7Mo7KZP02dC6LjghPQJeBsvXhJod/wnIBg==",
      "cpu": [
        "arm64"
      ],
      "dev": true,
      "license": "MPL-2.0",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": ">= 12.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/parcel"
      }
    },
    "node_modules/lightningcss-linux-x64-gnu": {
      "version": "1.32.0",
      "resolved": "https://registry.npmjs.org/lightningcss-linux-x64-gnu/-/lightningcss-linux-x64-gnu-1.32.0.tgz",
      "integrity": "sha512-V7Qr52IhZmdKPVr+Vtw8o+WLsQJYCTd8loIfpDaMRWGUZfBOYEJeyJIkqGIDMZPwPx24pUMfwSxxI8phr/MbOA==",
      "cpu": [
        "x64"
      ],
      "dev": true,
      "license": "MPL-2.0",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": ">= 12.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/parcel"
      }
    },
    "node_modules/lightningcss-linux-x64-musl": {
      "version": "1.32.0",
      "resolved": "https://registry.npmjs.org/lightningcss-linux-x64-musl/-/lightningcss-linux-x64-musl-1.32.0.tgz",
      "integrity": "sha512-bYcLp+Vb0awsiXg/80uCRezCYHNg1/l3mt0gzHnWV9XP1W5sKa5/TCdGWaR/zBM2PeF/HbsQv/j2URNOiVuxWg==",
      "cpu": [
        "x64"
      ],
      "dev": true,
      "license": "MPL-2.0",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": ">= 12.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/parcel"
      }
    },
    "node_modules/lightningcss-win32-arm64-msvc": {
      "version": "1.32.0",
      "resolved": "https://registry.npmjs.org/lightningcss-win32-arm64-msvc/-/lightningcss-win32-arm64-msvc-1.32.0.tgz",
      "integrity": "sha512-8SbC8BR40pS6baCM8sbtYDSwEVQd4JlFTOlaD3gWGHfThTcABnNDBda6eTZeqbofalIJhFx0qKzgHJmcPTnGdw==",
      "cpu": [
        "arm64"
      ],
      "dev": true,
      "license": "MPL-2.0",
      "optional": true,
      "os": [
        "win32"
      ],
      "engines": {
        "node": ">= 12.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/parcel"
      }
    },
    "node_modules/lightningcss-win32-x64-msvc": {
      "version": "1.32.0",
      "resolved": "https://registry.npmjs.org/lightningcss-win32-x64-msvc/-/lightningcss-win32-x64-msvc-1.32.0.tgz",
      "integrity": "sha512-Amq9B/SoZYdDi1kFrojnoqPLxYhQ4Wo5XiL8EVJrVsB8ARoC1PWW6VGtT0WKCemjy8aC+louJnjS7U18x3b06Q==",
      "cpu": [
        "x64"
      ],
      "dev": true,
      "license": "MPL-2.0",
      "optional": true,
      "os": [
        "win32"
      ],
      "engines": {
        "node": ">= 12.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/parcel"
      }
    },
    "node_modules/locate-path": {
      "version": "6.0.0",
      "resolved": "https://registry.npmjs.org/locate-path/-/locate-path-6.0.0.tgz",
      "integrity": "sha512-iPZK6eYjbxRu3uB4/WZ3EsEIMJFMqAoopl3R+zuq0UjcAm/MO6KCweDgPfP3elTztoKP3KtnVHxTn2NHBSDVUw==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "p-locate": "^5.0.0"
      },
      "engines": {
        "node": ">=10"
      },
      "funding": {
        "url": "https://github.com/sponsors/sindresorhus"
      }
    },
    "node_modules/lodash.merge": {
      "version": "4.6.2",
      "resolved": "https://registry.npmjs.org/lodash.merge/-/lodash.merge-4.6.2.tgz",
      "integrity": "sha512-0KpjqXRVvrYyCsX1swR/XTK0va6VQkQM6MNo7PqW77ByjAhoARA8EfrP1N4+KlKj8YS0ZUCtRT/YUuhyYDujIQ==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/loose-envify": {
      "version": "1.4.0",
      "resolved": "https://registry.npmjs.org/loose-envify/-/loose-envify-1.4.0.tgz",
      "integrity": "sha512-lyuxPGr/Wfhrlem2CL/UcnUc1zcqKAImBDzukY7Y5F/yQiNdko6+fRLevlw1HgMySw7f611UIY408EtxRSoK3Q==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "js-tokens": "^3.0.0 || ^4.0.0"
      },
      "bin": {
        "loose-envify": "cli.js"
      }
    },
    "node_modules/lru-cache": {
      "version": "5.1.1",
      "resolved": "https://registry.npmjs.org/lru-cache/-/lru-cache-5.1.1.tgz",
      "integrity": "sha512-KpNARQA3Iwv+jTA0utUVVbrh+Jlrr1Fv0e56GGzAFOXN7dk/FviaDW8LHmK52DlcH4WP2n6gI8vN1aesBFgo9w==",
      "dev": true,
      "license": "ISC",
      "dependencies": {
        "yallist": "^3.0.2"
      }
    },
    "node_modules/lucide-react": {
      "version": "1.14.0",
      "resolved": "https://registry.npmjs.org/lucide-react/-/lucide-react-1.14.0.tgz",
      "integrity": "sha512-+1mdWcfSJVUsaTIjN9zoezmUhfXo5l0vP7ekBMPo3jcS/aIkxHnXqAPsByszMZx/Y8oQBRJxJx5xg+RH3urzxA==",
      "license": "ISC",
      "peerDependencies": {
        "react": "^16.5.1 || ^17.0.0 || ^18.0.0 || ^19.0.0"
      }
    },
    "node_modules/magic-string": {
      "version": "0.30.21",
      "resolved": "https://registry.npmjs.org/magic-string/-/magic-string-0.30.21.tgz",
      "integrity": "sha512-vd2F4YUyEXKGcLHoq+TEyCjxueSeHnFxyyjNp80yg0XV4vUhnDer/lvvlqM/arB5bXQN5K2/3oinyCRyx8T2CQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "@jridgewell/sourcemap-codec": "^1.5.5"
      }
    },
    "node_modules/math-intrinsics": {
      "version": "1.1.0",
      "resolved": "https://registry.npmjs.org/math-intrinsics/-/math-intrinsics-1.1.0.tgz",
      "integrity": "sha512-/IXtbwEk5HTPyEwyKX6hGkYXxM9nbj64B+ilVJnC/R6B0pH5G4V3b0pVbL7DBj4tkhBAppbQUlf6F6Xl9LHu1g==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">= 0.4"
      }
    },
    "node_modules/merge2": {
      "version": "1.4.1",
      "resolved": "https://registry.npmjs.org/merge2/-/merge2-1.4.1.tgz",
      "integrity": "sha512-8q7VEgMJW4J8tcfVPy8g09NcQwZdbwFEqhe/WZkoIzjn/3TGDwtOCYtXGxA3O8tPzpczCCDgv+P2P5y00ZJOOg==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">= 8"
      }
    },
    "node_modules/micromatch": {
      "version": "4.0.8",
      "resolved": "https://registry.npmjs.org/micromatch/-/micromatch-4.0.8.tgz",
      "integrity": "sha512-PXwfBhYu0hBCPw8Dn0E+WDYb7af3dSLVWKi3HGv84IdF4TyFoC0ysxFd0Goxw7nSv4T/PzEJQxsYsEiFCKo2BA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "braces": "^3.0.3",
        "picomatch": "^2.3.1"
      },
      "engines": {
        "node": ">=8.6"
      }
    },
    "node_modules/minimatch": {
      "version": "3.1.5",
      "resolved": "https://registry.npmjs.org/minimatch/-/minimatch-3.1.5.tgz",
      "integrity": "sha512-VgjWUsnnT6n+NUk6eZq77zeFdpW2LWDzP6zFGrCbHXiYNul5Dzqk2HHQ5uFH2DNW5Xbp8+jVzaeNt94ssEEl4w==",
      "dev": true,
      "license": "ISC",
      "dependencies": {
        "brace-expansion": "^1.1.7"
      },
      "engines": {
        "node": "*"
      }
    },
    "node_modules/minimist": {
      "version": "1.2.8",
      "resolved": "https://registry.npmjs.org/minimist/-/minimist-1.2.8.tgz",
      "integrity": "sha512-2yyAR8qBkN3YuheJanUpWC5U3bb5osDywNB8RzDVlDwDHbocAJveqqj1u8+SVD7jkWT4yvsHCpWqqWqAxb0zCA==",
      "dev": true,
      "license": "MIT",
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/motion-dom": {
      "version": "12.38.0",
      "resolved": "https://registry.npmjs.org/motion-dom/-/motion-dom-12.38.0.tgz",
      "integrity": "sha512-pdkHLD8QYRp8VfiNLb8xIBJis1byQ9gPT3Jnh2jqfFtAsWUA3dEepDlsWe/xMpO8McV+VdpKVcp+E+TGJEtOoA==",
      "license": "MIT",
      "dependencies": {
        "motion-utils": "^12.36.0"
      }
    },
    "node_modules/motion-utils": {
      "version": "12.36.0",
      "resolved": "https://registry.npmjs.org/motion-utils/-/motion-utils-12.36.0.tgz",
      "integrity": "sha512-eHWisygbiwVvf6PZ1vhaHCLamvkSbPIeAYxWUuL3a2PD/TROgE7FvfHWTIH4vMl798QLfMw15nRqIaRDXTlYRg==",
      "license": "MIT"
    },
    "node_modules/ms": {
      "version": "2.1.3",
      "resolved": "https://registry.npmjs.org/ms/-/ms-2.1.3.tgz",
      "integrity": "sha512-6FlzubTLZG3J2a/NVCAleEhjzq5oxgHyaCU9yYXvcLsvoVaHJq/s5xXI6/XXP6tz7R9xAOtHnSO/tXtF3WRTlA==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/nanoid": {
      "version": "3.3.12",
      "resolved": "https://registry.npmjs.org/nanoid/-/nanoid-3.3.12.tgz",
      "integrity": "sha512-ZB9RH/39qpq5Vu6Y+NmUaFhQR6pp+M2Xt76XBnEwDaGcVAqhlvxrl3B2bKS5D3NH3QR76v3aSrKaF/Kiy7lEtQ==",
      "funding": [
        {
          "type": "github",
          "url": "https://github.com/sponsors/ai"
        }
      ],
      "license": "MIT",
      "bin": {
        "nanoid": "bin/nanoid.cjs"
      },
      "engines": {
        "node": "^10 || ^12 || ^13.7 || ^14 || >=15.0.1"
      }
    },
    "node_modules/napi-postinstall": {
      "version": "0.3.4",
      "resolved": "https://registry.npmjs.org/napi-postinstall/-/napi-postinstall-0.3.4.tgz",
      "integrity": "sha512-PHI5f1O0EP5xJ9gQmFGMS6IZcrVvTjpXjz7Na41gTE7eE2hK11lg04CECCYEEjdc17EV4DO+fkGEtt7TpTaTiQ==",
      "dev": true,
      "license": "MIT",
      "bin": {
        "napi-postinstall": "lib/cli.js"
      },
      "engines": {
        "node": "^12.20.0 || ^14.18.0 || >=16.0.0"
      },
      "funding": {
        "url": "https://opencollective.com/napi-postinstall"
      }
    },
    "node_modules/natural-compare": {
      "version": "1.4.0",
      "resolved": "https://registry.npmjs.org/natural-compare/-/natural-compare-1.4.0.tgz",
      "integrity": "sha512-OWND8ei3VtNC9h7V60qff3SVobHr996CTwgxubgyQYEpg290h9J0buyECNNJexkFm5sOajh5G116RYA1c8ZMSw==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/next": {
      "version": "16.2.4",
      "resolved": "https://registry.npmjs.org/next/-/next-16.2.4.tgz",
      "integrity": "sha512-kPvz56wF5frc+FxlHI5qnklCzbq53HTwORaWBGdT0vNoKh1Aya9XC8aPauH4NJxqtzbWsS5mAbctm4cr+EkQ2Q==",
      "license": "MIT",
      "dependencies": {
        "@next/env": "16.2.4",
        "@swc/helpers": "0.5.15",
        "baseline-browser-mapping": "^2.9.19",
        "caniuse-lite": "^1.0.30001579",
        "postcss": "8.4.31",
        "styled-jsx": "5.1.6"
      },
      "bin": {
        "next": "dist/bin/next"
      },
      "engines": {
        "node": ">=20.9.0"
      },
      "optionalDependencies": {
        "@next/swc-darwin-arm64": "16.2.4",
        "@next/swc-darwin-x64": "16.2.4",
        "@next/swc-linux-arm64-gnu": "16.2.4",
        "@next/swc-linux-arm64-musl": "16.2.4",
        "@next/swc-linux-x64-gnu": "16.2.4",
        "@next/swc-linux-x64-musl": "16.2.4",
        "@next/swc-win32-arm64-msvc": "16.2.4",
        "@next/swc-win32-x64-msvc": "16.2.4",
        "sharp": "^0.34.5"
      },
      "peerDependencies": {
        "@opentelemetry/api": "^1.1.0",
        "@playwright/test": "^1.51.1",
        "babel-plugin-react-compiler": "*",
        "react": "^18.2.0 || 19.0.0-rc-de68d2f4-20241204 || ^19.0.0",
        "react-dom": "^18.2.0 || 19.0.0-rc-de68d2f4-20241204 || ^19.0.0",
        "sass": "^1.3.0"
      },
      "peerDependenciesMeta": {
        "@opentelemetry/api": {
          "optional": true
        },
        "@playwright/test": {
          "optional": true
        },
        "babel-plugin-react-compiler": {
          "optional": true
        },
        "sass": {
          "optional": true
        }
      }
    },
    "node_modules/next/node_modules/postcss": {
      "version": "8.4.31",
      "resolved": "https://registry.npmjs.org/postcss/-/postcss-8.4.31.tgz",
      "integrity": "sha512-PS08Iboia9mts/2ygV3eLpY5ghnUcfLV/EXTOW1E2qYxJKGGBUtNjN76FYHnMs36RmARn41bC0AZmn+rR0OVpQ==",
      "funding": [
        {
          "type": "opencollective",
          "url": "https://opencollective.com/postcss/"
        },
        {
          "type": "tidelift",
          "url": "https://tidelift.com/funding/github/npm/postcss"
        },
        {
          "type": "github",
          "url": "https://github.com/sponsors/ai"
        }
      ],
      "license": "MIT",
      "dependencies": {
        "nanoid": "^3.3.6",
        "picocolors": "^1.0.0",
        "source-map-js": "^1.0.2"
      },
      "engines": {
        "node": "^10 || ^12 || >=14"
      }
    },
    "node_modules/node-exports-info": {
      "version": "1.6.0",
      "resolved": "https://registry.npmjs.org/node-exports-info/-/node-exports-info-1.6.0.tgz",
      "integrity": "sha512-pyFS63ptit/P5WqUkt+UUfe+4oevH+bFeIiPPdfb0pFeYEu/1ELnJu5l+5EcTKYL5M7zaAa7S8ddywgXypqKCw==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "array.prototype.flatmap": "^1.3.3",
        "es-errors": "^1.3.0",
        "object.entries": "^1.1.9",
        "semver": "^6.3.1"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/node-releases": {
      "version": "2.0.38",
      "resolved": "https://registry.npmjs.org/node-releases/-/node-releases-2.0.38.tgz",
      "integrity": "sha512-3qT/88Y3FbH/Kx4szpQQ4HzUbVrHPKTLVpVocKiLfoYvw9XSGOX2FmD2d6DrXbVYyAQTF2HeF6My8jmzx7/CRw==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/object-assign": {
      "version": "4.1.1",
      "resolved": "https://registry.npmjs.org/object-assign/-/object-assign-4.1.1.tgz",
      "integrity": "sha512-rJgTQnkUnH1sFw8yT6VSU3zD3sWmu6sZhIseY8VX+GRu3P6F7Fu+JNDoXfklElbLJSnc3FUQHVe4cU5hj+BcUg==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=0.10.0"
      }
    },
    "node_modules/object-inspect": {
      "version": "1.13.4",
      "resolved": "https://registry.npmjs.org/object-inspect/-/object-inspect-1.13.4.tgz",
      "integrity": "sha512-W67iLl4J2EXEGTbfeHCffrjDfitvLANg0UlX3wFUUSTx92KXRFegMHUVgSqE+wvhAbi4WqjGg9czysTV2Epbew==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/object-keys": {
      "version": "1.1.1",
      "resolved": "https://registry.npmjs.org/object-keys/-/object-keys-1.1.1.tgz",
      "integrity": "sha512-NuAESUOUMrlIXOfHKzD6bpPu3tYt3xvjNdRIQ+FeT0lNb4K8WR70CaDxhuNguS2XG+GjkyMwOzsN5ZktImfhLA==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">= 0.4"
      }
    },
    "node_modules/object.assign": {
      "version": "4.1.7",
      "resolved": "https://registry.npmjs.org/object.assign/-/object.assign-4.1.7.tgz",
      "integrity": "sha512-nK28WOo+QIjBkDduTINE4JkF/UJJKyf2EJxvJKfblDpyg0Q+pkOHNTL0Qwy6NP6FhE/EnzV73BxxqcJaXY9anw==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bind": "^1.0.8",
        "call-bound": "^1.0.3",
        "define-properties": "^1.2.1",
        "es-object-atoms": "^1.0.0",
        "has-symbols": "^1.1.0",
        "object-keys": "^1.1.1"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/object.entries": {
      "version": "1.1.9",
      "resolved": "https://registry.npmjs.org/object.entries/-/object.entries-1.1.9.tgz",
      "integrity": "sha512-8u/hfXFRBD1O0hPUjioLhoWFHRmt6tKA4/vZPyckBr18l1KE9uHrFaFaUi8MDRTpi4uak2goyPTSNJLXX2k2Hw==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bind": "^1.0.8",
        "call-bound": "^1.0.4",
        "define-properties": "^1.2.1",
        "es-object-atoms": "^1.1.1"
      },
      "engines": {
        "node": ">= 0.4"
      }
    },
    "node_modules/object.fromentries": {
      "version": "2.0.8",
      "resolved": "https://registry.npmjs.org/object.fromentries/-/object.fromentries-2.0.8.tgz",
      "integrity": "sha512-k6E21FzySsSK5a21KRADBd/NGneRegFO5pLHfdQLpRDETUNJueLXs3WCzyQ3tFRDYgbq3KHGXfTbi2bs8WQ6rQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bind": "^1.0.7",
        "define-properties": "^1.2.1",
        "es-abstract": "^1.23.2",
        "es-object-atoms": "^1.0.0"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/object.groupby": {
      "version": "1.0.3",
      "resolved": "https://registry.npmjs.org/object.groupby/-/object.groupby-1.0.3.tgz",
      "integrity": "sha512-+Lhy3TQTuzXI5hevh8sBGqbmurHbbIjAi0Z4S63nthVLmLxfbj4T54a4CfZrXIrt9iP4mVAPYMo/v99taj3wjQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bind": "^1.0.7",
        "define-properties": "^1.2.1",
        "es-abstract": "^1.23.2"
      },
      "engines": {
        "node": ">= 0.4"
      }
    },
    "node_modules/object.values": {
      "version": "1.2.1",
      "resolved": "https://registry.npmjs.org/object.values/-/object.values-1.2.1.tgz",
      "integrity": "sha512-gXah6aZrcUxjWg2zR2MwouP2eHlCBzdV4pygudehaKXSGW4v2AsRQUK+lwwXhii6KFZcunEnmSUoYp5CXibxtA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bind": "^1.0.8",
        "call-bound": "^1.0.3",
        "define-properties": "^1.2.1",
        "es-object-atoms": "^1.0.0"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/optionator": {
      "version": "0.9.4",
      "resolved": "https://registry.npmjs.org/optionator/-/optionator-0.9.4.tgz",
      "integrity": "sha512-6IpQ7mKUxRcZNLIObR0hz7lxsapSSIYNZJwXPGeF0mTVqGKFIXj1DQcMoT22S3ROcLyY/rz0PWaWZ9ayWmad9g==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "deep-is": "^0.1.3",
        "fast-levenshtein": "^2.0.6",
        "levn": "^0.4.1",
        "prelude-ls": "^1.2.1",
        "type-check": "^0.4.0",
        "word-wrap": "^1.2.5"
      },
      "engines": {
        "node": ">= 0.8.0"
      }
    },
    "node_modules/own-keys": {
      "version": "1.0.1",
      "resolved": "https://registry.npmjs.org/own-keys/-/own-keys-1.0.1.tgz",
      "integrity": "sha512-qFOyK5PjiWZd+QQIh+1jhdb9LpxTF0qs7Pm8o5QHYZ0M3vKqSqzsZaEB6oWlxZ+q2sJBMI/Ktgd2N5ZwQoRHfg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "get-intrinsic": "^1.2.6",
        "object-keys": "^1.1.1",
        "safe-push-apply": "^1.0.0"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/p-limit": {
      "version": "3.1.0",
      "resolved": "https://registry.npmjs.org/p-limit/-/p-limit-3.1.0.tgz",
      "integrity": "sha512-TYOanM3wGwNGsZN2cVTYPArw454xnXj5qmWF1bEoAc4+cU/ol7GVh7odevjp1FNHduHc3KZMcFduxU5Xc6uJRQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "yocto-queue": "^0.1.0"
      },
      "engines": {
        "node": ">=10"
      },
      "funding": {
        "url": "https://github.com/sponsors/sindresorhus"
      }
    },
    "node_modules/p-locate": {
      "version": "5.0.0",
      "resolved": "https://registry.npmjs.org/p-locate/-/p-locate-5.0.0.tgz",
      "integrity": "sha512-LaNjtRWUBY++zB5nE/NwcaoMylSPk+S+ZHNB1TzdbMJMny6dynpAGt7X/tl/QYq3TIeE6nxHppbo2LGymrG5Pw==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "p-limit": "^3.0.2"
      },
      "engines": {
        "node": ">=10"
      },
      "funding": {
        "url": "https://github.com/sponsors/sindresorhus"
      }
    },
    "node_modules/parent-module": {
      "version": "1.0.1",
      "resolved": "https://registry.npmjs.org/parent-module/-/parent-module-1.0.1.tgz",
      "integrity": "sha512-GQ2EWRpQV8/o+Aw8YqtfZZPfNRWZYkbidE9k5rpl/hC3vtHHBfGm2Ifi6qWV+coDGkrUKZAxE3Lot5kcsRlh+g==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "callsites": "^3.0.0"
      },
      "engines": {
        "node": ">=6"
      }
    },
    "node_modules/path-exists": {
      "version": "4.0.0",
      "resolved": "https://registry.npmjs.org/path-exists/-/path-exists-4.0.0.tgz",
      "integrity": "sha512-ak9Qy5Q7jYb2Wwcey5Fpvg2KoAc/ZIhLSLOSBmRmygPsGwkVVt0fZa0qrtMz+m6tJTAHfZQ8FnmB4MG4LWy7/w==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=8"
      }
    },
    "node_modules/path-key": {
      "version": "3.1.1",
      "resolved": "https://registry.npmjs.org/path-key/-/path-key-3.1.1.tgz",
      "integrity": "sha512-ojmeN0qd+y0jszEtoY48r0Peq5dwMEkIlCOu6Q5f41lfkswXuKtYrhgoTpLnyIcHm24Uhqx+5Tqm2InSwLhE6Q==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=8"
      }
    },
    "node_modules/path-parse": {
      "version": "1.0.7",
      "resolved": "https://registry.npmjs.org/path-parse/-/path-parse-1.0.7.tgz",
      "integrity": "sha512-LDJzPVEEEPR+y48z93A0Ed0yXb8pAByGWo/k5YYdYgpY2/2EsOsksJrq7lOHxryrVOn1ejG6oAp8ahvOIQD8sw==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/picocolors": {
      "version": "1.1.1",
      "resolved": "https://registry.npmjs.org/picocolors/-/picocolors-1.1.1.tgz",
      "integrity": "sha512-xceH2snhtb5M9liqDsmEw56le376mTZkEX/jEb/RxNFyegNul7eNslCXP9FDj/Lcu0X8KEyMceP2ntpaHrDEVA==",
      "license": "ISC"
    },
    "node_modules/picomatch": {
      "version": "2.3.2",
      "resolved": "https://registry.npmjs.org/picomatch/-/picomatch-2.3.2.tgz",
      "integrity": "sha512-V7+vQEJ06Z+c5tSye8S+nHUfI51xoXIXjHQ99cQtKUkQqqO1kO/KCJUfZXuB47h/YBlDhah2H3hdUGXn8ie0oA==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=8.6"
      },
      "funding": {
        "url": "https://github.com/sponsors/jonschlinkert"
      }
    },
    "node_modules/possible-typed-array-names": {
      "version": "1.1.0",
      "resolved": "https://registry.npmjs.org/possible-typed-array-names/-/possible-typed-array-names-1.1.0.tgz",
      "integrity": "sha512-/+5VFTchJDoVj3bhoqi6UeymcD00DAwb1nJwamzPvHEszJ4FpF6SNNbUbOS8yI56qHzdV8eK0qEfOSiodkTdxg==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">= 0.4"
      }
    },
    "node_modules/postcss": {
      "version": "8.5.14",
      "resolved": "https://registry.npmjs.org/postcss/-/postcss-8.5.14.tgz",
      "integrity": "sha512-SoSL4+OSEtR99LHFZQiJLkT59C5B1amGO1NzTwj7TT1qCUgUO6hxOvzkOYxD+vMrXBM3XJIKzokoERdqQq/Zmg==",
      "dev": true,
      "funding": [
        {
          "type": "opencollective",
          "url": "https://opencollective.com/postcss/"
        },
        {
          "type": "tidelift",
          "url": "https://tidelift.com/funding/github/npm/postcss"
        },
        {
          "type": "github",
          "url": "https://github.com/sponsors/ai"
        }
      ],
      "license": "MIT",
      "dependencies": {
        "nanoid": "^3.3.11",
        "picocolors": "^1.1.1",
        "source-map-js": "^1.2.1"
      },
      "engines": {
        "node": "^10 || ^12 || >=14"
      }
    },
    "node_modules/prelude-ls": {
      "version": "1.2.1",
      "resolved": "https://registry.npmjs.org/prelude-ls/-/prelude-ls-1.2.1.tgz",
      "integrity": "sha512-vkcDPrRZo1QZLbn5RLGPpg/WmIQ65qoWWhcGKf/b5eplkkarX0m9z8ppCat4mlOqUsWpyNuYgO3VRyrYHSzX5g==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">= 0.8.0"
      }
    },
    "node_modules/prop-types": {
      "version": "15.8.1",
      "resolved": "https://registry.npmjs.org/prop-types/-/prop-types-15.8.1.tgz",
      "integrity": "sha512-oj87CgZICdulUohogVAR7AjlC0327U4el4L6eAvOqCeudMDVU0NThNaV+b9Df4dXgSP1gXMTnPdhfe/2qDH5cg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "loose-envify": "^1.4.0",
        "object-assign": "^4.1.1",
        "react-is": "^16.13.1"
      }
    },
    "node_modules/punycode": {
      "version": "2.3.1",
      "resolved": "https://registry.npmjs.org/punycode/-/punycode-2.3.1.tgz",
      "integrity": "sha512-vYt7UD1U9Wg6138shLtLOvdAu+8DsC/ilFtEVHcH+wydcSpNE20AfSOduf6MkRFahL5FY7X1oU7nKVZFtfq8Fg==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=6"
      }
    },
    "node_modules/queue-microtask": {
      "version": "1.2.3",
      "resolved": "https://registry.npmjs.org/queue-microtask/-/queue-microtask-1.2.3.tgz",
      "integrity": "sha512-NuaNSa6flKT5JaSYQzJok04JzTL1CA6aGhv5rfLW3PgqA+M2ChpZQnAC8h8i4ZFkBS8X5RqkDBHA7r4hej3K9A==",
      "dev": true,
      "funding": [
        {
          "type": "github",
          "url": "https://github.com/sponsors/feross"
        },
        {
          "type": "patreon",
          "url": "https://www.patreon.com/feross"
        },
        {
          "type": "consulting",
          "url": "https://feross.org/support"
        }
      ],
      "license": "MIT"
    },
    "node_modules/react": {
      "version": "19.2.4",
      "resolved": "https://registry.npmjs.org/react/-/react-19.2.4.tgz",
      "integrity": "sha512-9nfp2hYpCwOjAN+8TZFGhtWEwgvWHXqESH8qT89AT/lWklpLON22Lc8pEtnpsZz7VmawabSU0gCjnj8aC0euHQ==",
      "license": "MIT",
      "engines": {
        "node": ">=0.10.0"
      }
    },
    "node_modules/react-dom": {
      "version": "19.2.4",
      "resolved": "https://registry.npmjs.org/react-dom/-/react-dom-19.2.4.tgz",
      "integrity": "sha512-AXJdLo8kgMbimY95O2aKQqsz2iWi9jMgKJhRBAxECE4IFxfcazB2LmzloIoibJI3C12IlY20+KFaLv+71bUJeQ==",
      "license": "MIT",
      "dependencies": {
        "scheduler": "^0.27.0"
      },
      "peerDependencies": {
        "react": "^19.2.4"
      }
    },
    "node_modules/react-is": {
      "version": "16.13.1",
      "resolved": "https://registry.npmjs.org/react-is/-/react-is-16.13.1.tgz",
      "integrity": "sha512-24e6ynE2H+OKt4kqsOvNd8kBpV65zoxbA4BVsEOB3ARVWQki/DHzaUoC5KuON/BiccDaCCTZBuOcfZs70kR8bQ==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/reflect.getprototypeof": {
      "version": "1.0.10",
      "resolved": "https://registry.npmjs.org/reflect.getprototypeof/-/reflect.getprototypeof-1.0.10.tgz",
      "integrity": "sha512-00o4I+DVrefhv+nX0ulyi3biSHCPDe+yLv5o/p6d/UVlirijB8E16FtfwSAi4g3tcqrQ4lRAqQSoFEZJehYEcw==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bind": "^1.0.8",
        "define-properties": "^1.2.1",
        "es-abstract": "^1.23.9",
        "es-errors": "^1.3.0",
        "es-object-atoms": "^1.0.0",
        "get-intrinsic": "^1.2.7",
        "get-proto": "^1.0.1",
        "which-builtin-type": "^1.2.1"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/regexp.prototype.flags": {
      "version": "1.5.4",
      "resolved": "https://registry.npmjs.org/regexp.prototype.flags/-/regexp.prototype.flags-1.5.4.tgz",
      "integrity": "sha512-dYqgNSZbDwkaJ2ceRd9ojCGjBq+mOm9LmtXnAnEGyHhN/5R7iDW2TRw3h+o/jCFxus3P2LfWIIiwowAjANm7IA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bind": "^1.0.8",
        "define-properties": "^1.2.1",
        "es-errors": "^1.3.0",
        "get-proto": "^1.0.1",
        "gopd": "^1.2.0",
        "set-function-name": "^2.0.2"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/resolve": {
      "version": "2.0.0-next.6",
      "resolved": "https://registry.npmjs.org/resolve/-/resolve-2.0.0-next.6.tgz",
      "integrity": "sha512-3JmVl5hMGtJ3kMmB3zi3DL25KfkCEyy3Tw7Gmw7z5w8M9WlwoPFnIvwChzu1+cF3iaK3sp18hhPz8ANeimdJfA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "es-errors": "^1.3.0",
        "is-core-module": "^2.16.1",
        "node-exports-info": "^1.6.0",
        "object-keys": "^1.1.1",
        "path-parse": "^1.0.7",
        "supports-preserve-symlinks-flag": "^1.0.0"
      },
      "bin": {
        "resolve": "bin/resolve"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/resolve-from": {
      "version": "4.0.0",
      "resolved": "https://registry.npmjs.org/resolve-from/-/resolve-from-4.0.0.tgz",
      "integrity": "sha512-pb/MYmXstAkysRFx8piNI1tGFNQIFA3vkE3Gq4EuA1dF6gHp/+vgZqsCGJapvy8N3Q+4o7FwvquPJcnZ7RYy4g==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=4"
      }
    },
    "node_modules/resolve-pkg-maps": {
      "version": "1.0.0",
      "resolved": "https://registry.npmjs.org/resolve-pkg-maps/-/resolve-pkg-maps-1.0.0.tgz",
      "integrity": "sha512-seS2Tj26TBVOC2NIc2rOe2y2ZO7efxITtLZcGSOnHHNOQ7CkiUBfw0Iw2ck6xkIhPwLhKNLS8BO+hEpngQlqzw==",
      "dev": true,
      "license": "MIT",
      "funding": {
        "url": "https://github.com/privatenumber/resolve-pkg-maps?sponsor=1"
      }
    },
    "node_modules/reusify": {
      "version": "1.1.0",
      "resolved": "https://registry.npmjs.org/reusify/-/reusify-1.1.0.tgz",
      "integrity": "sha512-g6QUff04oZpHs0eG5p83rFLhHeV00ug/Yf9nZM6fLeUrPguBTkTQOdpAWWspMh55TZfVQDPaN3NQJfbVRAxdIw==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "iojs": ">=1.0.0",
        "node": ">=0.10.0"
      }
    },
    "node_modules/run-parallel": {
      "version": "1.2.0",
      "resolved": "https://registry.npmjs.org/run-parallel/-/run-parallel-1.2.0.tgz",
      "integrity": "sha512-5l4VyZR86LZ/lDxZTR6jqL8AFE2S0IFLMP26AbjsLVADxHdhB/c0GUsH+y39UfCi3dzz8OlQuPmnaJOMoDHQBA==",
      "dev": true,
      "funding": [
        {
          "type": "github",
          "url": "https://github.com/sponsors/feross"
        },
        {
          "type": "patreon",
          "url": "https://www.patreon.com/feross"
        },
        {
          "type": "consulting",
          "url": "https://feross.org/support"
        }
      ],
      "license": "MIT",
      "dependencies": {
        "queue-microtask": "^1.2.2"
      }
    },
    "node_modules/safe-array-concat": {
      "version": "1.1.4",
      "resolved": "https://registry.npmjs.org/safe-array-concat/-/safe-array-concat-1.1.4.tgz",
      "integrity": "sha512-wtZlHyOje6OZTGqAoaDKxFkgRtkF9CnHAVnCHKfuj200wAgL+bSJhdsCD2l0Qx/2ekEXjPWcyKkfGb5CPboslg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bind": "^1.0.9",
        "call-bound": "^1.0.4",
        "get-intrinsic": "^1.3.0",
        "has-symbols": "^1.1.0",
        "isarray": "^2.0.5"
      },
      "engines": {
        "node": ">=0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/safe-push-apply": {
      "version": "1.0.0",
      "resolved": "https://registry.npmjs.org/safe-push-apply/-/safe-push-apply-1.0.0.tgz",
      "integrity": "sha512-iKE9w/Z7xCzUMIZqdBsp6pEQvwuEebH4vdpjcDWnyzaI6yl6O9FHvVpmGelvEHNsoY6wGblkxR6Zty/h00WiSA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "es-errors": "^1.3.0",
        "isarray": "^2.0.5"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/safe-regex-test": {
      "version": "1.1.0",
      "resolved": "https://registry.npmjs.org/safe-regex-test/-/safe-regex-test-1.1.0.tgz",
      "integrity": "sha512-x/+Cz4YrimQxQccJf5mKEbIa1NzeCRNI5Ecl/ekmlYaampdNLPalVyIcCZNNH3MvmqBugV5TMYZXv0ljslUlaw==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bound": "^1.0.2",
        "es-errors": "^1.3.0",
        "is-regex": "^1.2.1"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/scheduler": {
      "version": "0.27.0",
      "resolved": "https://registry.npmjs.org/scheduler/-/scheduler-0.27.0.tgz",
      "integrity": "sha512-eNv+WrVbKu1f3vbYJT/xtiF5syA5HPIMtf9IgY/nKg0sWqzAUEvqY/xm7OcZc/qafLx/iO9FgOmeSAp4v5ti/Q==",
      "license": "MIT"
    },
    "node_modules/semver": {
      "version": "6.3.1",
      "resolved": "https://registry.npmjs.org/semver/-/semver-6.3.1.tgz",
      "integrity": "sha512-BR7VvDCVHO+q2xBEWskxS6DJE1qRnb7DxzUrogb71CWoSficBxYsiAGd+Kl0mmq/MprG9yArRkyrQxTO6XjMzA==",
      "dev": true,
      "license": "ISC",
      "bin": {
        "semver": "bin/semver.js"
      }
    },
    "node_modules/set-function-length": {
      "version": "1.2.2",
      "resolved": "https://registry.npmjs.org/set-function-length/-/set-function-length-1.2.2.tgz",
      "integrity": "sha512-pgRc4hJ4/sNjWCSS9AmnS40x3bNMDTknHgL5UaMBTMyJnU90EgWh1Rz+MC9eFu4BuN/UwZjKQuY/1v3rM7HMfg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "define-data-property": "^1.1.4",
        "es-errors": "^1.3.0",
        "function-bind": "^1.1.2",
        "get-intrinsic": "^1.2.4",
        "gopd": "^1.0.1",
        "has-property-descriptors": "^1.0.2"
      },
      "engines": {
        "node": ">= 0.4"
      }
    },
    "node_modules/set-function-name": {
      "version": "2.0.2",
      "resolved": "https://registry.npmjs.org/set-function-name/-/set-function-name-2.0.2.tgz",
      "integrity": "sha512-7PGFlmtwsEADb0WYyvCMa1t+yke6daIG4Wirafur5kcf+MhUnPms1UeR0CKQdTZD81yESwMHbtn+TR+dMviakQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "define-data-property": "^1.1.4",
        "es-errors": "^1.3.0",
        "functions-have-names": "^1.2.3",
        "has-property-descriptors": "^1.0.2"
      },
      "engines": {
        "node": ">= 0.4"
      }
    },
    "node_modules/set-proto": {
      "version": "1.0.0",
      "resolved": "https://registry.npmjs.org/set-proto/-/set-proto-1.0.0.tgz",
      "integrity": "sha512-RJRdvCo6IAnPdsvP/7m6bsQqNnn1FCBX5ZNtFL98MmFF/4xAIJTIg1YbHW5DC2W5SKZanrC6i4HsJqlajw/dZw==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "dunder-proto": "^1.0.1",
        "es-errors": "^1.3.0",
        "es-object-atoms": "^1.0.0"
      },
      "engines": {
        "node": ">= 0.4"
      }
    },
    "node_modules/sharp": {
      "version": "0.34.5",
      "resolved": "https://registry.npmjs.org/sharp/-/sharp-0.34.5.tgz",
      "integrity": "sha512-Ou9I5Ft9WNcCbXrU9cMgPBcCK8LiwLqcbywW3t4oDV37n1pzpuNLsYiAV8eODnjbtQlSDwZ2cUEeQz4E54Hltg==",
      "hasInstallScript": true,
      "license": "Apache-2.0",
      "optional": true,
      "dependencies": {
        "@img/colour": "^1.0.0",
        "detect-libc": "^2.1.2",
        "semver": "^7.7.3"
      },
      "engines": {
        "node": "^18.17.0 || ^20.3.0 || >=21.0.0"
      },
      "funding": {
        "url": "https://opencollective.com/libvips"
      },
      "optionalDependencies": {
        "@img/sharp-darwin-arm64": "0.34.5",
        "@img/sharp-darwin-x64": "0.34.5",
        "@img/sharp-libvips-darwin-arm64": "1.2.4",
        "@img/sharp-libvips-darwin-x64": "1.2.4",
        "@img/sharp-libvips-linux-arm": "1.2.4",
        "@img/sharp-libvips-linux-arm64": "1.2.4",
        "@img/sharp-libvips-linux-ppc64": "1.2.4",
        "@img/sharp-libvips-linux-riscv64": "1.2.4",
        "@img/sharp-libvips-linux-s390x": "1.2.4",
        "@img/sharp-libvips-linux-x64": "1.2.4",
        "@img/sharp-libvips-linuxmusl-arm64": "1.2.4",
        "@img/sharp-libvips-linuxmusl-x64": "1.2.4",
        "@img/sharp-linux-arm": "0.34.5",
        "@img/sharp-linux-arm64": "0.34.5",
        "@img/sharp-linux-ppc64": "0.34.5",
        "@img/sharp-linux-riscv64": "0.34.5",
        "@img/sharp-linux-s390x": "0.34.5",
        "@img/sharp-linux-x64": "0.34.5",
        "@img/sharp-linuxmusl-arm64": "0.34.5",
        "@img/sharp-linuxmusl-x64": "0.34.5",
        "@img/sharp-wasm32": "0.34.5",
        "@img/sharp-win32-arm64": "0.34.5",
        "@img/sharp-win32-ia32": "0.34.5",
        "@img/sharp-win32-x64": "0.34.5"
      }
    },
    "node_modules/sharp/node_modules/semver": {
      "version": "7.7.4",
      "resolved": "https://registry.npmjs.org/semver/-/semver-7.7.4.tgz",
      "integrity": "sha512-vFKC2IEtQnVhpT78h1Yp8wzwrf8CM+MzKMHGJZfBtzhZNycRFnXsHk6E5TxIkkMsgNS7mdX3AGB7x2QM2di4lA==",
      "license": "ISC",
      "optional": true,
      "bin": {
        "semver": "bin/semver.js"
      },
      "engines": {
        "node": ">=10"
      }
    },
    "node_modules/shebang-command": {
      "version": "2.0.0",
      "resolved": "https://registry.npmjs.org/shebang-command/-/shebang-command-2.0.0.tgz",
      "integrity": "sha512-kHxr2zZpYtdmrN1qDjrrX/Z1rR1kG8Dx+gkpK1G4eXmvXswmcE1hTWBWYUzlraYw1/yZp6YuDY77YtvbN0dmDA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "shebang-regex": "^3.0.0"
      },
      "engines": {
        "node": ">=8"
      }
    },
    "node_modules/shebang-regex": {
      "version": "3.0.0",
      "resolved": "https://registry.npmjs.org/shebang-regex/-/shebang-regex-3.0.0.tgz",
      "integrity": "sha512-7++dFhtcx3353uBaq8DDR4NuxBetBzC7ZQOhmTQInHEd6bSrXdiEyzCvG07Z44UYdLShWUyXt5M/yhz8ekcb1A==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=8"
      }
    },
    "node_modules/side-channel": {
      "version": "1.1.0",
      "resolved": "https://registry.npmjs.org/side-channel/-/side-channel-1.1.0.tgz",
      "integrity": "sha512-ZX99e6tRweoUXqR+VBrslhda51Nh5MTQwou5tnUDgbtyM0dBgmhEDtWGP/xbKn6hqfPRHujUNwz5fy/wbbhnpw==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "es-errors": "^1.3.0",
        "object-inspect": "^1.13.3",
        "side-channel-list": "^1.0.0",
        "side-channel-map": "^1.0.1",
        "side-channel-weakmap": "^1.0.2"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/side-channel-list": {
      "version": "1.0.1",
      "resolved": "https://registry.npmjs.org/side-channel-list/-/side-channel-list-1.0.1.tgz",
      "integrity": "sha512-mjn/0bi/oUURjc5Xl7IaWi/OJJJumuoJFQJfDDyO46+hBWsfaVM65TBHq2eoZBhzl9EchxOijpkbRC8SVBQU0w==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "es-errors": "^1.3.0",
        "object-inspect": "^1.13.4"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/side-channel-map": {
      "version": "1.0.1",
      "resolved": "https://registry.npmjs.org/side-channel-map/-/side-channel-map-1.0.1.tgz",
      "integrity": "sha512-VCjCNfgMsby3tTdo02nbjtM/ewra6jPHmpThenkTYh8pG9ucZ/1P8So4u4FGBek/BjpOVsDCMoLA/iuBKIFXRA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bound": "^1.0.2",
        "es-errors": "^1.3.0",
        "get-intrinsic": "^1.2.5",
        "object-inspect": "^1.13.3"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/side-channel-weakmap": {
      "version": "1.0.2",
      "resolved": "https://registry.npmjs.org/side-channel-weakmap/-/side-channel-weakmap-1.0.2.tgz",
      "integrity": "sha512-WPS/HvHQTYnHisLo9McqBHOJk2FkHO/tlpvldyrnem4aeQp4hai3gythswg6p01oSoTl58rcpiFAjF2br2Ak2A==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bound": "^1.0.2",
        "es-errors": "^1.3.0",
        "get-intrinsic": "^1.2.5",
        "object-inspect": "^1.13.3",
        "side-channel-map": "^1.0.1"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/source-map-js": {
      "version": "1.2.1",
      "resolved": "https://registry.npmjs.org/source-map-js/-/source-map-js-1.2.1.tgz",
      "integrity": "sha512-UXWMKhLOwVKb728IUtQPXxfYU+usdybtUrK/8uGE8CQMvrhOpwvzDBwj0QhSL7MQc7vIsISBG8VQ8+IDQxpfQA==",
      "license": "BSD-3-Clause",
      "engines": {
        "node": ">=0.10.0"
      }
    },
    "node_modules/stable-hash": {
      "version": "0.0.5",
      "resolved": "https://registry.npmjs.org/stable-hash/-/stable-hash-0.0.5.tgz",
      "integrity": "sha512-+L3ccpzibovGXFK+Ap/f8LOS0ahMrHTf3xu7mMLSpEGU0EO9ucaysSylKo9eRDFNhWve/y275iPmIZ4z39a9iA==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/stop-iteration-iterator": {
      "version": "1.1.0",
      "resolved": "https://registry.npmjs.org/stop-iteration-iterator/-/stop-iteration-iterator-1.1.0.tgz",
      "integrity": "sha512-eLoXW/DHyl62zxY4SCaIgnRhuMr6ri4juEYARS8E6sCEqzKpOiE521Ucofdx+KnDZl5xmvGYaaKCk5FEOxJCoQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "es-errors": "^1.3.0",
        "internal-slot": "^1.1.0"
      },
      "engines": {
        "node": ">= 0.4"
      }
    },
    "node_modules/string.prototype.includes": {
      "version": "2.0.1",
      "resolved": "https://registry.npmjs.org/string.prototype.includes/-/string.prototype.includes-2.0.1.tgz",
      "integrity": "sha512-o7+c9bW6zpAdJHTtujeePODAhkuicdAryFsfVKwA+wGw89wJ4GTY484WTucM9hLtDEOpOvI+aHnzqnC5lHp4Rg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bind": "^1.0.7",
        "define-properties": "^1.2.1",
        "es-abstract": "^1.23.3"
      },
      "engines": {
        "node": ">= 0.4"
      }
    },
    "node_modules/string.prototype.matchall": {
      "version": "4.0.12",
      "resolved": "https://registry.npmjs.org/string.prototype.matchall/-/string.prototype.matchall-4.0.12.tgz",
      "integrity": "sha512-6CC9uyBL+/48dYizRf7H7VAYCMCNTBeM78x/VTUe9bFEaxBepPJDa1Ow99LqI/1yF7kuy7Q3cQsYMrcjGUcskA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bind": "^1.0.8",
        "call-bound": "^1.0.3",
        "define-properties": "^1.2.1",
        "es-abstract": "^1.23.6",
        "es-errors": "^1.3.0",
        "es-object-atoms": "^1.0.0",
        "get-intrinsic": "^1.2.6",
        "gopd": "^1.2.0",
        "has-symbols": "^1.1.0",
        "internal-slot": "^1.1.0",
        "regexp.prototype.flags": "^1.5.3",
        "set-function-name": "^2.0.2",
        "side-channel": "^1.1.0"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/string.prototype.repeat": {
      "version": "1.0.0",
      "resolved": "https://registry.npmjs.org/string.prototype.repeat/-/string.prototype.repeat-1.0.0.tgz",
      "integrity": "sha512-0u/TldDbKD8bFCQ/4f5+mNRrXwZ8hg2w7ZR8wa16e8z9XpePWl3eGEcUD0OXpEH/VJH/2G3gjUtR3ZOiBe2S/w==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "define-properties": "^1.1.3",
        "es-abstract": "^1.17.5"
      }
    },
    "node_modules/string.prototype.trim": {
      "version": "1.2.10",
      "resolved": "https://registry.npmjs.org/string.prototype.trim/-/string.prototype.trim-1.2.10.tgz",
      "integrity": "sha512-Rs66F0P/1kedk5lyYyH9uBzuiI/kNRmwJAR9quK6VOtIpZ2G+hMZd+HQbbv25MgCA6gEffoMZYxlTod4WcdrKA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bind": "^1.0.8",
        "call-bound": "^1.0.2",
        "define-data-property": "^1.1.4",
        "define-properties": "^1.2.1",
        "es-abstract": "^1.23.5",
        "es-object-atoms": "^1.0.0",
        "has-property-descriptors": "^1.0.2"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/string.prototype.trimend": {
      "version": "1.0.9",
      "resolved": "https://registry.npmjs.org/string.prototype.trimend/-/string.prototype.trimend-1.0.9.tgz",
      "integrity": "sha512-G7Ok5C6E/j4SGfyLCloXTrngQIQU3PWtXGst3yM7Bea9FRURf1S42ZHlZZtsNque2FN2PoUhfZXYLNWwEr4dLQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bind": "^1.0.8",
        "call-bound": "^1.0.2",
        "define-properties": "^1.2.1",
        "es-object-atoms": "^1.0.0"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/string.prototype.trimstart": {
      "version": "1.0.8",
      "resolved": "https://registry.npmjs.org/string.prototype.trimstart/-/string.prototype.trimstart-1.0.8.tgz",
      "integrity": "sha512-UXSH262CSZY1tfu3G3Secr6uGLCFVPMhIqHjlgCUtCCcgihYc/xKs9djMTMUOb2j1mVSeU8EU6NWc/iQKU6Gfg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bind": "^1.0.7",
        "define-properties": "^1.2.1",
        "es-object-atoms": "^1.0.0"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/strip-bom": {
      "version": "3.0.0",
      "resolved": "https://registry.npmjs.org/strip-bom/-/strip-bom-3.0.0.tgz",
      "integrity": "sha512-vavAMRXOgBVNF6nyEEmL3DBK19iRpDcoIwW+swQ+CbGiu7lju6t+JklA1MHweoWtadgt4ISVUsXLyDq34ddcwA==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=4"
      }
    },
    "node_modules/strip-json-comments": {
      "version": "3.1.1",
      "resolved": "https://registry.npmjs.org/strip-json-comments/-/strip-json-comments-3.1.1.tgz",
      "integrity": "sha512-6fPc+R4ihwqP6N/aIv2f1gMH8lOVtWQHoqC4yK6oSDVVocumAsfCqjkXnqiYMhmMwS/mEHLp7Vehlt3ql6lEig==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=8"
      },
      "funding": {
        "url": "https://github.com/sponsors/sindresorhus"
      }
    },
    "node_modules/styled-jsx": {
      "version": "5.1.6",
      "resolved": "https://registry.npmjs.org/styled-jsx/-/styled-jsx-5.1.6.tgz",
      "integrity": "sha512-qSVyDTeMotdvQYoHWLNGwRFJHC+i+ZvdBRYosOFgC+Wg1vx4frN2/RG/NA7SYqqvKNLf39P2LSRA2pu6n0XYZA==",
      "license": "MIT",
      "dependencies": {
        "client-only": "0.0.1"
      },
      "engines": {
        "node": ">= 12.0.0"
      },
      "peerDependencies": {
        "react": ">= 16.8.0 || 17.x.x || ^18.0.0-0 || ^19.0.0-0"
      },
      "peerDependenciesMeta": {
        "@babel/core": {
          "optional": true
        },
        "babel-plugin-macros": {
          "optional": true
        }
      }
    },
    "node_modules/supports-color": {
      "version": "7.2.0",
      "resolved": "https://registry.npmjs.org/supports-color/-/supports-color-7.2.0.tgz",
      "integrity": "sha512-qpCAvRl9stuOHveKsn7HncJRvv501qIacKzQlO/+Lwxc9+0q2wLyv4Dfvt80/DPn2pqOBsJdDiogXGR9+OvwRw==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "has-flag": "^4.0.0"
      },
      "engines": {
        "node": ">=8"
      }
    },
    "node_modules/supports-preserve-symlinks-flag": {
      "version": "1.0.0",
      "resolved": "https://registry.npmjs.org/supports-preserve-symlinks-flag/-/supports-preserve-symlinks-flag-1.0.0.tgz",
      "integrity": "sha512-ot0WnXS9fgdkgIcePe6RHNk1WA8+muPa6cSjeR3V8K27q9BB1rTE3R1p7Hv0z1ZyAc8s6Vvv8DIyWf681MAt0w==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/tailwindcss": {
      "version": "4.2.4",
      "resolved": "https://registry.npmjs.org/tailwindcss/-/tailwindcss-4.2.4.tgz",
      "integrity": "sha512-HhKppgO81FQof5m6TEnuBWCZGgfRAWbaeOaGT00KOy/Pf/j6oUihdvBpA7ltCeAvZpFhW3j0PTclkxsd4IXYDA==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/tapable": {
      "version": "2.3.3",
      "resolved": "https://registry.npmjs.org/tapable/-/tapable-2.3.3.tgz",
      "integrity": "sha512-uxc/zpqFg6x7C8vOE7lh6Lbda8eEL9zmVm/PLeTPBRhh1xCgdWaQ+J1CUieGpIfm2HdtsUpRv+HshiasBMcc6A==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=6"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/webpack"
      }
    },
    "node_modules/tinyglobby": {
      "version": "0.2.16",
      "resolved": "https://registry.npmjs.org/tinyglobby/-/tinyglobby-0.2.16.tgz",
      "integrity": "sha512-pn99VhoACYR8nFHhxqix+uvsbXineAasWm5ojXoN8xEwK5Kd3/TrhNn1wByuD52UxWRLy8pu+kRMniEi6Eq9Zg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "fdir": "^6.5.0",
        "picomatch": "^4.0.4"
      },
      "engines": {
        "node": ">=12.0.0"
      },
      "funding": {
        "url": "https://github.com/sponsors/SuperchupuDev"
      }
    },
    "node_modules/tinyglobby/node_modules/fdir": {
      "version": "6.5.0",
      "resolved": "https://registry.npmjs.org/fdir/-/fdir-6.5.0.tgz",
      "integrity": "sha512-tIbYtZbucOs0BRGqPJkshJUYdL+SDH7dVM8gjy+ERp3WAUjLEFJE+02kanyHtwjWOnwrKYBiwAmM0p4kLJAnXg==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=12.0.0"
      },
      "peerDependencies": {
        "picomatch": "^3 || ^4"
      },
      "peerDependenciesMeta": {
        "picomatch": {
          "optional": true
        }
      }
    },
    "node_modules/tinyglobby/node_modules/picomatch": {
      "version": "4.0.4",
      "resolved": "https://registry.npmjs.org/picomatch/-/picomatch-4.0.4.tgz",
      "integrity": "sha512-QP88BAKvMam/3NxH6vj2o21R6MjxZUAd6nlwAS/pnGvN9IVLocLHxGYIzFhg6fUQ+5th6P4dv4eW9jX3DSIj7A==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=12"
      },
      "funding": {
        "url": "https://github.com/sponsors/jonschlinkert"
      }
    },
    "node_modules/to-regex-range": {
      "version": "5.0.1",
      "resolved": "https://registry.npmjs.org/to-regex-range/-/to-regex-range-5.0.1.tgz",
      "integrity": "sha512-65P7iz6X5yEr1cwcgvQxbbIw7Uk3gOy5dIdtZ4rDveLqhrdJP+Li/Hx6tyK0NEb+2GCyneCMJiGqrADCSNk8sQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "is-number": "^7.0.0"
      },
      "engines": {
        "node": ">=8.0"
      }
    },
    "node_modules/ts-api-utils": {
      "version": "2.5.0",
      "resolved": "https://registry.npmjs.org/ts-api-utils/-/ts-api-utils-2.5.0.tgz",
      "integrity": "sha512-OJ/ibxhPlqrMM0UiNHJ/0CKQkoKF243/AEmplt3qpRgkW8VG7IfOS41h7V8TjITqdByHzrjcS/2si+y4lIh8NA==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=18.12"
      },
      "peerDependencies": {
        "typescript": ">=4.8.4"
      }
    },
    "node_modules/tsconfig-paths": {
      "version": "3.15.0",
      "resolved": "https://registry.npmjs.org/tsconfig-paths/-/tsconfig-paths-3.15.0.tgz",
      "integrity": "sha512-2Ac2RgzDe/cn48GvOe3M+o82pEFewD3UPbyoUHHdKasHwJKjds4fLXWf/Ux5kATBKN20oaFGu+jbElp1pos0mg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "@types/json5": "^0.0.29",
        "json5": "^1.0.2",
        "minimist": "^1.2.6",
        "strip-bom": "^3.0.0"
      }
    },
    "node_modules/tsconfig-paths/node_modules/json5": {
      "version": "1.0.2",
      "resolved": "https://registry.npmjs.org/json5/-/json5-1.0.2.tgz",
      "integrity": "sha512-g1MWMLBiz8FKi1e4w0UyVL3w+iJceWAFBAaBnnGKOpNa5f8TLktkbre1+s6oICydWAm+HRUGTmI+//xv2hvXYA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "minimist": "^1.2.0"
      },
      "bin": {
        "json5": "lib/cli.js"
      }
    },
    "node_modules/tslib": {
      "version": "2.8.1",
      "resolved": "https://registry.npmjs.org/tslib/-/tslib-2.8.1.tgz",
      "integrity": "sha512-oJFu94HQb+KVduSUQL7wnpmqnfmLsOA/nAh6b6EH0wCEoK0/mPeXU6c3wKDV83MkOuHPRHtSXKKU99IBazS/2w==",
      "license": "0BSD"
    },
    "node_modules/type-check": {
      "version": "0.4.0",
      "resolved": "https://registry.npmjs.org/type-check/-/type-check-0.4.0.tgz",
      "integrity": "sha512-XleUoc9uwGXqjWwXaUTZAmzMcFZ5858QA2vvx1Ur5xIcixXIP+8LnFDgRplU30us6teqdlskFfu+ae4K79Ooew==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "prelude-ls": "^1.2.1"
      },
      "engines": {
        "node": ">= 0.8.0"
      }
    },
    "node_modules/typed-array-buffer": {
      "version": "1.0.3",
      "resolved": "https://registry.npmjs.org/typed-array-buffer/-/typed-array-buffer-1.0.3.tgz",
      "integrity": "sha512-nAYYwfY3qnzX30IkA6AQZjVbtK6duGontcQm1WSG1MD94YLqK0515GNApXkoxKOWMusVssAHWLh9SeaoefYFGw==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bound": "^1.0.3",
        "es-errors": "^1.3.0",
        "is-typed-array": "^1.1.14"
      },
      "engines": {
        "node": ">= 0.4"
      }
    },
    "node_modules/typed-array-byte-length": {
      "version": "1.0.3",
      "resolved": "https://registry.npmjs.org/typed-array-byte-length/-/typed-array-byte-length-1.0.3.tgz",
      "integrity": "sha512-BaXgOuIxz8n8pIq3e7Atg/7s+DpiYrxn4vdot3w9KbnBhcRQq6o3xemQdIfynqSeXeDrF32x+WvfzmOjPiY9lg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bind": "^1.0.8",
        "for-each": "^0.3.3",
        "gopd": "^1.2.0",
        "has-proto": "^1.2.0",
        "is-typed-array": "^1.1.14"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/typed-array-byte-offset": {
      "version": "1.0.4",
      "resolved": "https://registry.npmjs.org/typed-array-byte-offset/-/typed-array-byte-offset-1.0.4.tgz",
      "integrity": "sha512-bTlAFB/FBYMcuX81gbL4OcpH5PmlFHqlCCpAl8AlEzMz5k53oNDvN8p1PNOWLEmI2x4orp3raOFB51tv9X+MFQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "available-typed-arrays": "^1.0.7",
        "call-bind": "^1.0.8",
        "for-each": "^0.3.3",
        "gopd": "^1.2.0",
        "has-proto": "^1.2.0",
        "is-typed-array": "^1.1.15",
        "reflect.getprototypeof": "^1.0.9"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/typed-array-length": {
      "version": "1.0.7",
      "resolved": "https://registry.npmjs.org/typed-array-length/-/typed-array-length-1.0.7.tgz",
      "integrity": "sha512-3KS2b+kL7fsuk/eJZ7EQdnEmQoaho/r6KUef7hxvltNA5DR8NAUM+8wJMbJyZ4G9/7i3v5zPBIMN5aybAh2/Jg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bind": "^1.0.7",
        "for-each": "^0.3.3",
        "gopd": "^1.0.1",
        "is-typed-array": "^1.1.13",
        "possible-typed-array-names": "^1.0.0",
        "reflect.getprototypeof": "^1.0.6"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/typescript": {
      "version": "5.9.3",
      "resolved": "https://registry.npmjs.org/typescript/-/typescript-5.9.3.tgz",
      "integrity": "sha512-jl1vZzPDinLr9eUt3J/t7V6FgNEw9QjvBPdysz9KfQDD41fQrC2Y4vKQdiaUpFT4bXlb1RHhLpp8wtm6M5TgSw==",
      "dev": true,
      "license": "Apache-2.0",
      "bin": {
        "tsc": "bin/tsc",
        "tsserver": "bin/tsserver"
      },
      "engines": {
        "node": ">=14.17"
      }
    },
    "node_modules/typescript-eslint": {
      "version": "8.59.2",
      "resolved": "https://registry.npmjs.org/typescript-eslint/-/typescript-eslint-8.59.2.tgz",
      "integrity": "sha512-pJw051uomb3ZeCzGTpRb8RbEqB5Y4WWet8gl/GcTlU35BSx0PVdZ86/bqkQCyKKuraVQEK7r6kBHQXF+fBhkoQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "@typescript-eslint/eslint-plugin": "8.59.2",
        "@typescript-eslint/parser": "8.59.2",
        "@typescript-eslint/typescript-estree": "8.59.2",
        "@typescript-eslint/utils": "8.59.2"
      },
      "engines": {
        "node": "^18.18.0 || ^20.9.0 || >=21.1.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/typescript-eslint"
      },
      "peerDependencies": {
        "eslint": "^8.57.0 || ^9.0.0 || ^10.0.0",
        "typescript": ">=4.8.4 <6.1.0"
      }
    },
    "node_modules/unbox-primitive": {
      "version": "1.1.0",
      "resolved": "https://registry.npmjs.org/unbox-primitive/-/unbox-primitive-1.1.0.tgz",
      "integrity": "sha512-nWJ91DjeOkej/TA8pXQ3myruKpKEYgqvpw9lz4OPHj/NWFNluYrjbz9j01CJ8yKQd2g4jFoOkINCTW2I5LEEyw==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bound": "^1.0.3",
        "has-bigints": "^1.0.2",
        "has-symbols": "^1.1.0",
        "which-boxed-primitive": "^1.1.1"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/undici-types": {
      "version": "6.21.0",
      "resolved": "https://registry.npmjs.org/undici-types/-/undici-types-6.21.0.tgz",
      "integrity": "sha512-iwDZqg0QAGrg9Rav5H4n0M64c3mkR59cJ6wQp+7C4nI0gsmExaedaYLNO44eT4AtBBwjbTiGPMlt2Md0T9H9JQ==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/unrs-resolver": {
      "version": "1.11.1",
      "resolved": "https://registry.npmjs.org/unrs-resolver/-/unrs-resolver-1.11.1.tgz",
      "integrity": "sha512-bSjt9pjaEBnNiGgc9rUiHGKv5l4/TGzDmYw3RhnkJGtLhbnnA/5qJj7x3dNDCRx/PJxu774LlH8lCOlB4hEfKg==",
      "dev": true,
      "hasInstallScript": true,
      "license": "MIT",
      "dependencies": {
        "napi-postinstall": "^0.3.0"
      },
      "funding": {
        "url": "https://opencollective.com/unrs-resolver"
      },
      "optionalDependencies": {
        "@unrs/resolver-binding-android-arm-eabi": "1.11.1",
        "@unrs/resolver-binding-android-arm64": "1.11.1",
        "@unrs/resolver-binding-darwin-arm64": "1.11.1",
        "@unrs/resolver-binding-darwin-x64": "1.11.1",
        "@unrs/resolver-binding-freebsd-x64": "1.11.1",
        "@unrs/resolver-binding-linux-arm-gnueabihf": "1.11.1",
        "@unrs/resolver-binding-linux-arm-musleabihf": "1.11.1",
        "@unrs/resolver-binding-linux-arm64-gnu": "1.11.1",
        "@unrs/resolver-binding-linux-arm64-musl": "1.11.1",
        "@unrs/resolver-binding-linux-ppc64-gnu": "1.11.1",
        "@unrs/resolver-binding-linux-riscv64-gnu": "1.11.1",
        "@unrs/resolver-binding-linux-riscv64-musl": "1.11.1",
        "@unrs/resolver-binding-linux-s390x-gnu": "1.11.1",
        "@unrs/resolver-binding-linux-x64-gnu": "1.11.1",
        "@unrs/resolver-binding-linux-x64-musl": "1.11.1",
        "@unrs/resolver-binding-wasm32-wasi": "1.11.1",
        "@unrs/resolver-binding-win32-arm64-msvc": "1.11.1",
        "@unrs/resolver-binding-win32-ia32-msvc": "1.11.1",
        "@unrs/resolver-binding-win32-x64-msvc": "1.11.1"
      }
    },
    "node_modules/update-browserslist-db": {
      "version": "1.2.3",
      "resolved": "https://registry.npmjs.org/update-browserslist-db/-/update-browserslist-db-1.2.3.tgz",
      "integrity": "sha512-Js0m9cx+qOgDxo0eMiFGEueWztz+d4+M3rGlmKPT+T4IS/jP4ylw3Nwpu6cpTTP8R1MAC1kF4VbdLt3ARf209w==",
      "dev": true,
      "funding": [
        {
          "type": "opencollective",
          "url": "https://opencollective.com/browserslist"
        },
        {
          "type": "tidelift",
          "url": "https://tidelift.com/funding/github/npm/browserslist"
        },
        {
          "type": "github",
          "url": "https://github.com/sponsors/ai"
        }
      ],
      "license": "MIT",
      "dependencies": {
        "escalade": "^3.2.0",
        "picocolors": "^1.1.1"
      },
      "bin": {
        "update-browserslist-db": "cli.js"
      },
      "peerDependencies": {
        "browserslist": ">= 4.21.0"
      }
    },
    "node_modules/uri-js": {
      "version": "4.4.1",
      "resolved": "https://registry.npmjs.org/uri-js/-/uri-js-4.4.1.tgz",
      "integrity": "sha512-7rKUyy33Q1yc98pQ1DAmLtwX109F7TIfWlW1Ydo8Wl1ii1SeHieeh0HHfPeL2fMXK6z0s8ecKs9frCuLJvndBg==",
      "dev": true,
      "license": "BSD-2-Clause",
      "dependencies": {
        "punycode": "^2.1.0"
      }
    },
    "node_modules/which": {
      "version": "2.0.2",
      "resolved": "https://registry.npmjs.org/which/-/which-2.0.2.tgz",
      "integrity": "sha512-BLI3Tl1TW3Pvl70l3yq3Y64i+awpwXqsGBYWkkqMtnbXgrMD+yj7rhW0kuEDxzJaYXGjEW5ogapKNMEKNMjibA==",
      "dev": true,
      "license": "ISC",
      "dependencies": {
        "isexe": "^2.0.0"
      },
      "bin": {
        "node-which": "bin/node-which"
      },
      "engines": {
        "node": ">= 8"
      }
    },
    "node_modules/which-boxed-primitive": {
      "version": "1.1.1",
      "resolved": "https://registry.npmjs.org/which-boxed-primitive/-/which-boxed-primitive-1.1.1.tgz",
      "integrity": "sha512-TbX3mj8n0odCBFVlY8AxkqcHASw3L60jIuF8jFP78az3C2YhmGvqbHBpAjTRH2/xqYunrJ9g1jSyjCjpoWzIAA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "is-bigint": "^1.1.0",
        "is-boolean-object": "^1.2.1",
        "is-number-object": "^1.1.1",
        "is-string": "^1.1.1",
        "is-symbol": "^1.1.1"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/which-builtin-type": {
      "version": "1.2.1",
      "resolved": "https://registry.npmjs.org/which-builtin-type/-/which-builtin-type-1.2.1.tgz",
      "integrity": "sha512-6iBczoX+kDQ7a3+YJBnh3T+KZRxM/iYNPXicqk66/Qfm1b93iu+yOImkg0zHbj5LNOcNv1TEADiZ0xa34B4q6Q==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bound": "^1.0.2",
        "function.prototype.name": "^1.1.6",
        "has-tostringtag": "^1.0.2",
        "is-async-function": "^2.0.0",
        "is-date-object": "^1.1.0",
        "is-finalizationregistry": "^1.1.0",
        "is-generator-function": "^1.0.10",
        "is-regex": "^1.2.1",
        "is-weakref": "^1.0.2",
        "isarray": "^2.0.5",
        "which-boxed-primitive": "^1.1.0",
        "which-collection": "^1.0.2",
        "which-typed-array": "^1.1.16"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/which-collection": {
      "version": "1.0.2",
      "resolved": "https://registry.npmjs.org/which-collection/-/which-collection-1.0.2.tgz",
      "integrity": "sha512-K4jVyjnBdgvc86Y6BkaLZEN933SwYOuBFkdmBu9ZfkcAbdVbpITnDmjvZ/aQjRXQrv5EPkTnD1s39GiiqbngCw==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "is-map": "^2.0.3",
        "is-set": "^2.0.3",
        "is-weakmap": "^2.0.2",
        "is-weakset": "^2.0.3"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/which-typed-array": {
      "version": "1.1.20",
      "resolved": "https://registry.npmjs.org/which-typed-array/-/which-typed-array-1.1.20.tgz",
      "integrity": "sha512-LYfpUkmqwl0h9A2HL09Mms427Q1RZWuOHsukfVcKRq9q95iQxdw0ix1JQrqbcDR9PH1QDwf5Qo8OZb5lksZ8Xg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "available-typed-arrays": "^1.0.7",
        "call-bind": "^1.0.8",
        "call-bound": "^1.0.4",
        "for-each": "^0.3.5",
        "get-proto": "^1.0.1",
        "gopd": "^1.2.0",
        "has-tostringtag": "^1.0.2"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/word-wrap": {
      "version": "1.2.5",
      "resolved": "https://registry.npmjs.org/word-wrap/-/word-wrap-1.2.5.tgz",
      "integrity": "sha512-BN22B5eaMMI9UMtjrGd5g5eCYPpCPDUy0FJXbYsaT5zYxjFOckS53SQDE3pWkVoWpHXVb3BrYcEN4Twa55B5cA==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=0.10.0"
      }
    },
    "node_modules/yallist": {
      "version": "3.1.1",
      "resolved": "https://registry.npmjs.org/yallist/-/yallist-3.1.1.tgz",
      "integrity": "sha512-a4UGQaWPH59mOXUYnAG2ewncQS4i4F43Tv3JoAM+s2VDAmS9NsK8GpDMLrCHPksFT7h3K6TOoUNn2pb7RoXx4g==",
      "dev": true,
      "license": "ISC"
    },
    "node_modules/yocto-queue": {
      "version": "0.1.0",
      "resolved": "https://registry.npmjs.org/yocto-queue/-/yocto-queue-0.1.0.tgz",
      "integrity": "sha512-rVksvsnNCdJ/ohGc6xgPwyN8eheCxsiLM8mxuE/t/mOVqJewPuO1miLpTHQiRgTKCLexL4MeAFVagts7HmNZ2Q==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=10"
      },
      "funding": {
        "url": "https://github.com/sponsors/sindresorhus"
      }
    },
    "node_modules/zod": {
      "version": "4.4.3",
      "resolved": "https://registry.npmjs.org/zod/-/zod-4.4.3.tgz",
      "integrity": "sha512-ytENFjIJFl2UwYglde2jchW2Hwm4GJFLDiSXWdTrJQBIN9Fcyp7n4DhxJEiWNAJMV1/BqWfW/kkg71UDcHJyTQ==",
      "dev": true,
      "license": "MIT",
      "funding": {
        "url": "https://github.com/sponsors/colinhacks"
      }
    },
    "node_modules/zod-validation-error": {
      "version": "4.0.2",
      "resolved": "https://registry.npmjs.org/zod-validation-error/-/zod-validation-error-4.0.2.tgz",
      "integrity": "sha512-Q6/nZLe6jxuU80qb/4uJ4t5v2VEZ44lzQjPDhYJNztRQ4wyWc6VF3D3Kb/fAuPetZQnhS3hnajCf9CsWesghLQ==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=18.0.0"
      },
      "peerDependencies": {
        "zod": "^3.25.0 || ^4.0.0"
      }
    }
  }
}

```

## frontend\package.json

```json
{
  "name": "frontend",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "eslint"
  },
  "dependencies": {
    "framer-motion": "^12.38.0",
    "lucide-react": "^1.14.0",
    "next": "16.2.4",
    "react": "19.2.4",
    "react-dom": "19.2.4"
  },
  "devDependencies": {
    "@tailwindcss/postcss": "^4",
    "@types/node": "^20",
    "@types/react": "^19",
    "@types/react-dom": "^19",
    "eslint": "^9",
    "eslint-config-next": "16.2.4",
    "tailwindcss": "^4",
    "typescript": "^5"
  }
}

```

## frontend\postcss.config.mjs

```mjs
const config = {
  plugins: {
    "@tailwindcss/postcss": {},
  },
};

export default config;

```

## frontend\README.md

````markdown
This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://nextjs.org/docs/app/api-reference/cli/create-next-app).

## Getting Started

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.

````

## frontend\tsconfig.json

```json
{
  "compilerOptions": {
    "target": "ES2017",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "react-jsx",
    "incremental": true,
    "plugins": [
      {
        "name": "next"
      }
    ],
    "paths": {
      "@/*": ["./*"]
    }
  },
  "include": [
    "next-env.d.ts",
    "**/*.ts",
    "**/*.tsx",
    ".next/types/**/*.ts",
    ".next/dev/types/**/*.ts",
    "**/*.mts"
  ],
  "exclude": ["node_modules"]
}

```

## rag_docs\hr\leave_policy.txt

```txt
Enterprise AI Copilot - Leave Policy v1.0

1. Casual Leave (CL): Employees are entitled to 12 days of casual leave per calendar year. Casual leave cannot be carried forward to the next year.
2. Sick Leave (SL): Employees are entitled to 8 days of sick leave per year. Unused sick leave can be carried forward up to a maximum of 30 days. Medical certificates are required for sick leaves exceeding 3 consecutive days.
3. Maternity Leave: Female employees are eligible for 26 weeks of paid maternity leave.
4. Bereavement Leave: Employees may take up to 3 days of paid leave in the event of the death of an immediate family member.
```

## rag_docs\it\hardware_policy.txt

```txt
Enterprise IT Asset Request Policy

1. Laptops: All full-time employees are provided with a standard company laptop. Requests for high-performance laptops (e.g., for developers or designers) require manager approval and justification.
2. Replacements: Hardware can be requested for replacement if it is older than 3 years or critically damaged. 
3. VPN Access: VPN tokens are provisioned automatically for remote workers. If you lose your token, you must report it immediately to IT support.
```

## rag_docs\hr\leave_policy.txt

```txt
Enterprise AI Copilot - Leave Policy v1.0

1. Casual Leave (CL): Employees are entitled to 12 days of casual leave per calendar year. Casual leave cannot be carried forward to the next year.
2. Sick Leave (SL): Employees are entitled to 8 days of sick leave per year. Unused sick leave can be carried forward up to a maximum of 30 days. Medical certificates are required for sick leaves exceeding 3 consecutive days.
3. Maternity Leave: Female employees are eligible for 26 weeks of paid maternity leave.
4. Bereavement Leave: Employees may take up to 3 days of paid leave in the event of the death of an immediate family member.
```

## rag_docs\it\hardware_policy.txt

```txt
Enterprise IT Asset Request Policy

1. Laptops: All full-time employees are provided with a standard company laptop. Requests for high-performance laptops (e.g., for developers or designers) require manager approval and justification.
2. Replacements: Hardware can be requested for replacement if it is older than 3 years or critically damaged. 
3. VPN Access: VPN tokens are provisioned automatically for remote workers. If you lose your token, you must report it immediately to IT support.
```

## scripts\ingest_docs.py

```python
import os
import glob
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv

# Load environment variables (API keys)
load_dotenv()

# Configuration
DOCS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "rag_docs"))
CHROMA_PERSIST_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "database", "chroma_db"))

def get_metadata_for_file(filepath: str) -> dict:
    """Determine metadata (department, roles allowed) based on file path."""
    department = "general"
    roles_allowed = "all" # Default public access
    doc_type = "policy"

    if "hr" in filepath.lower():
        department = "hr"
        # Example: Leave policies are visible to all employees
        roles_allowed = "employee,manager,hr,admin" 
    elif "it" in filepath.lower():
        department = "it"
        roles_allowed = "employee,manager,it,admin"
    elif "finance" in filepath.lower():
        department = "finance"
        # Example: Finance internal docs only for finance/admin
        if "internal" in filepath.lower():
            roles_allowed = "finance,admin"
        else:
            roles_allowed = "employee,manager,finance,admin"

    return {
        "department": department,
        "doc_type": doc_type,
        "roles_allowed": roles_allowed,
        "source": os.path.basename(filepath)
    }

def ingest_documents():
    print(f"Scanning directory: {DOCS_DIR}")
    
    documents = []
    # Find all txt and pdf files in subdirectories
    file_patterns = [os.path.join(DOCS_DIR, "**", "*.txt"), os.path.join(DOCS_DIR, "**", "*.pdf")]
    
    for pattern in file_patterns:
        for filepath in glob.glob(pattern, recursive=True):
            print(f"Loading: {filepath}")
            
            # Choose loader based on extension
            if filepath.endswith(".txt"):
                loader = TextLoader(filepath, encoding="utf-8")
            elif filepath.endswith(".pdf"):
                loader = PyPDFLoader(filepath)
            else:
                continue
                
            docs = loader.load()
            
            # Attach dynamic metadata to each document
            meta = get_metadata_for_file(filepath)
            for doc in docs:
                doc.metadata.update(meta)
                
            documents.extend(docs)

    if not documents:
        print("No documents found! Please add files to rag_docs/hr or rag_docs/it")
        return

    print(f"Loaded {len(documents)} document pages/files.")

    # Apply Token-based Chunking (512 tokens, 50 overlap)
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=512,
        chunk_overlap=50
    )
    
    chunks = text_splitter.split_documents(documents)
    print(f"Split into {len(chunks)} semantic chunks.")

    # Embed and Store in Vector DB
    print("Embedding chunks and saving to Vector DB...")
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=OpenAIEmbeddings(),
        persist_directory=CHROMA_PERSIST_DIR
    )
    
    print(f"✅ Ingestion complete! Vector DB saved to {CHROMA_PERSIST_DIR}")

if __name__ == "__main__":
    ingest_documents()
```

## scripts\__init__.py

```python
# This file makes `scripts/` a Python package so you can run:
#   python -m scripts.ingest_docs

```

## alembic.ini

```ini
# A generic, single database configuration.

[alembic]
# path to migration scripts.
# this is typically a path given in POSIX (e.g. forward slashes)
# format, relative to the token %(here)s which refers to the location of this
# ini file
script_location = %(here)s/alembic

# template used to generate migration file names; The default value is %%(rev)s_%%(slug)s
# Uncomment the line below if you want the files to be prepended with date and time
# see https://alembic.sqlalchemy.org/en/latest/tutorial.html#editing-the-ini-file
# for all available tokens
# file_template = %%(year)d_%%(month).2d_%%(day).2d_%%(hour).2d%%(minute).2d-%%(rev)s_%%(slug)s
# Or organize into date-based subdirectories (requires recursive_version_locations = true)
# file_template = %%(year)d/%%(month).2d/%%(day).2d_%%(hour).2d%%(minute).2d_%%(second).2d_%%(rev)s_%%(slug)s

# sys.path path, will be prepended to sys.path if present.
# defaults to the current working directory.  for multiple paths, the path separator
# is defined by "path_separator" below.
prepend_sys_path = .

# timezone to use when rendering the date within the migration file
# as well as the filename.
# If specified, requires the tzdata library which can be installed by adding
# `alembic[tz]` to the pip requirements.
# string value is passed to ZoneInfo()
# leave blank for localtime
# timezone =

# max length of characters to apply to the "slug" field
# truncate_slug_length = 40

# set to 'true' to run the environment during
# the 'revision' command, regardless of autogenerate
# revision_environment = false

# set to 'true' to allow .pyc and .pyo files without
# a source .py file to be detected as revisions in the
# versions/ directory
# sourceless = false

# version location specification; This defaults
# to <script_location>/versions.  When using multiple version
# directories, initial revisions must be specified with --version-path.
# The path separator used here should be the separator specified by "path_separator"
# below.
# version_locations = %(here)s/bar:%(here)s/bat:%(here)s/alembic/versions

# path_separator; This indicates what character is used to split lists of file
# paths, including version_locations and prepend_sys_path within configparser
# files such as alembic.ini.
# The default rendered in new alembic.ini files is "os", which uses os.pathsep
# to provide os-dependent path splitting.
#
# Note that in order to support legacy alembic.ini files, this default does NOT
# take place if path_separator is not present in alembic.ini.  If this
# option is omitted entirely, fallback logic is as follows:
#
# 1. Parsing of the version_locations option falls back to using the legacy
#    "version_path_separator" key, which if absent then falls back to the legacy
#    behavior of splitting on spaces and/or commas.
# 2. Parsing of the prepend_sys_path option falls back to the legacy
#    behavior of splitting on spaces, commas, or colons.
#
# Valid values for path_separator are:
#
# path_separator = :
# path_separator = ;
# path_separator = space
# path_separator = newline
#
# Use os.pathsep. Default configuration used for new projects.
path_separator = os


# set to 'true' to search source files recursively
# in each "version_locations" directory
# new in Alembic version 1.10
# recursive_version_locations = false

# the output encoding used when revision files
# are written from script.py.mako
# output_encoding = utf-8

# database URL.  This is consumed by the user-maintained env.py script only.
# other means of configuring database URLs may be customized within the env.py
# file.
sqlalchemy.url = driver://user:pass@localhost/dbname


[post_write_hooks]
# post_write_hooks defines scripts or Python functions that are run
# on newly generated revision scripts.  See the documentation for further
# detail and examples

# format using "black" - use the console_scripts runner, against the "black" entrypoint
# hooks = black
# black.type = console_scripts
# black.entrypoint = black
# black.options = -l 79 REVISION_SCRIPT_FILENAME

# lint with attempts to fix using "ruff" - use the module runner, against the "ruff" module
# hooks = ruff
# ruff.type = module
# ruff.module = ruff
# ruff.options = check --fix REVISION_SCRIPT_FILENAME

# Alternatively, use the exec runner to execute a binary found on your PATH
# hooks = ruff
# ruff.type = exec
# ruff.executable = ruff
# ruff.options = check --fix REVISION_SCRIPT_FILENAME

# Logging configuration.  This is also consumed by the user-maintained
# env.py script only.
[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARNING
handlers = console
qualname =

[logger_sqlalchemy]
level = WARNING
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S

```

## get_token.py

```python
from app.middleware.rbac import create_access_token

# Mint a 8-hour token using Bob's exact details from the database
bob_token = create_access_token(
    user_id="33333333-3333-3333-3333-333333333333",
    role="employee",
    email="bob.employee@company.com"
)

print("\n=== BOB'S JWT TOKEN ===")
print(bob_token)
print("=======================\n")
```

## pyproject.toml

```toml
[tool.poetry]
name = "enterprise-ai-copilot"
version = "1.0.0"
description = "Enterprise Multi-Agent AI Copilot for HR, IT & Finance Operations"
authors = ["Your Name <you@company.com>"]
python = "^3.11"

[tool.poetry.dependencies]
python            = "^3.11"

# ── Web framework ────────────────────────────────────────────────
fastapi           = "^0.115"
uvicorn           = {extras = ["standard"], version = "^0.30"}
httpx             = "^0.27"            # async HTTP (Power Automate calls)

# ── AI / Agents ──────────────────────────────────────────────────
langchain         = "^0.3"
langchain-openai  = "^0.2"
langchain-anthropic = "^0.3"          # optional: Claude models
langgraph         = "^0.2"
langsmith         = "^0.1"
fastmcp           = "^2.0"
openai            = "^1.40"

# ── RAG ──────────────────────────────────────────────────────────
chromadb          = "^0.5"            # local vector DB (dev)
pgvector          = "^0.3"            # pgvector ORM extension
unstructured      = {extras = ["pdf", "docx"], version = "^0.15"}
langchain-text-splitters = "^0.3"     # RecursiveCharacterTextSplitter
langchain-community = "^0.3"         # document loaders (PDF, DOCX, etc.)

# ── Database ─────────────────────────────────────────────────────
sqlalchemy        = {extras = ["asyncio"], version = "^2.0"}
asyncpg           = "^0.29"           # async PostgreSQL driver
alembic           = "^1.13"

# ── Cache / Session ───────────────────────────────────────────────
redis             = "^5.0"
hiredis           = "^2.3"            # C parser for redis (faster)

# ── Auth ──────────────────────────────────────────────────────────
pyjwt             = {extras = ["crypto"], version = "^2.8"}
passlib           = {extras = ["bcrypt"], version = "^1.7"}

# ── Config / Validation ───────────────────────────────────────────
pydantic          = "^2.8"
pydantic-settings = "^2.4"

# ── Logging / Observability ───────────────────────────────────────
structlog         = "^24.4"
python-json-logger = "^2.0"

# ── Utilities ─────────────────────────────────────────────────────
python-multipart  = "^0.0.9"          # file upload support
aiofiles          = "^24.1"

[tool.poetry.dev-dependencies]
pytest             = "^8.0"
pytest-asyncio     = "^0.23"
pytest-cov         = "^5.0"
httpx              = "^0.27"          # for TestClient
ruff               = "^0.5"           # linter + formatter
mypy               = "^1.10"

[tool.ruff]
line-length = 100
select = ["E", "F", "I", "UP", "B"]

[tool.mypy]
python_version = "3.11"
strict = true
ignore_missing_imports = true

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

## requirements.txt

```txt
# ── Core Framework ─────────────────────────────────────────────────────────────
fastapi
uvicorn[standard]
python-multipart
python-dotenv
pyjwt[crypto]

# ── Database & Migrations ─────────────────────────────────────────────────────
sqlalchemy[asyncio]
asyncpg
pgvector
alembic
greenlet

# ── AI & LangChain Ecosystem ──────────────────────────────────────────────────
openai
langchain
langchain-openai
langchain-anthropic
langchain-core
langchain-community
langchain-text-splitters
langgraph
langsmith
fastmcp
tiktoken

# ── Vector DB & RAG ───────────────────────────────────────────────────────────
langchain-chroma
chromadb

# ── Cache & Session (Rate Limiting) ───────────────────────────────────────────
redis
hiredis

# ── Auth & Security ───────────────────────────────────────────────────────────
passlib[bcrypt]

# ── Logging & Observability ───────────────────────────────────────────────────
structlog
python-json-logger

# ── Utilities ─────────────────────────────────────────────────────────────────
pydantic
pydantic-settings
httpx
aiofiles

# ── Document Processing (for ingestion) ───────────────────────────────────────
unstructured[pdf,docx]
pypdf
python-docx

```

## scratch_test.py

```python
"""Quick smoke-test: verify RAG tool imports + run a live query."""
import asyncio
from dotenv import load_dotenv
load_dotenv()

from app.tools.rag_tools import search_knowledge
from app.models import UserRole

async def main():
    print("Testing RAG search as 'employee' role...")
    result = await search_knowledge("What is the leave policy?", UserRole.employee)
    print(result)

asyncio.run(main())

```

## test_openai.py

```python
import os
import httpx
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

def test_connection():
    try:
        response = httpx.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": "Hello"}]
            },
            timeout=10.0
        )
        print("Status code:", response.status_code)
        print("Response:", response.text)
    except Exception as e:
        print("Exception:", str(e))

test_connection()

```

