from core.ai_client import generate_text
from agents.project_architect import build_project_brief
from agents.genre_style_curator import style_instruction


def generate_outline(project: dict, provider: str | None = None) -> str:
    prompt = f"""
Create a full writing outline for this project.

{build_project_brief(project)}

Style guidance:
{style_instruction(project)}

Return:
1. Logline
2. Back-cover-style short premise
3. Full synopsis
4. Core themes
5. Main characters or key subjects
6. Chapter-by-chapter outline for exactly {project.get('chapter_count')} chapters/sections
7. Major conflict or argument arc
8. Ending direction
9. Notes for continuity
"""
    return generate_text(prompt, purpose="outline", provider=provider, temperature=0.6)
