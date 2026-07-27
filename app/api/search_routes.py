from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import QueryHistory
from app.vectorstore.search import SemanticSearch
from app.vectorstore.chroma_store import collection

router = APIRouter(
    prefix="/search",
    tags=["Search"]
)


# ---------------------------------------
# Semantic Search
# ---------------------------------------
@router.post("/")
def search_documents(
    query: str,
    db: Session = Depends(get_db)
):

    results = SemanticSearch.search(query)

    response = []

    documents = results["documents"][0]
    metadata = results["metadatas"][0]

    for doc, meta in zip(documents, metadata):

        db.add(
            QueryHistory(
                query=query,
                document_name=meta["file_name"],
                query_type="Semantic Search"
            )
        )

        response.append(
            {
                "document": meta["file_name"],
                "page": meta["page_number"],
                "content": doc
            }
        )

    db.commit()

    return response


# ---------------------------------------
# Keyword Search
# ---------------------------------------
@router.post("/keyword")
def keyword_search(
    query: str,
    db: Session = Depends(get_db)
):

    results = collection.get(
        include=["documents", "metadatas"]
    )

    response = []

    keyword = query.lower()

    for document, metadata in zip(
        results["documents"],
        results["metadatas"]
    ):

        if keyword in document.lower():

            db.add(
                QueryHistory(
                    query=query,
                    document_name=metadata["file_name"],
                    query_type="Keyword Search"
                )
            )

            response.append(
                {
                    "document": metadata["file_name"],
                    "page": metadata["page_number"],
                    "content": document
                }
            )

    db.commit()

    return {
        "total_results": len(response),
        "results": response
    }