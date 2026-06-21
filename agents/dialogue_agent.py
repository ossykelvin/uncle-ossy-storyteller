from core.ai_client import generate_text


def improve_dialogue(scene: str, instruction: str, provider: str | None = None) -> str:
    prompt = f"""
Improve the dialogue in this scene.
Instruction: {instruction}
Make voices distinct, add subtext, remove exposition dumps, and preserve plot facts.

Scene:
{scene}
"""
    return generate_text(prompt, purpose="editing", provider=provider, temperature=0.65)
