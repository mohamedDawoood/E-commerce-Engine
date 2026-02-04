from fastapi import FastAPI
from app.db.session import engine, Base
from app.api import products as product_router
from app.api import  user as user_router
from app.api import  order as order_router
from fastapi.staticfiles import StaticFiles
from app.models import user as user_models
from app.models import product as product_models 


Base.metadata.create_all(bind=engine)

app = FastAPI(title="E-commerce Engine")
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(product_router.router)
app.include_router(user_router.router)
app.include_router(order_router.router)

@app.get("/")
def root():
    return {"message": "Welcome to the E-commerce Engine API"}