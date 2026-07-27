from pydantic import BaseModel
from datetime import datetime


class DocumentResponse(BaseModel):
    id: int
    file_name: str
    upload_timestamp: datetime
    total_pages: int
    total_chunks: int
    processing_status: str
    category: str

    class Config:
        from_attributes = True