"""
api/v1/endpoints/data.py
─────────────────────────
Data analytics and export endpoints.
"""

from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_active_user
from app.db.session import get_db
from app.models.user import User
from app.services.data_service import data_service

router = APIRouter()


@router.get("/analytics", response_model=Dict[str, Any])
async def get_chat_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get comprehensive chat analytics (pandas-powered). Saves result to MongoDB."""
    analytics = await data_service.get_chat_analytics(db)
    if "error" not in analytics:
        await data_service.save_analytics_to_mongodb(analytics)
    return {"success": True, "data": analytics, "message": "Chat analytics generated successfully"}


@router.get("/export/csv")
async def export_csv(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Export conversation data as a downloadable CSV file."""
    csv_data = await data_service.export_conversations_to_csv(db)
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=chat_data.csv"},
    )


@router.get("/analytics/history")
async def get_analytics_history():
    """Retrieve historical analytics snapshots from MongoDB (public)."""
    history = await data_service.get_analytics_history_from_mongodb()
    return {"success": True, "data": history, "count": len(history)}


@router.get("/analytics/public")
async def get_public_analytics(db: Session = Depends(get_db)):
    """Basic analytics without authentication — useful for dashboards/testing."""
    try:
        analytics = await data_service.get_chat_analytics(db)
        return {"success": True, "data": analytics}
    except Exception as exc:
        return {"success": False, "error": str(exc)}


@router.get("/sample")
async def get_sample_data(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Generate sample demo data."""
    sample = await data_service.create_sample_data(db)
    return {"success": True, "data": sample}


@router.post("/process")
async def process_data(data: List[Dict[str, Any]] = []):
    """Run pandas operations on supplied data (public — no auth required)."""
    try:
        results = data_service.process_dataframe_operations(data)
        suffix = " (using sample data)" if not data else ""
        return {"success": True, "data": results, "message": f"Data processed successfully{suffix}"}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error processing data: {exc}")


@router.get("/mongodb/stats")
async def get_mongodb_stats():
    """Full MongoDB database statistics (public)."""
    try:
        stats = await data_service.get_complete_mongodb_stats()
        return {"success": True, "data": stats}
    except Exception as exc:
        return {"success": False, "error": str(exc)}


@router.get("/pandas/analyze/{collection_name}")
async def analyze_collection(collection_name: str):
    """Pandas analysis on a specific MongoDB collection (public)."""
    try:
        analysis = await data_service.analyze_mongodb_data_with_pandas(collection_name)
        return {"success": True, "data": analysis}
    except Exception as exc:
        return {"success": False, "error": str(exc)}


@router.get("/pandas/analyze")
async def analyze_first_collection():
    """Pandas analysis on the first available MongoDB collection (public)."""
    try:
        analysis = await data_service.analyze_mongodb_data_with_pandas()
        return {"success": True, "data": analysis}
    except Exception as exc:
        return {"success": False, "error": str(exc)}


@router.post("/pandas/custom-analysis")
async def custom_pandas_analysis(data: List[Dict[str, Any]]):
    """Perform a full statistical pandas analysis on provided data (public)."""
    if not data:
        return {"success": False, "error": "No data provided"}

    try:
        import pandas as pd

        df = pd.DataFrame(data)
        numeric_cols = df.select_dtypes(include=[int, float]).columns
        categorical_cols = df.select_dtypes(include=["object"]).columns

        analysis: Dict[str, Any] = {
            "basic_info": {
                "shape": df.shape,
                "columns": df.columns.tolist(),
                "data_types": {k: str(v) for k, v in df.dtypes.items()},
            },
            "statistical_summary": {},
            "data_insights": {},
            "visualizations_data": {},
        }

        if len(numeric_cols) > 0:
            analysis["statistical_summary"]["numeric"] = df[numeric_cols].describe().to_dict()
            if len(numeric_cols) > 1:
                analysis["statistical_summary"]["correlations"] = df[numeric_cols].corr().to_dict()
            for col in numeric_cols:
                Q1, Q3 = df[col].quantile(0.25), df[col].quantile(0.75)
                IQR = Q3 - Q1
                outliers = df[(df[col] < Q1 - 1.5 * IQR) | (df[col] > Q3 + 1.5 * IQR)]
                analysis["data_insights"][f"{col}_outliers"] = {
                    "count": len(outliers),
                    "percentage": round(len(outliers) / len(df) * 100, 2),
                }

        if len(categorical_cols) > 0:
            cat_summary: Dict[str, Any] = {}
            for col in categorical_cols:
                vc = df[col].value_counts()
                cat_summary[col] = {
                    "unique_count": df[col].nunique(),
                    "most_frequent": vc.index[0] if len(vc) > 0 else None,
                    "top_5_values": vc.head().to_dict(),
                }
            analysis["statistical_summary"]["categorical"] = cat_summary

        missing = df.isnull().sum()
        analysis["data_insights"]["missing_data"] = {
            "total_missing": int(missing.sum()),
            "missing_by_column": missing.to_dict(),
        }

        return {"success": True, "data": analysis}

    except Exception as exc:
        return {"success": False, "error": str(exc)}


@router.get("/dashboard")
async def get_dashboard(db: Session = Depends(get_db)):
    """Aggregate dashboard data from all sources (public)."""
    try:
        analytics = await data_service.get_chat_analytics(db)
        sample = await data_service.create_sample_data(db)
        history = await data_service.get_analytics_history_from_mongodb()
        return {
            "success": True,
            "data": {
                "analytics": analytics,
                "sample_data": sample,
                "history_count": len(history),
                "latest_history": history[:3] if history else [],
            },
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/health")
async def data_health():
    """Health check for data services (public)."""
    try:
        import pandas as pd
        pd.DataFrame({"test": [1]})
        pandas_status = "operational"
    except Exception:
        pandas_status = "error"

    mongo_result = await data_service.get_analytics_history_from_mongodb()
    mongodb_status = "operational" if mongo_result is not None else "disconnected"

    return {
        "success": True,
        "services": {"pandas": pandas_status, "mongodb": mongodb_status},
    }
