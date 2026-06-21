import json
import requests
from core.config import env, env_bool, DEFAULT_PROVIDER, FALLBACK_PROVIDER, get_model
from core.prompts import SYSTEM_RULES


class AIClientError(Exception):
    pass


def _offline_fallback(prompt: str, purpose: str, errors: list[str]) -> str:
    """Return useful local content instead of crashing when AI is not configured.

    This keeps the Streamlit UI testable on first deployment while the user fixes
    API keys/model names in Streamlit Secrets or .env.local.
    """
    safe_errors = "\n".join(f"- {e}" for e in errors)
    header = (
        "⚠️ AI provider is not available yet, so Uncle Ossy StoryTeller used offline fallback mode.\n\n"
        "Fix this by adding valid API keys and model names in `.env.local` locally, "
        "or in Streamlit Cloud → Manage app → Settings → Secrets.\n\n"
        f"Provider diagnostics:\n{safe_errors}\n\n"
    )

    if purpose == "outline":
        return header + """# Working Outline Draft

## Premise
A compelling story built from the project brief, theme, genre, and selected style profile.

## Main Characters
1. Protagonist — wants something deeply personal and faces internal/external opposition.
2. Opposition Force — blocks the protagonist and raises the stakes.
3. Ally/Mentor — helps reveal the emotional or thematic truth.

## Structure
### Act 1 — Setup
- Introduce the world, central desire, ordinary life, and inciting incident.
- End with a decision that commits the protagonist to the journey.

### Act 2 — Confrontation
- Escalate conflict chapter by chapter.
- Reveal secrets, test relationships, and deepen the theme.
- Include a midpoint reversal that changes what the story means.

### Act 3 — Resolution
- Force the protagonist into a final choice.
- Resolve the main conflict and key emotional arc.
- Close with a memorable final image.

## Chapter-by-Chapter Starter
Replace this fallback outline after your AI provider is configured.
"""

    if purpose in {"writing", "editing"}:
        return header + """# Draft Placeholder

The AI provider is not configured yet, so this placeholder was created to keep the writing workflow from crashing. Once the provider is fixed, regenerate this section.

Suggested next step: open Settings, confirm provider health, then regenerate.
"""

    if purpose == "continuity":
        return header + "No continuity contradictions could be checked in offline fallback mode."

    if purpose == "qa":
        return header + "# Story QA Placeholder\n\nProvider configuration is required before a meaningful QA review can be generated."

    if purpose == "marketing":
        return header + "# Marketing Placeholder\n\nConfigure the AI provider to generate a back-cover blurb, synopsis, and cover prompt."

    return header + "AI generation unavailable. Configure provider settings and try again."


def provider_status() -> dict:
    """Return safe configuration status for UI diagnostics."""
    return {
        "default_provider": env("DEFAULT_PROVIDER", DEFAULT_PROVIDER),
        "fallback_provider": env("FALLBACK_PROVIDER", FALLBACK_PROVIDER),
        "openrouter_has_key": bool(env("OPENROUTER_API_KEY", "")),
        "openrouter_writing_model": env("OPENROUTER_WRITING_MODEL", ""),
        "gemini_has_key": bool(env("GEMINI_API_KEY", "")),
        "gemini_writing_model": env("GEMINI_WRITING_MODEL", ""),
    }


def _safe_error_body(response: requests.Response) -> str:
    text = (response.text or "").strip()
    if not text:
        return response.reason or "No error body returned."
    try:
        data = response.json()
        message = data.get("error", {}).get("message") or data.get("message") or text
        return str(message)[:600]
    except Exception:
        return text[:600]


def _openrouter_chat(prompt: str, purpose: str, temperature: float = 0.7) -> str:
    api_key = env("OPENROUTER_API_KEY", "")
    if not api_key:
        raise AIClientError("OpenRouter API key is missing. Add OPENROUTER_API_KEY in .env.local locally, or Streamlit secrets on Streamlit Cloud.")

    model = get_model("openrouter", purpose)
    if not model:
        raise AIClientError(f"OpenRouter model for '{purpose}' is missing. Set OPENROUTER_{purpose.upper()}_MODEL or OPENROUTER_WRITING_MODEL.")

    url = env("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1").rstrip("/") + "/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": env("APP_PUBLIC_URL", "http://localhost:8443"),
        "X-Title": env("APP_NAME", "Uncle Ossy StoryTeller"),
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_RULES},
            {"role": "user", "content": prompt},
        ],
        "temperature": temperature,
    }
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=90)
    except requests.RequestException as exc:
        raise AIClientError(f"OpenRouter request failed: {exc}") from exc

    if r.status_code >= 400:
        raise AIClientError(f"OpenRouter error {r.status_code}: {_safe_error_body(r)}")

    try:
        data = r.json()
        return data["choices"][0]["message"]["content"]
    except Exception as exc:
        raise AIClientError(f"OpenRouter returned an unexpected response shape: {json.dumps(data)[:600]}") from exc


def _gemini_chat(prompt: str, purpose: str, temperature: float = 0.7) -> str:
    api_key = env("GEMINI_API_KEY", "")
    if not api_key:
        raise AIClientError("Gemini API key is missing. Add GEMINI_API_KEY in .env.local locally, or Streamlit secrets on Streamlit Cloud.")

    model = get_model("gemini", purpose)
    if not model:
        raise AIClientError(f"Gemini model for '{purpose}' is missing. Set GEMINI_{purpose.upper()}_MODEL or GEMINI_WRITING_MODEL.")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": SYSTEM_RULES + "\n\n" + prompt}]}],
        "generationConfig": {"temperature": temperature},
    }
    try:
        r = requests.post(url, json=payload, timeout=90)
    except requests.RequestException as exc:
        raise AIClientError(f"Gemini request failed: {exc}") from exc

    if r.status_code >= 400:
        raise AIClientError(f"Gemini error {r.status_code}: {_safe_error_body(r)}")

    try:
        data = r.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as exc:
        raise AIClientError(f"Gemini returned an unexpected response shape: {json.dumps(data)[:600]}") from exc


def generate_text(prompt: str, purpose: str = "writing", provider: str | None = None, allow_fallback: bool = True, temperature: float = 0.7) -> str:
    selected = (provider or env("DEFAULT_PROVIDER", DEFAULT_PROVIDER)).strip().lower()
    fallback = env("FALLBACK_PROVIDER", FALLBACK_PROVIDER).strip().lower()

    candidates = [selected]
    if allow_fallback and fallback and fallback != selected:
        candidates.append(fallback)

    errors = []
    for candidate in candidates:
        try:
            if candidate == "openrouter":
                return _openrouter_chat(prompt, purpose, temperature)
            if candidate == "gemini":
                return _gemini_chat(prompt, purpose, temperature)
            raise AIClientError(f"Unsupported provider '{candidate}'. Use 'openrouter' or 'gemini'.")
        except AIClientError as exc:
            errors.append(f"{candidate}: {exc}")
        except Exception as exc:
            errors.append(f"{candidate}: unexpected error: {exc}")

    if env_bool("ENABLE_OFFLINE_FALLBACK", True):
        return _offline_fallback(prompt, purpose, errors)

    raise AIClientError(" | ".join(errors))
