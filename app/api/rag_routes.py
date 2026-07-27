from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import QueryHistory

from app.rag.rag_service import RAGService

router = APIRouter(
    prefix="/rag",
    tags=["RAG"]
)


@router.post("/ask")
def ask_question(
    question: str,
    session_id: str = "default",
    db: Session = Depends(get_db)
):

    response = RAGService.answer(
        question,
        session_id
    )

    document_name = "Unknown"

    if response["sources"]:
        document_name = response["sources"][0]["document"]

    db.add(
        QueryHistory(
            query=question,
            document_name=document_name,
            query_type="RAG"
        )
    )

    db.commit()

    return response