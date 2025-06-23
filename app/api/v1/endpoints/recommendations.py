from uuid import UUID

from fastapi import APIRouter
from app.core.recommender import BookRecommender
from app.db.postgres.session import get_db
import pandas as pd

router = APIRouter()
recommender = BookRecommender()


@router.on_event("startup")
async def startup_event():
    """Load data and train models on startup"""
    db = next(get_db())

    # Load ratings
    ratings = pd.read_sql("SELECT user_id, book_id, rating FROM ratings", db.connection())

    # Load books
    books = pd.read_sql("""
        SELECT id, title, author, genres 
        FROM books
    """, db.connection())

    recommender.load_data(ratings, books)
    recommender.train_collaborative()
    recommender.train_content_based()
    recommender.train_als()


@router.get("/recommend/{user_id}")
async def get_recommendations(user_id: UUID, limit: int = 5):
    """Get personalized recommendations"""
    return recommender.hybrid_recommend(user_id, top_n=limit)


@router.get("/similar/{book_id}")
async def get_similar(book_id: UUID, limit: int = 5):
    """Get similar books"""
    return recommender.get_similar_books(book_id, top_n=limit)


@router.get("/als/{user_id}")
async def get_als(user_id: UUID, limit: int = 5):
    """Get ALS recommendations"""
    return recommender.als_recommend(user_id, limit)
