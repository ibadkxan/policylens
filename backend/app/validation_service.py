import re
from collections import Counter

# Captures common currency/number/percentage expressions.
NUMBER_RE = re.compile(
    r"(?:₹|Rs\.?|INR|\$|USD|€|EUR|£|GBP)?\s*"
    r"\d[\d,]*(?:\.\d+)?\s*%?"
)

DATE_RE = re.compile(
    r"\b(?:"
    r"\d{1,2}[/-]\d{1,2}[/-]\d{2,4}"
    r"|"
    r"\d{4}[/-]\d{1,2}[/-]\d{1,2}"
    r"|"
    r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*"
    r"\s+\d{1,2},?\s+\d{4}"
    r")\b",
    flags=re.I,
)


def _tokens(pattern, text: str) -> list[str]:
    return [match.group(0).strip() for match in pattern.finditer(text)]


def validate_critical_facts(original: str, simplified: str) -> dict:
    original_numbers = _tokens(NUMBER_RE, original)
    simplified_numbers = _tokens(NUMBER_RE, simplified)

    original_dates = _tokens(DATE_RE, original)
    simplified_dates = _tokens(DATE_RE, simplified)

    original_counter = Counter(original_numbers)
    simplified_counter = Counter(simplified_numbers)

    missing_numbers = []
    for token, count in simplified_counter.items():
        if count > original_counter[token]:
            missing_numbers.extend([token] * (count - original_counter[token]))

    original_date_set = {d.lower() for d in original_dates}
    missing_dates = [
        d for d in simplified_dates
        if d.lower() not in original_date_set
    ]

    total_critical = len(set(original_numbers)) + len(set(original_dates))
    flagged = len(set(missing_numbers)) + len(set(missing_dates))

    preservation = (
        100.0 if total_critical == 0
        else max(0.0, round(100 * (1 - flagged / total_critical), 1))
    )

    return {
        "preservation_pct": preservation,
        "status": "PASS" if flagged == 0 else "REVIEW",
        "original_numbers": sorted(set(original_numbers)),
        "simplified_numbers": sorted(set(simplified_numbers)),
        "original_dates": sorted(set(original_dates)),
        "simplified_dates": sorted(set(simplified_dates)),
        "flagged_numbers": sorted(set(missing_numbers)),
        "flagged_dates": sorted(set(missing_dates)),
        "note": (
            "This is a heuristic consistency check, not a guarantee that "
            "the AI interpretation is legally correct."
        ),
    }
