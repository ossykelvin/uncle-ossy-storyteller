# Supabase Setup (Phase 5a) — Activate persistent storage + managed auth

The code is already wired. The app stays on **local login + JSON files** until you
fill in two values, then it automatically switches to **Supabase Auth + Postgres**
(so user data survives Streamlit Cloud restarts).

## 1. Create / open a Supabase project
<https://supabase.com> → New project. Wait for it to provision.

## 2. Apply the database schema
Supabase dashboard → **SQL Editor** → paste the contents of [`db/schema.sql`](db/schema.sql) → **Run**.
This creates the `projects` table and the Row-Level Security policies that scope
every row to its owner (`owner = auth.uid()`).

## 3. Get your API credentials
Dashboard → **Project Settings → API**:
- **Project URL** → `SUPABASE_URL`
- **anon / public** key → `SUPABASE_ANON_KEY`

Put them in `.env.local` (local) **and** Streamlit Cloud → Manage app → Settings → Secrets (deploy):
```
SUPABASE_URL="https://YOUR-REF.supabase.co"
SUPABASE_ANON_KEY="eyJ...your-anon-key..."
```
> Use the **anon** key, not the service-role key. RLS + the user's login token do the
> access control. The service-role key bypasses RLS and must never reach the client.

## 4. Configure email confirmation (choose one)
Dashboard → **Authentication → Providers → Email**:
- **Fastest for testing:** turn **Confirm email = OFF**. New sign-ups can log in immediately.
- **Production:** leave it ON and set a custom SMTP sender under **Authentication → Emails → SMTP**
  using your Brevo credentials (already in `.env.local`):
  - Host: `smtp-relay.brevo.com`, Port: `587`
  - Login / password: from your Brevo SMTP settings
  - Sender: `noreply@koptechnology.com` / `Ossy Story Teller`

## 5. Restart and verify
Restart the app. You should now see an **email/password** "Create Account" screen
instead of the local username login. Create an account, make a project, restart the
app, and confirm the project is still there.

---

## Email on signup

Two independent layers send mail on a new signup:

**1. Supabase verification email (the confirmation link) — REQUIRED for "verify on".**
With email verification ON, Supabase will not deliver the confirmation link until you
point it at a real SMTP provider. Configure Brevo SMTP:

Supabase → **Authentication → Emails → SMTP Settings** → enable custom SMTP:
- **Host:** `smtp-relay.brevo.com`   **Port:** `587`
- **Username:** your Brevo **SMTP login** (Brevo → **SMTP & API → SMTP** tab — looks like `8xxxxx@smtp-brevo.com`)
- **Password:** a Brevo **SMTP key** (generate under the same SMTP tab)
  - ⚠️ This is **not** the `xkeysib-...` API key — that one is for the transactional API
    (used by the app-side emails below). SMTP needs its own key.
- **Sender email:** `noreply@koptechnology.com`   **Sender name:** `Ossy Story Teller`

Then Supabase → **Authentication → URL Configuration** → set **Site URL** to your app URL
(`http://localhost:8443` for local, the `*.streamlit.app` URL once deployed) so the
confirmation link points back correctly.

**2. App-side Brevo emails (welcome + admin alert) — already wired.**
On each signup the app sends a welcome email to the new user and a "new signup" alert to
`BREVO_ADMIN_EMAIL`, via `core/email_brevo.py` using the `BREVO_API_KEY`. Best-effort: a
mail failure never blocks signup. Tested live and delivering.

---

### What changes when Supabase is active
| | Local (blank creds) | Supabase (creds set) |
|---|---|---|
| Login | username + PBKDF2 (`users.json`) | email + password (Supabase Auth) |
| Project storage | `data/projects/*.json` | Postgres `projects` table |
| Isolation | app-level owner check | Postgres Row-Level Security |
| Survives restart | no (ephemeral on cloud) | **yes** |

### Notes / follow-ups
- Access tokens last ~1 hour; very long idle sessions may need a re-login. Token refresh
  is a small follow-up if it becomes annoying.
- Exports (md/docx/pdf/epub) are staged to a local temp dir and streamed to the browser —
  they don't need persistent disk.
