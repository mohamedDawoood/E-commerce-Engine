from pydantic import BaseModel , Field
from datetime import datetime , timezone
from typing import Optional

class OrderCreate(BaseModel):
    product_id: int
    quantity: int = Field(gt= 0)

class OrderResponse (BaseModel):
    id : int
    user_id : int
    total_price : float
    created_at : Optional[datetime] = None
    status : str
    remaining_stock : str
    
    class Config:
        from_attributes = True    