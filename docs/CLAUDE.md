# CLAUDE.md — AI Agent Classification System

## Project Overview

**Panthera AI Agent Classifier** — a Flask web application for cataloguing, classifying, and exporting AI agents used in investment management. Built for the Panthera Group, it maps commercial, in-house, and academic AI systems against the firm's proprietary **Swan Theory** complexity framework and a 7-stage investment process pipeline.

- **Entry point**: `ai_agent_classifier/app.py` → `python app.py` (port 5000)
- **Landing page**: `/` and `/framework` both serve the framework explainer (`framework()`); the classification matrix lives at `/matrix`
- **Enterprise Stack**: `/enterprise` — a user flags which catalogue agents their own firm runs (`Agent.in_stack`), benchmarks that selection against the full catalogue on the same Complexity×Stage matrix, and gets commercial-only recommendations to close gaps — see [Enterprise Stack](#enterprise-stack)
- **Database**: SQLite at `ai_agent_classifier/instance/agents.db` for local dev; **PostgreSQL in production** (Railway) via the `DATABASE_URL` env var — see [Deployment](#deployment)
- **Framework**: Flask + SQLAlchemy (Python) · Bootstrap 5.3.3 dark theme (frontend) · Flask-Admin CRUD panel at `/admin`

---

## Tech Stack

| Layer | Technology |
|---|---|
| Web framework | Flask |
| ORM / DB | SQLAlchemy — SQLite (local dev) or PostgreSQL (production, via `DATABASE_URL`) |
| Admin CRUD | Flask-Admin (`/admin`, `AgentModelView`) |
| Frontend | Bootstrap 5.3.3 + vanilla JS |
| AI auto-classifier | Anthropic Claude API (`claude-opus-4-8`) |
| Excel export | openpyxl |
| Word export | python-docx |
| PDF export | reportlab |
| Production server | gunicorn (`Procfile`), deployed on Railway |

**Dependencies**: `requirements.txt` (repo root — installed before `cd ai_agent_classifier` per `Procfile`)  
`pip install flask flask-sqlalchemy flask-admin python-docx openpyxl reportlab anthropic gunicorn`

For auto-classification, set env var:
```
ANTHROPIC_API_KEY=sk-...
```

For a PostgreSQL backend (Railway or otherwise), set:
```
DATABASE_URL=postgresql://...
```
> `psycopg2-binary` is pinned in `requirements.txt` (added 2026-06-29 after a Railway crash loop — `ModuleNotFoundError: No module named 'psycopg2'`). A deployed service still needs a redeploy to pick up the change; editing the file alone doesn't fix an already-running worker.

---

## File Structure

> **Note**: `CLAUDE.md`, `DEV_LOG.md`, and `CLASSIFICATION_GUIDE.md` physically live under `docs/`, not at the repo root. `requirements.txt` and `Procfile` must stay at the repo root for Railway's buildpack to find them.

```
AI_classification/
├── README.md
├── requirements.txt                ← pip dependencies (installed from repo root)
├── Procfile                        ← Railway/gunicorn start command
├── docs/
│   ├── CLAUDE.md                   ← this file
│   ├── DEV_LOG.md                  ← rolling development log
│   ├── CLASSIFICATION_GUIDE.md     ← Swan Theory framework documentation
│   └── screenshots/                ← matrix, framework, guide, autonomy, advantage, pdf_export PNGs
├── presentation/
│   ├── build_deck.py               ← python-pptx generator for the stakeholder deck
│   └── Panthera_AI_Agent_Classifier.pptx
└── ai_agent_classifier/
    ├── app.py                      ← Flask routes + session wizard logic
    ├── models.py                   ← SQLAlchemy Agent model
    ├── auto_classify.py            ← Claude API batch classifier
    ├── exports.py                  ← Excel / Word / PDF export engine
    ├── build_agents_db.py          ← Seeds ~78 pre-classified agents (idempotent — safe to re-run)
    ├── migrate_to_postgres.py      ← one-time SQLite → Railway PostgreSQL data copy
    ├── seed_data.py                ← Legacy seed (disabled, returns early)
    ├── instance/
    │   └── agents.db               ← SQLite database (local dev only; production uses PostgreSQL)
    ├── static/
    │   ├── css/style.css           ← Design system (CSS custom properties)
    │   ├── js/app.js               ← Bootstrap tooltip + popover init, flash dismiss
    │   └── img/                    ← Panthera logo (PNG + SVG)
    └── templates/
        ├── base.html               ← Master layout (navbar, flash messages)
        ├── _macros.html            ← Shared Jinja macros: `info_icon()` ("?" help bubble), `add_to_stack()` (full vs. name-only add buttons)
        ├── framework.html          ← Landing page (`/`, `/framework`) — 5-dimension explainer + category cluster
        ├── matrix.html             ← Classification matrix (`/matrix`): Complexity×Stage / Stage×Advantage / Autonomy Scatter views
        ├── pipeline.html           ← Agent lifecycle management table
        ├── enterprise.html         ← Enterprise Stack (`/enterprise`) — tool picker, benchmark coverage map, recommendations
        ├── wizard.html             ← 4-step classification wizard
        ├── agent_detail.html       ← Per-agent profile view
        └── guide.html              ← Agent Finder — 5-step questionnaire (stage, advantage, autonomy, complexity, category)
```
> Also tracked in git but not part of the running application: `ai_agent_classifier/agents_production.db`, `instance/agents copy.db`, `instance/agents_broken.db`, `instance/agents_temp.db`, `instance/agents_b64.txt` — leftover artifacts from the PostgreSQL migration. See Known Issues in `DEV_LOG.md`.

---

## Database Schema

**Table: `agents`**

| Column | Type | Description |
|---|---|---|
| `id` | INTEGER PK | Auto-increment |
| `name` | TEXT NOT NULL | Display name |
| `url` | TEXT | Product / paper URL |
| `description` | TEXT | 2-3 sentence technical summary |
| `rationale` | TEXT | JSON dict (keys: advantage, complexity, autonomy, agent_type, stages, general) |
| `key_features` | TEXT | JSON array of 3-6 bullet strings |
| `advantage` | TEXT | `behavioral` · `analytical` · `informational` |
| `autonomy` | TEXT | `low` · `medium` · `high` · `full` |
| `agent_type` | TEXT | `commercial` · `in-house` · `academic` |
| `complexity` | TEXT | `white` · `light-grey` · `dark-grey` · `black` |
| `stages` | TEXT | JSON array of stage keys |
| `category_id` | TEXT | One of the 10 `CATEGORIES` ids defined in `app.py` (CAT-1…CAT-10), or `NULL` if uncategorized |
| `status` | TEXT NOT NULL | `pending` · `classified` · `rejected` |
| `in_stack` | BOOLEAN NOT NULL DEFAULT 0 | Flags this agent as part of the user's Enterprise Stack — added via `_migrate_db()` (`ALTER TABLE` guarded by a `PRAGMA table_info` check, same pattern as `category_id`) |
| `created_at` | DATETIME | UTC creation timestamp |

**Model helpers** (on `Agent` class):
- `agent.rationale_dict` — parsed JSON or `{}` fallback
- `agent.stages_list` — parsed JSON or `[]`
- `agent.features_list` — parsed JSON or `[]`

---

## Classification Framework

### Investment Process Stages (7)

| Key | Label |
|---|---|
| `idea-gen` | Idea Generation |
| `idea-assess` | Idea Assessment |
| `decision` | Decision Point |
| `execution` | Execution |
| `monitoring` | Monitoring |
| `compliance` | Compliance |
| `stakeholder` | Stakeholder Management |

An agent can cover multiple stages.

### Complexity — Swan Theory

| Tier | Label | Meaning |
|---|---|---|
| `white` | White Swan | Known, predictable, rule-based |
| `light-grey` | Light-Grey Swan | Mostly known, minor uncertainty |
| `dark-grey` | Dark-Grey Swan | Significant uncertainty, ML-driven |
| `black` | Black Swan | Rare, hard-to-model, tail-risk |

### Comparative Advantage

| Value | Meaning |
|---|---|
| `informational` | Edge from better data access / aggregation |
| `analytical` | Edge from superior processing / modelling |
| `behavioral` | Edge from removing human cognitive bias |

Only **one** advantage per agent.

### Autonomy

| Value | Label | Meaning |
|---|---|---|
| `low` | Low | Human decides; AI assists |
| `medium` | Medium | AI recommends; human approves |
| `high` | High | AI acts; human monitors within set parameters |
| `full` | Fully Autonomous | No human veto on individual decisions — live capital deployment (e.g. AIEQ, Numerai) |

`full` is reserved for systems where there is **no human override mechanism** on individual decisions. Applied to AIEQ/EquBot (ID:1) and Numerai Meta Model (ID:2). Displays as a pulsing crimson pip on the matrix badge.

### Agent Type

| Value | Meaning |
|---|---|
| `commercial` | Third-party vendor product |
| `in-house` | Built internally by firm |
| `academic` | Research paper / prototype |

### Category Label (10 categories)

A functional cluster describing the agent's primary role in the investment workflow, independent of the four core dimensions above. Defined as the `CATEGORIES` list in `app.py` (id, label, fullName, color, description) and assigned via `AGENT_CATEGORY_SEED` (name → category id) applied by `_migrate_db()` at startup. Selectable as a `<select>` in wizard step 1 and as a Q5 filter chip in the Guide.

| ID | Category |
|---|---|
| CAT-1 | Autonomous Trading Engines |
| CAT-2 | AI Execution Optimizers |
| CAT-3 | Agentic Quant Research Systems |
| CAT-4 | Quantitative Signal & Screening Tools |
| CAT-5 | AI Portfolio Construction & Management |
| CAT-6 | Investment Research & Document Intelligence |
| CAT-7 | Market Intelligence & Real-Time Monitoring |
| CAT-8 | Risk, AML & Surveillance Monitors |
| CAT-9 | ESG & Regulatory Compliance Platforms |
| CAT-10 | Client & Stakeholder Intelligence |

Some agents (general-purpose bank LLM suites, e.g. Goldman Sachs AI Assistant, JPMorgan LLM Suite) are intentionally left uncategorized — listed in `UNCATEGORIZED_AGENTS` — to avoid forcing a poor fit. **`auto_classify.py` does not assign `category_id`** — it is set only via seed data or manual edit. Full taxonomy history (CAT-5 dissolution, renames) is in `DEV_LOG.md` under "Taxonomy v2".

### In-App Help ("?" Bubbles)

Every dimension and value above is also explained inline via a small "?" hover/focus popover, so a user unfamiliar with Swan Theory doesn't need to leave the page they're on. Source of truth is four dicts in `app.py`, each entry shaped `{"label", "title", "blurb", "body"}` (`blurb` is a one-liner for native `title`-attribute tooltips on chips; `body` is the longer popover text, with `\n\n` for paragraph breaks):

- `COMPLEXITY_DIMENSION_INFO` / `COMPLEXITY_INFO` (per tier: `white`, `light-grey`, `dark-grey`, `black`)
- `AUTONOMY_DIMENSION_INFO` / `AUTONOMY_INFO` (per level: `low`, `medium`, `high`, `full`)
- `STAGE_DIMENSION_INFO` / `STAGE_INFO` (per stage key)

All seven dicts are injected into **every** template via `inject_globals()` (the same context processor that already provided `pending_count`/`today`), so no route needs to pass them explicitly. Templates render the bubble with the `info_icon(title, body)` macro from `templates/_macros.html`, e.g. `{{ m.info_icon(complexity_info[cx_key].title, complexity_info[cx_key].body) }}`. Bubbles appear on `matrix.html` (stage headers, complexity row labels, autonomy legends), `wizard.html` (step 2/3 option labels), `guide.html` (question headers + chip tooltips), `pipeline.html` (column headers), `agent_detail.html` (the agent's own complexity/autonomy/stage values), and `enterprise.html` (coverage-map headers).

Implementation note: popovers/tooltips are initialized in `app.js` with `container: "body"` — several of these bubbles live inside `overflow:auto` widgets (the matrix scroll wrapper, the gap-search popout), and without `container: "body"` the floating bubble gets visually clipped/buried by its own ancestor instead of rendering on top.

---

## Flask Routes

### Pages
| Method | Path | Function | Description |
|---|---|---|---|
| GET | `/`, `/framework` | `framework()` | Landing page — 5-dimension framework explainer + category cluster |
| GET | `/matrix` | `matrix()` | Classification matrix — Complexity×Stage, Stage×Advantage, and Autonomy Scatter views |
| GET | `/pipeline` | `pipeline()` | Agent lifecycle table |
| GET | `/guide` | `guide()` | Agent Finder — 5-step questionnaire, JS-filtered results |
| GET | `/enterprise` | `enterprise()` | Enterprise Stack — tool picker, benchmark coverage map, recommendations (see [Enterprise Stack](#enterprise-stack)) |
| GET | `/add` | `add_agent()` | Start full wizard (add mode) |
| POST | `/add/step/<n>` | `add_step()` | Wizard step n (1–4) |
| POST | `/add/save` | `add_save()` | Save new agent (status: classified) |
| GET | `/edit/<id>` | `edit_agent()` | Start wizard (edit mode) |
| POST | `/edit/<id>/step/<n>` | `edit_step()` | Edit wizard step |
| POST | `/edit/<id>/save` | `edit_save()` | Save edits |
| GET | `/agents/<id>` | `agent_detail()` | Agent profile page |
| GET | `/agents/<id>/classify` | `classify_agent()` | Start wizard (classify mode) |
| POST | `/agents/<id>/classify/step/<n>` | `classify_step()` | Classify wizard step |
| POST | `/agents/<id>/classify/save` | `classify_save()` | Save classification |

### Actions
| Method | Path | Description |
|---|---|---|
| POST | `/quick-add` | Add agent with name + URL only (status: pending). Optional form fields `next` (`"pipeline"` \| `"enterprise"`, default `"pipeline"`) and `in_stack` (truthy → sets `in_stack=True` and redirects back to `/enterprise`) let the Enterprise Stack page's "+ Add a custom tool" modal reuse this same route |
| POST | `/agents/<id>/reject` | Mark agent as rejected |
| POST | `/agents/<id>/restore` | Restore rejected → pending |
| POST | `/delete/<id>` | Permanently delete agent |
| POST | `/enterprise/save` | Bulk-set `in_stack` from the picker's checked `agent_ids[]` — unchecked agents are set to `False`, so this is a full sync, not additive |
| POST | `/enterprise/toggle/<id>` | Flip one agent's `in_stack` (used by the matrix's gap-search "+ Add with full details" / hover-card "Remove", and the recommendation cards) |
| POST | `/enterprise/add-minimal/<id>` | "Add name & link only" — creates a **separate** `pending` `Agent` row copying just `name`/`url` from the source agent, with `in_stack=True`. The source catalogue row is left untouched (not marked `in_stack`) |

### Exports
| Method | Path | Description |
|---|---|---|
| GET | `/export/excel` | Download .xlsx (3 sheets: matrix, details, stats) |
| GET | `/export/word` | Download .docx (cover + TOC + per-agent sections) |
| GET | `/export/pdf` | Download .pdf (same structure, ReportLab) |

### API
| Method | Path | Description |
|---|---|---|
| GET | `/api/agents` | JSON array of all agents with all fields |

### Admin
| Method | Path | Description |
|---|---|---|
| GET/POST | `/admin` | Flask-Admin (`AgentModelView`) — searchable/filterable CRUD over the `agents` table, with dropdowns for enum fields and JSON validation on the three JSON columns. **No authentication** — see Known Issues in `DEV_LOG.md`. |

---

## Wizard Flow (4 Steps)

Used for **add**, **edit**, and **classify** modes. State stored in `session['wizard_draft']`.

| Step | Fields |
|---|---|
| 1 | name, url, description, agent_type, category_id (select) |
| 2 | stages (checkboxes, ≥1 required) |
| 3 | complexity, advantage, autonomy (radios) |
| 4 | rationale (6 text fields), key_features (3-6 repeating) |

---

## Auto-Classification Script

**File**: `ai_agent_classifier/auto_classify.py`

Uses Claude `claude-opus-4-8` with a `classify_agent` tool that enforces structured output.

```bash
# Classify all pending agents
python auto_classify.py

# Add a new agent and classify immediately
python auto_classify.py add "Agent Name" --url https://example.com
```

The system prompt contains the full Swan Theory framework. Claude researches the agent and returns all classification fields in one structured tool call.

---

## Export Engine

**File**: `ai_agent_classifier/exports.py`

All three formats export **classified agents only** (status = "classified").

- **Excel**: Sheet 1 = Complexity × Stage matrix · Sheet 2 = tabular details · Sheet 3 = summary statistics. Colour-coded cells, hyperlinks, frozen panes.
- **Word**: Cover page → TOC → per-agent sections with 4-column header, classification table (6 rows), key features bullets, stage timeline.
- **PDF**: Same structure as Word, ReportLab-rendered with internal links.

---

## Enterprise Stack

**Route**: `GET /enterprise` (`enterprise()` in `app.py`) · **Template**: `templates/enterprise.html`

Lets a single user (no multi-tenancy — see [Key Design Decisions](#key-design-decisions)) mark which catalogue agents their firm actually runs, then benchmarks that selection against the full catalogue.

**Page sections, top to bottom:**
1. **Stat cards** — tools in stack, stage coverage (`X/7`), complexity coverage (`X/4`), and a "Benchmark" card showing `fillable_gaps` (empty cells a commercial tool *could* fill) vs. `dead_gaps` (empty cells with no catalogue solution at all).
2. **Build your stack** (`#picker`) — a searchable table of every non-rejected agent with a checkbox per row, wrapped in a `.card` for visual parity with the rest of the page. Defaults to a **"Commercial only" filter chip** (removable/re-addable, client-side `data-type` filtering — see [Design System](#design-system)). One `POST /enterprise/save` syncs the whole checked set in one request (not per-row toggles). "+ Add a custom tool" reuses `quick_add()` with `next=enterprise&in_stack=1`.
3. **Your coverage map** (`#matrix`) — the same Complexity×Stage cartography as `/matrix`, but populated only from `in_stack and status=="classified"` agents. Empty cells render one of three states: filled (agent badges), a **"🔍 Find solutions"** button + popout if `gap_candidates` has entries for that cell, or a plain "no tool yet" note if nothing in the catalogue covers it either.
4. **Stack composition** — four count-based bar charts (tools per stage / complexity tier / autonomy level / comparative advantage), each bar scaled to the *max within that chart*, not as a percentage of the catalogue — this was a deliberate correction after an earlier version showed a catalogue-relative ratio instead of plain counts.
5. **Recommended additions** (`#recommendations`) — up to 6 cards, **commercial-only**, ranked by how many empty cells on the user's own map each agent would fill (`reco_score` in `enterprise()`, derived from `gap_candidates` — no separate query).

**Server-side computation (`enterprise()` view), in order:**
- `stack_matrix[cx][stage]` — the user's own classified+in-stack agents, bucketed like the main matrix.
- `stack_names` — lowercased names of every agent currently in the stack (full **or** name-only), used to suppress an agent from `gap_candidates` (and therefore from recommendations and the gap-search popout) once the user has already added it under either form.
- `gap_candidates["{cx}|{stage}"]` — for every **empty** cell, classified catalogue agents that cover it, are not already `in_stack`, and aren't name-suppressed.
- `reco_score` — folds `gap_candidates` into one count per **commercial** agent ID (how many distinct empty cells it would fill) plus the set of stage keys it would newly cover; sorted desc by count, capped at 6.

**"Add to stack" — two intentionally different actions** (`templates/_macros.html`, `add_to_stack(agent, anchor, size)`):
| Action | Route | Effect |
|---|---|---|
| **+ Add with full details** | `POST /enterprise/toggle/<id>` | Flips `in_stack` on the existing, already-classified catalogue row. Free — the agent already carries a description, rationale, and full classification. |
| **Add name & link only** | `POST /enterprise/add-minimal/<id>` | Inserts a **new**, separate `pending` `Agent` row with just `name`/`url` copied over. The source catalogue row is left alone. Lets a user note "we use Bloomberg Terminal" without inheriting — or being forced to agree with — the catalogue's classification of it; the user can classify their own copy later via the normal Pipeline → Wizard flow. |

The macro renders both as plain inline buttons (not a Bootstrap dropdown) deliberately: the gap-search popout already sits inside a small `overflow:auto` panel, and a Popper-positioned dropdown menu nested in there would clip exactly the same way an unconfigured popover would (see [In-App Help](#in-app-help--bubbles)).

---

## Design System

**File**: `ai_agent_classifier/static/css/style.css`

**CSS Custom Properties**:
```css
--bg-base:        #1A1A1A   /* very dark background */
--accent:         #C4845A   /* Panthera copper / terracotta */
--accent-dark:    #8B5E3C   /* brown */
--text-primary:   #F0F0F0   /* off-white */
--text-secondary: #A0A0A0   /* medium grey */
--text-muted:     #666666   /* dark grey */
--inf:            #EF9F27   /* orange — informational */
--ana:            #1DB87A   /* green — analytical */
--beh:            #E0613A   /* rust — behavioral */
```

**Visual Language**: Dark UI with warm copper accents. The matrix widget uses a **3D cube motif** with a contrasting beige (`#FAF7F1`) background to frame the complexity × stage table. Agent badges carry three independent visual channels:

| Channel | Encoded by |
|---|---|
| Badge fill / border color | Comparative advantage (behavioral / analytical / informational) |
| Border style (solid / outlined / dashed) | Agent type (commercial / in-house / academic) |
| Small dot at bottom-right (`::after`) | Autonomy level (grey / amber / orange / crimson-pulsing) |

**Key CSS classes**:
- `.matrix-widget` — beige cube container
- `.matrix-table-3d` — main matrix table
- `.stage-cube` — 3D-effect column headers
- `.agent-badge` — advantage/type colour-coded chip; in matrix context gains `::after` autonomy pip
- `.badge-container[data-autonomy]` — drives pip color via CSS attribute selector
- `.legend-aut`, `.legend-aut-{low|med|high|full}` — autonomy pip legend items
- `.stat-card` — dashboard metric card
- `.badge-hover-card` — tooltip on badge hover
- `.stage-option`, `.cx-option` — wizard radio/checkbox labels
- `.scatter-widget` — autonomy scatter SVG container
- `.view-toggle-group`, `.vt-btn` — matrix / stage×advantage / scatter view switcher (`data-view="matrix|advmatrix|scatter"`)
- `.guide-cat-chip.selected` — category filter chip in Guide Q5, color driven by `--cat-chip-color` custom property set via JS
- `.guide-cat-label` — small category label shown on Guide result cards
- `.detail-category-card`, `.detail-category-value` — category block on the agent detail sidebar
- `.info-icon` — the "?" hover/focus bubble trigger (see [In-App Help](#in-app-help--bubbles)); `.popover` / `.tooltip` CSS-variable overrides re-theme Bootstrap's popovers and tooltips to the dark/copper palette (Bootstrap's own defaults are light-on-dark and don't match)
- `.form-check-input:checked` — global override so every checkbox/radio in the app uses `var(--accent)` instead of Bootstrap's default blue; added when the Enterprise Stack picker made the mismatch visible, but it fixes every checkbox app-wide (wizard included)
- `.ent-picker-card`, `.ent-picker-table-wrap`, `.ent-agent-link`, `.ent-type-pill`, `.ent-row-checked` — Enterprise Stack tool-picker table, wrapped in a `.card.shadow-sm` for visual parity with the rest of the page
- `.ent-filter-chip` / `.ent-filter-chip.active` — the dismissible/re-addable "Commercial only" picker filter
- `.ent-reco-card`, `.ent-reco-fill-badge`, `.ent-reco-stages` — Recommended Additions cards
- `.ent-add-btn-full`, `.ent-add-btn-minimal`, `.ent-add-actions-{lg|sm}` — the two "add to stack" choice buttons (spacious on recommendation cards, compact inside the gap-search popout)
- `.gap-search-btn`, `.gap-panel`, `.gap-candidate` — the matrix's "Find solutions" popout for empty benchmark-matrix cells

---

## Pre-Classified Agent Catalogue

The local database (`agents.db`) currently holds **81 agents — 78 classified, 1 pending, 2 rejected**. `build_agents_db.py` seeds the initial set (idempotent — checks for existing names before inserting); subsequent agents were added via the wizard and auto-classifier. Production (Railway) runs against PostgreSQL and may have drifted from this local snapshot — see [Deployment](#deployment).

Notable entries: AIEQ/EquBot · Numerai · Kavout K-Score · RavenPack · Kensho · AlphaSense · Dataminr · BlackRock Aladdin Copilot · BlackRock AlphaAgents · FinGPT/FinMem · BloombergGPT/ASKB · FactSet Mercury · Morningstar Mo · Goldman Sachs AI Assistant · JPMorgan LLM Suite · JPMorgan LOXM · Hebbia · Morgan Stanley AI Assistant · Morgan Stanley Debrief · Panthera Decision GPS · Shavandi & Khedmati Multi-Agent DRL · MSCI AI Portfolio Insights · Clarity AI · NICE Actimize SURVEIL-X · Behavox · Ayasdi · Blueflame AI · IndexGPT/COIN · ShareWorks/Equity Edge · Citi Sky/Arc · Aiden · TOGGLE Copilot · InvestGPT · Pluto.fi · Portrait Analytics · Terminal X · Bridget/ThemeWise · ARKEN Finance · and more

**URL flag**: ARKEN Finance (ID:37) URL `arkenfinance.com` resolves to a DeFi swap platform, not the AI portfolio construction tool described. Correct URL unverified — requires manual check.

**`agent_type` flag**: Panthera Decision GPS is tagged `commercial` in the seed data, which surfaces it in the Enterprise Stack's commercial-only filter and recommendation module — but it reads elsewhere (e.g. the README's catalogue list, `framework.html`'s product-type examples) as Panthera's own in-house build. Not corrected here since it's a data classification call, not an app bug; flagged for a manual seed-data review.

---

## Key Design Decisions

- **Session-based wizard**: Draft state stored in `session['wizard_draft']`; no partial DB rows during multi-step form.
- **JSON columns**: `stages`, `key_features`, and `rationale` are stored as JSON strings in TEXT columns. Parsed via model properties.
- **Single advantage per agent**: By design — forces analysts to identify the primary edge.
- **Export classified only**: Pending/rejected agents are excluded from all exports to keep reports clean.
- **Auto-classify uses tool_use**: Forces Claude to return structured JSON rather than parsing free text.
- **Database init on startup**: `db.create_all()` called in `app.py`; safe to run repeatedly.
- **Autonomy pip uses CSS `::after`**: The matrix pip indicator is a pseudo-element on `.agent-badge` inside `.matrix-table-3d .badge-container[data-autonomy="..."]`. No extra HTML — just a `data-autonomy` attribute on the container drives all four colors. Scoped to the matrix table so it doesn't affect badges elsewhere.
- **`full` autonomy threshold**: Reserved for live-deployed systems with **zero** human veto on individual decisions. "High" autonomy is for systems that execute within human-set parameters (LOXM, Aiden). "Full" is for systems where the AI owns the entire decision loop (AIEQ, Numerai).
- **Scatter view groups**: Ordered `full → high → medium → low` top-to-bottom; fully autonomous agents always appear in their own crimson-labeled group at the top.
- **Dual database backend via `DATABASE_URL`**: `app.py` reads `DATABASE_URL` and falls back to local SQLite if unset; `postgres://` is rewritten to `postgresql://` because SQLAlchemy 1.4+ dropped the old scheme. Lets the same codebase run locally (SQLite) and on Railway (Postgres) with no code changes.
- **Category migration is unconditional, not additive**: `_migrate_db()` re-applies every `AGENT_CATEGORY_SEED` mapping and clears dissolved/explicitly-uncategorized agents on every startup, so a taxonomy rename/restructure (see "Taxonomy v2" in `DEV_LOG.md`) propagates automatically without a manual data-fix script.
- **Landing page is the framework explainer, not the matrix**: `/` and `/framework` both render `framework.html`; the matrix moved to `/matrix` (see `DEV_LOG.md`, "Framework as landing page"). Anything that does `url_for('matrix')` still resolves correctly.
- **No separate "Profile" entity for the Enterprise Stack**: there's exactly one implicit profile, modeled as a single `Agent.in_stack` boolean column rather than a join table or a `Profile` model. Simplest thing that works for a single-user local tool; revisit only if multi-tenancy is ever required.
- **"Add name & link only" inserts a new row instead of stripping fields off the existing one**: keeps the catalogue's classification of an agent fully intact (other users/views still see it correctly classified) while letting this user's stack carry an unopinionated placeholder under the same name. The dedup-by-name check (`stack_names` in `enterprise()`) is what keeps the original from also reappearing in gap search / recommendations afterward.
- **Recommendations are computed from `gap_candidates`, not a second pass over the catalogue**: `reco_score` just re-aggregates the dict the gap-search popouts already built, scoped to `agent_type == "commercial"`. One source of truth for "what would help" — the matrix's popout and the recommendation cards can't drift out of sync.
- **Stack-composition bar charts are intentionally count-based, not catalogue ratios**: an earlier version sized each bar as `your_count / catalogue_count`, which read as "how big a slice of the market you own" rather than "how many tools you have." Bars now scale to the max count *within that chart only*.
- **Popover/tooltip `container: "body"`**: both are initialized in `app.js` with this option because several trigger icons live inside `overflow:auto` ancestors (the matrix scroll wrapper, the gap-search popout) that would otherwise clip or paint-order the floating bubble underneath page content.

---

## Deployment

Live instance: see the link in `README.md`. Hosted on **Railway**, started via `Procfile`:
```
web: cd ai_agent_classifier && gunicorn app:app --bind 0.0.0.0:$PORT --workers 2
```

**Required env vars in production**:
| Var | Purpose |
|---|---|
| `DATABASE_URL` | PostgreSQL connection string (Railway-provisioned) |
| `SECRET_KEY` | Flask session secret (falls back to `os.urandom(24)` if unset — sessions won't survive a restart without this) |
| `ANTHROPIC_API_KEY` | Only needed if running `auto_classify.py` against the deployed environment |

**Migrating data**: `migrate_to_postgres.py` is a one-time script that copies all rows from local `instance/agents.db` into the Postgres `DATABASE_URL` target, creating the table if missing and re-syncing the `id` sequence. It is not run automatically — invoke manually when seeding a fresh Postgres instance from local data.
