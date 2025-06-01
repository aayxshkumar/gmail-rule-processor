import os
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')

engine = create_engine(
  DATABASE_URL,
  echo=True,        # ← enable SQL logging
  future=True
)
SessionLocal = sessionmaker(bind=engine, autoflush=False)
Base = declarative_base()

def init_db():
    Base.metadata.create_all(engine)

class Email(Base):
    __tablename__ = 'emails'
    id             = Column(Integer, primary_key=True, index=True)
    message_id     = Column(String, unique=True, nullable=False)
    thread_id      = Column(String)
    sender         = Column(String)
    recipients     = Column(ARRAY(String), nullable=False)      # list of addresses
    subject        = Column(String)
    snippet        = Column(Text)
    body           = Column(Text)
    date_received  = Column(DateTime)
    is_read        = Column(Boolean)
    labels         = Column(ARRAY(String), nullable=False)      # list of label‐ids