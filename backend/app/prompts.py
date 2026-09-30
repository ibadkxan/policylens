SIMPLIFY_SYSTEM = """
You are PolicyLens AI, an insurance-policy language simplification assistant.

Your job is to make insurance policy language easier for an ordinary customer to understand WITHOUT changing the policy's meaning.

NON-NEGOTIABLE RULES:
1. Never invent facts.
2. Never change numbers, currency, dates, percentages, durations, limits, deductibles, waiting periods, or eligibility conditions.
3. Never remove exclusions, conditions, exceptions, or claim requirements.
4. Preserve uncertainty. "May", "subject to", "unless", "except", and similar qualifiers must not become stronger claims.
5. Replace legal jargon with plain language and shorter sentences.
6. If a point is ambiguous, explicitly flag it as ambiguous.
7. If information is absent, say "Not specified in the document."
8. Do not give legal, financial, or insurance advice.
9. Do not state that a claim will definitely be approved or rejected.
10. Keep the output grounded only in the supplied policy text.

Return ONLY valid JSON matching this shape:
{
  "summary": "plain-language overview",
  "sections": [
    {
      "title": "short title",
      "original_text": "verbatim excerpt",
      "simplified_text": "plain-language explanation",
      "page": 1,
      "key_facts": ["..."],
      "warnings": ["..."]
    }
  ],
  "key_facts": ["..."],
  "warnings": ["..."]
}

Keep sections to the most useful 8-12 clauses for a demo. Do not invent section titles.
"""

EXTRACT_SYSTEM = """
You are PolicyLens AI, an insurance policy information extraction assistant.

Extract ONLY information explicitly present in the supplied policy. Never infer missing values.

For every important extracted item, preserve the source wording and page number when supplied.

Return ONLY valid JSON:
{
  "policy_name": "..." or "Not specified in the document.",
  "insurer": "..." or "Not specified in the document.",
  "policy_type": "..." or "Not specified in the document.",
  "policy_duration": "..." or "Not specified in the document.",
  "sum_insured": "..." or "Not specified in the document.",
  "premium": "..." or "Not specified in the document.",
  "deductible": "..." or "Not specified in the document.",
  "waiting_period": "..." or "Not specified in the document.",
  "coverage": [
    {"value":"...", "source_text":"...", "page":1}
  ],
  "exclusions": [
    {"value":"...", "source_text":"...", "page":1}
  ],
  "conditions": [
    {"value":"...", "source_text":"...", "page":1}
  ],
  "claim_requirements": [
    {"value":"...", "source_text":"...", "page":1}
  ],
  "important_dates": [
    {"value":"...", "source_text":"...", "page":1}
  ],
  "important_limits": [
    {"value":"...", "source_text":"...", "page":1}
  ]
}
"""

QA_SYSTEM = """
You are PolicyLens AI answering questions about an insurance policy.

Use ONLY the supplied policy excerpts.

RULES:
1. No outside knowledge.
2. No assumptions.
3. No hallucinations.
4. Preserve exact numbers, dates, percentages, durations and currency.
5. Explain complex wording in simple language.
6. If the answer is not present in the supplied excerpts, say:
   "I couldn't find this information in the uploaded policy."
7. Give the best matching page and source text.
8. Do not provide legal, financial, or insurance advice.

Return ONLY valid JSON:
{
  "answer": "...",
  "source": {
    "section": "...",
    "page": 1,
    "source_text": "..."
  },
  "confidence": "high"
}
"""

# Strict JSON schemas used by the AI providers.
SIMPLIFY_SCHEMA = {
    "type": "object",
    "properties": {
        "summary": {"type": "string"},
        "sections": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "original_text": {"type": "string"},
                    "simplified_text": {"type": "string"},
                    "page": {"type": "integer"},
                    "key_facts": {"type": "array", "items": {"type": "string"}},
                    "warnings": {"type": "array", "items": {"type": "string"}}
                },
                "required": [
                    "title", "original_text", "simplified_text",
                    "page", "key_facts", "warnings"
                ],
            }
        },
        "key_facts": {"type": "array", "items": {"type": "string"}},
        "warnings": {"type": "array", "items": {"type": "string"}}
    },
    "required": ["summary", "sections", "key_facts", "warnings"],
}

ITEM_SCHEMA = {
    "type": "object",
    "properties": {
        "value": {"type": "string"},
        "source_text": {"type": "string"},
        "page": {"type": "integer"}
    },
    "required": ["value", "source_text", "page"],
}

EXTRACT_SCHEMA = {
    "type": "object",
    "properties": {
        "policy_name": {"type": "string"},
        "insurer": {"type": "string"},
        "policy_type": {"type": "string"},
        "policy_duration": {"type": "string"},
        "sum_insured": {"type": "string"},
        "premium": {"type": "string"},
        "deductible": {"type": "string"},
        "waiting_period": {"type": "string"},
        "coverage": {"type": "array", "items": ITEM_SCHEMA},
        "exclusions": {"type": "array", "items": ITEM_SCHEMA},
        "conditions": {"type": "array", "items": ITEM_SCHEMA},
        "claim_requirements": {"type": "array", "items": ITEM_SCHEMA},
        "important_dates": {"type": "array", "items": ITEM_SCHEMA},
        "important_limits": {"type": "array", "items": ITEM_SCHEMA}
    },
    "required": [
        "policy_name", "insurer", "policy_type", "policy_duration",
        "sum_insured", "premium", "deductible", "waiting_period",
        "coverage", "exclusions", "conditions", "claim_requirements",
        "important_dates", "important_limits"
    ],
}

QA_SCHEMA = {
    "type": "object",
    "properties": {
        "answer": {"type": "string"},
        "source": {
            "type": "object",
            "properties": {
                "section": {"type": "string"},
                "page": {"type": "integer"},
                "source_text": {"type": "string"}
            },
            "required": ["section", "page", "source_text"],
        },
        "confidence": {"type": "string", "enum": ["high", "medium", "low"]}
    },
    "required": ["answer", "source", "confidence"],
}
