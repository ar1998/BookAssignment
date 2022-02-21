from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

"""
This files contains the funtion which establishes a connection to the database.
"""

# using embedded sqlite database.
SQLALCHEMY_DATABASE_URL = "sqlite:///./data.db"


engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False},echo=True
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_db_sync():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()