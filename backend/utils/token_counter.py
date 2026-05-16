def estimate_tokens_from_text(text: str) -> int:
    """
    Estimation grossière : 1 token ≈ 4 caractères.
    Pour une estimation plus précise, utilisez une bibliothèque comme tiktoken.
    """
    return len(text) // 4

def estimate_tokens_from_messages(messages: list) -> int:
    """Estimation du nombre total de tokens pour une liste de messages."""
    total = 0
    for message in messages:
        content = message.get("content", "")
        total += estimate_tokens_from_text(content)
    return total