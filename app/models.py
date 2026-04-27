from sqlalchemy import Column, Integer, String, Float
from app.database import Base

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    price = Column(Float)
    rating = Column(String)
    category = Column(String)
    scraped_at = Column(String)