def build_project_brief(project: dict) -> str:
    return f"""
Project Title: {project.get('title')}
Type: {project.get('project_type')}
Fiction/Non-fiction: {project.get('fiction_type')}
Genre: {project.get('genre')}
Theme: {project.get('theme')}
Author-inspired label: {project.get('style_label')}
Safe style profile: {project.get('safe_style_profile')}
Custom style: {project.get('custom_style')}
Target word count: {project.get('target_word_count')}
Chapter count: {project.get('chapter_count')}
Seed idea: {project.get('seed_prompt')}
""".strip()
