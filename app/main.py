from fastapi import FastAPI

from app.database.database import Base, engine

import app.database.models

from app.api.document_routes import router as document_router
from app.api.search_routes import router as search_router
from app.api.rag_routes import router as rag_router
from app.api.summary_routes import router as summary_router
from app.api.comparison_routes import router as comparison_router
from app.api.analytics_routes import router as analytics_router


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Research & Knowledge Assistant",
    version="1.0.0",
    openapi_version="3.0.3"
)

app.include_router(document_router)
app.include_router(search_router)
app.include_router(rag_router)
app.include_router(summary_router)
app.include_router(comparison_router)
app.include_router(analytics_router)


@app.get("/")
def root():
    return {
        "status": "success",
        "message": "AI Research & Knowledge Assistant Running 🚀"
    }