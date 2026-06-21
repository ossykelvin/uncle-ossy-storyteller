GENRES = [
    "Mystery", "Spy Thriller", "Fantasy", "African Prose", "Folklore", "Romance", "Sci-Fi",
    "Horror", "Historical Fiction", "Literary Fiction", "Drama", "Comedy", "Poetry", "Spoken Word",
    "Memoir", "Non-Fiction", "Essay Collection"
]

STYLE_OPTIONS = {
    "Mystery": ["Agatha Christie", "Arthur Conan Doyle", "Raymond Chandler", "Classic puzzle mystery", "Detective deduction", "Hardboiled noir"],
    "Spy Thriller": ["Ian Fleming", "Len Deighton", "John le Carré", "Glamorous espionage", "Cold War realism", "Modern intelligence thriller"],
    "Fantasy": ["J. R. R. Tolkien", "Brandon Sanderson", "Mercedes Lackey", "George R. R. Martin", "Epic quest fantasy", "Hard magic fantasy", "Political fantasy"],
    "African Prose": ["Chinua Achebe", "Chimamanda Ngozi Adichie", "Wole Soyinka", "Tales by moonlight", "Oral storytelling", "Village realism", "Contemporary African literary fiction"],
    "Spoken Word": ["Rhythmic devotional", "Urban prophetic", "Political spoken word", "Emotional confessional", "Call-and-response performance"],
}

SAFE_STYLE_PROFILES = [
    "Classic puzzle mystery with social clues and elegant misdirection",
    "Hardboiled noir with sharp dialogue and moral ambiguity",
    "Cold War intelligence realism with bureaucracy, secrets, and paranoia",
    "Epic quest fantasy with mythic stakes and immersive worldbuilding",
    "Hard magic fantasy with rules, costs, and clever problem solving",
    "African oral storytelling with proverbs, rhythm, community memory, and folklore",
    "Contemporary African literary realism with family, society, and identity",
    "Rhythmic spoken word with repetition, emotional rise, and performance cadence",
    "Clean modern non-fiction with clear structure and practical insight",
]

def style_instruction(project: dict) -> str:
    return f"""
Use the author-inspired label only as a broad market/navigation label: {project.get('style_label', '')}.
Do not mimic exact living-author wording.
Apply this safe style profile: {project.get('safe_style_profile', '')}.
Custom style notes: {project.get('custom_style', '')}.
""".strip()
