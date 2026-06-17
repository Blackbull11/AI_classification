# DEV_LOG.md — Development Tracking

> **Instructions for Claude Code**: Update this file at the end of every prompt session. Add a new entry under `## Sessions` with the date, a one-line summary, files changed, and open items. Never delete old entries — append only.

---

## Project: Panthera AI Agent Classifier

**Stack**: Flask · SQLAlchemy · SQLite · Bootstrap 5 · Anthropic Claude API  
**Repo root**: `c:\Users\siand\dev\AI_classification\`  
**App entry**: `ai_agent_classifier/app.py`

---

## Feature Status

| Feature | Status | Notes |
|---|---|---|
| Classification matrix view (`/`) | ✅ Complete | 3D cube design, filter by advantage |
| Pipeline management (`/pipeline`) | ✅ Complete | Status filter, quick-add, all actions |
| 4-step classification wizard | ✅ Complete | Add / Edit / Classify modes |
| Agent detail page | ✅ Complete | Profile card + stage timeline |
| Quick-add (name + URL only) | ✅ Complete | Creates pending agent |
| Auto-classify via Claude API | ✅ Complete | `auto_classify.py`, tool-forced JSON |
| Excel export | ✅ Complete | 3 sheets: matrix, details, stats |
| Word export | ✅ Complete | Cover + TOC + per-agent sections |
| PDF export | ✅ Complete | Same structure, ReportLab |
| REST API (`/api/agents`) | ✅ Complete | Full JSON of all agents |
| Seed catalogue (40+ agents) | ✅ Complete | `build_agents_db.py` |
| Reject / Restore / Delete | ✅ Complete | Status lifecycle management |
| Agent Finder / Guide tab (`/guide`) | ✅ Complete | 4-step questionnaire, JS-filtered results |
| Framework page (`/framework`) | ✅ Complete | Visual explainer of all 3 axes + supporting dimensions |
| `full` autonomy tier | ✅ Complete | Pulsing crimson pip; applied to AIEQ (ID:1) + Numerai (ID:2) |
| Autonomy Scatter Plot view | ✅ Complete | Toggle on matrix page; dots = agents, X=stage, Y=autonomy |

---

## Known Issues & Tech Debt

> Add items here as they are discovered. Mark resolved items with ✅ and the date.

- [ ] No authentication / user accounts — app is open to anyone on the network
- [ ] `seed_data.py` is disabled (returns early); either clean up or re-enable
- [ ] `err.txt`, `out.txt`, `run_stderr.txt` etc. are leftover process logs — should be gitignored
- [ ] No `.gitignore` exists at project root
- [ ] No unit or integration tests
- [ ] ARKEN Finance (ID:37) URL (`arkenfinance.com`) resolves to a DeFi swap platform — correct URL unknown, needs manual verification

---

## Sessions

---

### 2026-06-17 — Flask-Admin panel at /admin

**Summary**: Integrated Flask-Admin 2.2.0 to provide a full database CRUD interface at `/admin`. The `AgentModelView` gives a searchable, filterable list of all agents plus an edit form with proper dropdowns for all enum fields (status, advantage, complexity, autonomy, agent_type, category_id) and TextArea fields with JSON validation for the three JSON columns (stages, key_features, rationale).

**Files changed**:
- `requirements.txt` — added `flask-admin`
- `ai_agent_classifier/app.py` — added imports (`flask_admin.Admin`, `flask_admin.contrib.sqla.ModelView`, `wtforms.TextAreaField`); added `AgentModelView` class with column config, form_choices, form_overrides, JSON validation in `on_model_change`; registered `Admin` instance at `/admin` and added the view at module level

**Design decisions**:
- `form_choices` covers all discrete fields so users get dropdowns, not raw text inputs
- JSON fields (stages, key_features, rationale) kept as TextArea with placeholder hints showing expected format; `on_model_change` validates JSON before saving to prevent corrupt data
- Admin registered at module level (not inside `if __name__ == "__main__"`) so it works under gunicorn too
- `template_mode` omitted — Flask-Admin 2.x removed that parameter

**Open items**:
- Admin panel has no authentication — only safe for local/internal use; add `is_accessible()` override if exposed on a network

---

### 2026-06-17 — Autonomy Scatter: category grouping boxes

**Summary**: Added category group boxes to the Autonomy Scatter view. Within each autonomy band, bars are now sorted and packed by their category label (e.g. "Trading Engine", "Market Intelligence"), then visually enclosed in a semi-transparent colored rounded rect with a small tag label above. Agents with no category_id are grouped together without a colored box. Also added `category_id` to the matrix route's `agents_json` payload and passed `CATEGORIES` to the matrix template.

**Files changed**:
- `ai_agent_classifier/app.py` — added `category_id` field to matrix `agents_json`; added `categories=CATEGORIES` to `render_template()` call
- `ai_agent_classifier/templates/matrix.html` — added `SCATTER_CATEGORIES` JS lookup; slot enrichment computes `topCatId`; band packing now groups by category then packs rows per group; draw loop draws colored category box + label tag before each group's bars; layout constants updated (`CAT_LABEL_H`, `CAT_BOX_PAD`, `CAT_GAP`)

**Design decisions**:
- Category box fill: category hex color at 9% opacity; border at 28% opacity; rx=5
- Label tag: small pill above the box top-left, filled at 18% opacity; text in full category color, uppercase, 8.5px
- Agents with no category grouped into a single un-colored group at the end of each band
- Category order within band = first-seen order (matches agent insertion order, roughly by autonomy level)

**Open items**: none from this session

---

### 2026-06-17 — Framework as landing page + animated CTA

**Summary**: Made the Framework page the app's landing page and added an animated "Explore the Matrix" CTA button at the bottom.

**Files changed**:
- `app.py` — matrix route changed from `"/"` to `"/matrix"`; framework route now serves both `"/"` and `"/framework"` via two decorators
- `templates/framework.html` — added `@keyframes` animations (`fw-glow-pulse`, `fw-arrow-bounce`, `fw-arrow-appear`) and CTA component classes (`.fw-cta-wrap`, `.fw-cta-btn`, `.fw-cta-arrow`, `.fw-cta-secondary`) to the inline `<style>` block; replaced the plain bottom button row with a `.fw-cta-wrap` panel featuring a pulsing glow button and bouncing arrow

**Design decisions**:
- `url_for('matrix')` still resolves to `/matrix` — no template changes needed elsewhere
- `pending_count` already provided by `inject_globals` context processor, so `/` on the framework route has no missing variables
- Animations are page-scoped (inline style block) to keep `style.css` clean

**Open items**: none from this session

---

### 2026-06-17 — Framework page content alignment with academic paper

**Summary**: Applied four targeted content edits to `framework.html` to align it precisely with the source Panthera paper (Schuller, Wierckx, Kuhn & Zilic, 2025). No CSS, layout, or visual theme was altered.

**Files changed**:
- `templates/framework.html` — four modifications:
  1. **Thesis grid**: replaced all four `.fw-thesis-card` headings and body text to match paper's exact problem framing (Inconsistent Taxonomy / Poor Strategic Deployment / Lack of Scalability & Interpretability / Regulatory & Ethical Ambiguity)
  2. **Swan card descriptions**: tightened White/Light Grey/Dark Grey/Black Swan `fw-cat-desc` text to reflect paper's epistemological language (objective probability basis; substantial search; hypothetico-deductive model; mathematical formula critique)
  3. **Informational Advantage**: extended description to note that barriers have "dropped dramatically due to web scraping, alternative data, and faster data feeds"
  4. **Supporting Dimensions section**: renamed from "Autonomy & Agent Type" → "Autonomy & Evaluation Parameters"; updated subtitle to spectrum framing; deleted Agent Type column (Commercial / In-House / Academic) and replaced with four Evaluation Parameters cards (Learning Capability, Interaction Mode, Regulatory Compliance, Decision Function)

**Design decisions**:
- `col-md-7` / `col-md-5` grid preserved; only inner content of `col-md-5` was swapped
- Autonomy's four cards (low/medium/high/full) left unchanged — spectrum framing achieved via subtitle rewrite

**Open items**: none from this session

---

### 2026-06-17 — Agent Category Labels feature

**Summary**: Added an 11-category labelling system ("Category Label") to group agents serving the same functional purpose, enabling a new filter in the Agent Finder and a category field in the wizard. The 11 categories span the investment AI taxonomy: Trading Engine → Execution Optimizer → Quant Alpha Platform → Stock Screener → Decision Copilot → Wealth Advisor → Research Assistant → Market Intelligence → Risk & AML Monitor → ESG & Compliance → Stakeholder Intelligence.

**Files changed**:
- `models.py` — added `category_id = db.Column(db.String(50))`
- `app.py` — added `CATEGORIES` list (11 dicts with id/label/fullName/color), `CATEGORY_MAP`, `AGENT_CATEGORY_SEED` (67 name→category mappings), `_migrate_db()` for automatic column addition + backfill, updated `_wizard_context()` / `_save_step_to_draft()` / all 3 save routes / `edit_agent` / `classify_agent` / `agent_detail` / `guide` routes
- `templates/wizard.html` — Step 1: category `<select>` dropdown (after description); Step 4: "Category" row in review summary table
- `templates/guide.html` — Q5 filter block (11 chips + "Any"), JS: `selectedCat` state + `updateResults()` logic + category pill on result cards; `CAT_LABELS` JS dict from Jinja
- `templates/agent_detail.html` — "Category Label" block in classification sidebar (colored text matching category hex)
- `static/css/style.css` — `.guide-cat-chip.selected` (uses `--cat-chip-color` CSS custom property), `.guide-cat-label` for result cards
- `build_agents_db.py` — `category_id TEXT` added to CREATE TABLE, runtime ALTER migration, `AGENT_CATEGORY_SEED` dict, category_id in INSERT for `agents_data_new`

**Design decisions**:
- Category kept as a **separate Q5 filter** (distinct from the 4 existing filters) with single-select chips per the existing chip system
- Category chip colors use per-chip CSS custom property (`--cat-chip-color`) set via JS so each category gets its own distinct color without generating 11 CSS rules
- Category label on result cards is rendered as a small all-caps muted text above the meta pills
- Migration is safe to run repeatedly: ALTER is guarded by PRAGMA check, UPDATE only fills NULL/empty rows
- 16 agents remain without category (general-purpose LLM suites like GS/JPM/Citi) — intentionally unassigned to avoid forcing a poor fit

**Open items**: none from this session

---

### 2026-06-16 — Agent detail page redesign

**Summary**: Redesigned `agent_detail.html` for better information hierarchy and full-width usage. Replaced the plain 50/50 label-value classification card with a hero header, a wider description+features column (col-xl-7), and a sticky classification sidebar (col-xl-5) using large visual metric blocks per classification axis.

**Changes applied**:
- `templates/agent_detail.html` — new layout: hero header (h1 name, status/type badges, URL, date), description + features on left, classification sidebar on right with `detail-metric-block` blocks per axis and `detail-stage-pill` stage chips
- `static/css/style.css` — added `.detail-hero`, `.detail-hero-name`, `.detail-hero-url`, `.detail-hero-meta`, `.detail-type-chip`, `.detail-section-title`, `.detail-description`, `.detail-features-list`, `.detail-metric-block`, `.detail-metric-label`, `.detail-metric-value`, `.detail-metric-rationale`, `.detail-meta-block`, `.detail-meta-value`, `.detail-stages-block`, `.detail-stage-pill`

**Design decisions**:
- Classification sidebar uses `position:sticky;top:16px` so it stays visible while scrolling long descriptions
- Advantage and Complexity tier show as large colored blocks (1.35rem bold value, tinted background matching the dimension's color palette)
- Autonomy and Agent Type condensed into a 2-column row of smaller meta blocks
- Process stages rendered as colored pills (border + tint matching stage cube palette from matrix)
- Features list uses `→` arrow prefix in accent color instead of default `<ul>` bullets

**Open items**: none from this session

---

### 2026-06-17 — Add 7 new agents as separate entries (non-destructive)

**Summary**: Added BlackRock Aladdin, BlackRock eFront, FinGPT, FinMem, TradingAgents, FinRL-Trading as new individual entries (FinRobot already existed). Modified `build_agents_db.py` to be non-destructive: removed the `os.remove(db_path)` deletion block and added a check-before-insert guard so the script is now idempotent. DB grew to 82 agents.

**Files changed**:
- `ai_agent_classifier/build_agents_db.py` — removed `os.remove(db_path)` block; added `SELECT id … WHERE name = ?` skip guard in insert loop; added 6 new entries to `agents_data_new`; added 7 new name→category_id mappings to `AGENT_CATEGORY_SEED`

**Design decisions**:
- BlackRock Aladdin (white/low/analytical, `institutional-quant-alpha`) and BlackRock eFront (white/low/analytical, `research-due-diligence`) added as separate entries; eFront targets private market DD/monitoring, Aladdin targets public market portfolio analytics
- FinGPT classified low-autonomy (text analysis/signal tool, not a standalone trader); FinMem, TradingAgents, FinRL-Trading all high-autonomy academic agents in `autonomous-trading-engines`
- `build_agents_db.py` is now safe to re-run without data loss — idempotent inserts

**Open items**: none from this session

---

### 2026-06-17 — Framework page

**Summary**: Added a standalone `/framework` page that visually explains the Panthera 3D classification system to someone who has never read the paper. Structured around 6 sections: problem/motivation, 3-axis overview with a mini interactive-style matrix diagram, Complexity Range (Swan tiers), Investment Process (7 stages), Comparative Advantage (3 types with durability bars), and Supporting Dimensions (Autonomy × Agent Type). Ends with a "how to read" guide and CTA links to the Matrix and Guide pages. Added "Framework" nav link to base navbar.

**Files changed**:
- `app.py` — added `/framework` route (static render, no DB queries)
- `templates/base.html` — added Framework nav item
- `templates/framework.html` — new page, ~400 lines, all styles inline in `<style>` block

**Design decisions**:
- All styles scoped locally inside the template (`<style>` block) to avoid polluting the global CSS with page-specific layout
- Swan spectrum rendered with a color bar (risk → uncertainty) to make the axis intuitive at a glance
- Advantage durability shown as a visual progress bar (informational=30%, analytical=60%, behavioral=100%)
- Agent Type section uses border-style (solid/dashed/dotted) to mirror how they render in the scatter plot

**Open items**: none from this session

---

### 2026-06-16 — Update documentation to match current project state

**Summary**: Updated `CLAUDE.md` and `DEV_LOG.md` to reflect all features added since initial creation — `full` autonomy tier, autonomy scatter plot, guide tab, 77-agent catalogue count, ARKEN Finance URL flag.

**Files changed**:
- `CLAUDE.md` — catalogue count 40+ → 77, added ARKEN URL flag, updated design system CSS classes, added scatter/guide to routes and file tree
- `DEV_LOG.md` — feature table now includes scatter plot and `full` autonomy; Known Issues includes ARKEN Finance

**Open items**: none from this session

---

### 2026-06-16 — Comprehensive classification quality pass (all 77 agents)

**Summary**: Systematic cleanup of every agent classification in `agents.db`, using Decision GPS, Affinity AI, AIEQ, Kavout, RavenPack, and Dataminr as quality benchmarks. No classification values (advantage, autonomy, complexity, agent_type, stages) were changed — only textual quality.

**Changes applied**:
- Removed all answer-label prefixes from every rationale field ("Analytical. …" → "…", "Low. …" → "…", "White Swan. …" → "…", etc.)
- Removed all Gemini references: "Correctly classified by Gemini.", "CORRECTION from Gemini (X → Y):", "NOTE: Incorrectly grouped with X by Gemini" — zero remaining
- Rewrote all bare stage lists into parenthetical per-stage explanations (e.g. "Execution. Correctly classified by Gemini." → "Execution (autonomous order placement optimizing against VWAP and arrival price benchmarks).")
- Fixed 3 wrong URLs: Portrait Analytics (`portraitanalytics.com` → `portrait-analytics.com`), Terminal X (`terminalx.com` → `terminal-x.ai`), Bridget/ThemeWise (`bridget.ai` → `bridgewise.com`)
- Updated Terminal X description and features to reflect its actual agentic platform positioning (formerly Project Pluto; not a Bloomberg alternative)
- Updated Bridget/ThemeWise description to cover both products (ThemeWise thematic baskets + Bridget conversational AI)
- Fixed InvestGPT truncated stages field

**Files changed**:
- `ai_agent_classifier/instance/agents.db` — all 77 agents updated

**Known issues**:
- ARKEN Finance (ID:37) URL (`arkenfinance.com`) points to a DeFi crypto swap platform, not the AI portfolio construction tool described. Correct URL not found — flagged for manual verification.

---

### 2026-06-16 — "Fully Autonomous" autonomy tier + matrix pip indicator

**Summary**: Added a fourth autonomy level `full` (Fully Autonomous) for systems that execute live capital allocation with no human veto on individual decisions. Applied to AIEQ/EquBot (ID:1) and Numerai/Meta Model (ID:2). Added a visual autonomy pip — a small colored dot at the bottom-right of every badge in the classification matrix, visible without hovering — plus an autonomy legend row.

**Changes applied**:
- DB: `autonomy='full'` set for AIEQ (ID:1) and Numerai (ID:2)
- `static/css/style.css`: `.agent-badge::after` pip indicator (grey=low, amber=medium, orange=high, crimson=full), pulsing animation for "full", `.legend-aut-*` legend styles
- `templates/matrix.html`: `data-autonomy` attribute on `.badge-container`, autonomy legend section, hover card shows "Fully Autonomous", scatter plot includes "full" group (crimson, top of sort order)
- `templates/wizard.html`: "Fully Autonomous" radio option in step 3 autonomy section
- `templates/agent_detail.html`: maps `full` → "Fully Autonomous" label
- `templates/guide.html`: "Fully Autonomous" filter option + `autLabel()` helper for result cards
- `auto_classify.py`: added `"full"` to autonomy enum with guidance note

**Design decisions**:
- Pip uses CSS `::after` on `.agent-badge` scoped to `.matrix-table-3d` — no extra HTML elements required
- "Full" agents show a pulsing crimson pip to visually signal absence of human oversight
- Scatter plot groups "Fully Autonomous" above "High" in the sort order

---

### 2026-06-16 — Autonomy Scatter: graph-like Gantt redesign

**Summary**: Complete rethink of the Autonomy Scatter view. Each agent is now its own horizontal bar (no grouping). Bars extend across all contiguous stage segments the agent covers (like a Gantt chart) with dashed bridges between non-adjacent segments. Y-axis = autonomy (top = Fully Autonomous, bottom = Low), encoded as a true chart axis on the left with tick marks and band labels. Name label lives inside the bar, colored by advantage (contrast-adjusted for dark/light fills). Click → agent profile. Greedy row-packing keeps the chart compact within each autonomy band.

**Files changed**:
- `ai_agent_classifier/templates/matrix.html` — complete rewrite of `renderScatter()`: `toSegments()` helper, per-agent items, band-based layout with LABEL_W Y-axis column, `segL`/`segR` coordinate helpers, solid rects per contiguous segment, dashed bridges between non-adjacent segments, clip-path text labels

**Design decisions**:
- `toSegments()` merges adjacent stage indices into runs → renders as single solid bar per run
- `segL(s)` / `segR(e)` compute left/right x of a stage range, consistent with COL_W and SEG_GAP
- Left column (88px) holds band labels + tick marks; vertical axis line at x=LABEL_W
- Bands ordered full → high → medium → low (top → bottom = most → least autonomous)
- Removed grouping/detail-panel; every bar is one agent

---

### 2026-06-16 — Autonomy Scatter: compact grouped view (completed)

**Summary**: Completed the grouped-slot redesign of the Autonomy Scatter. Agents sharing the same autonomy tier AND exact stage coverage pattern now collapse into one bar ("slot"). Single-member bars show the agent name; multi-member bars show "FirstName +N" label + click → detail panel listing all agents as clickable chips. Bars are colored by dominant complexity tier, with text color chosen by advantage using light/dark contrast logic. Row count is dramatically lower than the per-agent version (e.g. ~77 agents → ~30 distinct patterns). Detail panel with `#scatterDetailPanel` + `showDetail()` + `window._closeScatterDetail` is fully wired. Greedy row-packing uses slots not individual agents.

**Files changed**:
- `ai_agent_classifier/templates/matrix.html` — complete replacement of `renderScatter()` body with slot-based grouping; per-agent `items` array → `slotMap` → `slots` → `bands`; `showDetail()` and `_closeScatterDetail` restored; band label shows total agent count not slot count; row index bug fixed (`indexOf` → `ri` parameter)

**Design decisions**:
- Grouping key: `(autonomy, sorted_stage_indices)` — exact same stage pattern collapses
- Fill = dominant complexity of slot members; if mixed → warm neutral `#B0A080`
- Text color = advantage color, dark palette (`ADV_ON_DARK`) on dark fills, light palette (`ADV_ON_LIGHT`) on light fills
- Multi-member slot border is slightly thicker (stroke-width 2) to signal grouping
- `window._closeScatterDetail` assigned at SVG render time so the HTML close button `onclick` always reaches the current function

---

### 2026-06-16 — Autonomy Scatter Plot view

**Summary**: Added an "Autonomy Scatter" view accessible via a view-toggle pill above the matrix. Agents are plotted as dots (one per covered stage) with X = process stage, Y = autonomy base score (low=0, med=1, high=2) + 0.15 × number of stages covered. Dot fill = complexity tier (black→white). Label text color = advantage category (behavioral/analytical/informational). Hover tooltip shows name, complexity, advantage, autonomy, and Y-score. Click navigates to agent detail.

**Files changed**:
- `ai_agent_classifier/templates/matrix.html` — added view-toggle group, `id="matrixView"` on matrix widget, scatter widget div + tooltip div, scatter IIFE (SVG rendering + jitter logic + toggle handler)
- `ai_agent_classifier/static/css/style.css` — added `.view-toggle-group`, `.vt-btn`, `.scatter-widget`, `.scatter-legend`, `.scatter-cx-item` (complexity swatches), `.scatter-tooltip`, `.stt-name`, `.stt-meta`

**Design decisions**:
- Scatter rendered lazily (only when first switching to that view)
- Points at same (stage, similar Y) are bucketed and spread horizontally to prevent overlap
- Existing matrix widget and filter bar are unchanged; toggle only hides/shows the two view containers

---

### 2026-06-15 — Agent Finder / Guide tab

**Summary**: Added a `/guide` "Agent Finder" tab — a 4-step questionnaire that filters classified agents by stage, advantage, autonomy, and complexity and presents curated result cards.

**Files changed**:
- `ai_agent_classifier/app.py` — added `/guide` route serving classified agents as JSON to template
- `ai_agent_classifier/templates/base.html` — added "Guide" nav link
- `ai_agent_classifier/templates/guide.html` — new multi-step questionnaire template with JS filtering and result cards
- `ai_agent_classifier/static/css/style.css` — added guide-specific styles (step cards, option grid, stage/advantage color cues, result cards, summary pills)

**Design decisions**:
- Steps reveal progressively (step 1 requires "Continue" button; steps 2–4 auto-advance on radio selection)
- Results sorted by stage-overlap count descending
- All filtering is client-side (no extra DB round-trips); agents JSON embedded at page load

---

### 2026-06-15 — Initial Documentation

**Summary**: Created `CLAUDE.md` (full project context) and `DEV_LOG.md` (this file) from scratch based on codebase exploration.

**Files created**:
- `CLAUDE.md` — project overview, schema, routes, design system, key decisions
- `DEV_LOG.md` — this tracking document

**Files changed**: none

**Open items**:
- None from this session; see Known Issues above

---

### 2026-06-16 — README and CLASSIFICATION_GUIDE academic update

**Summary**: Created `README.md` and upgraded `CLASSIFICATION_GUIDE.md` with full academic framing referencing the founding paper (Schuller, Wierckx, Kuhn & Zilic, 2025, SSRN #6290078). README lists all platform features, installation, and agent catalogue; CLASSIFICATION_GUIDE now includes Swan Theory intellectual lineage (Taleb 2007, Knight 1921, Keynes 1921) and a formal references section.

**Files changed**:
- `README.md` — created: academic foundation, Swan Theory table, screenshot placeholder, full feature list, catalogue, tech stack, installation, file structure, references
- `CLASSIFICATION_GUIDE.md` — added: Academic Foundation section, Swan Theory theoretical background with Taleb/Knight/Keynes lineage, epistemic status column in Swan tier table, `full` autonomy tier docs, formal References section
- `docs/screenshots/` — created directory for matrix screenshot (placeholder; screenshot to be added manually)

**Open items**:
- Add an actual screenshot of the matrix to `docs/screenshots/matrix.png`

### 2026-06-18 — Taxonomy v2: 10-category restructure + category descriptions

**Summary**: Applied the final AI_Agent_Categories_Final.md taxonomy (Zilic/Wierckx/Kühn/Schuller, updated 17 June 2026). Dissolved the old CAT-5 "Investment Decision Copilots"; renumbered categories 5–10; renamed five categories; added descriptions to every category; updated ~25 agent category assignments; added a new "Agent Categories" section (section 6) to the Framework page; added category descriptions under the category name on the agent detail page; and ran DB migration to apply all changes.

**Key structural changes**:
- CAT-5 "Investment Decision Copilots" dissolved — 4 agents redistributed (InvestGPT → CAT-4, Finpilot/Investbanq → CAT-6, Panthera GPS → uncategorized)
- CAT-3 renamed: Institutional Quant Alpha → Agentic Quant Research Systems; FinRobot moved from CAT-1 to CAT-3; Pluto (Robinhood) moved from CAT-3 to CAT-1
- CAT-4 renamed: AI Stock Screeners → Quantitative Signal & Screening Tools; TOGGLE, InvestGPT, Theia Insights, Axyon added; Auquan/Aiera removed
- CAT-5 (new): AI Portfolio Construction & Management (= former CAT-6, renamed); Altruist removed to CAT-10, MDOTM added
- CAT-6 (new): Investment Research & Document Intelligence (= former CAT-7, expanded); AlphaSense, Auquan, Finpilot, Investbanq, Terminal X, Bloomberg ASKB, Needl, SmartKarma, Blueflame AI added; TOGGLE removed
- CAT-7 (new): Market Intelligence & Real-Time Monitoring (= former CAT-8); Acuity moved from CAT-2; Aiera, StockSnips moved here
- CAT-8–10: unchanged names; Hadrius moved from CAT-8 → CAT-9; YourStake/ShareWorks moved from CAT-9 → CAT-10; Altruist added to CAT-10
- Uncategorized: Panthera GPS, Cognaize, Harmonic, Arteria AI, JPMorgan COIN, Atlas AI, Citi Sky, Linedata, GS AI Assistant, JPMorgan LLM Suite, Kensho, Xceptor

**Files changed**:
- `ai_agent_classifier/app.py` — `CATEGORIES` (10 entries with new names, labels, descriptions; `investment-decision-copilots` removed); `AGENT_CATEGORY_SEED` (~61 entries with all reassignments); added `UNCATEGORIZED_AGENTS` list; `_migrate_db()` now unconditionally updates all known agents, clears dissolved category and explicitly uncategorized agents; `/framework` route now passes `categories=CATEGORIES`
- `ai_agent_classifier/build_agents_db.py` — `AGENT_CATEGORY_SEED` updated to match app.py
- `ai_agent_classifier/templates/agent_detail.html` — category card now shows `cat.description` paragraph below the full category name
- `ai_agent_classifier/templates/framework.html` — new section 6 "Agent Categories" (10 card grid with category name, CAT number, and description); "Reading the Matrix" renumbered from 6 → 7

**Open items**: none from this session

---

<!-- APPEND NEW SESSIONS ABOVE THIS LINE -->
