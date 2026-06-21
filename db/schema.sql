-- Uncle Ossy StoryTeller — Supabase schema (Phase 5a)
-- Tables live in a dedicated "StoryTeller" schema (not public).
-- Apply in Supabase → SQL Editor. NOTE the quoted, case-sensitive schema name.
--
-- After applying, the "StoryTeller" schema must be exposed to the API:
--   Dashboard → Project Settings → API → Exposed schemas → add "StoryTeller"
-- (or, transiently, the ALTER ROLE statement at the bottom of this file).

create schema if not exists "StoryTeller";

grant usage on schema "StoryTeller" to anon, authenticated, service_role;

create table if not exists "StoryTeller".projects (
    id            text primary key,
    owner         uuid not null references auth.users (id) on delete cascade,
    title         text,
    status        text,
    project_type  text,
    fiction_type  text,
    genre         text,
    chapter_count integer,
    updated_at    timestamptz not null default now(),
    bundle        jsonb not null
);

create index if not exists projects_owner_updated_idx
    on "StoryTeller".projects (owner, updated_at desc);

grant select, insert, update, delete on "StoryTeller".projects to authenticated;
grant select, insert, update, delete on "StoryTeller".projects to service_role;

-- ── Row-Level Security: every user sees only their own projects ─────────
alter table "StoryTeller".projects enable row level security;

drop policy if exists projects_select_own on "StoryTeller".projects;
create policy projects_select_own on "StoryTeller".projects
    for select using (owner = auth.uid());

drop policy if exists projects_insert_own on "StoryTeller".projects;
create policy projects_insert_own on "StoryTeller".projects
    for insert with check (owner = auth.uid());

drop policy if exists projects_update_own on "StoryTeller".projects;
create policy projects_update_own on "StoryTeller".projects
    for update using (owner = auth.uid()) with check (owner = auth.uid());

drop policy if exists projects_delete_own on "StoryTeller".projects;
create policy projects_delete_own on "StoryTeller".projects
    for delete using (owner = auth.uid());

-- ── Expose the schema to PostgREST (prefer the dashboard toggle above) ──
-- alter role authenticator set pgrst.db_schemas = 'public, graphql_public, StoryTeller';
-- notify pgrst, 'reload schema';
-- notify pgrst, 'reload config';
