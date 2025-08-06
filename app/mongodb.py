from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class MongoDB:
    client: AsyncIOMotorClient = None
    database = None

mongodb = MongoDB()

async def connect_to_mongo():
    """Create database connection"""
    try:
        mongodb.client = AsyncIOMotorClient(settings.MONGODB_URL)
        mongodb.database = mongodb.client[settings.MONGODB_DATABASE]
        
        # Test the connection
        await mongodb.client.admin.command('ping')
        logger.info(f"Connected to MongoDB at {settings.MONGODB_URL}")
        
    except Exception as e:
        logger.warning(f"Could not connect to MongoDB: {e}")
        logger.info("MongoDB features will be disabled")

async def close_mongo_connection():
    """Close database connection"""
    if mongodb.client:
        mongodb.client.close()
        logger.info("Disconnected from MongoDB")

async def get_mongodb():
    """Get MongoDB database instance"""
    return mongodb.database
