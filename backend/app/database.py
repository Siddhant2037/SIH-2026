import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
DB=os.getenv("DATABASE_URL","sqlite:///./tracex.db")
engine=create_engine(DB,connect_args={"check_same_thread":False} if DB.startswith("sqlite") else {})
SessionLocal=sessionmaker(bind=engine,autocommit=False,autoflush=False)
Base=declarative_base()
def get_db():
    db=SessionLocal()
    try: yield db
    finally: db.close()
