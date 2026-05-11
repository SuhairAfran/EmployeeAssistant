"""
Initialize passwords for seeded users.
=====================================
Sets a known default password (default: ``Password@123``) on every active user
in the DB so you can log in via /api/v1/auth/login during testing.

Usage:
    python -m scripts.init_passwords
    python -m scripts.init_passwords --password MyPass123
    python -m scripts.init_passwords --email emp.1@novigosolutions.com --password Foo
"""
from __future__ import annotations

import argparse
import asyncio

from passlib.context import CryptContext
from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def set_passwords(password: str, email: str | None) -> None:
    hashed = pwd_context.hash(password)

    async with AsyncSessionLocal() as db:
        stmt = select(User)
        if email:
            stmt = stmt.where(User.email == email.lower())
        result = await db.execute(stmt)
        users = result.scalars().all()

        if not users:
            print(f"No users matched (email filter: {email!r}).")
            return

        for u in users:
            u.password_hash = hashed

        await db.commit()

        print(f"Updated {len(users)} user(s) to password={password!r}")
        for u in users:
            print(f"  - {u.email}  (role={u.role.value}, employee_id={u.employee_id})")


def main() -> None:
    parser = argparse.ArgumentParser(description="Set bcrypt password hashes for seeded users.")
    parser.add_argument("--password", default="Password@123", help="Plaintext password to set (default: Password@123)")
    parser.add_argument("--email", default=None, help="If set, only update this single user.")
    args = parser.parse_args()

    asyncio.run(set_passwords(args.password, args.email))


if __name__ == "__main__":
    main()
