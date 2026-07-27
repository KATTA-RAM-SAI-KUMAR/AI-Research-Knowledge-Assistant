from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String

from app.database.database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)

    file_name = Column(String, nullable=False)

    upload_timestamp = Column(DateTime, default=datetime.utcnow)

    total_pages = Column(Integer, default=0)

    total_chunks = Column(Integer, default=0)

    processing_status = Column(String, default="PENDING")

    category = Column(String, default="Unknown")


class QueryHistory(Base):
    __tablename__ = "query_history"

    id = Column(Integer, primary_key=True, index=True)

    query = Column(String)

    document_name = Column(String)

    query_type = Column(String)

    timestamp = Column(DateTime, default=datetime.utcnow)