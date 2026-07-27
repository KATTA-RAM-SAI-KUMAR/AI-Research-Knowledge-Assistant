import os
import json

from sqlalchemy.orm import Session

from app.database.models import Document
from app.document_processing.pdf_processor import PDFProcessor
from app.llm.ollama_client import OllamaClient


class ComparisonService:

    @staticmethod
    def compare_documents(
        document1_id: int,
        document2_id: int,
        db: Session
    ):

        document1 = (
            db.query(Document)
            .filter(Document.id == document1_id)
            .first()
        )

        document2 = (
            db.query(Document)
            .filter(Document.id == document2_id)
            .first()
        )

        if document1 is None:
            raise Exception("First document not found.")

        if document2 is None:
            raise Exception("Second document not found.")

        file1 = os.path.join("uploads", document1.file_name)
        file2 = os.path.join("uploads", document2.file_name)

        if not os.path.exists(file1):
            raise Exception(f"{document1.file_name} not found.")

        if not os.path.exists(file2):
            raise Exception(f"{document2.file_name} not found.")

        pages1 = PDFProcessor.extract_text(file1)
        pages2 = PDFProcessor.extract_text(file2)

        text1 = "\n".join(page["text"] for page in pages1)
        text2 = "\n".join(page["text"] for page in pages2)

        # Keep prompts small for faster comparison
        text1 = text1[:3000]
        text2 = text2[:3000]

        prompt = f"""
You are an expert AI Research Assistant.

Compare the two documents below.

Return ONLY valid JSON.

Do not write markdown.
Do not write explanations.
Do not use ```json.

Format:

{{
    "similarities":[
        "...",
        "...",
        "..."
    ],
    "differences":[
        "...",
        "...",
        "..."
    ],
    "conclusion":"..."
}}

Document 1

{text1}


Document 2

{text2}
"""

        response = OllamaClient.generate(prompt)

        try:
            comparison = json.loads(response)

        except Exception:

            comparison = {
                "similarities": [],
                "differences": [],
                "conclusion": response
            }

        return {
            "document_1": document1.file_name,
            "document_2": document2.file_name,
            "comparison": comparison
        }