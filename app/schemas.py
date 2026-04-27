from pydantic import BaseModel, ConfigDict
from typing import Optional, List

class BookBase(BaseModel):
    title: str
    price: float
    rating: str
    category: str
    scraped_at: str

class BookResponse(BookBase):
    model_config = ConfigDict(from_attributes=True)
    id: int

class BookListResponse(BaseModel):
    page: int
    limit: int
    total: int
    pages: int
    books: List[BookResponse]

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class StatsResponse(BaseModel):
    total_books: int
    average_price: float
    min_price: float
    max_price: float
    last_scraped: str

class LoginRequest(BaseModel):
    username: str
    password: str