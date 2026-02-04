from fastapi import APIRouter , HTTPException 
from typing import List
from app.api.deps import user_dependency 
from app.db.session import db_dependency
from app.models.order import Order
from app.models.product import Product
from app.schemas.order import OrderCreate , OrderResponse


router = APIRouter(prefix='/orders' , tags=['Orders']) 

@router.post("/" , response_model= OrderResponse)
async def  place_order( order_in : OrderCreate , db : db_dependency , current_user: user_dependency):

    product = db.query(Product).with_for_update().filter(Product.id == order_in.product_id).first()

    if product is None:
        raise HTTPException(status_code=404 , detail="Product not found")
    
    if product.stock < order_in.quantity :
        raise HTTPException(status_code=400, detail=f"We have just {product.stock}")
    

    total = product.price * order_in.quantity

    product.stock = product.stock - order_in.quantity

    new_order = Order(user_id = current_user.id , total_price = total)

    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    return  {
    "id": new_order.id,
    "total_price": new_order.total_price,
    "status": "Success",
    "remaining_stock": f"{product.stock} items left"
}



@router.get("/me" , response_model= List[OrderResponse])
async def get_my_orders(db : db_dependency , current_user : user_dependency):
    all_my_orders = db.query(Order).filter(Order.user_id == current_user.id).all()
    return all_my_orders
