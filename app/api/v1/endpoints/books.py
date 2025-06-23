import uuid
from uuid import UUID

from bson import ObjectId
from fastapi import APIRouter, HTTPException
from fastapi.openapi.models import Response
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.recommender import BookRecommender
from app.db.postgres.models import Book
from app.db.postgres.session import get_db
import pandas as pd
from fastapi.responses import StreamingResponse
from fastapi import UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pymongo import MongoClient
from bson.binary import Binary
import os

from app.models.schemas import BookUpdate, BookCreate

# MongoDB connection (sync PyMongo)
MONGO_HOST = "mongo"  # Docker service name
MONGO_USER = "root"
MONGO_PASS = "example"
MONGO_URI = f"mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}:27017"

client = MongoClient(MONGO_URI)
mongo_db = client["books"]  # Database name
books_collection = mongo_db["books"]  # Collection name

router = APIRouter()
recommender = BookRecommender()

db = next(get_db())

@router.get("")
async def get_books():
    """Get all books info"""
    try:
        book_df = pd.read_sql(
            f"SELECT * FROM books",
            db.connection()
        )
        if book_df.empty:
            raise HTTPException(status_code=404, detail="Books not found")
        book_data = book_df.to_dict(orient="records")

        return book_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Books fetching error: {str(e)}")

@router.get("/{book_id}")
async def get_book(book_id: UUID):
    """Get book info"""
    try:
        book_df = pd.read_sql(
            f"SELECT * FROM books WHERE id = '{book_id}'",
            db.connection()
        )
        if book_df.empty:
            raise HTTPException(status_code=404, detail="Book not found")
        book_data = book_df.to_dict(orient="records")[0]

        return book_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Book fetching book: {str(e)}")


@router.get("/download-book/{book_id}")
async def download_book(book_id: UUID):
    try:
        book = books_collection.find_one({"book_id": str(book_id)})
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")

        return StreamingResponse(
            iter([book["pdf_data"]]),  # Binary data
            media_type=book["content_type"],
            headers={"Content-Disposition": f"attachment; filename={book['filename']}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload-book/{book_id}")
async def upload_book(book_id: UUID, file: UploadFile):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    try:
        # Read the PDF file as bytes
        pdf_bytes = await file.read()

        # Store in MongoDB as a binary document
        book_data = {
            "book_id": str(book_id),
            "filename": file.filename,
            "pdf_data": Binary(pdf_bytes),  # Convert to BSON Binary
            "content_type": "application/pdf"
        }
        result = books_collection.insert_one(book_data)

        return JSONResponse(
            status_code=200,
            content={"message": "PDF uploaded successfully", "book_id": str(book_id)}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")
    finally:
        await file.close()


@router.post("/", status_code=201)
async def create_book(book: BookCreate):
    """Create a new book"""
    try:
        # Create ORM model instance
        db_book = Book(
            id=uuid.uuid4(),  # Generates UUID automatically
            title=book.title,
            author=book.author,
            description=book.description,
            isbn=book.isbn,
            publish_year=book.publish_year,
            genres=book.genres,
            cover_image_url=book.cover_image_url,
            language=book.language,
            page_count=book.page_count
        )

        # Add to session and commit
        db.add(db_book)
        db.commit()
        db.refresh(db_book)  # Refresh to get any database defaults

        return {
            "id": str(db_book.id),
            **book.dict()
        }

    except Exception as e:
        db.rollback()  # Important for failed transactions
        raise HTTPException(
            status_code=400,
            detail=f"Error creating book: {str(e)}"
        )


from fastapi import Response, status


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: UUID):
    """Delete a book by ID"""
    try:
        # Check if book exists and delete in one operation
        deleted_count = db.query(Book).filter(Book.id == book_id).delete()

        if not deleted_count:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Book not found"
            )

        db.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting book: {str(e)}"
        )


@router.put("/{book_id}")
async def update_book(book_id: UUID, book: BookUpdate):
    """Update a book by ID"""
    try:
        # Check if book exists
        db_book = db.query(Book).filter(Book.id == book_id).first()
        if not db_book:
            raise HTTPException(status_code=404, detail="Book not found")

        # Get updates
        update_data = book.dict(exclude_unset=True, exclude_none=True)
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")

        # Update fields
        for field, value in update_data.items():
            setattr(db_book, field, value)

        db.commit()
        db.refresh(db_book)

        return db_book

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating book: {str(e)}")
