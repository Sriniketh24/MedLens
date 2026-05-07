import re

REFUSAL_PATTERNS = [
    r"\bshould i take\b",
    r"\bwhat should i do about my\b",
    r"\bdiagnose me\b",
    r"\bprescribe\b",
    r"\bmy symptoms\b",
    r"\bam i sick\b",
    r"\bdo i have\b",
    r"\btreat my\b",
    r"\bwhat medication\b",
    r"\bshould i see a doctor\b",
]

REFUSAL_MESSAGE = (
    "I cannot provide personal medical advice, diagnosis, or treatment recommendations. "
    "This tool searches published medical literature for research purposes only. "
    "Please consult a qualified healthcare professional for personal health concerns."
)


def check_query_safety(query: str) -> tuple[bool, str | None]:
    """Returns (is_safe, refusal_message). If is_safe=False, return the refusal."""
    query_lower = query.lower().strip()

    for pattern in REFUSAL_PATTERNS:
        if re.search(pattern, query_lower):
            return False, REFUSAL_MESSAGE

    return True, None
