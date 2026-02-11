from pydantic import BaseModel, ConfigDict, EmailStr

class UserCreate(BaseModel):
    username : str
    first_name : str
    last_name : str 
    email : EmailStr
    password : str
    phone_number : str

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id : int
    username : str
    email : str

    


