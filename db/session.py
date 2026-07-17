import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.models import Base

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///local_dev.db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


def init_db():
    Base.metadata.create_all(engine)


def get_session():
    return SessionLocal()