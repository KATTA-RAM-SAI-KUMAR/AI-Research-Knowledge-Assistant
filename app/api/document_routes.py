import os
import shutil

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import Document

from app.document_processing.pdf_processor import PDFProcessor
from app.document_processing.chunker import TextChunker

from app.embeddings.embedding_model import EmbeddingModel
from app.vectorstore.chroma_store import ChromaStore

from app.ml.predictor import classifier


router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# -----------------------------------
# Upload PDF
# -----------------------------------
@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed."
        )

    file_path = os.path.join(
        UPLOAD_FOLDER,
        file.filename
    )

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Extract PDF
    pages = PDFProcessor.extract_text(file_path)

    # Create chunks
    chunks = TextChunker.create_chunks(pages)

    # Merge all page text for ML prediction
    full_text = " ".join(
        page["text"] for page in pages
    )

    # Predict category
    predicted_category = classifier.predict(full_text)

    # Save metadata
    document = Document(
        file_name=file.filename,
        total_pages=len(pages),
        total_chunks=len(chunks),
        processing_status="PROCESSED",
        category=predicted_category
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    # Store embeddings
    embedding_model = EmbeddingModel()

    ChromaStore.add_chunks(
        document_id=document.id,
        file_name=document.file_name,
        chunks=chunks,
        embedding_model=embedding_model
    )

    return {
        "message": "Document uploaded successfully",
        "document": {
            "id": document.id,
            "file_name": document.file_name,
            "category": document.category,
            "total_pages": document.total_pages,
            "total_chunks": document.total_chunks,
            "status": document.processing_status
        }
    }


# -----------------------------------
# List Documents
# -----------------------------------
@router.get("/")
def list_documents(
    db: Session = Depends(get_db)
):

    documents = db.query(Document).order_by(
        Document.upload_timestamp.desc()
    ).all()

    return {
        "total_documents": len(documents),
        "documents": [
            {
                "id": doc.id,
                "file_name": doc.file_name,
                "upload_timestamp": doc.upload_timestamp,
                "total_pages": doc.total_pages,
                "total_chunks": doc.total_chunks,
                "processing_status": doc.processing_status,
                "category": doc.category
            }
            for doc in documents
        ]
    }


# -----------------------------------
# Reprocess Document
# -----------------------------------
@router.post("/{document_id}/reprocess")
def reprocess_document(
    document_id: int,
    db: Session = Depends(get_db)
):

    document = db.query(Document).filter(
        Document.id == document_id
    ).first()

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found."
        )

    file_path = os.path.join(
        UPLOAD_FOLDER,
        document.file_name
    )

    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=404,
            detail="PDF file not found."
        )

    pages = PDFProcessor.extract_text(file_path)

    chunks = TextChunker.create_chunks(pages)

    full_text = " ".join(
        page["text"] for page in pages
    )

    predicted_category = classifier.predict(full_text)

    embedding_model = EmbeddingModel()

    # Delete old embeddings
    ChromaStore.delete_document(document.id)

    # Store new embeddings
    ChromaStore.add_chunks(
        document_id=document.id,
        file_name=document.file_name,
        chunks=chunks,
        embedding_model=embedding_model
    )

    # Update metadata
    document.total_pages = len(pages)
    document.total_chunks = len(chunks)
    document.processing_status = "PROCESSED"
    document.category = predicted_category

    db.commit()

    return {
        "message": "Document reprocessed successfully",
        "document": {
            "id": document.id,
            "file_name": document.file_name,
            "category": document.category,
            "total_pages": document.total_pages,
            "total_chunks": document.total_chunks,
            "processing_status": document.processing_status
        }
    }


# -----------------------------------
# Delete Document
# -----------------------------------
@router.delete("/{document_id}")
def delete_document(
    document_id: int,
    db: Session = Depends(get_db)
):

    document = db.query(Document).filter(
        Document.id == document_id
    ).first()

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found."
        )

    file_path = os.path.join(
        UPLOAD_FOLDER,
        document.file_name
    )

    if os.path.exists(file_path):
        os.remove(file_path)

    # Delete embeddings
    ChromaStore.delete_document(document.id)

    db.delete(document)
    db.commit()

    return {
        "message": "Document deleted successfully"
    }