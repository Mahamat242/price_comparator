from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from sqlalchemy import func 
from backend.app.db.database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    price = Column(Float, nullable=False)
    currency = Column(String, default="FCFA")
    source = Column(String, nullable=False, index=True)
    product_url = Column(String, unique=True, nullable=False)
    image_url = Column(String, nullable=True)
    metadata_info = Column(JSON, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())