# services/formatter.py
# Converts the routed response into plain text (user-facing answer only,
# dev metadata is never included in the plain text version).

def format_answer(result: dict) -> str:
    """
        Extracts the plain answer text from the result dict, or empty string if anser is missing.
    """
    return result.get("answer", "")