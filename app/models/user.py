from sqlalchemy import Column , Integer , String, Boolean
from app.db.session import Base


class User(Base):
    __tablename__ = "users"

    username = Column(String , index =True)
    id = Column( Integer , primary_key = True , index = True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String , unique=True , index= True)
    hashed_password = Column(String)
    role =Column (String , default="user")
    is_active =Column(Boolean , default=True)