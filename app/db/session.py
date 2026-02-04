from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker , declarative_base , Session
from typing import Annotated
from fastapi import Depends

DATABASE_URL = "postgresql+psycopg2://postgres:superdawod@localhost:5432/ecommerce_db"

engine = create_engine( DATABASE_URL )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal() 
    try:
        yield db 
    finally:
        db.close() 

db_dependency = Annotated[Session, Depends(get_db)]
