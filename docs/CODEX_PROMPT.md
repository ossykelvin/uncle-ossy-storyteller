# Codex Prompt — Uncle Ossy StoryTeller

You are continuing the build of **Uncle Ossy StoryTeller**, a Streamlit-first personal writing assistant.

## Product direction

Build a personal writing studio and project dashboard where a user can create poems, spoken word pieces, short stories, novels, and non-fiction books. The first build uses local login and local JSON storage. OpenRouter is the default AI provider, Gemini is the fallback, and providers/models are selectable in Settings. All keys, paths, model names, theme values, and runtime parameters must be stored in `.env.local`; do not hardcode configurable values.

## Must preserve

- Streamlit first
- Local login
- Local project storage
- KOP blue theme with modern writing studio UI
- OpenRouter default, Gemini fallback
- Separate models for outline, writing, editing, research, continuity, QA, marketing, and export
- User-defined chapter count
- Full outline + user input workflow
- Chapter approval before next chapter
- Rewrite chapter in different tone
- Author-inspired labels plus safe style profiles
- Custom style profiles
- Editable Story Bible
- Auto chapter summary
- Continuity/contradiction warnings
- Exports: MD, PDF, DOCX, EPUB, HTML
- Book cover prompt and back-cover blurb
- Future compatibility with Supabase, Vercel, and React Native mobile

## Immediate engineering tasks

1. Review the whole codebase for correctness and missing imports.
2. Improve the Streamlit UI without changing the product direction.
3. Make the AI responses parse cleanly where JSON is expected, but gracefully support prose fallbacks.
4. Improve local login security while keeping local-only MVP simplicity.
5. Add robust error handling for missing API keys and failed provider calls.
6. Ensure exports work even when optional packages have edge-case issues.
7. Add tests or lightweight validation scripts where practical.
8. Keep credit/token usage efficient.

## Rule

Do not remove any existing feature unless replacing it with a better implementation.
