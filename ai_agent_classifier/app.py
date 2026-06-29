import json
import os
from datetime import date

from flask import (
    Flask,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    send_file,
    session,
    url_for,
)
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from wtforms import TextAreaField

from models import Agent, db
from seed_data import seed_database
from exports import build_excel, build_word, build_pdf

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)
_db_url = os.environ.get("DATABASE_URL", "sqlite:///agents.db")
if _db_url.startswith("postgres://"):
    _db_url = _db_url.replace("postgres://", "postgresql://", 1)
app.config["SQLALCHEMY_DATABASE_URI"] = _db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

admin = Admin(app, name="Panthera Admin", url="/admin")

STAGES = [
    ("idea-gen",    "Idea Generation"),
    ("idea-assess", "Idea Assessment"),
    ("decision",    "Decision Point"),
    ("execution",   "Execution"),
    ("monitoring",  "Monitoring"),
    ("compliance",  "Compliance"),
    ("stakeholder", "Stakeholder Mgmt"),
]
STAGE_KEYS   = [s[0] for s in STAGES]
STAGE_LABELS = [s[1] for s in STAGES]

COMPLEXITIES = [
    ("black",      "Black Swan"),
    ("dark-grey",  "Dark Grey Swan"),
    ("light-grey", "Light Grey Swan"),
    ("white",      "White Swan"),
]

ADVANTAGES = [
    ("behavioral",    "Behavioral"),
    ("analytical",    "Analytical"),
    ("informational", "Informational"),
]

CATEGORIES = [
    {
        "id": "autonomous-trading-engines",
        "label": "Trading Engine",
        "fullName": "CAT-1 — Autonomous Trading Engines",
        "color": "#1A3A2A",
        "description": "Fully or highly autonomous systems that execute trades without per-trade human input. The AI drives the full pipeline from signal generation through live execution, either by selecting portfolios outright or by running user-defined strategies end-to-end.",
    },
    {
        "id": "ai-execution-optimizers",
        "label": "Execution Optimizer",
        "fullName": "CAT-2 — AI Execution Optimizers",
        "color": "#1E3A5F",
        "description": "Narrowly specialized in how an already-decided trade is executed — minimizing market impact, slippage, and timing costs. These agents receive a trading decision from upstream; they do not generate it. The edge is microstructure optimization, not strategy.",
    },
    {
        "id": "institutional-quant-alpha",
        "label": "Quant Research",
        "fullName": "CAT-3 — Agentic Quant Research Systems",
        "color": "#2D5016",
        "description": "The AI drives the research process itself — self-initiating hypothesis generation, running iterative evaluation loops, or orchestrating multi-agent debate without per-step human instruction. Distinct from screeners by autonomy: the system decides what to research, not just how to execute a human-defined query.",
    },
    {
        "id": "ai-stock-screeners",
        "label": "Signal & Screening",
        "fullName": "CAT-4 — Quantitative Signal & Screening Tools",
        "color": "#4A7C59",
        "description": "The human defines the research question; the tool executes the analysis and returns scores, signals, or backtested results. Low autonomy is the structural separator from CAT-3. Output is always an input to a human decision — never a recommendation acted upon without review.",
    },
    {
        "id": "ai-wealth-portfolio-advisors",
        "label": "Portfolio Construction",
        "fullName": "CAT-5 — AI Portfolio Construction & Management",
        "color": "#5C2D6E",
        "description": "Goes beyond signal generation to construct and manage actual portfolio allocations at scale. Output is an actionable portfolio with risk attribution, rebalancing rules, and monitoring — not a signal or research document. Medium autonomy: the system acts within pre-approved mandates; humans review the mandate, not each trade.",
    },
    {
        "id": "research-due-diligence",
        "label": "Research & Intelligence",
        "fullName": "CAT-6 — Investment Research & Document Intelligence",
        "color": "#5C4A1E",
        "description": "Pull-based knowledge synthesis — the human asks a question or defines a task; the system searches documents, filings, research, or databases and produces a synthesized output. Distinguished from CAT-7 by being document-heavy and query-driven rather than push-based and real-time.",
    },
    {
        "id": "market-intelligence-aggregators",
        "label": "Market Intelligence",
        "fullName": "CAT-7 — Market Intelligence & Real-Time Monitoring",
        "color": "#1A4A5C",
        "description": "Push-based intelligence — the system continuously monitors data sources and proactively surfaces alerts or structured signals when relevant events occur, without being queried. Output is a data feed, structured alert, or event notification, not a document or analytical synthesis.",
    },
    {
        "id": "risk-aml-surveillance",
        "label": "Risk & AML Monitor",
        "fullName": "CAT-8 — Risk, AML & Surveillance Monitors",
        "color": "#5C1A1A",
        "description": "Automated watchdog systems that detect misconduct, financial crime, or anomalies in transaction and communication data. The analytical edge is pattern recognition across noisy, high-dimensional data streams. These agents operate in the regulatory compliance perimeter, not the investment decision pipeline.",
    },
    {
        "id": "esg-regulatory-compliance",
        "label": "ESG & Compliance",
        "fullName": "CAT-9 — ESG & Regulatory Compliance Platforms",
        "color": "#2E5C3E",
        "description": "Tools focused on sustainability intelligence, regulatory reporting, and compliance workflow automation. Distinct from CAT-8 in subject matter: these agents assess non-financial risk dimensions (ESG, regulatory obligations, operational due diligence) rather than detecting misconduct or financial crime.",
    },
    {
        "id": "client-stakeholder-intelligence",
        "label": "Stakeholder Intel",
        "fullName": "CAT-10 — Client & Stakeholder Intelligence",
        "color": "#3D3D1A",
        "description": "AI tools serving client-facing teams — relationship intelligence, meeting capture, client reporting, equity plan administration, and investor communications. The output serves the advisor-client or IR relationship, not the investment decision process.",
    },
]
CATEGORY_MAP = {c["id"]: c for c in CATEGORIES}


# ─── Plain-language help text (powers the "?" hover bubbles across the app) ──

COMPLEXITY_DIMENSION_INFO = {
    "title": "Complexity Tier — how predictable is this problem?",
    "body": (
        "Asks one question: how well can we know the range of likely outcomes? "
        "There are 4 tiers, from fully predictable (White Swan) to genuinely "
        "unprecedented (Black Swan).\n\n"
        "It matters because the right AI approach is different at each tier — a "
        "tool built for predictable problems can be actively misleading when "
        "pointed at an unprecedented one. Hover any tier name to see its definition."
    ),
}

COMPLEXITY_INFO = {
    "white": {
        "label": "White Swan",
        "title": "White Swan — predictable, the rules are known",
        "blurb": "Predictable — the rules are known.",
        "body": (
            "Outcomes and their odds can be measured directly from real data. "
            "This is the safest zone for AI: statistical models and automation "
            "don't just work here, they typically beat human judgement.\n\n"
            "Example: trade execution cost optimization, options pricing, "
            "compliance rule-checks."
        ),
    },
    "light-grey": {
        "label": "Light Grey Swan",
        "title": "Light Grey Swan — noisy, the pattern is hidden",
        "blurb": "Noisy — the pattern exists, but it's hidden.",
        "body": (
            "A real signal exists in the data, but it's buried in noise or keeps "
            "shifting over time. Machine learning is needed to find it — and the "
            "result should be treated as a probability, not a certainty.\n\n"
            "Example: news-sentiment trading signals, factor-based stock screening."
        ),
    },
    "dark-grey": {
        "label": "Dark Grey Swan",
        "title": "Dark Grey Swan — understood, but not measurable",
        "blurb": "Understood, but not measurable.",
        "body": (
            "We can reason about the likely causes and effects, but there isn't "
            "enough clean data for a reliable statistical model. This calls for "
            "scenario analysis and expert judgement, with AI as a research "
            "assistant rather than a decision-maker.\n\n"
            "Example: macro regime shifts, geopolitical risk, early-stage credit risk."
        ),
    },
    "black": {
        "label": "Black Swan",
        "title": "Black Swan — unprecedented, no track record",
        "blurb": "Unprecedented — no track record to learn from.",
        "body": (
            "A genuinely novel situation with no comparable historical pattern. "
            "Any model trained on the past is guessing. Human judgement should "
            "lead, with AI used only to support — never replace — that judgement.\n\n"
            "Example: an unprecedented market crisis, a brand-new fraud pattern."
        ),
    },
}

AUTONOMY_DIMENSION_INFO = {
    "title": "Autonomy — how much human oversight remains?",
    "body": (
        "Measures how much a human has to sign off before this tool's output "
        "becomes a real action — from \"AI only assists\" (Low) to \"AI acts with "
        "no human veto at all\" (Fully Autonomous).\n\n"
        "This is usually the first thing a risk or compliance reviewer asks "
        "about a new AI tool. Hover any level to see its definition."
    ),
}

AUTONOMY_INFO = {
    "low": {
        "label": "Low",
        "title": "Low autonomy — AI assists, a human decides",
        "blurb": "AI assists — a human decides everything.",
        "body": (
            "The tool surfaces information, flags, or suggestions. Every action "
            "is reviewed and approved by a person before anything happens. The "
            "safest level, and the right default for high-stakes or "
            "poorly-understood situations.\n\n"
            "Example: a research copilot that summarizes filings for an analyst."
        ),
    },
    "medium": {
        "label": "Medium",
        "title": "Medium autonomy — AI recommends, a human signs off",
        "blurb": "AI recommends — a human signs off.",
        "body": (
            "The tool proposes a specific action (a trade, a rebalancing, a "
            "flag), but a person must actively approve it before it takes "
            "effect. Faster than Low, but a human is still the final checkpoint "
            "on every decision.\n\n"
            "Example: a rebalancing suggestion a PM has to click \"approve\" on."
        ),
    },
    "high": {
        "label": "High",
        "title": "High autonomy — AI acts within limits a human set",
        "blurb": "AI acts — within limits a human already set.",
        "body": (
            "The tool executes on its own, but only inside boundaries a human "
            "configured in advance (position limits, venues, price bands). "
            "Humans monitor outcomes and can intervene, but don't approve each "
            "individual action.\n\n"
            "Example: an execution algorithm working a large order across venues."
        ),
    },
    "full": {
        "label": "Fully Autonomous",
        "title": "Fully Autonomous — AI owns the decision, no veto",
        "blurb": "AI owns the decision — no human veto.",
        "body": (
            "There is no human checkpoint on individual decisions — the system "
            "decides and acts on real capital end-to-end. The highest-stakes "
            "level, and deserves the most scrutiny before adoption: understand "
            "exactly how it fails, not just how it succeeds.\n\n"
            "Example: a fully automated trading model managing its own book live."
        ),
    },
}

STAGE_DIMENSION_INFO = {
    "title": "Investment Process Stage — where does this tool act?",
    "body": (
        "Where in the investment lifecycle a tool actually does its work — "
        "from spotting an opportunity to reporting results to clients. There "
        "are 7 stages, and a single tool can cover more than one. Hover any "
        "stage name to see what happens there."
    ),
}

STAGE_INFO = {
    "idea-gen": {
        "label": "Idea Generation",
        "title": "Idea Generation — where opportunities are first spotted",
        "blurb": "Where opportunities are first spotted.",
        "body": (
            "The top of the funnel: screening the market, scanning data, or "
            "generating hypotheses about what to invest in. AI widens the "
            "universe a person could realistically search by hand.\n\n"
            "Typical output: a candidate list, a sourced lead, a flagged anomaly."
        ),
    },
    "idea-assess": {
        "label": "Idea Assessment",
        "title": "Idea Assessment — where an idea gets tested before it's trusted",
        "blurb": "Where an idea gets tested before it's trusted.",
        "body": (
            "Once an idea exists, it has to be researched, valued, and "
            "stress-tested against the portfolio's existing constraints. AI "
            "accelerates the depth and speed of this due diligence.\n\n"
            "Typical output: financial models, comparable-company analysis, "
            "document review."
        ),
    },
    "decision": {
        "label": "Decision Point",
        "title": "Decision Point — where capital actually gets committed",
        "blurb": "Where capital actually gets committed.",
        "body": (
            "The formal buy / sell / hold / size call. The highest-stakes, most "
            "human-judgement-heavy stage in the process — AI should support this "
            "decision, not make it alone, especially outside the White Swan tier.\n\n"
            "Typical output: a portfolio manager's final sign-off on a position."
        ),
    },
    "execution": {
        "label": "Execution",
        "title": "Execution — where the trade actually happens",
        "blurb": "Where the trade actually happens.",
        "body": (
            "Turning a decision into a filled order: choosing venues, timing, "
            "and order types to minimize cost and market impact. One of the "
            "most mature and AI-friendly stages.\n\n"
            "Typical output: a filled order, at the best achievable price."
        ),
    },
    "monitoring": {
        "label": "Monitoring",
        "title": "Monitoring — keeping watch after the trade is on",
        "blurb": "Keeping watch after the trade is on.",
        "body": (
            "Ongoing tracking of whether a position or portfolio is still "
            "behaving as expected — performance, risk exposure, and whether the "
            "original thesis still holds.\n\n"
            "Typical output: drift alerts, exposure dashboards, thesis-breaking "
            "news flags."
        ),
    },
    "compliance": {
        "label": "Compliance",
        "title": "Compliance — making sure nothing breaks the rules",
        "blurb": "Making sure nothing breaks the rules.",
        "body": (
            "Checking trades and portfolios against regulatory and internal "
            "mandate limits, before and after the fact, and keeping the audit "
            "trail regulators will eventually ask for.\n\n"
            "Typical output: pre-trade limit checks, automated regulatory filings."
        ),
    },
    "stakeholder": {
        "label": "Stakeholder Management",
        "title": "Stakeholder Management — explaining what happened, and why",
        "blurb": "Explaining what happened, and why.",
        "body": (
            "Communicating performance, rationale, and risk to clients, "
            "investors, and internal stakeholders. AI turns raw numbers into a "
            "narrative a non-specialist can act on.\n\n"
            "Typical output: auto-generated client reports, performance summaries."
        ),
    },
}


# ─── Admin panel ──────────────────────────────────────────────────────────────

class AgentModelView(ModelView):
    # List view
    column_list = ("id", "name", "status", "complexity", "advantage", "autonomy", "agent_type", "category_id", "created_at")
    column_searchable_list = ("name", "description", "url")
    column_filters = ("status", "complexity", "advantage", "autonomy", "agent_type", "category_id")
    column_sortable_list = ("id", "name", "status", "complexity", "advantage", "autonomy", "created_at")
    column_default_sort = ("id", False)
    column_labels = {
        "category_id": "Category",
        "agent_type":  "Type",
        "created_at":  "Added",
    }

    # Form layout
    form_columns = (
        "name", "url", "description",
        "agent_type", "category_id", "status",
        "advantage", "complexity", "autonomy",
        "stages", "key_features", "rationale",
    )
    form_choices = {
        "status":      [("pending", "Pending"), ("classified", "Classified"), ("rejected", "Rejected")],
        "advantage":   [("", "— none —"), ("behavioral", "Behavioral"), ("analytical", "Analytical"), ("informational", "Informational")],
        "complexity":  [("", "— none —"), ("black", "Black Swan"), ("dark-grey", "Dark Grey Swan"), ("light-grey", "Light Grey Swan"), ("white", "White Swan")],
        "autonomy":    [("", "— none —"), ("low", "Low"), ("medium", "Medium"), ("high", "High"), ("full", "Full")],
        "agent_type":  [("", "— none —"), ("commercial", "Commercial"), ("in-house", "In-House"), ("academic", "Academic")],
        "category_id": [("", "— none —")] + [(c["id"], c["fullName"]) for c in CATEGORIES],
    }
    form_overrides = {
        "stages":       TextAreaField,
        "key_features": TextAreaField,
        "rationale":    TextAreaField,
    }
    form_widget_args = {
        "description":  {"rows": 4},
        "stages":       {"rows": 2, "placeholder": '["idea-gen", "decision", "monitoring"]'},
        "key_features": {"rows": 4, "placeholder": '["Feature one", "Feature two"]'},
        "rationale":    {"rows": 6, "placeholder": '{"advantage": "...", "complexity": "...", "autonomy": "..."}'},
        "url":          {"placeholder": "https://"},
    }

    # Validate JSON fields before saving
    def on_model_change(self, form, model, is_created):
        for field in ("stages", "key_features", "rationale"):
            raw = getattr(form, field).data or ""
            raw = raw.strip()
            if raw:
                try:
                    json.loads(raw)
                except json.JSONDecodeError as exc:
                    raise ValueError(f"'{field}' is not valid JSON: {exc}") from exc
            setattr(model, field, raw or None)


admin.add_view(AgentModelView(Agent, db.session, name="Agents", endpoint="admin_agents"))


# Maps exact agent DB names → category id for seeding/migration
AGENT_CATEGORY_SEED = {
    "AIEQ / EquBot":                                          "autonomous-trading-engines",
    "Numerai (Meta Model)":                                   "autonomous-trading-engines",
    "Academic Trading Agents (FinGPT / FinMem / TradingAgents)": "autonomous-trading-engines",
    "FLAG-Trader":                                            "autonomous-trading-engines",
    # CAT-2: AI Execution Optimizers
    "JPMorgan LOXM":                                          "ai-execution-optimizers",
    "Shavandi & Khedmati Multi-Agent DRL":                    "ai-execution-optimizers",
    "Aiden (VWAP & Arrival) — RBC Capital Markets":           "ai-execution-optimizers",
    # CAT-3: Agentic Quant Research Systems
    "QuantAgent":                                             "institutional-quant-alpha",
    "JPMorgan IndexGPT":                                      "institutional-quant-alpha",
    "BlackRock AlphaAgents":                                  "institutional-quant-alpha",
    "FinRobot":                                               "institutional-quant-alpha",
    # CAT-4: Quantitative Signal & Screening Tools
    "Kavout":                                                 "ai-stock-screeners",
    "Kavout K-Score":                                         "ai-stock-screeners",
    "StockBench":                                             "ai-stock-screeners",
    "Axyon AI":                                               "ai-stock-screeners",
    "Axyon Foresight":                                        "ai-stock-screeners",
    "Axyon IRIS":                                             "ai-stock-screeners",
    "Boosted.ai":                                             "ai-stock-screeners",
    "Bridget / ThemeWise":                                    "ai-stock-screeners",
    "Neural Alpha":                                           "ai-stock-screeners",
    "SigTech":                                                "ai-stock-screeners",
    "Theia Insights":                                         "ai-stock-screeners",
    "TOGGLE Copilot / Pro":                                   "ai-stock-screeners",
    "InvestGPT (Kavout)":                                     "ai-stock-screeners",
    # CAT-5: AI Portfolio Construction & Management
    "Vise AI":                                                "ai-wealth-portfolio-advisors",
    "ARKEN Finance":                                          "ai-wealth-portfolio-advisors",
    "MDOTM (Sei)":                                            "ai-wealth-portfolio-advisors",
    # CAT-6: Investment Research & Document Intelligence
    "Wokelo Agentic Builder":                                 "research-due-diligence",
    "Hebbia":                                                 "research-due-diligence",
    "V7 Go (Due Diligence Agent)":                            "research-due-diligence",
    "AlphaSense":                                             "research-due-diligence",
    "Auquan":                                                 "research-due-diligence",
    "Finpilot":                                               "research-due-diligence",
    "Investbanq Co-Pilot":                                    "research-due-diligence",
    "EILLA AI":                                               "research-due-diligence",
    "BlackRock Aladdin":                                      "research-due-diligence",
    "DiligenceSquared":                                       "research-due-diligence",
    "Bloomberg ASKB":                                         "research-due-diligence",
    "Terminal X":                                             "research-due-diligence",
    "Morgan Stanley AI Assistant":                            "research-due-diligence",
    "AskResearchGPT (Morgan Stanley)":                        "research-due-diligence",
    "FactSet Intelligence":                                   "research-due-diligence",
    "Blueflame AI":                                           "research-due-diligence",
    "Rogo":                                                   "research-due-diligence",
    "SmartKarma":                                             "research-due-diligence",
    "Needl":                                                  "research-due-diligence",
    # CAT-7: Market Intelligence & Real-Time Monitoring
    "RavenPack News Analytics / Bigdata.com":                 "market-intelligence-aggregators",
    "RavenPack  / Bigdata.com":                               "market-intelligence-aggregators",
    "Dataminr":                                               "market-intelligence-aggregators",
    "Acuity (Acuity Trading)":                                "market-intelligence-aggregators",
    "StockSnips":                                             "market-intelligence-aggregators",
    "Aiera":                                                  "market-intelligence-aggregators",
    # CAT-8: Risk, AML & Surveillance Monitors
    "Ayasdi (SymphonyAI)":                                    "risk-aml-surveillance",
    "NICE Actimize SURVEIL-X / Actimize Intelligence":        "risk-aml-surveillance",
    "Holistic AI":                                            "risk-aml-surveillance",
    "Behavox (Quantum / Polaris)":                            "risk-aml-surveillance",
    # CAT-9: ESG & Regulatory Compliance Platforms
    "Clarity AI":                                             "esg-regulatory-compliance",
    "MSCI AI Portfolio Insights":                             "esg-regulatory-compliance",
    "Riskspan":                                               "esg-regulatory-compliance",
    "Hadrius":                                                "esg-regulatory-compliance",
    "Norm AI":                                                "esg-regulatory-compliance",
    # CAT-10: Client & Stakeholder Intelligence
    "Affinity AI":                                            "client-stakeholder-intelligence",
    "Portrait Analytics":                                     "client-stakeholder-intelligence",
    "AI @ Morgan Stanley Debrief":                            "client-stakeholder-intelligence",
    "Morningstar 'Mo' / Intelligence Engine":                 "client-stakeholder-intelligence",
    "Altruist AI Agents":                                     "client-stakeholder-intelligence",
    "ShareWorks / Equity Edge MCP (Morgan Stanley)":          "client-stakeholder-intelligence",
    "YourStake":                                              "client-stakeholder-intelligence",
}


@app.context_processor
def inject_globals():
    pending_count = Agent.query.filter_by(status="pending").count()
    in_stack_count = Agent.query.filter_by(in_stack=True).count()
    return {
        "pending_count": pending_count,
        "in_stack_count": in_stack_count,
        "today": date.today(),
        "complexity_dim_info": COMPLEXITY_DIMENSION_INFO,
        "complexity_info": COMPLEXITY_INFO,
        "autonomy_dim_info": AUTONOMY_DIMENSION_INFO,
        "autonomy_info": AUTONOMY_INFO,
        "stage_dim_info": STAGE_DIMENSION_INFO,
        "stage_info": STAGE_INFO,
    }


# ─── Matrix ───────────────────────────────────────────────────────────────────

@app.route("/matrix")
def matrix():
    classified = Agent.query.filter_by(status="classified").all()

    # Flat matrix: one row per complexity, all advantages merged per cell
    matrix_flat = {}
    for cx_key, _ in COMPLEXITIES:
        matrix_flat[cx_key] = {}
        for stage_key, _ in STAGES:
            matrix_flat[cx_key][stage_key] = [
                a for a in classified
                if a.complexity == cx_key and stage_key in a.stages_list
            ]

    # Stats
    total_classified     = len(classified)
    behavioral_count     = sum(1 for a in classified if a.advantage == "behavioral")
    analytical_count     = sum(1 for a in classified if a.advantage == "analytical")
    black_swan_count     = sum(1 for a in classified if a.complexity == "black")
    dark_grey_count      = sum(1 for a in classified if a.complexity == "dark-grey")
    low_autonomy_pct     = (
        round(sum(1 for a in classified if a.autonomy == "low") / total_classified * 100)
        if total_classified else 0
    )
    full_autonomy_count  = sum(1 for a in classified if a.autonomy == "full")
    analytical_pct       = (
        round(analytical_count / total_classified * 100) if total_classified else 0
    )
    pending_count = Agent.query.filter_by(status="pending").count()

    # Row totals (unique agents per complexity)
    row_totals = {}
    for cx_key, _ in COMPLEXITIES:
        agents_in_cx = [a for a in classified if a.complexity == cx_key]
        row_totals[cx_key] = len(set(a.id for a in agents_in_cx))

    # Column totals (unique agents per stage)
    col_totals = {}
    for stage_key, _ in STAGES:
        col_totals[stage_key] = len(set(a.id for a in classified if stage_key in a.stages_list))

    # Advantage totals
    adv_totals = {
        "behavioral":    sum(1 for a in classified if a.advantage == "behavioral"),
        "analytical":    sum(1 for a in classified if a.advantage == "analytical"),
        "informational": sum(1 for a in classified if a.advantage == "informational"),
    }

    # Stage bar chart data
    stage_counts = [(label, col_totals[key]) for key, label in STAGES]
    max_stage_count = max((c for _, c in stage_counts), default=1)

    # Advantage bar chart data
    adv_bar_data = [
        ("Informational", adv_totals["informational"], "#EF9F27"),
        ("Analytical",    adv_totals["analytical"],    "#1D9E75"),
        ("Behavioral",    adv_totals["behavioral"],    "#D85A30"),
    ]
    adv_total_for_pct = max(total_classified, 1)

    # Advantage × Stage matrix (new view)
    adv_matrix = {}
    for adv_key, _ in ADVANTAGES:
        adv_matrix[adv_key] = {}
        for stage_key, _ in STAGES:
            adv_matrix[adv_key][stage_key] = [
                a for a in classified
                if a.advantage == adv_key and stage_key in a.stages_list
            ]

    adv_row_totals = {}
    for adv_key, _ in ADVANTAGES:
        adv_row_totals[adv_key] = len(set(
            a.id for a in classified if a.advantage == adv_key
        ))

    agents_json = json.dumps([
        {
            "id":          a.id,
            "name":        a.name,
            "url":         a.url,
            "description": a.description,
            "advantage":   a.advantage,
            "autonomy":    a.autonomy,
            "complexity":  a.complexity,
            "agent_type":  a.agent_type,
            "stages":      a.stages_list,
            "features":    a.features_list,
            "category_id": a.category_id,
        }
        for a in classified
    ])

    return render_template(
        "matrix.html",
        classified=classified,
        matrix_flat=matrix_flat,
        adv_matrix=adv_matrix,
        adv_row_totals=adv_row_totals,
        stages=STAGES,
        complexities=COMPLEXITIES,
        advantages=ADVANTAGES,
        total_classified=total_classified,
        behavioral_count=behavioral_count,
        analytical_count=analytical_count,
        analytical_pct=analytical_pct,
        black_swan_count=black_swan_count,
        dark_grey_count=dark_grey_count,
        low_autonomy_pct=low_autonomy_pct,
        full_autonomy_count=full_autonomy_count,
        pending_count=pending_count,
        row_totals=row_totals,
        col_totals=col_totals,
        adv_totals=adv_totals,
        grand_total=total_classified,
        stage_counts=stage_counts,
        max_stage_count=max_stage_count,
        adv_bar_data=adv_bar_data,
        adv_total_for_pct=adv_total_for_pct,
        agents_json=agents_json,
        categories=CATEGORIES,
    )


# ─── Pipeline ────────────────────────────────────────────────────────────────

STATUS_ORDER = {"pending": 0, "classified": 1, "rejected": 2}

@app.route("/pipeline")
def pipeline():
    agents = Agent.query.all()
    agents = sorted(agents, key=lambda a: (STATUS_ORDER.get(a.status, 9), a.name.lower()))
    pending    = sum(1 for a in agents if a.status == "pending")
    classified = sum(1 for a in agents if a.status == "classified")
    rejected   = sum(1 for a in agents if a.status == "rejected")

    stage_map = dict(STAGES)

    return render_template(
        "pipeline.html",
        agents=agents,
        pending=pending,
        classified=classified,
        rejected=rejected,
        stage_map=stage_map,
        category_map=CATEGORY_MAP,
    )


@app.route("/quick-add", methods=["POST"])
def quick_add():
    name = request.form.get("name", "").strip()
    url  = request.form.get("url",  "").strip()
    next_page = request.form.get("next", "pipeline")
    if next_page not in ("pipeline", "enterprise"):
        next_page = "pipeline"
    if not name:
        flash("Agent name is required.", "warning")
        return redirect(url_for(next_page))
    agent = Agent(name=name, url=url or None, status="pending")
    if request.form.get("in_stack"):
        agent.in_stack = True
    db.session.add(agent)
    db.session.commit()
    if agent.in_stack:
        flash(f"'{name}' added to your enterprise stack — finish classifying it "
              f"in the Pipeline so it appears on your coverage map.", "success")
    else:
        flash(f"'{name}' added to the pipeline.", "success")
    return redirect(url_for(next_page))


# ─── Enterprise Stack ─────────────────────────────────────────────────────────

@app.route("/enterprise")
def enterprise():
    all_agents = Agent.query.filter(Agent.status != "rejected").order_by(Agent.name).all()
    stack_agents     = [a for a in all_agents if a.in_stack]
    stack_classified = [a for a in stack_agents if a.status == "classified"]
    stack_pending    = [a for a in stack_agents if a.status != "classified"]
    classified_all   = [a for a in all_agents if a.status == "classified"]

    # Coverage matrix scoped to the user's stack (complexity × stage)
    stack_matrix = {}
    for cx_key, _ in COMPLEXITIES:
        stack_matrix[cx_key] = {}
        for stage_key, _ in STAGES:
            stack_matrix[cx_key][stage_key] = [
                a for a in stack_classified
                if a.complexity == cx_key and stage_key in a.stages_list
            ]

    # Names already represented in the stack (covers both full and name-only adds),
    # so a tool the user already added isn't suggested again under its catalogue entry
    stack_names = {a.name.strip().lower() for a in stack_agents}

    # For every empty cell, find catalogue agents (not yet in the stack) that cover it
    gap_candidates = {}
    for cx_key, _ in COMPLEXITIES:
        for stage_key, _ in STAGES:
            if stack_matrix[cx_key][stage_key]:
                continue
            candidates = [
                a for a in classified_all
                if a.complexity == cx_key and stage_key in a.stages_list
                and not a.in_stack and a.name.strip().lower() not in stack_names
            ]
            if candidates:
                gap_candidates[f"{cx_key}|{stage_key}"] = candidates

    # Recommendations: commercial-only candidates, ranked by how many gap cells they'd fill
    reco_score = {}   # agent.id -> {"count": int, "stages": set(stage_key)}
    for key, candidates in gap_candidates.items():
        cx_key, stage_key = key.split("|", 1)
        for a in candidates:
            if a.agent_type != "commercial":
                continue
            entry = reco_score.setdefault(a.id, {"agent": a, "count": 0, "stages": set()})
            entry["count"] += 1
            entry["stages"].add(stage_key)
    recommendations = sorted(
        reco_score.values(), key=lambda e: (-e["count"], e["agent"].name.lower())
    )[:6]

    # Row / column totals for the stack matrix
    stack_row_totals = {
        cx_key: len(set(a.id for a in stack_classified if a.complexity == cx_key))
        for cx_key, _ in COMPLEXITIES
    }
    stack_col_totals = {
        stage_key: len(set(a.id for a in stack_classified if stage_key in a.stages_list))
        for stage_key, _ in STAGES
    }

    stages_covered = sum(1 for stage_key, _ in STAGES if stack_col_totals[stage_key] > 0)
    tiers_covered  = sum(1 for cx_key, _ in COMPLEXITIES if stack_row_totals[cx_key] > 0)
    total_cells    = len(STAGES) * len(COMPLEXITIES)
    filled_cells   = sum(
        1 for cx_key, _ in COMPLEXITIES for stage_key, _ in STAGES
        if stack_matrix[cx_key][stage_key]
    )
    fillable_gaps  = len(gap_candidates)
    dead_gaps      = total_cells - filled_cells - fillable_gaps

    autonomy_counts = {
        lvl: sum(1 for a in stack_classified if a.autonomy == lvl)
        for lvl, _ in [("low", None), ("medium", None), ("high", None), ("full", None)]
    }
    advantage_counts = {
        adv_key: sum(1 for a in stack_classified if a.advantage == adv_key)
        for adv_key, _ in ADVANTAGES
    }

    return render_template(
        "enterprise.html",
        all_agents=all_agents,
        stack_agents=stack_agents,
        stack_classified=stack_classified,
        stack_pending=stack_pending,
        stages=STAGES,
        complexities=COMPLEXITIES,
        advantages=ADVANTAGES,
        category_map=CATEGORY_MAP,
        stack_matrix=stack_matrix,
        gap_candidates=gap_candidates,
        recommendations=recommendations,
        stack_row_totals=stack_row_totals,
        stack_col_totals=stack_col_totals,
        stages_covered=stages_covered,
        tiers_covered=tiers_covered,
        total_cells=total_cells,
        filled_cells=filled_cells,
        fillable_gaps=fillable_gaps,
        dead_gaps=dead_gaps,
        autonomy_counts=autonomy_counts,
        advantage_counts=advantage_counts,
    )


@app.route("/enterprise/save", methods=["POST"])
def enterprise_save():
    selected_ids = set(int(i) for i in request.form.getlist("agent_ids") if i.isdigit())
    all_agents = Agent.query.filter(Agent.status != "rejected").all()
    for a in all_agents:
        a.in_stack = a.id in selected_ids
    db.session.commit()
    flash(f"Enterprise stack saved — {len(selected_ids)} tool(s) in your stack.", "success")
    return redirect(url_for("enterprise") + "#picker")


@app.route("/enterprise/toggle/<int:agent_id>", methods=["POST"])
def enterprise_toggle(agent_id):
    agent = Agent.query.get_or_404(agent_id)
    agent.in_stack = not agent.in_stack
    db.session.commit()
    anchor = request.form.get("anchor", "")
    flash(
        f"'{agent.name}' {'added to' if agent.in_stack else 'removed from'} your enterprise stack.",
        "success",
    )
    return redirect(url_for("enterprise") + (f"#{anchor}" if anchor else ""))


@app.route("/enterprise/add-minimal/<int:agent_id>", methods=["POST"])
def enterprise_add_minimal(agent_id):
    """Add a lightweight reference (name + link only) instead of the catalogue's
    full classification — a separate pending record, decoupled from the source agent."""
    source = Agent.query.get_or_404(agent_id)
    clone = Agent(name=source.name, url=source.url, status="pending", in_stack=True)
    db.session.add(clone)
    db.session.commit()
    flash(
        f"'{source.name}' added to your stack as name + link only — classify it from "
        f"the Pipeline to position it on the coverage map.",
        "success",
    )
    anchor = request.form.get("anchor", "")
    return redirect(url_for("enterprise") + (f"#{anchor}" if anchor else ""))


# ─── Wizard ───────────────────────────────────────────────────────────────────

def _wizard_context(mode, step, draft, agent=None):
    return {
        "mode":  mode,
        "step":  step,
        "draft": draft,
        "agent": agent,
        "stages": STAGES,
        "complexities": COMPLEXITIES,
        "advantages": ADVANTAGES,
        "categories": CATEGORIES,
    }


@app.route("/add")
def add_agent():
    session["wizard_draft"] = {}
    return render_template(
        "wizard.html",
        **_wizard_context("add", 1, {})
    )


@app.route("/add/step/<int:n>", methods=["POST"])
def add_step(n):
    draft = session.get("wizard_draft", {})
    draft = _save_step_to_draft(draft, n, request.form)
    session["wizard_draft"] = draft

    if n < 4:
        return render_template("wizard.html", **_wizard_context("add", n + 1, draft))
    return render_template("wizard.html", **_wizard_context("add", 4, draft))


@app.route("/add/save", methods=["POST"])
def add_save():
    draft = session.get("wizard_draft", {})
    draft = _save_step_to_draft(draft, 4, request.form)

    agent = Agent(
        name=draft.get("name", ""),
        url=draft.get("url") or None,
        description=draft.get("description") or None,
        agent_type=draft.get("agent_type") or None,
        stages=json.dumps(draft.get("stages", [])),
        advantage=draft.get("advantage") or None,
        complexity=draft.get("complexity") or None,
        autonomy=draft.get("autonomy") or None,
        rationale=draft.get("rationale") or None,
        key_features=json.dumps([f for f in draft.get("features", []) if f.strip()]),
        category_id=draft.get("category_id") or None,
        status="classified",
    )
    db.session.add(agent)
    db.session.commit()
    session.pop("wizard_draft", None)
    flash(f"'{agent.name}' successfully classified.", "success")
    return redirect(url_for("matrix"))


@app.route("/edit/<int:agent_id>")
def edit_agent(agent_id):
    agent = Agent.query.get_or_404(agent_id)
    draft = {
        "name":          agent.name,
        "url":           agent.url or "",
        "description":   agent.description or "",
        "agent_type":    agent.agent_type or "",
        "stages":        agent.stages_list,
        "advantage":     agent.advantage or "",
        "complexity":    agent.complexity or "",
        "autonomy":      agent.autonomy or "",
        "rationale":     agent.rationale or "",
        "rationale_data": agent.rationale_dict,
        "features":      agent.features_list or [""],
        "category_id":   agent.category_id or "",
    }
    session["wizard_draft"] = draft
    return render_template("wizard.html", **_wizard_context("edit", 1, draft, agent=agent))


@app.route("/edit/<int:agent_id>/step/<int:n>", methods=["POST"])
def edit_step(agent_id, n):
    agent = Agent.query.get_or_404(agent_id)
    draft = session.get("wizard_draft", {})
    draft = _save_step_to_draft(draft, n, request.form)
    session["wizard_draft"] = draft
    if n < 4:
        return render_template("wizard.html", **_wizard_context("edit", n + 1, draft, agent=agent))
    return render_template("wizard.html", **_wizard_context("edit", 4, draft, agent=agent))


@app.route("/edit/<int:agent_id>/save", methods=["POST"])
def edit_save(agent_id):
    agent = Agent.query.get_or_404(agent_id)
    draft = session.get("wizard_draft", {})
    draft = _save_step_to_draft(draft, 4, request.form)

    agent.name        = draft.get("name", agent.name)
    agent.url         = draft.get("url") or None
    agent.description = draft.get("description") or None
    agent.agent_type  = draft.get("agent_type") or None
    agent.stages      = json.dumps(draft.get("stages", []))
    agent.advantage   = draft.get("advantage") or None
    agent.complexity  = draft.get("complexity") or None
    agent.autonomy    = draft.get("autonomy") or None
    agent.rationale   = draft.get("rationale") or None
    agent.key_features = json.dumps([f for f in draft.get("features", []) if f.strip()])
    agent.category_id = draft.get("category_id") or None
    agent.status      = "classified"
    db.session.commit()
    session.pop("wizard_draft", None)
    flash(f"'{agent.name}' successfully classified.", "success")
    return redirect(url_for("matrix"))


@app.route("/agents/<int:agent_id>")
def agent_detail(agent_id):
    agent = Agent.query.get_or_404(agent_id)
    classified_count = Agent.query.filter_by(status="classified").count()
    return render_template(
        "agent_detail.html",
        agent=agent,
        stage_map=dict(STAGES),
        complexity_labels=dict(COMPLEXITIES),
        advantage_labels=dict(ADVANTAGES),
        category_map=CATEGORY_MAP,
        classified_count=classified_count,
    )


@app.route("/agents/<int:agent_id>/classify")
def classify_agent(agent_id):
    agent = Agent.query.get_or_404(agent_id)
    draft = {
        "name":          agent.name,
        "url":           agent.url or "",
        "description":   agent.description or "",
        "agent_type":    agent.agent_type or "",
        "stages":        agent.stages_list,
        "advantage":     agent.advantage or "",
        "complexity":    agent.complexity or "",
        "autonomy":      agent.autonomy or "",
        "rationale":     agent.rationale or "",
        "rationale_data": agent.rationale_dict,
        "features":      agent.features_list or [""],
        "category_id":   agent.category_id or "",
    }
    session["wizard_draft"] = draft
    return render_template("wizard.html", **_wizard_context("classify", 1, draft, agent=agent))


@app.route("/agents/<int:agent_id>/classify/step/<int:n>", methods=["POST"])
def classify_step(agent_id, n):
    agent = Agent.query.get_or_404(agent_id)
    draft = session.get("wizard_draft", {})
    draft = _save_step_to_draft(draft, n, request.form)
    session["wizard_draft"] = draft
    if n < 4:
        return render_template("wizard.html", **_wizard_context("classify", n + 1, draft, agent=agent))
    return render_template("wizard.html", **_wizard_context("classify", 4, draft, agent=agent))


@app.route("/agents/<int:agent_id>/classify/save", methods=["POST"])
def classify_save(agent_id):
    agent = Agent.query.get_or_404(agent_id)
    draft = session.get("wizard_draft", {})
    draft = _save_step_to_draft(draft, 4, request.form)

    agent.name         = draft.get("name", agent.name)
    agent.url          = draft.get("url") or None
    agent.description  = draft.get("description") or None
    agent.agent_type   = draft.get("agent_type") or None
    agent.stages       = json.dumps(draft.get("stages", []))
    agent.advantage    = draft.get("advantage") or None
    agent.complexity   = draft.get("complexity") or None
    agent.autonomy     = draft.get("autonomy") or None
    agent.rationale    = draft.get("rationale") or None
    agent.key_features = json.dumps([f for f in draft.get("features", []) if f.strip()])
    agent.category_id  = draft.get("category_id") or None
    agent.status       = "classified"
    db.session.commit()
    session.pop("wizard_draft", None)
    flash(f"'{agent.name}' successfully classified.", "success")
    return redirect(url_for("matrix"))


@app.route("/agents/<int:agent_id>/reject", methods=["POST"])
def reject_agent(agent_id):
    agent = Agent.query.get_or_404(agent_id)
    agent.status = "rejected"
    db.session.commit()
    flash(f"'{agent.name}' marked as not relevant.", "warning")
    return redirect(url_for("pipeline"))


@app.route("/agents/<int:agent_id>/restore", methods=["POST"])
def restore_agent(agent_id):
    agent = Agent.query.get_or_404(agent_id)
    agent.status = "pending"
    db.session.commit()
    flash(f"'{agent.name}' restored to pending.", "info")
    return redirect(url_for("pipeline"))


@app.route("/delete/<int:agent_id>", methods=["POST"])
def delete_agent(agent_id):
    agent = Agent.query.get_or_404(agent_id)
    name = agent.name
    db.session.delete(agent)
    db.session.commit()
    flash(f"'{name}' permanently deleted.", "danger")
    return redirect(url_for("pipeline"))


# ─── Exports ─────────────────────────────────────────────────────────────────

@app.route("/export/excel")
def export_excel():
    agents = Agent.query.filter_by(status="classified").all()
    buf = build_excel(agents)
    filename = f"AI_Agents_Classification_{date.today().isoformat()}.xlsx"
    return send_file(
        buf,
        as_attachment=True,
        download_name=filename,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@app.route("/export/pdf")
def export_pdf():
    agents   = Agent.query.filter_by(status="classified").all()
    buf      = build_pdf(agents)
    filename = f"AI_Agents_Classification_{date.today().isoformat()}.pdf"
    return send_file(buf, as_attachment=True, download_name=filename,
                     mimetype="application/pdf")


@app.route("/export/word")
def export_word():
    agents = Agent.query.filter_by(status="classified").all()
    buf = build_word(agents)
    filename = f"AI_Agents_Classification_{date.today().isoformat()}.docx"
    return send_file(
        buf,
        as_attachment=True,
        download_name=filename,
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )


# ─── Guide ───────────────────────────────────────────────────────────────────

@app.route("/guide")
def guide():
    classified = Agent.query.filter_by(status="classified").all()
    agents_json = json.dumps([
        {
            "id":          a.id,
            "name":        a.name,
            "url":         a.url,
            "description": a.description,
            "advantage":   a.advantage,
            "autonomy":    a.autonomy,
            "complexity":  a.complexity,
            "agent_type":  a.agent_type,
            "stages":      a.stages_list,
            "features":    a.features_list,
            "category_id": a.category_id,
        }
        for a in classified
    ])
    return render_template(
        "guide.html",
        agents_json=agents_json,
        stages=STAGES,
        complexities=COMPLEXITIES,
        advantages=ADVANTAGES,
        categories=CATEGORIES,
    )


# ─── Framework ───────────────────────────────────────────────────────────────

@app.route("/")
@app.route("/framework")
def framework():
    return render_template("framework.html", categories=CATEGORIES)


# ─── API ─────────────────────────────────────────────────────────────────────

@app.route("/api/agents")
def api_agents():
    agents = Agent.query.all()
    return jsonify([
        {
            "id":           a.id,
            "name":         a.name,
            "url":          a.url,
            "description":  a.description,
            "rationale":    a.rationale,
            "key_features": a.features_list,
            "advantage":    a.advantage,
            "autonomy":     a.autonomy,
            "agent_type":   a.agent_type,
            "complexity":   a.complexity,
            "stages":       a.stages_list,
            "status":       a.status,
            "created_at":   a.created_at.isoformat() if a.created_at else None,
        }
        for a in agents
    ])


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _save_step_to_draft(draft, step, form):
    if step == 1:
        draft["name"]        = form.get("name", "").strip()
        draft["url"]         = form.get("url", "").strip()
        draft["description"] = form.get("description", "").strip()
        draft["agent_type"]  = form.get("agent_type", "")
        draft["category_id"] = form.get("category_id", "")
    elif step == 2:
        draft["stages"] = form.getlist("stages")
    elif step == 3:
        draft["advantage"]  = form.get("advantage", "")
        draft["complexity"] = form.get("complexity", "")
        draft["autonomy"]   = form.get("autonomy", "")
    elif step == 4:
        rationale_data = {
            "advantage":  form.get("rationale_advantage", "").strip(),
            "complexity": form.get("rationale_complexity", "").strip(),
            "autonomy":   form.get("rationale_autonomy", "").strip(),
            "agent_type": form.get("rationale_agent_type", "").strip(),
            "stages":     form.get("rationale_stages", "").strip(),
            "general":    form.get("rationale_general", "").strip(),
        }
        draft["rationale_data"] = rationale_data
        draft["rationale"] = json.dumps(rationale_data)
        features = form.getlist("features")
        draft["features"] = features if features else [""]
    return draft


# ─── Entry point ─────────────────────────────────────────────────────────────

UNCATEGORIZED_AGENTS = [
    "Panthera Decision GPS",
    "Cognaize",
    "Harmonic",
    "Arteria AI",
    "JPMorgan COIN",
    "Atlas AI",
    "Citi Sky / Arc Platform",
    "Linedata",
    "Goldman Sachs GS AI Assistant",
    "JPMorgan LLM Suite",
    "Kensho NERD / Classify / Scribe",
    "Xceptor",
]


def _migrate_db():
    """Add missing columns and re-apply category assignments from current taxonomy."""
    from sqlalchemy import text
    with db.engine.connect() as conn:
        cols = [row[1] for row in conn.execute(text("PRAGMA table_info(agents)")).fetchall()]
        if "category_id" not in cols:
            conn.execute(text("ALTER TABLE agents ADD COLUMN category_id VARCHAR(50)"))
            conn.commit()
        if "in_stack" not in cols:
            conn.execute(text("ALTER TABLE agents ADD COLUMN in_stack BOOLEAN DEFAULT 0"))
            conn.execute(text("UPDATE agents SET in_stack = 0 WHERE in_stack IS NULL"))
            conn.commit()
        # Unconditionally update all known agent categories (overwrites stale assignments)
        for name, cat_id in AGENT_CATEGORY_SEED.items():
            conn.execute(
                text("UPDATE agents SET category_id = :cat WHERE name = :name"),
                {"cat": cat_id, "name": name},
            )
        # Clear category for dissolved category and explicitly uncategorized agents
        conn.execute(
            text("UPDATE agents SET category_id = NULL WHERE category_id = 'investment-decision-copilots'")
        )
        for name in UNCATEGORIZED_AGENTS:
            conn.execute(
                text("UPDATE agents SET category_id = NULL WHERE name = :name"),
                {"name": name},
            )
        conn.commit()


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        seed_database(app, db, Agent)
        _migrate_db()
    app.run(debug=True, port=5000)
