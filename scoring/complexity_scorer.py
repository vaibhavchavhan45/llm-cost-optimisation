# scoring/complexity_scorer.py
# 9-rule, pure rule-based complexity scoring. No LLM call involved,
# since this decision itself must stay free to preserve the cost savings.

import re

SIMPLE_OVERRIDE_WORDS = ["brief", "one-liner", "one liner", "short", "summarize"]

SIMPLE_QUESTION_STARTS = ["what is", "define", "what's"]

SIMPLE_TASK_KEYWORDS = [
    "convert", "translate", "list", "format", "extract",
    "proofread", "rewrite", "fix", "grammar"
]

COMPLEX_QUESTION_STARTS = ["design", "build", "implement", "architect"]

TECHNICAL_KEYWORDS = [
    "architecture", "algorithm", "database", "distributed", "concurrency",
    "security", "scalability", "migration", "refactor", "optimize", "system"
]

CODE_KEYWORDS = ["write a function", "debug", "fix this code", "regex", "write code"]

VAGUE_KEYWORDS = ["help me with", "thoughts on", "ideas for"]

CONSTRAINT_KEYWORDS = ["edge case", "constraint", "trade-off", "tradeoff", "under load", "considering"]

MULTI_PART_CONNECTORS = [" and ", " also ", " then "]


def check_complexity_score(text: str) -> dict:
    """
        Scores task complexity based on keyword and defined rules.
        Returns the final score and the list of rules that matched. 
    """
    text_lower = text.lower().strip()
    matched_rules = []

    # Rule 1: simple override (send to LIGHT model) skip everything else
    if any(word in text_lower for word in SIMPLE_OVERRIDE_WORDS):
        return {
            "score": 0,
            "matched_rules": ["simple_override"],
        }

    score = 0

    # Rule 2: simple question start
    if any(text_lower.startswith(start) for start in SIMPLE_QUESTION_STARTS):
        score -= 3
        matched_rules.append("simple_question_type")

    # Rule 3: simple task keywords
    if any(k in text_lower for k in SIMPLE_TASK_KEYWORDS):
        score -= 2
        matched_rules.append("simple_task_keyword")

    # Rule 4: complex question start
    if any(text_lower.startswith(start) for start in COMPLEX_QUESTION_STARTS):
        score += 4
        matched_rules.append("complex_question_type")

    # Rule 5: technical keywords
    if any(k in text_lower for k in TECHNICAL_KEYWORDS):
        score += 4
        matched_rules.append("technical_keyword")

    # Rule 6: multi-part detection
    has_connector = any(c in text_lower for c in MULTI_PART_CONNECTORS)
    has_numbered_list = bool(re.search(r"\b[1-9]\.\s", text))
    if has_connector or has_numbered_list:
        score += 3
        matched_rules.append("multi_part_task")

    # Rule 7: code-related detection
    if any(k in text_lower for k in CODE_KEYWORDS):
        score += 3
        matched_rules.append("code_related")

    # Rule 8: vague/open-ended detection
    if any(k in text_lower for k in VAGUE_KEYWORDS):
        score += 2
        matched_rules.append("vague_open_ended")

    # Rule 9: constraint/edge-case detection
    if any(k in text_lower for k in CONSTRAINT_KEYWORDS):
        score += 3
        matched_rules.append("constraint_edge_case")

    # Rule 10 (tie-breaker only): length, applied only if score is borderline
    if 3 <= score <= 5:
        if len(text) > 300:
            score += 1
            matched_rules.append("length_tiebreaker")

    return {
        "score": score,
        "matched_rules": matched_rules,
    }