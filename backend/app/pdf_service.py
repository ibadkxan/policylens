import os
import re
import uuid
from pathlib import Path

import fitz


def make_doc_id() -> str:
    return uuid.uuid4().hex[:12]


def clean(text: str) -> str:
    text = text.replace("\x00", " ")

    # Common page-number/footer patterns.
    text = re.sub(r"\bPage\s+\d+\s*(?:of\s+\d+)?\b", " ", text, flags=re.I)
    text = re.sub(r"^\s*\d+\s*$", " ", text, flags=re.M)

    # Preserve paragraph boundaries first.
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def extract_pages(pdf_path: str) -> list[dict]:
    pages = []

    with fitz.open(pdf_path) as doc:
        for index, page in enumerate(doc):
            raw = page.get_text("text") or ""
            text = clean(raw)

            if text:
                pages.append({
                    "page": index + 1,
                    "text": text,
                })

    return pages


def chunk_pages(
    pages: list[dict],
    chunk_size: int = 1800,
    overlap: int = 250,
) -> list[dict]:
    chunks = []

    for page in pages:
        text = page["text"]
        start = 0

        while start < len(text):
            end = min(start + chunk_size, len(text))
            piece = text[start:end].strip()

            if piece:
                chunks.append({
                    "page": page["page"],
                    "text": piece,
                })

            if end >= len(text):
                break

            start = end - overlap

    return chunks


def save_upload(upload_dir: str, doc_id: str, content: bytes) -> str:
    Path(upload_dir).mkdir(parents=True, exist_ok=True)
    path = os.path.join(upload_dir, f"{doc_id}.pdf")

    with open(path, "wb") as file:
        file.write(content)

    return path
