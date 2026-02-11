from pydantic import BaseModel, ConfigDict , Field
from datetime import datetime , timezone
from typing import Optional

class OrderCreate(BaseModel):
    product_id: int
    quantity: int = Field(gt= 0)

class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    total_price: float
    created_at: Optional[datetime] = None
    status: Optional[str] = "Success" 
    remaining_stock: Optional[str] = "N/A"
    
       