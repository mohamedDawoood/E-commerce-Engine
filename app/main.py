import os
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.db.session import engine, Base
from app.api import products as product_router
from app.api import user as user_router
from app.api import order as order_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="E-commerce Engine")

BASE_DIR = Path(__file__).resolve().parent.parent

static_path = BASE_DIR / "static"
if not static_path.exists():
    static_path = Path("static")

templates_path = BASE_DIR / "templates"
if not templates_path.exists():
    templates_path = Path("templates")

if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")
else:
    print(f"⚠️ Warning: Static folder not found at {static_path.absolute()}")

templates = Jinja2Templates(directory=str(templates_path))

app.include_router(product_router.router)
app.include_router(user_router.router)
app.include_router(order_router.router)

@app.get("/")
def test(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})