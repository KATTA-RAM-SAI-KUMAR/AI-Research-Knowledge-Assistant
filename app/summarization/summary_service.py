import os

from sqlalchemy.orm import Session

from app.database.models import Document
from app.document_processing.pdf_processor import PDFProcessor
from app.llm.ollama_client import OllamaClient


class SummaryService:

    @staticmethod
    def summarize(document_id: int, db: Session):

        document = (
            db.query(Document)
            .filter(Document.id == document_id)
            .first()
        )

        if document is None:
            raise Exception("Document not found.")

        file_path = os.path.join("uploads", document.file_name)

        if not os.path.exists(file_path):
            raise Exception("PDF file not found.")

        pages = PDFProcessor.extract_text(file_path)

        full_text = ""

        for page in pages:
            full_text += page["text"] + "\n"

        # Split into smaller chunks
        chunk_size = 5000
        text_chunks = [
            full_text[i:i + chunk_size]
            for i in range(0, len(full_text), chunk_size)
        ]

        chunk_summaries = []

        for index, chunk in enumerate(text_chunks):

            prompt = f"""
You are an AI Research Assistant.

Summarize the following part of a document.

Keep only the important information.

Document Part:

{chunk}
"""

            summary = OllamaClient.generate(prompt)

            chunk_summaries.append(summary)

        combined_summary = "\n".join(chunk_summaries)

        final_prompt = f"""
You are an AI Research Assistant.

Using the summaries below, generate the final response in EXACTLY this format.

Executive Summary:
<paragraph>

Technical Summary:
<paragraph>

Bullet Point Summary:
- point
- point
- point

Key Takeaways:
- takeaway
- takeaway
- takeaway

Summaries:

{combined_summary}
"""

        final_summary = OllamaClient.generate(final_prompt)

        return {
            "document": document.file_name,
            "summary": final_summary
        }