from fastapi import Depends, APIRouter, status, HTTPException, Path, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordRequestForm
from typing import List
import os

from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.db.session import db_dependency
from app.core.security import (
    get_password_hash, 
    authinticate_user, 
    create_access_token, 
    verify_password
)
from app.api.deps import user_dependency, admin_user
from app.core.email import send_verification_email

# إعدادات المسارات والـ Templates
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

router = APIRouter(prefix="/users", tags=["Users"])

# ==========================
# 1. Page Routes (HTML)
# ==========================

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

@router.get("/forgot-password", response_class=HTMLResponse)
async def forgot_password_page(request: Request):
    return templates.TemplateResponse("forgot_password.html", {"request": request})

@router.get("/view-products", response_class=HTMLResponse)
async def products_page(request: Request):
    return templates.TemplateResponse("products.html", {"request": request})

@router.get("/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})

@router.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request):
    return templates.TemplateResponse("profile.html", {"request": request})

# ==========================
# 2. Authentication Logic
# ==========================

@router.post("/token")
@router.post("/login")
async def login(db: db_dependency, form_data: OAuth2PasswordRequestForm = Depends()):
    user = authinticate_user(form_data.username, form_data.password, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Wrong username or password"
        )
    
    token_data = {
        "sub": user.username,
        "id": user.id,
        "role": user.role
    }
    
    token = create_access_token(data=token_data)
    
    return {
        "access_token": token, 
        "token_type": "bearer",
        "role": user.role 
    }

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(user_in: UserCreate, db: db_dependency):
    hashed_pwd = get_password_hash(user_in.password)
    new_user = User(
        username=user_in.username,
        email=user_in.email,
        first_name=user_in.first_name,
        last_name=user_in.last_name,
        hashed_password=hashed_pwd,
        role="user"  # القيمة الافتراضية
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# ==========================
# 3. Admin Operations
# ==========================

@router.get("/admin", response_model=List[UserResponse])
async def read_all_user(db: db_dependency, current_user: admin_user):
    return db.query(User).all()

@router.delete("/admin_delete_user/{user_id}")
async def delete_user_admin(db: db_dependency, current_user: admin_user, user_id: int = Path(gt=0)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="You can't delete yourself")
    db.delete(user)
    db.commit()
    return {"message": f"User {user.username} deleted by Admin"}

# ==========================
# 4. Password & OTP Logic
# ==========================

@router.post("/forgot-password")
async def forgot_password_logic(email: str, db: db_dependency):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Email not found")
    otp = await send_verification_email(user.email)
    user.otp_code = otp 
    db.commit()
    return {"message": "Reset code sent to your email"}

@router.post("/reset-password")
async def reset_password_logic(email: str, otp: str, new_password: str, db: db_dependency):
    user = db.query(User).filter(User.email == email).first()
    if not user or user.otp_code != otp:
        raise HTTPException(status_code=400, detail="Invalid code or email")
    user.hashed_password = get_password_hash(new_password) 
    user.otp_code = None 
    db.commit()
    return {"message": "Password updated successfully"}

@router.post("/send-otp")
async def request_otp(db: db_dependency, current_user: user_dependency):
    otp = await send_verification_email(current_user.email)
    user = db.query(User).filter(User.id == current_user.id).first()
    user.otp_code = otp
    db.commit()
    return {"message": "Verification code sent to your email"}

@router.post("/verify-otp")
async def verify_otp(otp_input: str, db: db_dependency, current_user: user_dependency):
    user = db.query(User).filter(User.id == current_user.id).first()
    if user.otp_code == otp_input:
        user.is_verified = True
        user.otp_code = None
        db.commit()
        return {"message": "Account verified successfully!"}
    raise HTTPException(status_code=400, detail="Invalid verification code")

# ==========================
# 5. User Profile Operations
# ==========================

@router.get("/", response_model=List[UserResponse])
async def read_users(db: db_dependency):
    return db.query(User).all()

@router.get("/{user_id}", response_model=UserResponse)
async def read_user(db: db_dependency, user_id: int = Path(gt=0)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}")
async def update_user(user_update: UserCreate, db: db_dependency, current_user: user_dependency, user_id: int = Path(gt=0)):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    user = db.query(User).filter(User.id == user_id).first()
    user.username = user_update.username
    user.email = user_update.email
    user.first_name = user_update.first_name
    user.last_name = user_update.last_name
    user.hashed_password = get_password_hash(user_update.password)
    db.commit()
    return {"message": "Profile updated"}

@router.delete("/{user_id}")
async def self_delete_user(db: db_dependency, current_user: user_dependency, user_id: int = Path(gt=0)):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    user = db.query(User).filter(User.id == user_id).first()
    db.delete(user)
    db.commit()
    return {"message": "Your account has been deleted"}