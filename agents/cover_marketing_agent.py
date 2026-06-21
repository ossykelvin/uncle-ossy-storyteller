from core.ai_client import generate_text


def generate_back_cover(project: dict, outline: str, story_bible: dict, provider: str | None = None) -> str:
    prompt = f"""
Create a compelling back-cover blurb for this project.
Avoid spoilers, but make the hook strong.

Project: {project}
Outline: {outline}
Story Bible: {story_bible}
"""
    return generate_text(prompt, purpose="marketing", provider=provider, temperature=0.65)


def generate_cover_prompt(project: dict, outline: str, story_bible: dict, provider: str | None = None) -> str:
    prompt = f"""
Create a detailed book cover image generation prompt for this project.
Include composition, mood, typography guidance, colour palette, symbolic objects, and genre cues.
Do not generate the image; return only the prompt.

Project: {project}
Outline: {outline}
Story Bible: {story_bible}
"""
    return generate_text(prompt, purpose="marketing", provider=provider, temperature=0.7)
