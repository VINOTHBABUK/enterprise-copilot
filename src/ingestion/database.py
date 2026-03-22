from sqlalchemy import create_engine, Column, String, \
    Integer, Float, Text, DateTime, JSON
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/copilot.db")
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
Base = declarative_base()


class Document(Base):
    __tablename__ = "documents"
    id         = Column(Integer, primary_key=True)
    url        = Column(String, unique=True)
    title      = Column(String)
    department = Column(String)
    summary    = Column(Text)
    raw_text   = Column(Text)
    key_facts  = Column(JSON)
    doc_type   = Column(String)
    hash       = Column(String)
    scraped_at = Column(DateTime, default=datetime.utcnow)


class Meeting(Base):
    __tablename__ = "meetings"
    id           = Column(Integer, primary_key=True)
    title        = Column(String)
    date         = Column(DateTime)
    transcript   = Column(Text)
    summary      = Column(Text)
    action_items = Column(JSON)
    decisions    = Column(JSON)
    risk_flags   = Column(JSON)
    created_at   = Column(DateTime, default=datetime.utcnow)


class LLMLog(Base):
    __tablename__ = "llm_logs"
    id          = Column(Integer, primary_key=True)
    user        = Column(String)
    query       = Column(Text)
    tool_called = Column(String)
    model       = Column(String)
    tokens_in   = Column(Integer)
    tokens_out  = Column(Integer)
    latency_ms  = Column(Float)
    cost_usd    = Column(Float)
    eval_score  = Column(Float)
    created_at  = Column(DateTime, default=datetime.utcnow)

class User(Base):
    __tablename__ = "users"
    id            = Column(String, primary_key=True)
    email         = Column(String, unique=True, nullable=False)
    name          = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    role          = Column(String, default="general")
    departments   = Column(JSON, default=["general"])
    is_active     = Column(String, default="true")
    created_at    = Column(DateTime, default=datetime.utcnow)
    last_login    = Column(DateTime, nullable=True)


def init_db():
    os.makedirs("data", exist_ok=True)
    Base.metadata.create_all(engine)
    print("✓ Database initialised at", DATABASE_URL)


if __name__ == "__main__":
    init_db()