# Deploy to Streamlit Community Cloud

The repo is deploy-ready: pinned `requirements.txt`, `.python-version` (3.12),
entry point `app.py`, and secrets kept out of git.

## 1. Code is on GitHub
Repo: see `git remote -v`. Secrets (`.env.local`, `data/`, `.venv`) are gitignored,
so nothing sensitive is committed.

## 2. Create the app on Streamlit Cloud
1. Go to <https://share.streamlit.io> → sign in with GitHub.
2. **Create app → Deploy a public app from GitHub** (works for private repos too once GitHub is authorized).
3. Settings:
   - **Repository:** your repo
   - **Branch:** `main`
   - **Main file path:** `app.py`
   - **Advanced → Python version:** `3.12`

## 3. Add secrets
**Manage app → Settings → Secrets**, paste the TOML from
[`.streamlit/secrets.toml.example`](.streamlit/secrets.toml.example) with your real
values. `core/config.py` reads `st.secrets` automatically, so no code change is needed.

> Use the Supabase **publishable** key, never the service-role key.

## 4. Supabase: allow the deployed URL
After the first deploy you get a URL like `https://<app>.streamlit.app`.
In Supabase → **Authentication → URL Configuration**, add it to **Site URL** /
**Redirect URLs** so auth emails/links point at the live app.

Also make the custom schema exposure durable (one-time):
Supabase → **Settings → API → Exposed schemas** → add **`StoryTeller`**.

## 5. Verify
Open the app URL → create an account (or use the confirmed test login) →
make a project → reload. Data persists in Postgres.

---

### Storage note
Project data lives in Supabase Postgres (persistent). The only thing written to the
container's ephemeral disk is **export staging** (md/docx/pdf/epub) right before the
browser downloads it — that's fine to lose on restart.

### Updating the deployed app
Push to `main`; Streamlit Cloud redeploys automatically.
