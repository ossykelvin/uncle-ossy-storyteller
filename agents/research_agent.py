from core.ai_client import generate_text


def research_brief(topic: str, project: dict, provider: str | None = None) -> str:
    prompt = f"""
Prepare a concise research brief for a writing project.
Topic: {topic}
Project: {project}
Include factual context, risks of inaccuracy, useful details for scenes/chapters, and questions the writer should verify with external sources.
"""
    return generate_text(prompt, purpose="research", provider=provider, temperature=0.35)
