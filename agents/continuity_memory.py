from core.ai_client import generate_text


def summarize_chapter(project: dict, chapter_number: int, chapter_content: str, provider: str | None = None) -> str:
    prompt = f"""
Summarise Chapter/Section {chapter_number} of {project.get('title')} for continuity memory.
Include: key events, character changes, location changes, timeline notes, objects/clues introduced, unresolved threads, and future setup.
Keep it concise but useful.

Chapter:
{chapter_content}
"""
    return generate_text(prompt, purpose="continuity", provider=provider, temperature=0.3)


def check_contradictions(project: dict, story_bible: dict, chapters: list, proposed_content: str, provider: str | None = None) -> str:
    prompt = f"""
Check this proposed chapter for contradictions against the project memory.
Return either 'No major contradictions found.' or a bullet list of warnings with severity and suggested fix.

Project: {project}
Story Bible: {story_bible}
Approved Chapters: {[{'chapter_number': c.get('chapter_number'), 'summary': c.get('summary')} for c in chapters if c.get('status') == 'approved']}

Proposed Chapter:
{proposed_content}
"""
    return generate_text(prompt, purpose="continuity", provider=provider, temperature=0.2)


def update_story_bible(project: dict, story_bible: dict, chapter_number: int, chapter_summary: str, provider: str | None = None) -> str:
    prompt = f"""
Update the Story Bible JSON below using this new chapter summary.
Preserve existing useful details. Add new characters, locations, plot points, timeline notes, objects, relationships, unresolved threads, glossary items, and chapter summaries.
Return valid JSON only.

Project: {project}
Existing Story Bible JSON: {story_bible}
Chapter {chapter_number} summary: {chapter_summary}
"""
    return generate_text(prompt, purpose="continuity", provider=provider, temperature=0.2)
