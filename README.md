# PolicyLens AI

AI-powered Insurance Policy Document Simplification Tool.

## Problem

Insurance policies are long, complex and filled with legal language. PolicyLens converts that content into plain-language explanations while preserving important facts such as amounts, dates, waiting periods, exclusions and conditions.

## Architecture

Browser (React + Vite + Tailwind)
        |
      Axios
        |
FastAPI :8000
        |
        +-- PyMuPDF extraction + cleaning
        +-- page-aware chunking
        +-- Gemini / OpenAI structured AI
        +-- readability analysis
        +-- critical number/date validation
        +-- in-memory document store

## MVP features

- PDF upload
- Page-aware text extraction
- AI policy simplification
- Structured key-fact extraction
- Coverage
- Exclusions
- Conditions
- Original vs simplified clauses
- Readability before/after
- Critical number/date consistency validation
- Grounded policy Q&A with page references
- No database required

## 1. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Windows:

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Set an API key in `backend/.env`.

Then:

```bash
uvicorn app.main:app --reload --port 8000
```

## 2. Frontend

Open a new terminal:

```bash
cd frontend
npm install
npm run dev
```

Open:

http://localhost:5173

## 3. API documentation

http://localhost:8000/docs

## 4. Quick demo

Use the included synthetic sample data:

`backend/sample_policy.txt`

To create a PDF for the demo, paste the sample text into a document and export it as PDF, then upload it through the UI.

## Hackathon build order

P0:
1. Upload
2. Extraction
3. Simplification
4. Structured extraction
5. Readability
6. Fact validation
7. Dashboard

P1:
8. Q&A
9. Page references

P2:
10. OCR
11. Embeddings/RAG
12. Multilingual support

Do not add P2 features until the complete P0 flow works.

## Important design decision

The project deliberately does not use MongoDB, LangChain, LangGraph, a vector database, authentication or microservices. This keeps the prototype fast and reliable for a short hackathon.

The Q&A feature uses lightweight keyword retrieval. Embeddings can be introduced later if required.

## AI provider

`AI_PROVIDER=auto` tries Gemini first and falls back to OpenAI.

Gemini uses the current Google GenAI Python SDK and structured JSON output.

OpenAI uses structured JSON schema output.

Never commit `.env` or API keys.
