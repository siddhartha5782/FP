import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///./app.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

class ScanHistory(Base):
    __tablename__ = "scan_history"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    image_path = Column(String)
    findings_json = Column(Text) # JSON string
    chat_log = Column(Text) # JSON string
    heatmaps_json = Column(Text, nullable=True) # JSON string of base64 heatmaps

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
