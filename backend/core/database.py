import os
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.sql import func
from core.config import BASE_DIR

DB_PATH = os.path.join(BASE_DIR, "file_index.db")
engine = create_engine(f"sqlite:///{DB_PATH}")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class FileRecord(Base):
    __tablename__ = "files"
    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(String, unique=True, index=True)  # Google Drive ID or generated ID
    file_name = Column(String)
    file_hash = Column(String, index=True)
    category = Column(String)
    tags = Column(String) # Stored as comma-separated
    original_path = Column(String)
    current_path = Column(String)
    is_duplicate = Column(Boolean, default=False)
    duplicate_of = Column(String, nullable=True) # ID of original file
    is_archived = Column(Boolean, default=False)
    processed_at = Column(DateTime(timezone=True), server_default=func.now())

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
