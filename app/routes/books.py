from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models import Book
from app.schemas import BookResponse, BookListResponse
from app.auth import verify_token
from loguru import logger

router = APIRouter(prefix="/books", tags=["Books"])

@router.get("", response_model=BookListResponse)
def list_books(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    min_price: Optional[float] = Query(None, description="Minimum price filter"),
    max_price: Optional[float] = Query(None, description="Maximum price filter"),
    rating: Optional[str] = Query(None, description="Filter by rating"),
    db: Session = Depends(get_db),
    user: str = Depends(verify_token)
):
    logger.info(f"User {user} listing books - page {page}")
    query = db.query(Book)
    if min_price: query = query.filter(Book.price >= min_price)
    if max_price: query = query.filter(Book.price <= max_price)
    if rating: query = query.filter(Book.rating == rating)
    total = query.count()
    books = query.offset((page - 1) * limit).limit(limit).all()
    return {
        "page": page,
        "limit": limit,
        "total": total,
        "pages": (total + limit - 1) // limit,
        "books": books
    }

@router.get("/search/{title}", response_model=list[BookResponse])
def search_book(
    title: str,
    db: Session = Depends(get_db),
    user: str = Depends(verify_token)
):
    logger.info(f"User {user} searching for: {title}")
    books = db.query(Book).filter(Book.title.ilike(f"%{title}%")).all()
    if not books:
        raise HTTPException(status_code=404, detail="No books found")
    return books

@router.get("/{book_id}", response_model=BookResponse)
def get_book(
    book_id: int,
    db: Session = Depends(get_db),
    user: str = Depends(verify_token)
):
    logger.info(f"User {user} fetching book id: {book_id}")
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book