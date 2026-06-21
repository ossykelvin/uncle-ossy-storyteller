from core.ai_client import generate_text


def create_character(project: dict, brief: str, provider: str | None = None) -> str:
    prompt = f"""
Create a rich character profile for this project.
Project: {project}
Character brief: {brief}
Return name, role, goal, fear, secret, relationships, voice, arc, and visual notes.
"""
    return generate_text(prompt, purpose="writing", provider=provider, temperature=0.65)
