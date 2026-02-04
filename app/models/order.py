from sqlalchemy import Column , String , Integer , Float , DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base
class Order(Base):
    __tablename__ = "orders"
    id = Column( Integer , primary_key=True , index= True )
    created_at = Column(DateTime , server_default=func.now() )
    total_price =Column (Float , nullable= False)
    user_id =Column (Integer , ForeignKey("users.id") , nullable= False)

    user = relationship("User", back_populates="orders")