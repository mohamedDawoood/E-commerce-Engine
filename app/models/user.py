from sqlalchemy import Column , Integer , String, Boolean
from app.db.session import Base
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "users"

    username = Column(String , index =True)
    id = Column( Integer , primary_key = True , index = True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String , unique=True , index= True)
    hashed_password = Column(String)
    role =Column (String , default="user")
    #add new column 
    phone_number = Column(Integer , nullable= True)
    is_active =Column(Boolean , default=True)

    orders = relationship("Order", back_populates="user")