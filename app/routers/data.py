from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session
from typing import Dict, List, Any

from app.database import get_db
from app.dependencies import get_current_active_user
from app.schemas.user import User
from app.services.data_service import data_service

router = APIRouter()

@router.get("/analytics", response_model=Dict[str, Any])
async def get_chat_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get comprehensive chat analytics using pandas"""
    
    analytics = await data_service.get_chat_analytics(db)
    
    # Save to MongoDB for historical tracking
    if "error" not in analytics:
        await data_service.save_analytics_to_mongodb(analytics)
    
    return {
        "success": True,
        "data": analytics,
        "message": "Chat analytics generated successfully"
    }

@router.get("/export/csv", response_class=PlainTextResponse)
async def export_data_to_csv(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Export conversation data to CSV format"""
    
    csv_data = await data_service.export_conversations_to_csv(db)
    
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=chat_data.csv"}
    )

@router.get("/analytics/history")
async def get_analytics_history():
    """Get historical analytics data from MongoDB - No authentication required"""
    
    history = await data_service.get_analytics_history_from_mongodb()
    
    return {
        "success": True,
        "data": history,
        "count": len(history),
        "message": "Analytics history retrieved successfully"
    }

@router.get("/sample")
async def get_sample_data(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get sample data for demonstration"""
    
    sample_data = await data_service.create_sample_data(db)
    
    return {
        "success": True,
        "data": sample_data,
        "message": "Sample data generated successfully"
    }

@router.post("/process")
async def process_data(
    data: List[Dict[str, Any]] = []
):
    """Process provided data using pandas operations - No authentication required"""
    
    try:
        results = data_service.process_dataframe_operations(data)
        
        return {
            "success": True,
            "data": results,
            "message": "Data processed successfully" + (" (using sample data)" if not data else "")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing data: {str(e)}")

@router.get("/mongodb/stats")
async def get_mongodb_stats():
    """Get complete MongoDB database statistics - No authentication required"""
    
    try:
        stats = await data_service.get_complete_mongodb_stats()
        print(stats,"stats........................................")  # Debugging line to check stats structure

        return {
            "success": True,
            "data": stats,
            "message": "MongoDB statistics retrieved successfully"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Error retrieving MongoDB statistics"
        }

@router.get("/pandas/analyze/{collection_name}")
async def analyze_collection_with_pandas(collection_name: str):
    """Analyze a specific MongoDB collection using pandas - No authentication required"""
    
    try:
        
        analysis = await data_service.analyze_mongodb_data_with_pandas(collection_name)
        
        return {
            "success": True,
            "data": analysis,
            "message": f"Pandas analysis completed for collection: {collection_name}"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Error analyzing collection with pandas"
        }

@router.get("/pandas/analyze")
async def analyze_first_collection_with_pandas():
    """Analyze the first available MongoDB collection using pandas - No authentication required"""
    try:
        analysis = await data_service.analyze_mongodb_data_with_pandas()
        
        return {
            "success": True,
            "data": analysis,
            "message": "Pandas analysis completed for first available collection"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Error analyzing collection with pandas"
        }

@router.post("/pandas/custom-analysis")
async def custom_pandas_analysis(data: List[Dict[str, Any]]):
    """Perform custom pandas analysis on provided data - No authentication required"""
    
    if not data:
        return {
            "success": False,
            "error": "No data provided",
            "message": "Please provide data for analysis"
        }
    
    try:
        import pandas as pd
        
        # Create DataFrame
        df = pd.DataFrame(data)
        
        # Custom pandas operations
        analysis = {
            "basic_info": {
                "shape": df.shape,
                "columns": df.columns.tolist(),
                "data_types": df.dtypes.to_dict()
            },
            "statistical_summary": {},
            "data_insights": {},
            "visualizations_data": {}
        }
        
        # Numerical analysis
        numeric_cols = df.select_dtypes(include=[int, float]).columns
        if len(numeric_cols) > 0:
            analysis["statistical_summary"]["numeric"] = df[numeric_cols].describe().to_dict()
            
            # Correlation matrix
            if len(numeric_cols) > 1:
                analysis["statistical_summary"]["correlations"] = df[numeric_cols].corr().to_dict()
            
            # Outlier detection using IQR
            for col in numeric_cols:
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                outliers = df[(df[col] < Q1 - 1.5 * IQR) | (df[col] > Q3 + 1.5 * IQR)]
                
                analysis["data_insights"][f"{col}_outliers"] = {
                    "count": len(outliers),
                    "percentage": round(len(outliers) / len(df) * 100, 2),
                    "values": outliers[col].tolist()[:10]  # First 10 outliers
                }
        
        # Categorical analysis
        categorical_cols = df.select_dtypes(include=['object']).columns
        if len(categorical_cols) > 0:
            analysis["statistical_summary"]["categorical"] = {}
            for col in categorical_cols:
                value_counts = df[col].value_counts()
                analysis["statistical_summary"]["categorical"][col] = {
                    "unique_count": df[col].nunique(),
                    "most_frequent": value_counts.index[0] if len(value_counts) > 0 else None,
                    "top_5_values": value_counts.head().to_dict()
                }
        
        # Missing data analysis
        missing_data = df.isnull().sum()
        analysis["data_insights"]["missing_data"] = {
            "total_missing": missing_data.sum(),
            "missing_by_column": missing_data.to_dict(),
            "missing_percentage": (missing_data / len(df) * 100).round(2).to_dict()
        }
        
        # Data for visualizations (aggregated data that can be used for charts)
        if len(numeric_cols) > 0:
            # Histogram data for first numeric column
            first_numeric = numeric_cols[0]
            hist_data = df[first_numeric].value_counts().sort_index()
            analysis["visualizations_data"]["histogram"] = {
                "column": first_numeric,
                "bins": hist_data.index.tolist(),
                "counts": hist_data.values.tolist()
            }
        
        if len(categorical_cols) > 0:
            # Bar chart data for first categorical column
            first_categorical = categorical_cols[0]
            bar_data = df[first_categorical].value_counts().head(10)
            analysis["visualizations_data"]["bar_chart"] = {
                "column": first_categorical,
                "categories": bar_data.index.tolist(),
                "counts": bar_data.values.tolist()
            }
        
        return {
            "success": True,
            "data": analysis,
            "message": "Custom pandas analysis completed successfully"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Error performing custom pandas analysis"
        }

@router.get("/dashboard")
async def get_dashboard_data(
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_active_user)
):
    """Get comprehensive dashboard data combining multiple sources"""
    
    try:
        # Get analytics
        analytics = await data_service.get_chat_analytics(db)
        
        # Get sample data
        sample_data = await data_service.create_sample_data(db)
        
        # Get MongoDB history (if available)
        history = await data_service.get_analytics_history_from_mongodb()
        
        dashboard_data = {
            "analytics": analytics,
            "sample_data": sample_data,
            "history_count": len(history),
            "latest_history": history[:3] if history else [],
            "status": {
                "sqlite_connected": True,
                "mongodb_connected": len(history) > 0 or await data_service.save_analytics_to_mongodb({"test": True}),
                "pandas_available": True
            }
        }
        
        return {
            "success": True,
            "data": dashboard_data,
            "message": "Dashboard data retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving dashboard data: {str(e)}")

@router.get("/health")
async def data_service_health():
    """Check the health of data services - No authentication required"""
    
    try:
        # Test pandas
        import pandas as pd
        df = pd.DataFrame({"test": [1, 2, 3]})
        pandas_status = "operational"
    except Exception:
        pandas_status = "error"
    
    # Test MongoDB connection
    mongodb_status = "operational" if await data_service.get_analytics_history_from_mongodb() is not None else "disconnected"
    
    return {
        "success": True,
        "services": {
            "pandas": pandas_status,
            "mongodb": mongodb_status,
            "data_processing": "operational"
        },
        "message": "Data service health check completed"
    }

@router.get("/analytics/public")
async def get_public_analytics(db: Session = Depends(get_db)):
    """Get basic analytics without authentication (for testing)"""
    
    try:
        analytics = await data_service.get_chat_analytics(db)
        
        return {
            "success": True,
            "data": analytics,
            "message": "Public analytics generated successfully",
            "note": "This is a simplified version. Use /data/analytics with authentication for full features."
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Error generating analytics"
        }
