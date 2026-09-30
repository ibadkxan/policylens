import json
import os

from dotenv import load_dotenv

from app.prompts import (
    SIMPLIFY_SYSTEM,
    EXTRACT_SYSTEM,
    QA_SYSTEM,
    SIMPLIFY_SCHEMA,
    EXTRACT_SCHEMA,
    QA_SCHEMA,
)

load_dotenv()

PROVIDER = os.getenv("AI_PROVIDER", "groq").lower()

GROQ_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

GEMINI_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")


def _make_groq_strict(schema):
    """
    Groq strict JSON schemas require additionalProperties=False
    on every object in the schema.
    """
    if isinstance(schema, dict):
        result = {}

        for key, value in schema.items():
            result[key] = _make_groq_strict(value)

        if result.get("type") == "object":
            result["additionalProperties"] = False

        return result

    if isinstance(schema, list):
        return [_make_groq_strict(item) for item in schema]

    return schema


def _provider_order():
    if PROVIDER == "groq":
        return ["groq"]

    if PROVIDER == "gemini":
        return ["gemini"]

    order = []

    if GEMINI_KEY:
        order.append("gemini")

    if GROQ_KEY:
        order.append("groq")

    return order


def _groq_json(system: str, user: str, schema: dict, name: str) -> dict:

    from openai import OpenAI

    if not GROQ_KEY:
        raise RuntimeError("GROQ_API_KEY is not configured.")

    client = OpenAI(
        api_key=GROQ_KEY,
        base_url="https://api.groq.com/openai/v1",
    )

    groq_schema = _make_groq_strict(schema)

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        temperature=0.1,
        messages=[
            {
                "role": "system",
                "content": system,
            },
            {
                "role": "user",
                "content": user,
            },
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": name,
                "strict": True,
                "schema": groq_schema,
            },
        },
    )

    content = response.choices[0].message.content

    if not content:
        raise RuntimeError("Groq returned an empty response.")

    return json.loads(content)


def _gemini_json(system: str, user: str, schema: dict) -> dict:

    from google import genai
    from google.genai import types

    if not GEMINI_KEY:
        raise RuntimeError("GEMINI_API_KEY is not configured.")

    client = genai.Client(api_key=GEMINI_KEY)

    prompt = f"{system}\n\nUSER INPUT:\n{user}"

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.1,
            response_mime_type="application/json",
            response_schema=schema,
        ),
    )

    if not response.text:
        raise RuntimeError("Gemini returned an empty response.")

    return json.loads(response.text)


def _call_json(system: str, user: str, schema: dict, name: str) -> dict:

    errors = []

    for provider in _provider_order():

        try:
            if provider == "groq":
                return _groq_json(
                    system,
                    user,
                    schema,
                    name,
                )

            if provider == "gemini":
                return _gemini_json(
                    system,
                    user,
                    schema,
                )

        except Exception as exc:
            errors.append(f"{provider}: {exc}")

    if not _provider_order():
        raise RuntimeError(
            "No AI provider configured. "
            "Set GROQ_API_KEY or GEMINI_API_KEY in .env."
        )

    raise RuntimeError(
        "AI provider failed. " + " | ".join(errors)
    )


def simplify(text: str) -> dict:
    return _call_json(
        SIMPLIFY_SYSTEM,
        text,
        SIMPLIFY_SCHEMA,
        "policy_simplification",
    )


def extract(text: str) -> dict:
    return _call_json(
        EXTRACT_SYSTEM,
        text,
        EXTRACT_SCHEMA,
        "policy_extraction",
    )


def answer_question(question: str, chunks: list[dict]) -> dict:

    stopwords = {
        "the",
        "a",
        "an",
        "of",
        "is",
        "to",
        "and",
        "in",
        "for",
        "what",
        "does",
        "do",
        "my",
        "this",
        "that",
        "are",
        "how",
        "can",
        "i",
        "on",
        "with",
        "be",
        "it",
    }

    q_terms = {
        token.strip(".,?!:;()[]{}").lower()
        for token in question.split()
        if token.strip(".,?!:;()[]{}").lower() not in stopwords
    }

    def score(chunk):
        words = {
            token.strip(".,?!:;()[]{}").lower()
            for token in chunk["text"].split()
        }

        return len(q_terms & words)

    ranked = sorted(
        chunks,
        key=score,
        reverse=True,
    )

    top = [
        c for c in ranked[:6]
        if score(c) > 0
    ]

    if not top:
        top = chunks[:4]

    context = "\n\n".join(
        f"[Page {c['page']}]\n{c['text']}"
        for c in top
    )

    user = (
        f"POLICY EXCERPTS:\n{context}\n\n"
        f"QUESTION:\n{question}"
    )

    return _call_json(
        QA_SYSTEM,
        user,
        QA_SCHEMA,
        "policy_answer",
    )


def provider_status() -> dict:

    return {
        "provider_mode": PROVIDER,
        "groq_configured": bool(GROQ_KEY),
        "gemini_configured": bool(GEMINI_KEY),
        "groq_model": GROQ_MODEL,
        "gemini_model": GEMINI_MODEL,
    }