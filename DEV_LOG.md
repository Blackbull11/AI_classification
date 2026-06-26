# Development Log

Append-only. Newest entries at the bottom.

---

## 2026-06-19 — Authors/tutor presentation deck

**Summary:** Built a 15-slide professional PowerPoint deck presenting the platform to the paper's four authors and the internship tutor. Top-down narrative (goal → problem → framework → methodology → platform tour → results → reflections → limitations → conclusions), styled to the platform's dark/copper design system, embedding the six `docs/screenshots`. Includes per-slide speaker notes and personal design-decision commentary.

**Files created:**
- `presentation/build_deck.py` — python-pptx generator (palette, layout helpers, image-fit, speaker notes).
- `presentation/Panthera_AI_Agent_Classifier.pptx` — the rendered 15-slide deck.
- `DEV_LOG.md` — this log (was referenced in memory but did not exist yet).

**Notes / data used:** Pulled live stats from `instance/agents.db` — 78 classified agents; complexity skew to white (39) / light-grey (40), dark-grey 1, black 0; advantage analytical 49 / informational 30 / behavioral 1; autonomy low 54 / medium 14 / high 10 / full 2; stage coverage led by idea-assess (56) and idea-gen (31). These drive the "Results / market view" slide.

**Open items:**
- Presenter name/date on title + closing slides are placeholders (Andrea Signoretti, June 2026) — confirm/edit.
- "~99%" and "63%" stat-card figures are rounded from the classified set; re-confirm if the DB changes before the talk.
- Deck regenerates via `python presentation/build_deck.py`; PowerPoint COM was used only for visual QA (temp `_render/` removed).

---

## 2026-06-25 — Panthera Insights commercialization plan

**Summary:** Analysed the current internal classifier against the "AI agents Classification Framework in Action" business brief (priority idea = Panthera Insights, a two-sided discovery/classification SaaS). Produced a phased written plan to turn the internal Flask tool into a commercial product. Key finding: the four taxonomy dimensions already map 1:1 to existing fields (`stages`/`autonomy`/`advantage`/`complexity`), so commercialization is an access-control + two-audience layer, not a rewrite. Flagged security-critical gap: back-office routes (`/pipeline`, `/add`, `/edit`, `/delete`, `/quick-add`, `/classify*`, `/api/agents`, `/admin`) are currently unauthenticated.

**Files created:**
- `docs/PANTHERA_INSIGHTS_PLAN.md` — gap analysis, target architecture/roles, data-model changes, 5-phase roadmap.

**Decisions locked:** explicit `premium` boolean for the 50% freemium split; Decision GPS kept with a "Panthera-affiliated" disclosure; written plan first, no code changes this session.

**Open items:**
- `_migrate_db()` uses SQLite-only `PRAGMA`; prod is now PostgreSQL — make dialect-aware or adopt Flask-Migrate/Alembic before Phase 1.
- Phase 1 (auth + route lockdown) is security-critical and should proceed regardless of monetization timing.

### Update — clarity, punchlines & navigation

Extended `docs/PANTHERA_INSIGHTS_PLAN.md` with four new sections (§12–§15) to make the product instantly legible: a master tagline ("the reference map of AI agents in investment management"), a reusable punchline library, plain-language statements of goals/targets/methodology/offer, a buyer-first navbar/IA redesign (verb-led labels, persistent shortlist chip, back-office moved out of public nav), and a drop-in landing-page copy draft. Clarity is folded into Phase 2 as a first-class workstream; copy reuses existing `framework.html` component styles so it's templating, not new CSS. Methodology reframed as four plain questions (where it works / how independently / what edge / how it handles the unknown) mapping to the four existing dimensions.

---

## 2026-06-26 — Phase 1: Auth & back-office lockdown (`insights` branch)

**Summary:** Implemented Phase 1 of `docs/PANTHERA_INSIGHTS_PLAN.md` on a new `insights` branch. Added a `User` model (email/password-hash/role) and wired up Flask-Login. Every back-office route — `/pipeline`, `/add*`, `/edit*`, `/quick-add`, `/classify*`, `/reject`, `/restore`, `/delete`, `/api/agents` — and the Flask-Admin views (`AgentModelView`, admin index) are now gated behind a new `admin_required` decorator (`login_required` + `role == 'admin'`, else 403). Public pages (`/matrix`, `/guide`, `/framework`, `/agents/<id>`, exports) remain open per the plan; exports/freemium gating is Phase 2 scope.

**Files created:**
- `ai_agent_classifier/templates/login.html` — login form.
- `ai_agent_classifier/create_admin.py` — CLI to bootstrap/promote an admin: `python create_admin.py <email> "<password>"`.

**Files modified:**
- `ai_agent_classifier/models.py` — new `User(db.Model, UserMixin)` with `set_password`/`check_password`.
- `ai_agent_classifier/app.py` — `LoginManager` + `user_loader`, `admin_required` decorator, secured `AgentModelView`/`AdminIndexView`, `/login`/`/logout` routes, decorator applied to all back-office routes.
- `ai_agent_classifier/templates/base.html` — Pipeline nav link and pending-count badge hidden for non-admins; login/logout control in navbar.
- `ai_agent_classifier/templates/matrix.html`, `agent_detail.html` — Quick Add button/modal, Full Wizard link, pending banner, Classify/Edit buttons, Pipeline breadcrumb hidden for non-admins (these leaked into public pages even though the underlying routes were already locked down server-side).
- `ai_agent_classifier/requirements.txt` — added `flask-login`.

**Bug found & fixed (round 1, incomplete):** `ai_agent_classifier/requirements.txt` was never tracked by git — caught by the `.gitignore` rule `ai_agent_classifier/*.txt` (meant for scratch debug logs). Added a `!ai_agent_classifier/requirements.txt` exception. This turned out not to be the actual deploy mechanism — see the 06-26 follow-up below.

**Verification:** Ran the app locally and curl-tested all three identities (anonymous, `visitor` role, `admin` role) against the locked-down routes and the UI-leak fixes; confirmed 403/redirect-to-login for non-admins and full access for admin. Test users and DB residue reverted out of the tracked `instance/agents.db` fixture afterward via `git checkout --`.

Committed and pushed as `5f0850e "Step 1 - Panthera Insights"`.

### Follow-up — real root cause of the Railway crash

The round-1 fix didn't actually solve it: Railway crashed with `ModuleNotFoundError: No module named 'flask_login'` right after deploy. Real cause — there are **two** `requirements.txt` files (repo root and `ai_agent_classifier/`); Railway/Nixpacks installs from the **root** one only (confirmed via its commit history, "First Railway Deployment"). `flask-login` had been added to the nested file, which Railway never reads. The root file was also missing `psycopg2-binary` despite prod using Postgres — a second crash waiting to happen right after the first was fixed.

**Fixed by:** adding `flask-login` + `psycopg2-binary` to the root `requirements.txt`, deleting the nested duplicate so the two can't drift apart again, dropping the now-pointless `.gitignore` exception, and updating `README.md`'s install instructions/file-structure diagram to point at the single root file. Committed as `a461967 "Phase 1 - debug"`.

**Open items:**
- Phases 2–5 (freemium + landing/nav redesign, compare/shortlist, supplier portal, billing) — Phase 2 underway, see below.

---

## 2026-06-26 — Phase 2: Freemium gating + landing page + nav redesign (`insights` branch)

**Summary:** Implemented Phase 2 of `docs/PANTHERA_INSIGHTS_PLAN.md` — the `premium` flag, the teaser/gated agent profile, gated exports, the new `/` marketing landing page, and the buyer-first nav redesign (§12–§14 punchlines/copy).

**Files created:**
- `ai_agent_classifier/templates/landing.html` — new `/` marketing page (hero, problem, 4-question methodology, 3-card offer, audience cards, neutrality statement, CTA), reusing `framework.html`'s `fw-*` component classes per the plan.
- `ai_agent_classifier/templates/subscribe.html` — `/subscribe` stub (early-access request via mailto; no real billing yet, per the plan's MVP shortcut).

**Files modified:**
- `ai_agent_classifier/models.py` — `Agent.premium` (Boolean, default False).
- `ai_agent_classifier/app.py` — `has_premium_access()` helper (admin or `subscription_active`) and `premium_required` decorator; `/export/*` now gated; `agent_detail` computes and passes `locked`; `/` now serves `landing()` (was aliased to `framework()`), new `/subscribe` route; `premium` added to `AgentModelView` form/list/filters.
- `ai_agent_classifier/templates/agent_detail.html` — locked agents show a teaser (badges/description visible, Key Features + Analyst Notes + per-metric rationale hidden behind a "Subscribe to unlock" CTA); `★ Premium` chip; Decision GPS gets the §9 "Panthera-affiliated product" disclosure banner.
- `ai_agent_classifier/templates/base.html` — nav renamed (Matrix → "Explore the Map", Guide → "Find an Agent", Framework → "How it works"); brand logo now links to landing; Exports dropdown only shows for admin/subscribers, replaced by a "Subscribe" link otherwise.
- `ai_agent_classifier/templates/matrix.html` — found and fixed an Edit-link leak: the badge hover-card "Edit ✎" button was visible to every visitor (not just admins) even though the underlying route was already locked down — same class of leak as the Phase 1 Quick-Add/breadcrumb fixes.

**Bug found & fixed (unrelated to the brief, found while wiring the migration):** `db.create_all()` / `_migrate_db()` only ran inside `if __name__ == "__main__":`, which never executes under `gunicorn app:app` (Railway's actual entry point) — only under `python app.py`. So the `users` table from Phase 1 and the new `premium` column would never have been created in production. Moved the init calls to module level (run on import, so every gunicorn worker initializes the DB). Also made `_migrate_db()` dialect-aware (it used SQLite-only `PRAGMA table_info`, flagged as a risk in the original plan) — Postgres path uses an atomic `ADD COLUMN IF NOT EXISTS` (safe across concurrent workers), SQLite path falls back to an existence check (`IF NOT EXISTS` isn't valid SQLite syntax for `ADD COLUMN`).

**Verification:** Ran locally; marked one agent `premium=True` and created admin/subscriber/visitor test accounts. Confirmed: anonymous and visitor see the locked teaser and get 403 on exports; subscriber and admin see full content and can export; Flask-Admin list/form shows the `premium` toggle; Decision GPS shows the disclosure banner; nav renames and Exports/Subscribe swap render correctly for each role. Test users and the premium flag reverted out of the tracked `instance/agents.db` fixture via `git checkout --`.

**Open items:**
- `/subscribe`'s contact address (`insights@panthera.design`) is a placeholder — confirm or change.
- Phase 3 (Compare & Shortlist) and Phase 4 (Supplier portal) nav items intentionally omitted from the navbar — adding them now would be dead links until those phases land.

### Follow-up — premium curation rule

The "which ~50%" open item above was resolved with two explicit business rules: only **commercial** agents may be premium (in-house/academic always free), and every process stage must keep **at least 40% free**. Added `ai_agent_classifier/set_premium.py` — a rerunnable greedy selection (cheapest agents by stage-count first, capped per stage at 60% premium) — rather than a one-off manual pick, so it can be regenerated after future agents are added. Applied to the local `instance/agents.db` fixture: **39/78 (50%) marked premium**, all commercial, free% per stage ranges 42%–100% (compliance is tightest at 42%, still clears the 40% floor). Production (Postgres) needs the same script run against it — `DATABASE_URL` makes `set_premium.py` environment-aware, so it can run there too (e.g. via `railway run python set_premium.py`).
- Nothing committed yet — all Phase 2 changes are local on the `insights` branch pending review.
