"""
scripts/seed_db.py
───────────────────
Database seeding script — populates the database with demo data.

Usage:
    python scripts/seed_db.py
"""

import sys
import os

# Allow running from the project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import Base, engine, SessionLocal
from app.models.user import User
from app.models.conversation import Conversation
from app.models.message import Message
from app.core.security import get_password_hash


SEED_USERS = [
    {"username": "admin", "email": "admin@example.com", "password": "AdminPass123!", "full_name": "Admin User"},
    {"username": "demo",  "email": "demo@example.com",  "password": "DemoPass123!",  "full_name": "Demo User"},
]

SEED_CONVERSATIONS = [
    {"title": "Getting Started"},
    {"title": "Feature Questions"},
]


def seed():
    print("🌱 Creating database tables...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        for user_data in SEED_USERS:
            existing = db.query(User).filter(User.username == user_data["username"]).first()
            if existing:
                print(f"  ⏭  User '{user_data['username']}' already exists — skipping.")
                continue

            user = User(
                username=user_data["username"],
                email=user_data["email"],
                full_name=user_data["full_name"],
                hashed_password=get_password_hash(user_data["password"]),
            )
            db.add(user)
            db.flush()

            for conv_data in SEED_CONVERSATIONS:
                conversation = Conversation(title=conv_data["title"], user_id=user.id)
                db.add(conversation)
                db.flush()

                db.add(Message(
                    content=f"Hello! I'm in the '{conv_data['title']}' conversation.",
                    conversation_id=conversation.id,
                    user_id=user.id,
                    is_ai_response=False,
                ))
                db.add(Message(
                    content="Hi there! I'm your AI assistant. How can I help?",
                    conversation_id=conversation.id,
                    user_id=user.id,
                    is_ai_response=True,
                ))

            print(f"  ✅ Created user '{user_data['username']}' with {len(SEED_CONVERSATIONS)} conversations.")

        db.commit()
        print("\n✅ Database seeded successfully.")

    except Exception as exc:
        db.rollback()
        print(f"\n❌ Seeding failed: {exc}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
