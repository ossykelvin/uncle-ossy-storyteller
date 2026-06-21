from core.ai_client import generate_text


def qa_project(project: dict, outline: str, story_bible: dict, chapters: list, provider: str | None = None) -> str:
    prompt = f"""
Act as a senior story QA reviewer. Review this project for plot holes, weak motivations, repetition, timeline errors, unresolved threads, pacing issues, genre mismatch, and continuity problems.
Provide a practical report with severity ratings and fixes.

Project: {project}
Outline: {outline}
Story Bible: {story_bible}
Chapters: {[{'chapter_number': c.get('chapter_number'), 'title': c.get('title'), 'summary': c.get('summary'), 'status': c.get('status')} for c in chapters]}
"""
    return generate_text(prompt, purpose="qa", provider=provider, temperature=0.35)
