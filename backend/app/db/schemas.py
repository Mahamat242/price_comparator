from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class ProductBase(BaseModel):
    title: str
    price: float
    currency: str = "FCFA"
    source: str
    product_url: str
    image_url: Optional[str] = None
    metadata_info: Optional[Dict[str, Any]] = None

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True