import re
import textstat

LEGAL_WORDS = [
    "notwithstanding", "heretofore", "hereinafter", "aforementioned",
    "theretofore", "whereas", "hereunder", "thereof", "therewith",
    "indemnify", "indemnification", "admissible", "pursuant",
    "provisions", "stipulated", "undertaking", "liability"
]


def readability(text: str) -> dict:
    if not text.strip():
        return {
            "flesch_reading_ease": 0,
            "grade_level": 0,
            "word_count": 0,
            "sentences": 0,
            "avg_sentence_length": 0,
            "long_sentence_ratio": 0,
            "legalese_density": 0,
            "verdict": "No text",
        }

    try:
        ease = float(textstat.flesch_reading_ease(text))
        grade = float(textstat.flesch_kincaid_grade(text))
    except Exception:
        ease = 0.0
        grade = 0.0

    sentences = [
        s.strip()
        for s in re.split(r"[.!?]+", text)
        if s.strip()
    ]
    words = text.split()
    word_count = len(words)

    long_sentences = sum(
        1 for sentence in sentences if len(sentence.split()) > 30
    )

    lower = text.lower()
    legal_hits = sum(lower.count(term) for term in LEGAL_WORDS)

    verdict = (
        "Easy" if ease >= 60
        else "Moderate" if ease >= 40
        else "Difficult"
    )

    return {
        "flesch_reading_ease": round(ease, 1),
        "grade_level": round(grade, 1),
        "word_count": word_count,
        "sentences": len(sentences),
        "avg_sentence_length": round(
            word_count / max(len(sentences), 1), 1
        ),
        "long_sentence_ratio": round(
            long_sentences / max(len(sentences), 1), 3
        ),
        "legalese_density": round(
            legal_hits / max(word_count, 1) * 1000, 2
        ),
        "verdict": verdict,
    }


def compare(before: str, after: str) -> dict:
    before_report = readability(before)
    after_report = readability(after)

    return {
        "before": before_report,
        "after": after_report,
        "reading_ease_delta": round(
            after_report["flesch_reading_ease"]
            - before_report["flesch_reading_ease"], 1
        ),
        "grade_level_delta": round(
            after_report["grade_level"]
            - before_report["grade_level"], 1
        ),
        "legalese_density_delta": round(
            after_report["legalese_density"]
            - before_report["legalese_density"], 2
        ),
        "note": (
            "Flesch-style readability scores are indicative only and "
            "have limitations for legal/insurance language."
        ),
    }
