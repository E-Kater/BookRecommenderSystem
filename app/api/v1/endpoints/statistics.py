from uuid import UUID

from fastapi import APIRouter, HTTPException
from app.core.recommender import BookRecommender
from app.db.postgres.session import get_db
import pandas as pd

router = APIRouter()
recommender = BookRecommender()

db = next(get_db())


@router.get("/avg-user-rating/{user_id}")
async def get_user(user_id: UUID):
    """Get user info"""
    try:
        user_df = pd.read_sql(
            f"SELECT AVG(rating) FROM ratings WHERE user_id = '{user_id}' GROUP BY user_id",
            db.connection()
        )
        if user_df.empty:
            raise HTTPException(status_code=404, detail="User not found")
        user_data = user_df.to_dict(orient="records")[0]

        return user_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching avg user rating: {str(e)}")


@router.get("/avg-users-rating")
async def get_users():
    """Get user info"""
    try:
        user_df = pd.read_sql(
            f"SELECT AVG(rating), user_id FROM ratings GROUP BY user_id",
            db.connection()
        )
        if user_df.empty:
            raise HTTPException(status_code=404, detail="User not found")
        user_data = user_df.to_dict(orient="records")

        return user_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching avg user rating: {str(e)}")


@router.get("/avg-book-rating/{book_id}")
async def get_book(book_id: UUID):
    """Get user info"""
    try:
        book_df = pd.read_sql(
            f"SELECT AVG(rating) FROM ratings WHERE book_id = '{book_id}' GROUP BY book_id",
            db.connection()
        )
        if book_df.empty:
            raise HTTPException(status_code=404, detail="Book not found")
        book_data = book_df.to_dict(orient="records")[0]

        return book_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching avg book rating: {str(e)}")


@router.get("/avg-books-rating")
async def get_books():
    """Get user info"""
    try:
        user_df = pd.read_sql(
            f"SELECT AVG(rating), book_id FROM ratings GROUP BY book_id",
            db.connection()
        )
        if user_df.empty:
            raise HTTPException(status_code=404, detail="Books not found")
        user_data = user_df.to_dict(orient="records")

        return user_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching avg user rating: {str(e)}")
