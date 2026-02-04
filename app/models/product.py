from sqlalchemy import Column, Integer, String, Float, Boolean , ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base

class Product(Base):
    __tablename__ = "products" 

    id = Column (Integer , primary_key=True , index= True)
    name = Column(String , index = True)
    description = Column (String , nullable= True)
    price = Column (Float)
    stock = Column(Integer , default=0)
    is_active = Column (Boolean , default= True)
    image_url = Column(String)

    owner_id = Column(Integer , ForeignKey("users.id"))
    owner = relationship("User")
    
    
