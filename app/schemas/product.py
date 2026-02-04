from pydantic import BaseModel
from app.models.product import Product
from typing import Optional

class ProductBase(BaseModel):
    name : str 
    description : Optional[str] = None
    price : float
    stock : int

class ProductCreate(ProductBase):
    pass 

class ProductResponse(ProductBase):
    id: int
    name: str
    price: float
    description: Optional[str] = None
    stock: int
    image_url: Optional[str] = None
    owner_id: Optional[int] = None
    
    class Config:
        from_attributes = True    
    