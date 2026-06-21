# UI/UX Improvement Plan

Phased from the UI/UX review (2026-06-21). These are labelled **UI-A … UI-F** to keep
them distinct from the build Phases 1–5a. All work is contained to `ui/` + `ui/theme.py`
(plus tiny wiring in `app.py`); none of it touches auth, storage, or Supabase, so each
phase ships independently and safely behind the live deploy.

---

## UI-A — Quick wins: legibility & clutter  ·  ✅ DONE
Highest payoff per effort; improves every screen.
- Fix sidebar `* { color: white !important }` so inputs/captions aren't white-on-white — `ui/theme.py:18`
- Show the hero only on Dashboard; slim contextual header elsewhere — `app.py:103`
- Move "Project JSON" into an **Advanced** expander — `ui/writing_studio.py:32`
- Replace raw tracebacks (`st.code(str(exc))`) with friendly errors + collapsible details
- Remove dead `.studio-card` / `.metric-card` / `*-box` CSS (or adopt consistently)

**Exit:** every screen legible, no debug surfaces front-and-center, less vertical waste.

## UI-B — Dashboard & navigation  ·  ~half day  ·  🟡
- Replace the `"This is / MVP"` metric with real ones (chapters approved, words written)
- Per-project **progress bar** (approved ÷ total), last-edited, and row actions (open / delete / export)
- Surface current project in the sidebar (switcher / "Currently editing: …")
- Stronger empty state with one primary "Create your first story" CTA

**Exit:** dashboard is a useful control center; projects are deletable from the UI.

## UI-C — Writing Studio flow  ·  ~half day  ·  🟡 (mockup already approved)
- Status **stepper**: Idea → Outline → Drafting → Review → Complete
- Word-count vs target, **read/edit toggle**, larger editor for long prose
- **Unsaved-changes** indicator; consolidate the button sprawl
- Rename tabs to the writer's mental model

**Exit:** writers always know where they are and never silently lose edits.

## UI-D — Story Bible structured editor  ·  ✅ DONE
The biggest leap for non-technical writers.
- Replace raw-JSON `text_area`s with `st.data_editor` grids per section (add/remove rows, typed columns)
- **Validate on save** — surface errors instead of silently discarding bad JSON
- Keep "Raw JSON" as an Advanced tab for power users

**Exit:** the Story Bible is editable without ever seeing JSON.

## UI-E — Forms & onboarding  ·  ~2–3 hrs  ·  🟡
- Group New Project into **Basics / Style / Scope / Your idea** with `help=` tooltips & progressive disclosure
- First-run onboarding nudge or an optional sample/template project

**Exit:** a first-time user can start a project without feeling overwhelmed.

## UI-F — Visual system & accessibility polish  ·  ~2–3 hrs  ·  🟢
- Calmer writing surface (reduce full-page gradient under editors); consistent design tokens/cards
- Responsive export controls (wrap the 5-button row / use selectbox + one button)
- Accessibility: contrast, visible focus states, status not encoded by colour alone

**Exit:** cohesive, accessible, production-grade look.

---

## Recommended sequence
**UI-A → UI-D → UI-C → UI-B → UI-E → UI-F**
(Quick wins for instant lift, then the flagship Story Bible, then the writing flow, then
dashboard, then onboarding, then polish.)

After each phase I restart the app so you can see the change live at http://localhost:8443.
