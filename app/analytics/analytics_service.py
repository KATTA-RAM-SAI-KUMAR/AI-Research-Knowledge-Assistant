from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database.models import Document, QueryHistory


class AnalyticsService:

    @staticmethod
    def get_dashboard(db: Session):

        total_documents = db.query(Document).count()

        processed_documents = (
            db.query(Document)
            .filter(Document.processing_status == "PROCESSED")
            .count()
        )

        pending_documents = (
            db.query(Document)
            .filter(Document.processing_status == "PENDING")
            .count()
        )

        total_pages = (
            db.query(
                func.coalesce(func.sum(Document.total_pages), 0)
            ).scalar()
        )

        total_chunks = (
            db.query(
                func.coalesce(func.sum(Document.total_chunks), 0)
            ).scalar()
        )

        average_chunks = round(
            total_chunks / total_documents,
            2
        ) if total_documents else 0

        category_data = (
            db.query(
                Document.category,
                func.count(Document.id)
            )
            .group_by(Document.category)
            .all()
        )

        categories = {
            category: count
            for category, count in category_data
        }

        total_embeddings = total_chunks

        total_questions_answered = (
            db.query(QueryHistory).count()
        )

        most_queried = (
            db.query(
                QueryHistory.document_name,
                func.count(QueryHistory.id).label("count")
            )
            .group_by(QueryHistory.document_name)
            .order_by(func.count(QueryHistory.id).desc())
            .limit(5)
            .all()
        )

        return {
            "total_documents": total_documents,
            "processed_documents": processed_documents,
            "pending_documents": pending_documents,
            "total_pages": total_pages,
            "total_chunks": total_chunks,
            "total_embeddings": total_embeddings,
            "average_chunks_per_document": average_chunks,
            "total_questions_answered": total_questions_answered,
            "most_queried_documents": [
                {
                    "document": name,
                    "queries": count
                }
                for name, count in most_queried
            ],
            "categories": categories
        }