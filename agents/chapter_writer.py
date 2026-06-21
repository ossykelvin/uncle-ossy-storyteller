from core.ai_client import generate_text
from agents.project_architect import build_project_brief
from agents.genre_style_curator import style_instruction


def write_chapter(project: dict, outline: str, story_bible: dict, chapters: list, chapter_number: int, user_instruction: str = "", provider: str | None = None) -> str:
    previous_summaries = "\n".join([f"Chapter {c.get('chapter_number')}: {c.get('summary','')}" for c in chapters if c.get('summary')])
    target = max(500, int(project.get('target_word_count', 3000)) // max(1, int(project.get('chapter_count', 1))))
    prompt = f"""
Write Chapter/Section {chapter_number} for this project.

{build_project_brief(project)}

Style guidance:
{style_instruction(project)}

Approved outline:
{outline}

Story Bible:
{story_bible}

Previous chapter summaries:
{previous_summaries or 'None yet.'}

User instruction for this chapter:
{user_instruction or 'Follow the outline and maintain continuity.'}

Target length: about {target} words.

Return a polished chapter with a clear title. Do not include analysis before or after the chapter.
"""
    return generate_text(prompt, purpose="writing", provider=provider, temperature=0.75)


def rewrite_chapter(project: dict, chapter_content: str, tone: str, provider: str | None = None) -> str:
    prompt = f"""
Rewrite the chapter below in this tone: {tone}.
Preserve plot facts, continuity, names, and chapter purpose.
Do not introduce contradictions.

Project: {project.get('title')}
Genre: {project.get('genre')}

Chapter:
{chapter_content}
"""
    return generate_text(prompt, purpose="editing", provider=provider, temperature=0.7)
