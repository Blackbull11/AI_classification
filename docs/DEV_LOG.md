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

<!-- APPEND NEW SESSIONS ABOVE THIS LINE -->
