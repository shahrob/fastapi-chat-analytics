"""
scripts/create_superuser.py
────────────────────────────
Interactive CLI script to create an admin / superuser account.

Usage:
    python scripts/create_superuser.py
    python scripts/create_superuser.py --username admin --email admin@example.com
"""

import argparse
import getpass
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import Base, engine, SessionLocal
from app.models.user import User
from app.core.security import get_password_hash


def create_superuser(username: str, email: str, password: str, full_name: str = "") -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        existing = db.query(User).filter(
            (User.username == username) | (User.email == email)
        ).first()
        if existing:
            print(f"❌ A user with username '{username}' or email '{email}' already exists.")
            sys.exit(1)

        user = User(
            username=username,
            email=email,
            full_name=full_name or username,
            hashed_password=get_password_hash(password),
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"✅ Superuser '{username}' created successfully (id={user.id}).")
    except Exception as exc:
        db.rollback()
        print(f"❌ Error: {exc}")
        raise
    finally:
        db.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a superuser account.")
    parser.add_argument("--username", help="Username")
    parser.add_argument("--email", help="Email address")
    parser.add_argument("--full-name", default="", help="Full name (optional)")
    args = parser.parse_args()

    username = args.username or input("Username: ").strip()
    email = args.email or input("Email: ").strip()
    full_name = args.full_name or input("Full name (optional): ").strip()
    password = getpass.getpass("Password: ")
    confirm = getpass.getpass("Confirm password: ")

    if password != confirm:
        print("❌ Passwords do not match.")
        sys.exit(1)

    if len(password) < 8:
        print("❌ Password must be at least 8 characters.")
        sys.exit(1)

    create_superuser(username, email, password, full_name)


if __name__ == "__main__":
    main()
