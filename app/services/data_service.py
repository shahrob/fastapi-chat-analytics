import pandas as pd
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import io
from bson import ObjectId
from app.db.mongodb import get_mongodb
from app.models.message import Message
from app.models.conversation import Conversation
from app.models.user import User
from sqlalchemy.orm import Session

class DataService:
    
    @staticmethod
    def convert_objectid_to_str(obj):
        """Recursively convert ObjectId instances to strings"""
        if isinstance(obj, ObjectId):
            return str(obj)
        elif isinstance(obj, dict):
            return {key: DataService.convert_objectid_to_str(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [DataService.convert_objectid_to_str(item) for item in obj]
        elif isinstance(obj, datetime):
            return obj.isoformat()
        else:
            return obj
    
    @staticmethod
    def flatten_dict(d, parent_key='', sep='_'):
        """Flatten nested dictionaries and convert lists to strings"""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(DataService.flatten_dict(v, new_key, sep=sep).items())
            elif isinstance(v, list):
                # Convert lists to string representation to make them hashable
                items.append((new_key, str(v)))
            else:
                items.append((new_key, v))
        return dict(items)
    
    @staticmethod
    def prepare_data_for_pandas(documents):
        """Prepare MongoDB documents for pandas DataFrame creation"""
        processed_docs = []
        
        for doc in documents:
            # First convert ObjectId and datetime
            doc_clean = DataService.convert_objectid_to_str(doc)
            
            # Then flatten nested structures and handle lists
            doc_flat = DataService.flatten_dict(doc_clean)
            
            processed_docs.append(doc_flat)
        
        return processed_docs
    
    @staticmethod
    async def get_chat_analytics(db: Session) -> Dict[str, Any]:
        """Generate chat analytics using pandas"""
        
        # Get all messages
        messages = db.query(Message).all()
        print(f"Total messages retrieved: {len(messages)}")
        if not messages:
            return {"error": "No data available"}
        
        # Convert to pandas DataFrame
        data = []
        for msg in messages:
            data.append({
                "id": msg.id,
                "content": msg.content,
                "conversation_id": msg.conversation_id,
                "user_id": msg.user_id,
                "is_ai_response": msg.is_ai_response,
                "created_at": msg.created_at,
                "message_length": len(msg.content),
                "word_count": len(msg.content.split())
            })
        
        df = pd.DataFrame(data)
        
        # Generate analytics
        analytics = {
            "total_messages": len(df),
            "total_conversations": df['conversation_id'].nunique(),
            "total_users": df['user_id'].nunique(),
            "ai_messages": len(df[df['is_ai_response'] == True]),
            "user_messages": len(df[df['is_ai_response'] == False]),
            "average_message_length": df['message_length'].mean(),
            "average_words_per_message": df['word_count'].mean(),
            "messages_by_hour": df.groupby(df['created_at'].dt.hour).size().to_dict(),
            "messages_by_day": df.groupby(df['created_at'].dt.date).size().to_dict(),
            "top_conversations": df['conversation_id'].value_counts().head(10).to_dict(),
            "most_active_users": df['user_id'].value_counts().head(10).to_dict()
        }
        
        # Convert datetime objects to strings for JSON serialization
        for key, value in analytics.items():
            if isinstance(value, dict):
                analytics[key] = {str(k): v for k, v in value.items()}
        
        return analytics
    
    @staticmethod
    async def export_conversations_to_csv(db: Session) -> str:
        """Export conversations data to CSV format"""
        
        # Query conversations with related data
        conversations = db.query(Conversation).all()
        
        data = []
        for conv in conversations:
            messages = db.query(Message).filter(Message.conversation_id == conv.id).all()
            user = db.query(User).filter(User.id == conv.user_id).first()
            
            data.append({
                "conversation_id": conv.id,
                "title": conv.title,
                "user_id": conv.user_id,
                "username": user.username if user else "Unknown",
                "created_at": conv.created_at,
                "updated_at": conv.updated_at,
                "message_count": len(messages),
                "total_characters": sum(len(msg.content) for msg in messages),
                "ai_messages": sum(1 for msg in messages if msg.is_ai_response),
                "user_messages": sum(1 for msg in messages if not msg.is_ai_response)
            })
        
        df = pd.DataFrame(data)
        
        # Convert to CSV
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        return csv_buffer.getvalue()
    
    @staticmethod
    async def save_analytics_to_mongodb(analytics_data: Dict[str, Any]) -> bool:
        """Save analytics data to MongoDB"""
        try:
            db = await get_mongodb()
            if db is None:
                return False
            
            # Add timestamp
            analytics_data["timestamp"] = datetime.utcnow()
            analytics_data["type"] = "chat_analytics"
            
            # Insert into MongoDB
            await db.analytics.insert_one(analytics_data)
            return True
            
        except Exception as e:
            print(f"Error saving to MongoDB: {e}")
            return False
    
    @staticmethod
    async def get_analytics_history_from_mongodb() -> List[Dict[str, Any]]:
        """Get analytics history from MongoDB"""
        try:
            db = await get_mongodb()
            if db is None:
                return []
            
            # Get latest 10 analytics records
            cursor = db.analytics.find(
                {"type": "chat_analytics"}
            ).sort("timestamp", -1).limit(10)
            
            analytics_list = []
            async for doc in cursor:
                # Convert all ObjectId and datetime instances
                doc = DataService.convert_objectid_to_str(doc)
                analytics_list.append(doc)
            
            return analytics_list
            
        except Exception as e:
            print(f"Error retrieving from MongoDB: {e}")
            return []
    
    @staticmethod
    async def create_sample_data(db: Session) -> Dict[str, Any]:
        """Create sample data for demonstration"""
        
        # Sample data
        sample_data = {
            "users": [
                {"id": 1, "name": "Alice", "email": "alice@example.com"},
                {"id": 2, "name": "Bob", "email": "bob@example.com"},
                {"id": 3, "name": "Charlie", "email": "charlie@example.com"}
            ],
            "products": [
                {"id": 1, "name": "Laptop", "price": 999.99, "category": "Electronics"},
                {"id": 2, "name": "Book", "price": 19.99, "category": "Education"},
                {"id": 3, "name": "Coffee", "price": 4.99, "category": "Food"}
            ],
            "orders": [
                {"id": 1, "user_id": 1, "product_id": 1, "quantity": 1, "total": 999.99},
                {"id": 2, "user_id": 2, "product_id": 2, "quantity": 3, "total": 59.97},
                {"id": 3, "user_id": 1, "product_id": 3, "quantity": 2, "total": 9.98}
            ]
        }
        
        # Save to MongoDB if available
        try:
            db_mongo = await get_mongodb()
            if db_mongo is not None:
                sample_data["timestamp"] = datetime.utcnow()
                sample_data["type"] = "sample_data"
                await db_mongo.sample_data.insert_one(sample_data.copy())
        except Exception as e:
            print(f"Could not save sample data to MongoDB: {e}")
        
        return sample_data
    
    @staticmethod
    def process_dataframe_operations(data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform various pandas operations on data"""
        
        if not data:
            # Provide sample data to demonstrate functionality
            data = [
                {"name": "Alice", "age": 25, "city": "New York", "salary": 50000, "department": "Engineering"},
                {"name": "Bob", "age": 30, "city": "Los Angeles", "salary": 60000, "department": "Marketing"},
                {"name": "Charlie", "age": 35, "city": "Chicago", "salary": 55000, "department": "Engineering"},
                {"name": "Diana", "age": 28, "city": "Houston", "salary": 52000, "department": "Sales"},
                {"name": "Eve", "age": 32, "city": "Phoenix", "salary": 58000, "department": "Marketing"}
            ]
        
        df = pd.DataFrame(data)
        
        # Basic statistics
        results = {
            "shape": df.shape,
            "columns": df.columns.tolist(),
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "info": {
                "memory_usage": int(df.memory_usage().sum()),
                "null_values": {col: int(count) for col, count in df.isnull().sum().items()},
                "unique_values": {col: int(count) for col, count in df.nunique().items()}
            },
            "sample_data_used": not bool([x for x in [data] if x])  # True if original data was empty
        }
        
        # Numerical statistics if available
        numeric_cols = df.select_dtypes(include=[int, float]).columns
        if len(numeric_cols) > 0:
            describe_stats = df[numeric_cols].describe()
            stats_dict = {}
            for col in describe_stats.columns:
                stats_dict[col] = {
                    stat: float(value) if not pd.isna(value) else None 
                    for stat, value in describe_stats[col].items()
                }
            results["statistics"] = stats_dict
        
        # Categorical analysis
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        if len(categorical_cols) > 0:
            results["categorical_analysis"] = {}
            for col in categorical_cols[:5]:  # Limit to first 5 columns
                value_counts = df[col].value_counts().head(10)
                results["categorical_analysis"][col] = {
                    str(k): int(v) for k, v in value_counts.to_dict().items()
                }
        
        return results

    @staticmethod
    async def get_complete_mongodb_stats() -> Dict[str, Any]:
        print("Getting complete MongoDB stats...")
        """Get comprehensive MongoDB database statistics"""
        
        try:
            db = await get_mongodb()
            if db is None:
                return {"error": "MongoDB connection not available"}
            
            # Get database statistics
            try:
                db_stats = await db.command("dbStats")
                if not isinstance(db_stats, dict):
                    db_stats = {}
                # Convert any ObjectId instances in db_stats
                db_stats = DataService.convert_objectid_to_str(db_stats)
            except Exception as e:
                db_stats = {"error": f"Could not get db stats: {str(e)}"}
            print(f"Database stats: {db_stats}")
            # Get collection statistics
            collections = await db.list_collection_names()
            collection_stats = {}
            print(f"Collections: {collections}")
            # Ensure collections is a list
            if not isinstance(collections, list):
                collections = []
            
            for collection_name in collections:
                print(f"Processing collection: {collection_name}")  
                try:
                    # Ensure collection_name is a string
                    if not isinstance(collection_name, str):
                        continue
                        
                    # Get collection stats
                    coll_stats = await db.command("collStats", collection_name)
                    print(f"Collection stats for {collection_name}: {coll_stats}")
                    # Convert ObjectId instances in collection stats
                    coll_stats = DataService.convert_objectid_to_str(coll_stats)
                    
                    # Get document count and sample documents
                    collection = db[collection_name]
                    doc_count = await collection.count_documents({})
                    print(f"Document count for {collection_name}: {doc_count}")
                    
                    # Get sample documents (first 3)
                    sample_docs = []
                    async for doc in collection.find().limit(3):
                        # Convert all ObjectId and datetime instances recursively
                        doc = DataService.convert_objectid_to_str(doc)
                        sample_docs.append(doc)
                    
                    collection_stats[collection_name] = {
                        "document_count": doc_count,
                        "size_bytes": coll_stats.get("size", 0),
                        "storage_size_bytes": coll_stats.get("storageSize", 0),
                        "avg_obj_size": coll_stats.get("avgObjSize", 0),
                        "indexes": coll_stats.get("nindexes", 0),
                        "total_index_size": coll_stats.get("totalIndexSize", 0),
                        "sample_documents": sample_docs
                    }
                except Exception as e:
                    collection_stats[collection_name] = {"error": str(e)}
            print(f"Collection stats: {collection_stats}")
            # Get server status (limited info)
            
            try:
                server_status = await db.command("serverStatus")
                # Convert ObjectId instances in server status
                server_status = DataService.convert_objectid_to_str(server_status)
                uptime = server_status.get("uptime", 0)
                connections = server_status.get("connections", {})
            except Exception:
                uptime = 0
                connections = {}
            
            # Compile comprehensive stats
            complete_stats = {
                "database_info": {
                    "name": db.name,
                    "collections_count": len(collections),
                    "collections": collections,
                    "data_size_bytes": db_stats.get("dataSize", 0),
                    "storage_size_bytes": db_stats.get("storageSize", 0),
                    "index_size_bytes": db_stats.get("indexSize", 0),
                    "objects_count": db_stats.get("objects", 0),
                    "avg_obj_size": db_stats.get("avgObjSize", 0),
                    "file_size_bytes": db_stats.get("fileSize", 0)
                },
                "server_info": {
                    "uptime_seconds": uptime,
                    "connections": connections
                },
                "collections_detail": collection_stats,
                "summary": {
                    "total_documents": sum(
                        stats.get("document_count", 0) 
                        for stats in collection_stats.values() 
                        if isinstance(stats, dict) and "document_count" in stats
                    ),
                    "largest_collection": max(
                        collection_stats.items(),
                        key=lambda x: x[1].get("document_count", 0) if isinstance(x[1], dict) else 0,
                        default=("none", {"document_count": 0})
                    )[0] if collection_stats else "none"
                }
            }
            
            # Final conversion to ensure no ObjectId instances remain
            complete_stats = DataService.convert_objectid_to_str(complete_stats)

            return complete_stats
        except Exception as e:
            return {
                "error": f"Error retrieving MongoDB stats: {str(e)}",
                "connection_status": "failed"
            }

    @staticmethod
    async def analyze_mongodb_data_with_pandas(collection_name: str = None) -> Dict[str, Any]:
        """Use pandas to analyze MongoDB collection data"""
        
        try:
            db = await get_mongodb()
            if db is None:
                return {"error": "MongoDB connection not available"}
            
            # If no collection specified, analyze all collections
            if not collection_name:
                collections = await db.list_collection_names()
                if not collections:
                    return {"error": "No collections found"}
                # collection_name = collections[0]  # Use first collection
                collection_name = "clients"  # Use first collection for analysis
            
            collection = db[collection_name]
            
            # Get all documents from the collection
            documents = []
            async for doc in collection.find():
                documents.append(doc)
            
            if not documents:
                return {"error": f"No documents found in collection {collection_name}"}
            
            # Prepare data for pandas (handle nested structures and lists)
            processed_documents = DataService.prepare_data_for_pandas(documents)
            
            # Create pandas DataFrame
            df = pd.DataFrame(processed_documents)
            print(df.head()," DataFrame created with shape:", df.shape)
            # Pandas Analysis
            analysis = {
                "collection_name": collection_name,
                "pandas_info": {
                    "shape": df.shape,
                    "columns": df.columns.tolist(),
                    "data_types": {col: str(dtype) for col, dtype in df.dtypes.items()},
                    "memory_usage_mb": round(df.memory_usage(deep=True).sum() / 1024 / 1024, 2)
                },
                "data_quality": {
                    "null_values": df.isnull().sum().to_dict(),
                    "null_percentage": (df.isnull().sum() / len(df) * 100).round(2).to_dict(),
                    "unique_values": df.nunique().to_dict(),
                    "duplicate_rows": int(df.duplicated().sum())
                }
            }
            print("Data quality analysis:", analysis["data_quality"])
            # Numerical analysis
            numeric_cols = df.select_dtypes(include=[int, float]).columns
            if len(numeric_cols) > 0:
                # Convert all numpy values to native Python types for JSON serialization
                describe_stats = df[numeric_cols].describe()
                stats_dict = {}
                for col in describe_stats.columns:
                    stats_dict[col] = {
                        stat: float(value) if not pd.isna(value) else None 
                        for stat, value in describe_stats[col].items()
                    }
                
                correlations = {}
                if len(numeric_cols) > 1:
                    corr_matrix = df[numeric_cols].corr()
                    for col1 in corr_matrix.columns:
                        correlations[col1] = {
                            col2: float(corr_matrix.loc[col1, col2]) if not pd.isna(corr_matrix.loc[col1, col2]) else None
                            for col2 in corr_matrix.columns
                        }
                
                analysis["numerical_analysis"] = {
                    "statistics": stats_dict,
                    "correlations": correlations
                }
            
            # Categorical analysis
            categorical_cols = df.select_dtypes(include=['object']).columns
            if len(categorical_cols) > 0:
                analysis["categorical_analysis"] = {}
                for col in categorical_cols[:5]:  # Limit to 5 columns
                    value_counts = df[col].value_counts().head(10)
                    analysis["categorical_analysis"][col] = {
                        "top_values": {str(k): int(v) for k, v in value_counts.to_dict().items()},
                        "unique_count": int(df[col].nunique()),
                        "most_frequent": str(value_counts.index[0]) if len(value_counts) > 0 else None
                    }
            print("Categorical analysis:", analysis["categorical_analysis"])    
            # Time series analysis (if timestamp/date columns exist)
            try:
                # Try to find columns that might contain datetime strings
                for col in df.columns:
                    if any(keyword in col.lower() for keyword in ['time', 'date', 'created', 'updated', 'timestamp']):
                        try:
                            # Try to convert to datetime
                            df_temp = df.copy()
                            df_temp[col] = pd.to_datetime(df_temp[col], errors='coerce')
                            
                            # Check if conversion was successful (not all NaT)
                            if not df_temp[col].isna().all():
                                if "time_series_analysis" not in analysis:
                                    analysis["time_series_analysis"] = {}
                                
                                analysis["time_series_analysis"][col] = {
                                    "date_range": {
                                        "start": str(df_temp[col].min()),
                                        "end": str(df_temp[col].max())
                                    }
                                }
                                
                                # Only add groupby operations if we have valid dates
                                try:
                                    monthly_counts = df_temp.groupby(df_temp[col].dt.to_period('M')).size()
                                    analysis["time_series_analysis"][col]["records_by_month"] = {
                                        str(k): v for k, v in monthly_counts.to_dict().items()
                                    }
                                except:
                                    pass
                                
                                try:
                                    daily_counts = df_temp.groupby(df_temp[col].dt.date).size()
                                    analysis["time_series_analysis"][col]["records_by_day"] = {
                                        str(k): v for k, v in daily_counts.to_dict().items()
                                    }
                                except:
                                    pass
                        except:
                            continue
            except Exception as e:
                # If time series analysis fails, just skip it
                pass
            print('Time series analysis completed.')
            # Sample data preview
            try:
                # Convert to native Python types for JSON serialization
                def convert_to_json_serializable(obj):
                    """Convert pandas/numpy types to JSON serializable types"""
                    import numpy as np
                    if pd.isna(obj):
                        return None
                    elif isinstance(obj, (np.integer, np.int64, np.int32)):
                        return int(obj)
                    elif isinstance(obj, (np.floating, np.float64, np.float32)):
                        return float(obj)
                    elif isinstance(obj, np.bool_):
                        return bool(obj)
                    elif isinstance(obj, (np.ndarray, list)):
                        return [convert_to_json_serializable(item) for item in obj]
                    elif isinstance(obj, dict):
                        return {k: convert_to_json_serializable(v) for k, v in obj.items()}
                    else:
                        return str(obj)
                
                # Get sample data and convert to JSON serializable format
                first_5 = df.head().fillna("null").to_dict('records')
                last_5 = df.tail().fillna("null").to_dict('records')
                random_sample = df.sample(min(3, len(df))).fillna("null").to_dict('records') if len(df) > 0 else []
                
                analysis["data_preview"] = {
                    "first_5_rows": [
                        {k: convert_to_json_serializable(v) for k, v in row.items()} 
                        for row in first_5
                    ],
                    "last_5_rows": [
                        {k: convert_to_json_serializable(v) for k, v in row.items()} 
                        for row in last_5
                    ],
                    "random_sample": [
                        {k: convert_to_json_serializable(v) for k, v in row.items()} 
                        for row in random_sample
                    ]
                }
            except Exception as e:
                analysis["data_preview"] = {
                    "error": f"Could not generate data preview: {str(e)}"
                }
            
            return analysis
            
        except Exception as e:
            return {
                "error": f"Error analyzing MongoDB data with pandas: {str(e)}"
            }

data_service = DataService()
