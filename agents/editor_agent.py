from core.ai_client import generate_text


def edit_text(text: str, mode: str, provider: str | None = None) -> str:
    prompt = f"""
Edit the following writing using this mode: {mode}.
Preserve core meaning and continuity.

TEXT:
{text}
"""
    return generate_text(prompt, purpose="editing", provider=provider, temperature=0.55)
