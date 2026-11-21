"""Create (or update) an admin user. Run with:

    docker compose run --rm -v "${PWD}:/repo" -w /repo api python scripts/create_admin.py

Override credentials with ADMIN_EMAIL / ADMIN_PASSWORD environment variables.
"""

import asyncio
import os
import sys
from pathlib import Path

API_DIR = Path(__file__).resolve().parents[1] / "apps" / "api"
if (API_DIR / "app").exists():
    sys.path.insert(0, str(API_DIR))

from sqlalchemy import select

from app.core.security import hash_password
from app.db.session import AsyncSessionLocal
from app.models import User

EMAIL = os.getenv("ADMIN_EMAIL", "admin@example.com")
PASSWORD = os.getenv("ADMIN_PASSWORD", "change-this-password")


async def main() -> None:
    async with AsyncSessionLocal() as db:
        user = (await db.execute(select(User).where(User.email == EMAIL))).scalar_one_or_none()
        if user:
            user.password_hash = hash_password(PASSWORD)
            user.role = "admin"
            action = "Updated"
        else:
            db.add(User(email=EMAIL, password_hash=hash_password(PASSWORD), role="admin"))
            action = "Created"
        await db.commit()
    print(f"{action} admin account: {EMAIL}")


if __name__ == "__main__":
    asyncio.run(main())
