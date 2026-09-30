# PolicyLens AI — Backend

## Quick start

### 1. Create environment

macOS/Linux:

```bash
cd backend
python -m venv venv
source venv/bin/activate
```

Windows:

```powershell
cd backend
python -m venv venv
venv\Scripts\activate
```

### 2. Install

```bash
pip install -r requirements.txt
```

### 3. Configure AI

Copy `.env.example` to `.env`.

For Gemini:

```env
AI_PROVIDER=gemini
GEMINI_API_KEY=your_key
GEMINI_MODEL=gemini-2.5-flash
```

Or OpenAI:

```env
AI_PROVIDER=openai
OPENAI_API_KEY=your_key
OPENAI_MODEL=gpt-4o-mini
```

Or use:

```env
AI_PROVIDER=auto
```

which tries Gemini first when configured, then OpenAI.

### 4. Run

```bash
uvicorn app.main:app --reload --port 8000
```

API:
http://localhost:8000

Swagger:
http://localhost:8000/docs

Health:
http://localhost:8000/health

## Architecture

PDF -> PyMuPDF -> page-aware chunks -> AI extraction/simplification -> readability -> critical-fact validation -> React dashboard.

The document store is an in-memory Python dictionary because this is a hackathon/demo prototype. Restarting the backend clears uploaded documents.

## Notes

- MVP supports text-based PDFs.
- Scanned PDF OCR is intentionally not included in the first build.
- Q&A uses keyword retrieval for speed and simplicity.
- Embeddings/RAG can be added after the core MVP works.
