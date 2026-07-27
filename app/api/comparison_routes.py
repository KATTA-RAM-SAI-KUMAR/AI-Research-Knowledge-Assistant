from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.comparison.comparison_service import ComparisonService
from app.schemas.comparison_schema import ComparisonRequest

router = APIRouter(
    prefix="/compare",
    tags=["Document Comparison"]
)


@router.post("/")
def compare_documents(
    request: ComparisonRequest,
    db: Session = Depends(get_db)
):

    try:

        return ComparisonService.compare_documents(
            document1_id=request.document1_id,
            document2_id=request.document2_id,
            db=db
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )