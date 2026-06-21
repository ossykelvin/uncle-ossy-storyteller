NEXT_ACTIONS = [
    "Create or approve outline",
    "Generate next chapter",
    "Review chapter",
    "Rewrite chapter",
    "Approve chapter",
    "Update Story Bible",
    "Run continuity check",
    "Export manuscript",
]

def next_chapter_number(chapters: list) -> int:
    approved = [c for c in chapters if c.get("status") == "approved"]
    return len(approved) + 1

def can_generate_next(project: dict, chapters: list) -> tuple[bool, str]:
    next_no = next_chapter_number(chapters)
    if next_no > int(project.get("chapter_count", 1)):
        return False, "All planned chapters have been approved."
    drafts = [c for c in chapters if c.get("status") == "draft"]
    if drafts:
        return False, "Approve or rewrite the current draft before generating the next chapter."
    return True, f"Ready to generate Chapter/Section {next_no}."
