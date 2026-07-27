from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.summarization.summary_service import SummaryService

router = APIRouter(
    prefix="/summary",
    tags=["Summary"]
)


@router.post("/{document_id}")
def summarize_document(
    document_id: int,
    db: Session = Depends(get_db)
):

    try:

        return SummaryService.summarize(
            document_id,
            db
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )