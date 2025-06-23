from uuid import UUID

from fastapi import APIRouter, HTTPException
from app.core.recommender import BookRecommender
from app.db.postgres.session import get_db
import pandas as pd

router = APIRouter()
recommender = BookRecommender()

db = next(get_db())


@router.get("/{user_id}")
async def get_user(user_id: UUID):
    """Get user info"""
    try:
        user_df = pd.read_sql(
            f"SELECT * FROM users WHERE id = '{user_id}'",
            db.connection()
        )
        if user_df.empty:
            raise HTTPException(status_code=404, detail="User not found")
        user_data = user_df.to_dict(orient="records")[0]

        return user_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching user: {str(e)}")
