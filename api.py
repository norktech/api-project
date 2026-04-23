from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session
from jose import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Optional

# ── Configuração ──────────────────────────────────────────────
SECRET_KEY = "norktech-secret-2026"
ALGORITHM = "HS256"
DATABASE_URL = "sqlite:///./books.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
security = HTTPBearer()

app = FastAPI(
    title="NorkTech Books API",
    description="Professional REST API for scraped book data with authentication, pagination and filtering.",
    version="2.0.0",
    contact={"name": "NorkTech", "url": "https://github.com/norktech"}
)

# ── Database ──────────────────────────────────────────────────
class Base(DeclarativeBase):
    pass

class Book(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    price = Column(Float)
    rating = Column(String)
    category = Column(String)
    scraped_at = Column(String)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ── Auth ──────────────────────────────────────────────────────
USERS = {
    "admin": bcrypt.hashpw("norktech123".encode(), bcrypt.gensalt())
}

def hash_password(password: str) -> bytes:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

def verify_password(password: str, hashed: bytes) -> bool:
    return bcrypt.checkpw(password.encode(), hashed)

def create_token(username: str):
    expire = datetime.utcnow() + timedelta(hours=24)
    return jwt.encode({"sub": username, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        return payload["sub"]
    except:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

# ── Endpoints ─────────────────────────────────────────────────
@app.get("/", tags=["General"])
def home():
    return {
        "api": "NorkTech Books API",
        "version": "2.0.0",
        "status": "online",
        "docs": "/docs"
    }

@app.post("/auth/login", tags=["Auth"])
def login(username: str, password: str):
    if username not in USERS or not verify_password(password, USERS[username]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_token(username)
    return {"access_token": token, "token_type": "bearer"}

@app.get("/books", tags=["Books"])
def list_books(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    rating: Optional[str] = None,
    db: Session = Depends(get_db),
    user: str = Depends(verify_token)
):
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
        "books": [{"id": b.id, "title": b.title, "price": b.price, "rating": b.rating, "scraped_at": b.scraped_at} for b in books]
    }

@app.get("/books/search/{title}", tags=["Books"])
def search_book(title: str, db: Session = Depends(get_db), user: str = Depends(verify_token)):
    books = db.query(Book).filter(Book.title.ilike(f"%{title}%")).all()
    if not books:
        raise HTTPException(status_code=404, detail="No books found")
    return {"total": len(books), "books": books}

@app.get("/books/{book_id}", tags=["Books"])
def get_book(book_id: int, db: Session = Depends(get_db), user: str = Depends(verify_token)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@app.get("/stats", tags=["Statistics"])
def stats(db: Session = Depends(get_db), user: str = Depends(verify_token)):
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