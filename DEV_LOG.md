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

**Bug found & fixed:** `requirements.txt` was never tracked by git — the existing `.gitignore` rule `ai_agent_classifier/*.txt` (meant for scratch debug logs) was silently also matching the dependency manifest, so it had never reached a commit and Railway's Nixpacks build was never actually installing from it (README's manual `pip install flask flask-sqlalchemy ...` instructions were a workaround for this, not a style choice). Fixed by adding `!ai_agent_classifier/requirements.txt` to `.gitignore` right after the wildcard rule. This means `flask-login` (and any future dependency) would not have reached the production deploy without this fix.

**Verification:** Ran the app locally and curl-tested all three identities (anonymous, `visitor` role, `admin` role) against the locked-down routes and the UI-leak fixes; confirmed 403/redirect-to-login for non-admins and full access for admin. Test users and DB residue reverted out of the tracked `instance/agents.db` fixture afterward via `git checkout --`.

**Open items:**
- Nothing staged or committed yet — `.gitignore`, `requirements.txt` (newly trackable), and all Phase 1 files are sitting as local changes on the `insights` branch pending review.
- Phases 2–5 (freemium + landing/nav redesign, compare/shortlist, supplier portal, billing) not started.
