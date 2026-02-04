from fastapi import Depends , APIRouter , status , HTTPException , Path
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from typing import List
from app.db.session import db_dependency
from app.core.security import get_password_hash , authinticate_user ,is_admin
from app.core.security import create_access_token , verify_password
from fastapi.security import OAuth2PasswordRequestForm
from app.api.deps import user_dependency, admin_user


router = APIRouter(prefix="/users" , tags=["Users"] )




@router.get("/admin" , 
            response_model=List[UserResponse],
            status_code= status.HTTP_200_OK)
async def read_all_user(db : db_dependency , current_user : admin_user):
    return db.query(User).all()
     

@router.delete("/admin_delete_user/{user_id}")
async def delete_user( 
                    db : db_dependency ,
                    current_user : admin_user ,
                    user_id : int = Path(gt=0) ):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None :
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , detail="Not found , Boss")
    if user.id == current_user.id:
        raise HTTPException(status_code=400 ,  detail="You can't delete your self , BOSS")
    db.delete(user)
    db.commit()
    return {"message" : f"User {user.username} has been deleted , BOSS"}

    



@router.post("/signup" , response_model=UserResponse , status_code=status.HTTP_201_CREATED)
async def signup(user_in : UserCreate , db : db_dependency):
    hashed_pwd = get_password_hash(user_in.password)

    new_user = User(
        username =user_in.username,
        email = user_in.email ,
        first_name = user_in.first_name,
        last_name = user_in.last_name,
        hashed_password = hashed_pwd ,
        role ="user"

    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user





@router.post("/login")
async def login(db: db_dependency, form_data: OAuth2PasswordRequestForm = Depends()):

    user = authinticate_user(form_data.username , form_data.password, db)


    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Wrong username or password"
        )
    
    token = create_access_token(data={"sub": user.username})
    
    return {"access_token": token, "token_type": "bearer"}







@router.get("/{user_id}" , response_model=UserResponse )
async def read_user( db : db_dependency , 
                    user_id : int = Path(gt=0),):
    get_user = db.query(User).filter(User.id == user_id).first()

    if not get_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return get_user


@router.get("/" , response_model=List[UserResponse] )
async def read_user(db : db_dependency):
    get_users = db.query(User).all()
    return get_users


@router.put("/{user_id}")
async def update_user(
                    user_update: UserCreate,
                    db: db_dependency,
                    current_user: user_dependency ,
                    user_id: int =Path(gt=0),):
    
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="You can only update your own profile")


    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.username = user_update.username
    user.email = user_update.email
    user.first_name = user_update.first_name
    user.last_name = user_update.last_name
    user.hashed_password = get_password_hash(user_update.password) 
    #add phone number update
    user.phone_number = user_update.phone_number

    db.commit()
    db.refresh(user)
    
    return {"message": f"The user {user.username} has been updated"}


@router.delete("/{user_id}")
async def delete_user( db :db_dependency ,
                       current_user: user_dependency ,
                       user_id : int = Path(gt=0),):
    

    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="u dont have access to delete this user")
                      
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return{"messege" : f"The user has beem deleted"}

    




