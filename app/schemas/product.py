from pydantic import BaseModel, ConfigDict , Field
from app.models.product import Product
from typing import Optional


class ProductBase(BaseModel):
    name : str = Field(min_length=3 , max_length= 45)
    description : Optional[str] = Field(max_length=100) 
    price : float =Field(gt=-1)
    stock : int = Field(gt=-1)

class ProductCreate(ProductBase):
    pass 

class ProductResponse(ProductBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    image_url: Optional[str] = None
    owner_id: Optional[int] = None

    