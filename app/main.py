import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.db.session import engine, Base
from app.api import products as product_router
from app.api import user as user_router
from app.api import order as order_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="E-commerce Engine")

# تحديد مسار المجلد الرئيسي للمشروع (اللي فيه app و templates و static)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ربط المجلدات من المسار الرئيسي بره فولدر app
static_path = os.path.join(BASE_DIR, "static")
templates_path = os.path.join(BASE_DIR, "templates")

# التأكد من وجود المجلدات قبل الـ Mount
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")
else:
    print(f"Error: Static folder not found at {static_path}")

templates = Jinja2Templates(directory=templates_path)

app.include_router(product_router.router)
app.include_router(user_router.router)
app.include_router(order_router.router)

@app.get("/")
def test(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})