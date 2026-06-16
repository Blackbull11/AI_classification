# AI Agent Classification Guide

This guide explains the database schema, what each classification field means, how to decide the correct value for each dimension, and how to use the automated classifier.

---

## Database Schema

The database is a single SQLite table (`agents`), managed by SQLAlchemy. The file is at `ai_agent_classifier/instance/agents.db`.

| Column | Type | Nullable | Description |
|---|---|---|---|
| `id` | INTEGER | PK | Auto-increment primary key |
| `name` | TEXT | No | Display name of the agent |
| `url` | TEXT | Yes | Product or paper URL |
| `description` | TEXT | Yes | 2–3 sentence technical summary |
| `rationale` | TEXT | Yes | Framework justification for the assigned classification |
| `key_features` | TEXT (JSON) | Yes | JSON array of bullet-point features |
| `advantage` | TEXT | Yes | `"behavioral"` \| `"analytical"` \| `"informational"` |
| `autonomy` | TEXT | Yes | `"low"` \| `"medium"` \| `"high"` |
| `agent_type` | TEXT | Yes | `"commercial"` \| `"in-house"` \| `"academic"` |
| `complexity` | TEXT | Yes | `"white"` \| `"light-grey"` \| `"dark-grey"` \| `"black"` |
| `stages` | TEXT (JSON) | Yes | JSON array of stage keys (see below) |
| `status` | TEXT | No | `"pending"` \| `"classified"` \| `"rejected"` |
| `created_at` | DATETIME | Yes | UTC timestamp of creation |

### JSON fields

`stages` and `key_features` are stored as JSON text in SQLite.

```json
stages       = ["idea-gen", "idea-assess", "monitoring"]
key_features = ["Real-time NLP over 40k news sources", "REST API delivery", "Historical archive"]
```

The model exposes `.stages_list` and `.features_list` as Python lists via properties that call `json.loads()`.

---

## Status Lifecycle

```
quick-add / seed  →  pending  →  classify  →  classified
                              ↘              ↗
                               reject  →  rejected  →  restore  →  pending
```

An agent is `pending` until someone (or the auto-classifier) fills all classification fields and sets `status = "classified"`. Agents can also be `rejected` if they are not relevant to the investment workflow.

---

## Classification Dimensions

### 1. Complexity — Swan Theory Tier

The Swan Theory describes how well-defined the problem domain is, specifically the **probability distribution of outcomes**. This is the most important and most nuanced dimension.

| Value | Label | When to use |
|---|---|---|
| `white` | White Swan | The outcome distribution is well-characterized and stable. Data is abundant and representative. The problem is a pure optimization over a known distribution. |
| `light-grey` | Light Grey Swan | A distribution theoretically exists but is non-stationary, fat-tailed, or hard to fit. The signal must be searched for with ML or heuristics, not read off directly. |
| `dark-grey` | Dark Grey Swan | A causal identification problem: we know the drivers, but the causal chain cannot be fully modeled. Requires scenario analysis and expert judgment. |
| `black` | Black Swan | The distribution of outcomes is fundamentally unknowable. Novel, unprecedented, structurally uncertain situations. |

**Decision heuristic:**

1. Is the objective function fully specified and stable? → `white`
2. Is there a theoretically correct answer but it requires searching with ML to find it? → `light-grey`
3. Do we understand the causal factors but can't fully model the causal chain? → `dark-grey`
4. Are we in genuinely unknown territory with no reference distribution? → `black`

**Examples:**
- Trade execution optimization (minimize market impact) → `white` — objective is well-defined, microstructure data is abundant
- News sentiment signal generation → `light-grey` — distribution exists but is noisy and non-stationary
- Behavioral bias detection in PM decisions → `dark-grey` — we know biases exist but can't fully model when/how they activate
- Tail-risk scenario modeling for unprecedented macro events → `black`

---

### 2. Advantage

What **edge** does this agent provide to the investment firm?

| Value | When to use |
|---|---|
| `informational` | The agent's edge comes from **data**: faster access to information the market doesn't yet have, broader coverage, or exclusive/proprietary data sources. Ask: "Is the same data available to everyone, but we get it faster or more completely?" |
| `analytical` | The agent's edge comes from **computation**: superior processing, synthesis, or modeling of data that is otherwise available to market participants. Same data, better algorithms. |
| `behavioral` | The agent's edge comes from **psychology**: overcoming the firm's own cognitive biases, or exploiting predictable behavioral patterns of other market participants. |

**Only one value is allowed** — choose the primary edge. If a tool provides both faster data and better analysis, ask: "What would it lose more if stripped away — the data feed or the algorithm?"

**Examples:**
- RavenPack (real-time structured news from 40k sources) → `informational` — the edge is coverage breadth and speed
- BlackRock Aladdin Copilot (synthesis across portfolio exposures) → `analytical` — same Aladdin data, better synthesis
- Essentia Analytics (detects PM's own behavioral biases) → `behavioral` — the edge is psychological, not data or compute

---

### 3. Autonomy

How much human oversight is required for the agent to act?

| Value | Meaning |
|---|---|
| `low` | **Human-in-the-loop.** The agent surfaces recommendations, insights, or alerts. A human reviews and makes every decision. |
| `medium` | **Semi-autonomous.** The agent acts within defined parameters but humans monitor and can intervene. May require periodic human review. |
| `high` | **Fully autonomous.** The agent executes decisions within pre-configured constraints without per-action human approval. |

**Note:** "autonomous" here refers to the investment action, not the underlying software architecture. A fully agentic AI that still requires a human to approve every trade is `low`.

---

### 4. Agent Type

What is the origin of the agent?

| Value | Meaning |
|---|---|
| `commercial` | A product sold or licensed by a vendor. Available to any firm as a SaaS subscription or data feed. |
| `in-house` | Built and operated internally by the investment firm itself. Not available externally. |
| `academic` | A research prototype or tool originating from a university or research institution. May not be production-ready. |

---

### 5. Stages

Which phases of the investment process does this agent support? **Select all that apply.**

| Key | Label | Description |
|---|---|---|
| `idea-gen` | Idea Generation | Generating raw investment ideas, signals, or alpha sources. Top of the funnel. |
| `idea-assess` | Idea Assessment | Screening, evaluating, and scoring investment ideas before committing research resources. |
| `decision` | Decision Point | The moment of deciding to buy, sell, hold, or size a position. |
| `execution` | Execution | Implementing a trade decision: order routing, timing, transaction cost optimization. |
| `monitoring` | Monitoring | Ongoing surveillance of portfolio risk, performance attribution, exposure drift, and alerts. |
| `compliance` | Compliance | Regulatory reporting, pre-trade/post-trade compliance checks, risk limit enforcement. |
| `stakeholder` | Stakeholder Management | Investor reporting, client communication, board materials, governance documentation. |

An agent can span multiple stages. For example, a portfolio risk platform might cover `idea-assess`, `decision`, `monitoring`, and `compliance` simultaneously.

---

### 6. Description

A factual, 2–3 sentence technical summary. It should answer:
- What does the agent do technically?
- What data or capabilities make it distinctive?
- What is its scale or scope (if known)?

Do not include marketing language. Do not include classification rationale here.

---

### 7. Key Features

A JSON array of 3–6 short bullet points. Each bullet should be a concrete, specific fact — not a generic capability claim.

**Good:** `"Deep RL trained on billions of historical trades"`  
**Bad:** `"Uses machine learning for better results"`

---

### 8. Rationale

2–4 sentences explaining **why** the chosen classifications were assigned. Reference the specific Panthera framework criteria. This is the most important free-text field — it is what distinguishes a thoughtful classification from a surface-level one.

A good rationale:
1. Names the classification for each key dimension
2. References the specific criteria that drove the decision
3. Acknowledges any borderline calls

**Example:**
> "Classified Light Grey Swan because equity return distributions are theoretically estimable but non-stationary and fat-tailed in practice — the true distribution must be searched with ML, not read off directly. Analytical advantage: the crowdsourcing mechanism aggregates thousands of diverse models, which is itself evidence that no single model reliably finds the distribution. Autonomy is High because the Meta Model trades its own book autonomously within pre-set parameters."

---

## Auto-Classifier Script

`auto_classify.py` uses `claude-opus-4-8` with adaptive thinking and forced tool use to automatically classify agents. It requires the `anthropic` Python package and an `ANTHROPIC_API_KEY` environment variable.

### Setup

```bash
cd ai_agent_classifier
pip install anthropic
set ANTHROPIC_API_KEY=sk-ant-...
```

### Usage

**Classify all pending agents:**
```bash
python auto_classify.py
# or equivalently:
python auto_classify.py pending
```

**Add a new agent and classify it immediately:**
```bash
python auto_classify.py add "Kensho LENS"
python auto_classify.py add "Two Sigma Venn" --url https://venn.twosigma.com
```

### How it works

1. Queries the database for all agents with `status = "pending"` (or creates a new record)
2. Sends the agent name and URL to Claude with the Swan Theory framework as a system prompt
3. Forces Claude to respond via the `classify_agent` tool, producing a structured JSON object
4. Writes all fields back to the database and sets `status = "classified"`

Claude researches the agent based on its training knowledge. For agents released after Claude's knowledge cutoff, provide a URL so Claude can attempt to reason from the domain and context. If the agent is completely unknown, the auto-classifier will still produce a best-effort classification based on the name and any context available — review these manually.

### Reviewing auto-classifications

After running the auto-classifier, review the results in the web app (`/pipeline` → click an agent to see its detail). Pay particular attention to:
- **Complexity tier** — the most nuanced dimension, most likely to need human review
- **Rationale** — should reference specific Swan Theory criteria, not just restate the classification
- **Stages** — ensure nothing is missing; Claude may under-select if the agent's documentation is sparse

To edit a classification, use the Edit button in the web app or re-run with the wizard.
