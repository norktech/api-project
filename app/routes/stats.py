from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Book
from app.schemas import StatsResponse
from app.auth import verify_token
from loguru import logger

router = APIRouter(prefix="/stats", tags=["Statistics"])

@router.get("", response_model=StatsResponse)
def get_stats(
    db: Session = Depends(get_db),
    user: str = Depends(verify_token)
):
    logger.info(f"User {user} fetching stats")
    books = db.query(Book).all()
    if not books:
        raise HTTPException(status_code=404, detail="No data available")
    prices = [b.price for b in books]
    return {
        "total_books": len(books),
        "average_price": round(sum(prices) / len(prices), 2),
        "min_price": min(prices),
        "max_price": max(prices),
        "last_scraped": max(b.scraped_at for b in books)
    }