from .llm import call_groq
from ..utils.token_counter import estimate_tokens_from_messages

SUMMARY_SYSTEM_PROMPT = (
    "Tu es un assistant qui résume des conversations techniques. "
    "Résume de manière concise mais complète l'échange suivant, "
    "en conservant toutes les informations techniques importantes, "
    "les commandes, les erreurs et les solutions mentionnées."
)

async def summarize_messages(messages: list, model: str = "llama-3.1-8b-instant") -> str:
    """Résume une liste de messages en un paragraphe concis."""
    if not messages:
        return ""

    # Formatage des messages pour le résumé
    formatted = "\n".join(
        f"{m.get('role', 'unknown')}: {m.get('content', '')}" for m in messages
    )

    summary_messages = [
        {"role": "system", "content": SUMMARY_SYSTEM_PROMPT},
        {"role": "user", "content": f"Résume cette conversation :\n{formatted}"}
    ]

    try:
        return await call_groq(summary_messages, model=model, max_tokens=500)
    except Exception:
        return "Résumé non disponible."

async def manage_context_window(
    api_messages: list,
    model: str,
    max_tokens: int = 100000
) -> list:
    """
    Vérifie si le contexte dépasse la limite de tokens.
    Si c'est le cas, remplace les messages les plus anciens par un résumé.
    """
    if not api_messages:
        return api_messages

    estimated = estimate_tokens_from_messages(api_messages)
    if estimated <= max_tokens:
        return api_messages

    # On conserve le message système (indice 0) et les deux derniers messages
    system_msg = api_messages[0] if api_messages[0]["role"] == "system" else None
    last_two = api_messages[-2:] if len(api_messages) >= 2 else api_messages

    # Déterminer les messages à résumer
    start_idx = 1 if system_msg else 0
    middle = api_messages[start_idx:-2] if len(api_messages) > 2 else []

    if not middle:
        return api_messages  # Rien à résumer

    summary = await summarize_messages(middle, model)

    # Reconstruction : system + résumé + derniers messages
    new_messages = []
    if system_msg:
        new_messages.append(system_msg)
    new_messages.append({
        "role": "system",
        "content": f"[Résumé de la conversation précédente] {summary}"
    })
    new_messages.extend(last_two)

    return new_messages