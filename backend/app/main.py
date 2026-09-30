import os
import shutil
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app import ai_service
from app.pdf_service import (
    chunk_pages,
    extract_pages,
    make_doc_id,
    save_upload,
)
from app.readability_service import compare
from app.validation_service import validate_critical_facts

load_dotenv()

app = FastAPI(
    title="PolicyLens AI",
    description="AI-powered insurance policy simplification prototype",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
MAX_ANALYSIS_CHARS = int(os.getenv("MAX_ANALYSIS_CHARS", "50000"))

Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)

# Demo-only in-memory document store.
DOCS: dict[str, dict] = {}


class Question(BaseModel):
    question: str = Field(min_length=2, max_length=1000)


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "documents_loaded": len(DOCS),
        "ai": ai_service.provider_status(),
    }


@app.post("/api/upload")
async def upload(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(400, "A file is required.")

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are supported in the MVP.")

    content = await file.read()

    if not content:
        raise HTTPException(400, "The uploaded file is empty.")

    doc_id = make_doc_id()
    path = save_upload(UPLOAD_DIR, doc_id, content)

    try:
        pages = extract_pages(path)
    except Exception as exc:
        if os.path.exists(path):
            os.remove(path)
        raise HTTPException(400, f"Could not read PDF: {exc}")

    if not pages:
        if os.path.exists(path):
            os.remove(path)
        raise HTTPException(
            400,
            "No extractable text was found. This MVP expects a text-based PDF; OCR can be added later."
        )

    chunks = chunk_pages(pages)

    DOCS[doc_id] = {
        "filename": file.filename,
        "path": path,
        "pages": pages,
        "chunks": chunks,
        "analysis": None,
    }

    return {
        "document_id": doc_id,
        "filename": file.filename,
        "pages": len(pages),
        "chunks": len(chunks),
        "status": "uploaded",
    }


@app.post("/api/analyze/{document_id}")
async def analyze(document_id: str):
    doc = DOCS.get(document_id)

    if not doc:
        raise HTTPException(404, "Document not found.")

    full_text = "\n\n".join(
        f"[Page {p['page']}]\n{p['text']}"
        for p in doc["pages"]
    )

    analysis_text = full_text[:MAX_ANALYSIS_CHARS]

    try:
        extraction = ai_service.extract(analysis_text)
        simplification = ai_service.simplify(analysis_text)
    except Exception as exc:
        raise HTTPException(502, f"AI analysis failed: {exc}")

    simplified_text = simplification.get("summary", "")
    for section in simplification.get("sections", []):
        simplified_text += "\n\n" + section.get("simplified_text", "")

    readability = compare(full_text, simplified_text)
    validation = validate_critical_facts(full_text, simplified_text)

    analysis = {
        "summary": simplification.get("summary", ""),
        "key_facts": simplification.get("key_facts", []),
        "warnings": simplification.get("warnings", []),
        "sections": simplification.get("sections", []),
        "key_details": extraction,
        "readability": readability,
        "validation": validation,
    }

    doc["analysis"] = analysis

    return {
        "document_id": document_id,
        "analysis": analysis,
    }


@app.post("/api/ask/{document_id}")
async def ask(document_id: str, body: Question):
    doc = DOCS.get(document_id)

    if not doc:
        raise HTTPException(404, "Document not found.")

    try:
        return await _ask_sync(doc, body.question)
    except Exception as exc:
        raise HTTPException(502, f"AI Q&A failed: {exc}")


async def _ask_sync(doc: dict, question: str):
    return ai_service.answer_question(question, doc["chunks"])


@app.get("/api/documents/{document_id}")
async def get_document(document_id: str):
    doc = DOCS.get(document_id)

    if not doc:
        raise HTTPException(404, "Document not found.")

    return {
        "document_id": document_id,
        "filename": doc["filename"],
        "pages": len(doc["pages"]),
        "analyzed": bool(doc["analysis"]),
        "analysis": doc["analysis"],
    }


@app.delete("/api/documents/{document_id}")
async def delete_document(document_id: str):
    doc = DOCS.pop(document_id, None)

    if not doc:
        raise HTTPException(404, "Document not found.")

    path = doc.get("path")
    if path and os.path.exists(path):
        os.remove(path)

    return {"status": "deleted"}
