# AI Research & Knowledge Assistant

## Overview

AI Research & Knowledge Assistant is a production-oriented backend application built using FastAPI, TensorFlow, ChromaDB, and Retrieval-Augmented Generation (RAG). It enables users to upload technical documents, perform semantic search, interact with an AI assistant, summarize and compare documents, and automatically classify uploaded documents using a TensorFlow model.

---

## Features

- PDF Upload
- Automatic Text Extraction
- Intelligent Text Chunking
- Metadata Management
- Semantic Search
- Keyword Search
- Retrieval-Augmented Generation (RAG)
- Conversation Memory
- Document Summarization
- Multi-document Comparison
- TensorFlow Document Classification
- Analytics Dashboard APIs
- Swagger API Documentation

---

## Technology Stack

- Python
- FastAPI
- TensorFlow
- ChromaDB
- Sentence Transformers
- SQLite
- SQLAlchemy
- PyMuPDF
- OpenAI API
- Uvicorn

---

## Project Structure

```
app/
│
├── api/
├── analytics/
├── comparison/
├── database/
├── document_processing/
├── embeddings/
├── memory/
├── ml/
├── rag/
├── search/
├── summary/
├── vectorstore/
│
models/
uploads/
```

---

## Installation

Clone the repository

```bash
git clone https://github.com/yourusername/AI-Research-Knowledge-Assistant.git
```

Move into the project

```bash
cd AI-Research-Knowledge-Assistant
```

Create virtual environment

```bash
python -m venv venv
```

Activate environment

Windows

```bash
venv\Scripts\activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run the application

```bash
uvicorn app.main:app --reload
```

Swagger Documentation

```
http://127.0.0.1:8000/docs
```

---

## API Endpoints

### Documents

- Upload Document
- List Documents
- Delete Document
- Reprocess Document

### Search

- Semantic Search
- Keyword Search

### RAG

- Ask Questions

### Summary

- Executive Summary
- Technical Summary
- Bullet Summary
- Key Takeaways

### Comparison

- Compare Documents

### Analytics

- Document Statistics
- Usage Analytics

---

## TensorFlow Model

Categories

- Artificial Intelligence
- Machine Learning
- Computer Vision
- Natural Language Processing
- Robotics
- Cyber Security
- Cloud Computing

The trained TensorFlow model automatically classifies uploaded documents during the upload process.

---

## Future Improvements

- Authentication
- Docker Deployment
- OCR Support
- Hybrid Search
- Multi-user Support
- Cloud Deployment

---

## Author

Ram Sai Kumar Katta