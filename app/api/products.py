from fastapi import Depends, HTTPException, status, APIRouter, Path, Request, File, UploadFile, Form
from app.schemas.product import ProductCreate, ProductResponse
from app.db.session import db_dependency
from app.models.product import Product
from typing import List, Optional
from app.api.deps import user_dependency
import shutil
import os
from sqlalchemy import or_
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates") 

router = APIRouter(prefix="/products", tags=["Products"])

# ==========================================
# 1. Page Routes 
# ==========================================

@router.get("/view", response_class=HTMLResponse)
async def view_products_page(request: Request):
    """فتح صفحة المتجر لليوزر العادي"""
    return templates.TemplateResponse("product.html", {"request": request})

# ==========================================
# 2. CRUD Operations
# ==========================================

import uuid 

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_product(
    db: db_dependency,
    current_user: user_dependency,
    name: str = Form(...),
    price: float = Form(...),
    description: str = Form(None),
    stock: int = Form(0),
    file: UploadFile = File(...)
):
    upload_folder = "static/images"
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
        

    file_extension = os.path.splitext(file.filename)[1] 
    unique_filename = f"{uuid.uuid4()}{file_extension}" 
    file_path = os.path.join(upload_folder, unique_filename)
    

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        

    new_product = Product(
        name=name,
        price=price,
        description=description,
        stock=stock,
        image_url=file_path.replace("\\", "/"), 
        owner_id=current_user.id
    )
    
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    
    return {"message": "Product created successfully", "product": new_product}

@router.get("/", response_model=List[ProductResponse])
async def read_all_products(
    db: db_dependency, 
    skip: int = 0, 
    limit: int = 100, 
    search: Optional[str] = None
):

    query = db.query(Product)
    if search:
        query = query.filter(
            or_(
                Product.name.ilike(f"%{search}%"),
                Product.description.ilike(f"%{search}%")
            )
        )
    return query.offset(skip).limit(limit).all()

@router.get("/{product_id}", response_model=ProductResponse)
async def read_single_product(db: db_dependency, product_id: int = Path(gt=0)):

    product = db.query(Product).filter(Product.id == product_id).first() 
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.get("/user/my-products", response_model=List[ProductResponse])
async def get_my_products(current_user: user_dependency, db: db_dependency):

    products = db.query(Product).filter(Product.owner_id == current_user.id).all()
    return products

@router.put("/{product_id}", status_code=status.HTTP_202_ACCEPTED)
async def update_product(
    product_update: ProductCreate,
    db: db_dependency, 
    current_user: user_dependency,
    product_id: int = Path(gt=0)
):

    db_product = db.query(Product).filter(Product.id == product_id).first()

    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    

    if db_product.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to update")
    
    update_data = product_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_product, key, value)
    
    db.commit()
    db.refresh(db_product)
    return db_product

@router.delete("/{product_id}")
async def delete_product(
    db: db_dependency,
    current_user: user_dependency, 
    product_id: int = Path(gt=0)
):

    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")


    if product.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to delete this product")
    

    if os.path.exists(product.image_url):
        os.remove(product.image_url)

    db.delete(product)
    db.commit()
    
    return {"message": "Product has been successfully deleted"}