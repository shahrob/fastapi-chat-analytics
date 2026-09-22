"""
db/mongodb.py
─────────────
Async MongoDB client management using Motor.

Usage
-----
Call ``connect_to_mongo()`` on application startup and
``close_mongo_connection()`` on shutdown.

To get the database instance inside an endpoint or service, inject
``get_mongodb`` as a FastAPI dependency, or import ``mongodb`` directly.
"""

import logging

from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings

logger = logging.getLogger(__name__)


class _MongoDB:
    """Internal singleton that holds the Motor client and database reference."""

    client: AsyncIOMotorClient = None
    database = None


mongodb = _MongoDB()


async def connect_to_mongo() -> None:
    """Create the MongoDB connection and verify it with a ping."""
    try:
        mongodb.client = AsyncIOMotorClient(settings.MONGODB_URL)
        mongodb.database = mongodb.client[settings.MONGODB_DATABASE]
        await mongodb.client.admin.command("ping")
        logger.info("Connected to MongoDB at %s", settings.MONGODB_URL)
    except Exception as exc:
        logger.warning("Could not connect to MongoDB: %s — MongoDB features disabled.", exc)


async def close_mongo_connection() -> None:
    """Close the MongoDB connection gracefully."""
    if mongodb.client:
        mongodb.client.close()
        logger.info("Disconnected from MongoDB")


async def get_mongodb():
    """FastAPI dependency — yields the Motor database instance."""
    return mongodb.database
