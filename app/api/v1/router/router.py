from fastapi import APIRouter
from app.api.v1.endpoints import users, recommendations, books, ratings, statistics

api_router = APIRouter()
api_router.include_router(books.router, prefix="/books", tags=["books"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(recommendations.router, prefix="/recommendations", tags=["recommendations"])
api_router.include_router(ratings.router, prefix="/ratings", tags=["ratings"])
api_router.include_router(statistics.router, prefix="/statistics", tags=["statistics"])