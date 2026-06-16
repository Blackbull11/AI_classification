# CLAUDE.md — AI Agent Classification System

## Project Overview

**Panthera AI Agent Classifier** — a Flask web application for cataloguing, classifying, and exporting AI agents used in investment management. Built for the Panthera Group, it maps commercial, in-house, and academic AI systems against the firm's proprietary **Swan Theory** complexity framework and a 7-stage investment process pipeline.

- **Entry point**: `ai_agent_classifier/app.py` → `python app.py` (port 5000)
- **Database**: SQLite at `ai_agent_classifier/instance/agents.db`
- **Framework**: Flask + SQLAlchemy (Python) · Bootstrap 5.3.3 dark theme (frontend)

---

## Tech Stack

| Layer | Technology |
|---|---|
| Web framework | Flask |
| ORM / DB | SQLAlchemy + SQLite |
| Frontend | Bootstrap 5.3.3 + vanilla JS |
| AI auto-classifier | Anthropic Claude API (`claude-opus-4-8`) |
| Excel export | openpyxl |
| Word export | python-docx |
| PDF export | reportlab |

**Dependencies**: `ai_agent_classifier/requirements.txt`  
`pip install flask flask-sqlalchemy python-docx openpyxl reportlab anthropic`

For auto-classification, set env var:
```
ANTHROPIC_API_KEY=sk-...
```

---

## File Structure

```
AI_classification/
├── CLAUDE.md                      ← this file
├── DEV_LOG.md                     ← rolling development log
├── CLASSIFICATION_GUIDE.md        ← Swan Theory framework documentation
└── ai_agent_classifier/
    ├── app.py                     ← Flask routes + session wizard logic
    ├── models.py                  ← SQLAlchemy Agent model
    ├── auto_classify.py           ← Claude API batch classifier
    ├── exports.py                 ← Excel / Word / PDF export engine
    ├── build_agents_db.py         ← Seed 40+ pre-classified agents
    ├── seed_data.py               ← Legacy seed (disabled, returns early)
    ├── requirements.txt
    ├── instance/
    │   └── agents.db              ← SQLite database
    ├── static/
    │   ├── css/style.css          ← Design system (CSS custom properties)
    │   ├── js/app.js              ← Bootstrap tooltip init + flash dismiss
    │   └── img/                   ← Panthera logo (PNG + SVG)
    └── templates/
        ├── base.html              ← Master layout (navbar, flash messages)
        ├── matrix.html            ← 3D cube classification matrix + autonomy scatter
        ├── pipeline.html          ← Agent lifecycle management table
        ├── wizard.html            ← 4-step classification wizard
        ├── agent_detail.html      ← Per-agent profile view
        └── guide.html             ← Agent Finder — 4-step questionnaire + filtered results
```

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
| `status` | TEXT NOT NULL | `pending` · `classified` · `rejected` |
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

---

## Flask Routes

### Pages
| Method | Path | Function | Description |
|---|---|---|---|
| GET | `/` | `matrix()` | 3D classification matrix + autonomy scatter view |
| GET | `/pipeline` | `pipeline()` | Agent lifecycle table |
| GET | `/guide` | `guide()` | Agent Finder — 4-step questionnaire, JS-filtered results |
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
| POST | `/quick-add` | Add agent with name + URL only (status: pending) |
| POST | `/agents/<id>/reject` | Mark agent as rejected |
| POST | `/agents/<id>/restore` | Restore rejected → pending |
| POST | `/delete/<id>` | Permanently delete agent |

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

---

## Wizard Flow (4 Steps)

Used for **add**, **edit**, and **classify** modes. State stored in `session['wizard_draft']`.

| Step | Fields |
|---|---|
| 1 | name, url, description, agent_type |
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
- `.view-toggle-group`, `.vt-btn` — matrix / scatter view switcher

---

## Pre-Classified Agent Catalogue

The live database (`agents.db`) contains **77 classified agents**. `build_agents_db.py` seeds the initial set; subsequent agents were added via the wizard and auto-classifier.

Notable entries: AIEQ/EquBot · Numerai · Kavout K-Score · RavenPack · Kensho · AlphaSense · Dataminr · BlackRock Aladdin Copilot · BlackRock AlphaAgents · FinGPT/FinMem · BloombergGPT/ASKB · FactSet Mercury · Morningstar Mo · Goldman Sachs AI Assistant · JPMorgan LLM Suite · JPMorgan LOXM · Hebbia · Morgan Stanley AI Assistant · Morgan Stanley Debrief · Panthera Decision GPS · Shavandi & Khedmati Multi-Agent DRL · MSCI AI Portfolio Insights · Clarity AI · NICE Actimize SURVEIL-X · Behavox · Ayasdi · Blueflame AI · IndexGPT/COIN · ShareWorks/Equity Edge · Citi Sky/Arc · Aiden · TOGGLE Copilot · InvestGPT · Pluto.fi · Portrait Analytics · Terminal X · Bridget/ThemeWise · ARKEN Finance · and more

**URL flag**: ARKEN Finance (ID:37) URL `arkenfinance.com` resolves to a DeFi swap platform, not the AI portfolio construction tool described. Correct URL unverified — requires manual check.

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
