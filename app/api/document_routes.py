import os
import shutil
from typing import Annotated

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
# Upload Multiple PDFs
# -----------------------------------
from fastapi import UploadFile, File

@router.post("/upload")
async def upload_documents(
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db)
):

    uploaded_documents = []
    failed_documents = []

    embedding_model = EmbeddingModel()

    for file in files:

        # Validate extension
        if not file.filename.lower().endswith(".pdf"):
            failed_documents.append(
                {
                    "file_name": file.filename,
                    "reason": "Only PDF files are allowed."
                }
            )
            continue

        # Check duplicate
        existing_document = db.query(Document).filter(
            Document.file_name == file.filename
        ).first()

        if existing_document:
            failed_documents.append(
                {
                    "file_name": file.filename,
                    "reason": "Document already exists."
                }
            )
            continue

        file_path = os.path.join(
            UPLOAD_FOLDER,
            file.filename
        )

        try:

            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            # Extract PDF
            pages = PDFProcessor.extract_text(file_path)

            if not pages or all(
                not page["text"].strip()
                for page in pages
            ):
                raise Exception(
                    "PDF contains no readable text."
                )

            # Create chunks
            chunks = TextChunker.create_chunks(
                pages
            )

            # Merge text
            full_text = " ".join(
                page["text"]
                for page in pages
            )

            # Predict category
            predicted_category = classifier.predict(
                full_text
            )

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
            ChromaStore.add_chunks(
                document_id=document.id,
                file_name=document.file_name,
                chunks=chunks,
                embedding_model=embedding_model
            )

            uploaded_documents.append(
                {
                    "id": document.id,
                    "file_name": document.file_name,
                    "category": document.category,
                    "total_pages": document.total_pages,
                    "total_chunks": document.total_chunks,
                    "status": document.processing_status
                }
            )

        except Exception as e:

            db.rollback()

            if os.path.exists(file_path):
                os.remove(file_path)

            failed_documents.append(
                {
                    "file_name": file.filename,
                    "reason": str(e)
                }
            )

    return {
        "message": "Upload completed.",
        "uploaded_count": len(uploaded_documents),
        "failed_count": len(failed_documents),
        "uploaded_documents": uploaded_documents,
        "failed_documents": failed_documents
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

    try:

        pages = PDFProcessor.extract_text(file_path)

        if not pages or all(
            not page["text"].strip()
            for page in pages
        ):
            raise Exception(
                "PDF contains no readable text."
            )

        chunks = TextChunker.create_chunks(
            pages
        )

        full_text = " ".join(
            page["text"]
            for page in pages
        )

        predicted_category = classifier.predict(
            full_text
        )

        embedding_model = EmbeddingModel()

        # Delete old embeddings
        ChromaStore.delete_document(
            document.id
        )

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
        db.refresh(document)

        return {
            "message": "Document reprocessed successfully.",
            "document": {
                "id": document.id,
                "file_name": document.file_name,
                "category": document.category,
                "total_pages": document.total_pages,
                "total_chunks": document.total_chunks,
                "processing_status": document.processing_status
            }
        }

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Failed to reprocess document: {str(e)}"
        )


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

    try:

        if os.path.exists(file_path):
            os.remove(file_path)

        # Delete embeddings
        ChromaStore.delete_document(
            document.id
        )

        db.delete(document)
        db.commit()

        return {
            "message": "Document deleted successfully."
        }

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete document: {str(e)}"
        )