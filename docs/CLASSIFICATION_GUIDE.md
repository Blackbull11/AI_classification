# AI Agent Classification Guide

## Academic Foundation

This classification system implements the multi-dimensional framework proposed in:

> **Schuller, B., Wierckx, T., Kuhn, M., & Zilic, I.** (2025). *A Multi-Dimensional Classification System For AI Agents In The Investment Industry*. SSRN Working Paper. https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6290078

The paper introduces a structured taxonomy for mapping AI systems against the investment process, arguing that the proliferation of AI agents in asset management requires a principled framework — one that captures not only *what* an agent does but *how* it behaves epistemically, where it intervenes in the investment workflow, and what class of competitive advantage it confers.

The framework rests on four orthogonal dimensions:

1. **Complexity** — epistemic classification via Swan Theory (how well-defined is the underlying problem?)
2. **Comparative Advantage** — what edge does the agent generate? (informational, analytical, or behavioral)
3. **Autonomy** — what degree of human oversight remains? (low → medium → high → fully autonomous)
4. **Investment Process Stage** — which phase of the investment lifecycle does the agent support?

A fifth dimension — **Agent Type** (commercial / in-house / academic) — is added for provenance tracking.

A sixth field — **Category Label** (10 functional clusters, CAT-1 through CAT-10) — is tracked for catalogue organization and Agent Finder filtering. It is a Panthera platform addition, not part of the original academic framework.

---

## Swan Theory — Theoretical Background

The complexity dimension adapts Nassim Nicholas Taleb's *Black Swan* theory (Taleb, 2007) into a four-tier operational taxonomy calibrated to the specific epistemic challenges of investment decision-making.

Taleb's original insight — that financial markets are dominated by rare, high-impact events that lie outside the predictive reach of classical probability models — is generalized here into a spectrum of *outcome knowability*. The key question is not whether uncertainty exists (it always does) but whether the **probability distribution of outcomes** can be meaningfully characterized.

| Tier | Label | Epistemic Status | Taleb Mapping |
|---|---|---|---|
| `white` | White Swan | Distribution fully known and stable | Risk (classical probability) |
| `light-grey` | Light-Grey Swan | Distribution theoretically exists but must be discovered | Mild uncertainty |
| `dark-grey` | Dark-Grey Swan | Causal structure understood but distribution non-parametric | Deep uncertainty |
| `black` | Black Swan | Distribution unknowable; structural singularity | True Black Swan domain |

This taxonomy operationalizes the distinction between **risk** (quantifiable), **uncertainty** (unquantifiable but bounded), and **radical uncertainty** (unknowable in principle) — a distinction traceable through Knight (1921), Keynes (1921), and Taleb (2007) — for the practical purpose of AI system classification.

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
| `autonomy` | TEXT | Yes | `"low"` \| `"medium"` \| `"high"` \| `"full"` |
| `agent_type` | TEXT | Yes | `"commercial"` \| `"in-house"` \| `"academic"` |
| `complexity` | TEXT | Yes | `"white"` \| `"light-grey"` \| `"dark-grey"` \| `"black"` |
| `stages` | TEXT (JSON) | Yes | JSON array of stage keys (see below) |
| `category_id` | TEXT | Yes | One of 10 category ids (CAT-1…CAT-10), or `NULL` if uncategorized — see §4a below |
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
| `light-grey` | Light-Grey Swan | A distribution theoretically exists but is non-stationary, fat-tailed, or hard to fit. The signal must be searched for with ML or heuristics, not read off directly. |
| `dark-grey` | Dark-Grey Swan | A causal identification problem: we know the drivers, but the causal chain cannot be fully modeled. Requires scenario analysis and expert judgment. |
| `black` | Black Swan | The distribution of outcomes is fundamentally unknowable. Novel, unprecedented, structurally uncertain situations. |

**Theoretical grounding:**

The `white` / `light-grey` boundary maps to Knight's (1921) distinction between *risk* and *uncertainty*: white-swan problems are in the risk domain (quantifiable); light-grey problems involve uncertainty that can be reduced with data and ML but not eliminated.

The `dark-grey` / `black` boundary maps to the transition between *deep uncertainty* (structural but non-parametric causal systems) and *radical uncertainty* (Taleb's Black Swan domain, where the reference class itself does not exist).

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

### 2. Comparative Advantage

*Schuller et al. (2025) §3.2* — What **edge** does this agent provide to the investment firm?

The framework adapts the information-advantage taxonomy common in market microstructure theory: agents differ not just in capability but in the *type* of asymmetry they exploit.

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

*Schuller et al. (2025) §3.3* — How much human oversight is required for the agent to act?

| Value | Meaning |
|---|---|
| `low` | **Human-in-the-loop.** The agent surfaces recommendations, insights, or alerts. A human reviews and makes every decision. |
| `medium` | **Semi-autonomous.** The agent acts within defined parameters but humans monitor and can intervene. May require periodic human review. |
| `high` | **Fully autonomous within constraints.** The agent executes decisions within pre-configured parameters without per-action human approval. |
| `full` | **Fully Autonomous.** No human veto on individual decisions. The AI owns the complete decision loop including live capital deployment. |

The `full` tier is reserved for systems where there is **no human override mechanism** on individual decisions — systems that both make and execute investment decisions autonomously (e.g. AIEQ/EquBot, Numerai Meta Model). "High" autonomy applies to systems that execute within human-set parameters; "full" applies when the parameters themselves are AI-determined.

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

### 4a. Category Label

A functional cluster describing the agent's primary role in the investment workflow — orthogonal to the four dimensions above. Ten categories, defined in `app.py` as `CATEGORIES` and assigned per-agent via `AGENT_CATEGORY_SEED`:

| ID | Category | What distinguishes it |
|---|---|---|
| CAT-1 | Autonomous Trading Engines | AI drives signal-to-execution end-to-end with no per-trade human input |
| CAT-2 | AI Execution Optimizers | Receives a trading decision from upstream; optimizes only *how* it's executed |
| CAT-3 | Agentic Quant Research Systems | AI decides *what* to research, not just how to execute a human-defined query |
| CAT-4 | Quantitative Signal & Screening Tools | Human defines the question; tool returns scores/signals as input to a human decision |
| CAT-5 | AI Portfolio Construction & Management | Constructs and manages actual allocations within a pre-approved mandate |
| CAT-6 | Investment Research & Document Intelligence | Pull-based, query-driven synthesis over documents/filings/research |
| CAT-7 | Market Intelligence & Real-Time Monitoring | Push-based — proactively surfaces alerts without being queried |
| CAT-8 | Risk, AML & Surveillance Monitors | Detects misconduct/financial crime in transaction/communication data |
| CAT-9 | ESG & Regulatory Compliance Platforms | Sustainability and regulatory-reporting workflows, not misconduct detection |
| CAT-10 | Client & Stakeholder Intelligence | Serves the advisor-client / IR relationship, not the investment decision |

Categories are **lenses, not rigid boxes** — pick the cluster that matches the agent's primary workflow role. Some general-purpose bank LLM suites (e.g. Goldman Sachs AI Assistant, JPMorgan LLM Suite, Kensho) are intentionally left uncategorized rather than forced into a poor fit. `auto_classify.py` does not assign categories — they are set only via seed data (`build_agents_db.py` / `AGENT_CATEGORY_SEED`) or manual edit in the wizard / `/admin`.

---

### 5. Stages

*Schuller et al. (2025) §3.4* — Which phases of the investment process does this agent support? **Select all that apply.**

The seven-stage pipeline maps the full lifecycle of an investment decision, from idea origination through to investor reporting.

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
> "Classified Light Grey Swan because equity return distributions are theoretically estimable but non-stationary and fat-tailed in practice — the true distribution must be searched with ML, not read off directly. Analytical advantage: the crowdsourcing mechanism aggregates thousands of diverse models, which is itself evidence that no single model reliably finds the distribution. Autonomy is Full because the Meta Model trades its own book with no human veto on individual position decisions."

---

## References

- Taleb, N. N. (2007). *The Black Swan: The Impact of the Highly Improbable*. Random House.
- Knight, F. H. (1921). *Risk, Uncertainty and Profit*. Hart, Schaffner & Marx; Houghton Mifflin.
- Keynes, J. M. (1921). *A Treatise on Probability*. Macmillan.
- Schuller, B., Wierckx, T., Kuhn, M., & Zilic, I. (2025). *A Multi-Dimensional Classification System For AI Agents In The Investment Industry*. SSRN Working Paper #6290078. https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6290078

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
