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
