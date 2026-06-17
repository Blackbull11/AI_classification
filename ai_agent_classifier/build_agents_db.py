import sqlite3
import json
import os
from datetime import datetime, timezone

def generate_database():
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'agents.db')
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    conn   = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS agents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            url TEXT,
            description TEXT,
            rationale TEXT,
            key_features TEXT,
            advantage TEXT,
            autonomy TEXT,
            agent_type TEXT,
            complexity TEXT,
            stages TEXT,
            category_id TEXT,
            status TEXT NOT NULL,
            created_at DATETIME
        )
    ''')

    # Add category_id column to existing databases that predate this field
    existing_cols = [row[1] for row in cursor.execute("PRAGMA table_info(agents)").fetchall()]
    if "category_id" not in existing_cols:
        cursor.execute("ALTER TABLE agents ADD COLUMN category_id TEXT")

    AGENT_CATEGORY_SEED = {
        "AIEQ / EquBot":                                          "autonomous-trading-engines",
        "Numerai (Meta Model)":                                   "autonomous-trading-engines",
        "Academic Trading Agents (FinGPT / FinMem / TradingAgents)": "autonomous-trading-engines",
        "FLAG-Trader":                                            "autonomous-trading-engines",
        "FinRobot":                                               "autonomous-trading-engines",
        "JPMorgan LOXM":                                          "ai-execution-optimizers",
        "Shavandi & Khedmati Multi-Agent DRL":                    "ai-execution-optimizers",
        "Aiden (VWAP & Arrival) — RBC Capital Markets":           "ai-execution-optimizers",
        "Acuity (Acuity Trading)":                                "ai-execution-optimizers",
        "QuantAgent":                                             "institutional-quant-alpha",
        "JPMorgan IndexGPT":                                      "institutional-quant-alpha",
        "BlackRock AlphaAgents":                                  "institutional-quant-alpha",
        "BlackRock Aladdin":                                      "institutional-quant-alpha",
        "BlackRock eFront":                                       "research-due-diligence",
        "FinGPT":                                                 "autonomous-trading-engines",
        "FinMem":                                                 "autonomous-trading-engines",
        "TradingAgents":                                          "autonomous-trading-engines",
        "FinRL-Trading":                                          "autonomous-trading-engines",
        "Pluto.fi (Robinhood)":                                   "institutional-quant-alpha",
        "Pluto (Robinhood)":                                      "institutional-quant-alpha",
        "Axyon AI":                                               "institutional-quant-alpha",
        "Neural Alpha":                                           "institutional-quant-alpha",
        "Boosted.ai":                                             "institutional-quant-alpha",
        "SigTech":                                                "institutional-quant-alpha",
        "MDOTM (Sei)":                                            "institutional-quant-alpha",
        "Kavout":                                                 "ai-stock-screeners",
        "Auquan":                                                 "ai-stock-screeners",
        "StockBench":                                             "ai-stock-screeners",
        "Bridget / ThemeWise":                                    "ai-stock-screeners",
        "Aiera":                                                  "ai-stock-screeners",
        "InvestGPT (Kavout)":                                     "investment-decision-copilots",
        "Finpilot":                                               "investment-decision-copilots",
        "Investbanq Co-Pilot":                                    "investment-decision-copilots",
        "Panthera Decision GPS":                                  "investment-decision-copilots",
        "Vise AI":                                                "ai-wealth-portfolio-advisors",
        "ARKEN Finance":                                          "ai-wealth-portfolio-advisors",
        "Altruist AI Agents":                                     "ai-wealth-portfolio-advisors",
        "Wokelo Agentic Builder":                                 "research-due-diligence",
        "V7 Go (Due Diligence Agent)":                            "research-due-diligence",
        "TOGGLE Copilot / Pro":                                   "research-due-diligence",
        "Hebbia":                                                 "research-due-diligence",
        "DiligenceSquared":                                       "research-due-diligence",
        "EILLA AI":                                               "research-due-diligence",
        "SmartKarma":                                             "research-due-diligence",
        "Rogo":                                                   "research-due-diligence",
        "Cognaize":                                               "research-due-diligence",
        "Harmonic":                                               "research-due-diligence",
        "RavenPack News Analytics / Bigdata.com":                 "market-intelligence-aggregators",
        "Dataminr":                                               "market-intelligence-aggregators",
        "AlphaSense":                                             "market-intelligence-aggregators",
        "Bloomberg ASKB":                                          "market-intelligence-aggregators",
        "Needl":                                                  "market-intelligence-aggregators",
        "Terminal X":                                             "market-intelligence-aggregators",
        "Theia Insights":                                         "market-intelligence-aggregators",
        "Ayasdi (SymphonyAI)":                                    "risk-aml-surveillance",
        "NICE Actimize SURVEIL-X / Actimize Intelligence":        "risk-aml-surveillance",
        "Holistic AI":                                            "risk-aml-surveillance",
        "Behavox (Quantum / Polaris)":                            "risk-aml-surveillance",
        "Hadrius":                                                "risk-aml-surveillance",
        "Clarity AI":                                             "esg-regulatory-compliance",
        "MSCI AI Portfolio Insights":                             "esg-regulatory-compliance",
        "ShareWorks / Equity Edge MCP (Morgan Stanley)":          "esg-regulatory-compliance",
        "Riskspan":                                               "esg-regulatory-compliance",
        "YourStake":                                              "esg-regulatory-compliance",
        "Norm AI":                                                "esg-regulatory-compliance",
        "Arteria AI":                                             "esg-regulatory-compliance",
        "JPMorgan COIN":                                          "esg-regulatory-compliance",
        "Affinity AI":                                            "client-stakeholder-intelligence",
        "Portrait Analytics":                                     "client-stakeholder-intelligence",
        "AI @ Morgan Stanley Debrief":                            "client-stakeholder-intelligence",
        "Morningstar 'Mo' / Intelligence Engine":                 "client-stakeholder-intelligence",
        "StockSnips":                                             "client-stakeholder-intelligence",
        "Atlas AI":                                               "client-stakeholder-intelligence",
    }
    for name, cat_id in AGENT_CATEGORY_SEED.items():
        cursor.execute(
            "UPDATE agents SET category_id = ? WHERE name = ? AND (category_id IS NULL OR category_id = '')",
            (cat_id, name),
        )

    # Rationale is stored as a JSON dict with keys:
    #   advantage, complexity, autonomy, agent_type, stages, general
    agents_data =  [
        {
            "name": "AIEQ / EquBot",
            "url": "https://amplifyetfs.com/aieq",
            "description": "The world's first AI-driven ETF, using IBM Watson to autonomously select and weight US equities by processing ~1M+ data points daily across ~6,000 stocks — with no human veto on portfolio construction. Uniquely, full investment autonomy is wrapped in a standard exchange-traded product accessible to retail investors.",
            "key_features": [
            "Processes ~1M+ daily data points across ~6,000 US equities with fully autonomous portfolio construction — no human override",
            "Only AI-managed ETF offering retail investors direct exposure to a high-autonomy investment AI without minimum thresholds"
            ],
            "rationale": {
            "advantage": "Analytical. Superior computational synthesis of public market data at a scale no human team could match — the edge is processing power and breadth of signal integration, not privileged data access.",
            "complexity": "Light-Grey Swan. Optimal stock weights must be searched across a vast, non-stationary signal space; the probability distribution is theoretically defined but computationally intractable to optimize exactly.",
            "autonomy": "High. The AI autonomously selects and weights the full portfolio; no human reviews or vetoes individual stock decisions. Confirmed by Amplify ETF prospectus.",
            "agent_type": "Commercial. Public ETF product available on NYSE.",
            "stages": "Idea Generation, Idea Assessment, Decision, Execution, Monitoring. CORRECTION from Gemini: stages were cut at [idea-gen, decision] — the ETF continuously rebalances (Execution) and monitors holdings (Monitoring) autonomously. Full process coverage is accurate."
            },
            "advantage": "analytical",
            "autonomy": "high",
            "agent_type": "commercial",
            "complexity": "light-grey",
            "stages": [
            "idea-gen",
            "idea-assess",
            "decision",
            "execution",
            "monitoring"
            ],
            "status": "classified"
        },
        {
            "name": "Numerai (Meta Model)",
            "url": "https://numer.ai",
            "description": "A crowdsourced hedge fund that aggregates thousands of independently trained, encrypted ML models from external data scientists into a single Meta Model that trades a global equity market-neutral book. Contributors never see the raw financial data — only obfuscated features — preserving diversity while crowdsourcing the broadest hypothesis search of any agent in this list.",
            "key_features": [
            "Aggregates thousands of encrypted, independently trained ML models — the widest hypothesis search space of any single fund in this list",
            "NMR cryptocurrency staking acts as a quality filter: contributors stake tokens on their model's predictions, aligning incentives with performance"
            ],
            "rationale": {
            "advantage": "Analytical. The Meta Model's edge is the decentralized search over hypothesis space — superior synthesis of diverse analytical frameworks rather than privileged data access.",
            "complexity": "Light-Grey Swan. Non-stationary global equity market-neutral signals must be searched; the challenge is computationally finding the best predictive factors, not unknowable structural uncertainty.",
            "autonomy": "High. The aggregated Meta Model automatically dictates and executes the fund's trading book without per-trade human input.",
            "agent_type": "In-house. Numerai operates its own fund; trading decisions are made by the platform, not the contributing data scientists.",
            "stages": "Idea Generation, Idea Assessment, Decision, Execution, Monitoring. CORRECTION: Gemini missed Monitoring — the NMR staking mechanism creates continuous model performance surveillance, and fund positions are monitored against targets."
            },
            "advantage": "analytical",
            "autonomy": "high",
            "agent_type": "in-house",
            "complexity": "light-grey",
            "stages": [
            "idea-gen",
            "idea-assess",
            "decision",
            "execution",
            "monitoring"
            ],
            "status": "classified"
        },
        {
            "name": "Kavout",
            "url": "https://www.kavout.com",
            "description": "An AI investment screening platform that distills fundamental, technical, and alternative data across 7,000+ US equities into a single 1-9 K-Score rating. It operates as a pure screening and analyst-assist tool — no execution, no allocation — maintaining clear human judgment at the decision point.",
            "key_features": [
            "Proprietary K-Score (1–9) unifies multiple data types into one actionable signal per equity, reducing cognitive load for equity analysts",
            "Pure screening layer with no execution capability — human retains full decision authority downstream of the score"
            ],
            "rationale": {
            "advantage": "Analytical. Synthesizes disparate public data sources into a unified predictive score — superior interpretation of available information is the edge, not privileged access.",
            "complexity": "Light-Grey Swan. ML models optimize predictive signals across non-stationary market data; the challenge is finding robust signals in a noisy environment.",
            "autonomy": "Low. Acts strictly as an idea-generation and screening tool; the human portfolio manager acts on the K-Score.",
            "agent_type": "Commercial. Sold as a SaaS platform to investment professionals.",
            "stages": "Idea Generation, Idea Assessment. Correctly classified by Gemini."
            },
            "advantage": "analytical",
            "autonomy": "low",
            "agent_type": "commercial",
            "complexity": "light-grey",
            "stages": [
            "idea-gen",
            "idea-assess"
            ],
            "status": "classified"
        },
        {
            "name": "RavenPack News Analytics / Bigdata.com",
            "url": "https://www.ravenpack.com",
            "description": "Converts unstructured public text from 40,000+ global sources in 13 languages into structured, time-stamped sentiment scores, event tags, and entity-level signals delivered via API — not a chat interface. Every signal is traceable to its source with point-in-time accuracy, making it the auditability benchmark for NLP-based alpha data.",
            "key_features": [
            "API/data-feed delivery (not chat) — structured signals integrate directly into quant pipelines, OMS, and risk management systems",
            "Full source auditability: every insight is timestamped and traceable, enabling model governance and regulatory audit trails"
            ],
            "rationale": {
            "advantage": "Informational. Converts unstructured public text into structured signals — the edge is speed and breadth of perception, not synthesis depth. Consistent with the paper's own Case 2 classification.",
            "complexity": "Light-Grey Swan. Identifying valid signals vs. noise in massive real-time streams requires continuous ML heuristics; signal probability is theoretically known but requires heavy search.",
            "autonomy": "Low. Generates signals and metadata; takes no action. CORRECTION: Gemini's rationale said 'Low to Medium' but the structured field said Low — aligned here to Low, consistent with the paper's Case 2 classification.",
            "agent_type": "Commercial. API and data feed provider.",
            "stages": "Idea Generation, Monitoring, Stakeholder Management. CORRECTION: Gemini omitted Monitoring (headline-risk monitoring) and Stakeholder (explanatory overlays for reporting) — both explicitly noted in the paper's Case 2."
            },
            "advantage": "informational",
            "autonomy": "low",
            "agent_type": "commercial",
            "complexity": "light-grey",
            "stages": [
            "idea-gen",
            "monitoring",
            "stakeholder"
            ],
            "status": "classified"
        },
        {
            "name": "Kensho NERD / Classify / Scribe",
            "url": "https://kensho.com",
            "description": "Three NLP infrastructure tools from S&P Global that structure raw financial text into machine-readable entities (NERD), thematic tags (Classify), and transcripts (Scribe) — each linked to Capital IQ identifiers. Unlike document-search platforms, Kensho operates as upstream data plumbing: it does not surface insights but enables downstream systems to do so.",
            "key_features": [
            "Entity-level traceability linking every mention to Capital IQ identifiers — enables compliance audits and precise downstream data lineage",
            "Pure infrastructure layer — API-only with no decision interface, designed to be embedded inside other analytical systems"
            ],
            "rationale": {
            "advantage": "Informational. Structures text into machine-readable entities faster than manual effort — the edge is speed and precision of information extraction, not analytical synthesis.",
            "complexity": "White Swan. Entity recognition and transcription rely on stable linguistic rules and well-defined taxonomies — deterministic, not probabilistic search.",
            "autonomy": "Low. Pure preprocessing infrastructure; no recommendations, no decisions.",
            "agent_type": "Commercial. NLP building blocks sold by S&P Global / Kensho.",
            "stages": "Idea Generation, Idea Assessment. Pre-processing layer enabling downstream analysis. Correctly classified by Gemini."
            },
            "advantage": "informational",
            "autonomy": "low",
            "agent_type": "commercial",
            "complexity": "white",
            "stages": [
            "idea-gen",
            "idea-assess"
            ],
            "status": "classified"
        },
        {
            "name": "AlphaSense",
            "url": "https://www.alpha-sense.com",
            "description": "A market intelligence platform that uses LLM-powered Generative Search and Smart Summaries to synthesize insights across 300M+ documents covering public filings, broker research, earnings calls, and news — with sentence-level citations. Distinctive from Bloomberg and FactSet in the breadth of third-party content ingestion and its agentic Slide Agent for generating investor-facing presentations.",
            "key_features": [
            "Synthesizes across 300M+ documents including third-party broker research and alternative data — broader content coverage than terminal-tied platforms",
            "AI Workflow Agents (including Slide Agent) extend it beyond search into light content generation for stakeholder-facing outputs"
            ],
            "rationale": {
            "advantage": "Analytical. CORRECTION from Gemini (Informational → Analytical): AlphaSense's moat is synthesis quality across publicly available documents — competitors can access the same filings and research. The value is in comprehension and cross-document reasoning, not exclusive data access.",
            "complexity": "White Swan. Document retrieval, summarization, and synthesis operate over a fixed, structured corpus — well-defined queries against known documents, not probabilistic signal search.",
            "autonomy": "Low. CORRECTION from Gemini (Medium → Low): generates summaries and surfaces documents for human interpretation. No investment recommendations or decisions are made autonomously.",
            "agent_type": "Commercial. SaaS platform sold to investment professionals.",
            "stages": "Idea Assessment, Monitoring, Stakeholder Management. CORRECTION: Gemini listed only [idea-assess] — Monitoring (tracking document changes over time) and Stakeholder (Slide Agent for presentations) are explicit product capabilities."
            },
            "advantage": "analytical",
            "autonomy": "low",
            "agent_type": "commercial",
            "complexity": "white",
            "stages": [
            "idea-assess",
            "monitoring",
            "stakeholder"
            ],
            "status": "classified"
        },
        {
            "name": "Dataminr",
            "url": "https://www.dataminr.com",
            "description": "A real-time AI alerting platform that scans multimodal public data — text, image, and video — from social media and global open sources to surface market-moving events and geopolitical risks seconds before traditional news wires. Unlike RavenPack, Dataminr's edge is velocity and tail-risk early warning rather than deep NLP signal structuring for alpha generation.",
            "key_features": [
            "Detects events from raw social media in seconds — primarily a tail-risk early-warning system, not an alpha signal generator",
            "Multimodal detection (text, image, video) distinguishes it from all other NLP platforms in this list, which are text-only"
            ],
            "rationale": {
            "advantage": "Informational. Extreme speed of market-event detection from public sources is the edge — accessing critical information before other market participants.",
            "complexity": "Light-Grey Swan. Identifying valid signals in real-time, noisy social streams requires continuous ML heuristics; separating genuine events from noise is computationally intensive.",
            "autonomy": "Low. Generates alerts for human decision-makers; takes no action.",
            "agent_type": "Commercial.",
            "stages": "Monitoring, Idea Generation. Monitoring is primary (tail-risk surveillance); Idea Generation is secondary (novel event discovery). Correctly classified by Gemini."
            },
            "advantage": "informational",
            "autonomy": "low",
            "agent_type": "commercial",
            "complexity": "light-grey",
            "stages": [
            "monitoring",
            "idea-gen"
            ],
            "status": "classified"
        },
        {
            "name": "BlackRock Aladdin Copilot / eFront Copilot",
            "url": "https://www.blackrock.com/aladdin/solutions/aladdin-copilot",
            "description": "A generative AI copilot embedded in BlackRock's Aladdin platform that translates natural language queries into portfolio exposures, risk summaries, and scenario analyses using Aladdin's structured system-of-record — with strict guardrails and no trading authority. This is the paper's own Case 1: the benchmark implementation of a low-autonomy, high-control investment AI copilot.",
            "key_features": [
            "Operates strictly within Aladdin's scoped data environment — no open-web access, no hallucination of portfolio data outside the system of record",
            "All outputs require human sign-off: no allocation, no trading authority, making human judgment a formal requirement in the workflow"
            ],
            "rationale": {
            "advantage": "Analytical. Synthesizes Aladdin's portfolio and risk data to answer complex queries — the edge is reasoning over a rich structured data environment, not raw data access.",
            "complexity": "White Swan. CORRECTION from Gemini (Light-Grey → White): Aladdin Copilot operates over structured, deterministic portfolio and risk data within Aladdin's system of record — not searching for signals in noisy market data.",
            "autonomy": "Low. CORRECTION from Gemini (Medium → Low): the paper explicitly states 'no trading or allocation authority; supports analysis' with 'retention of human judgment and formal sign-offs.' Medium autonomy contradicts the paper's own Case 1 classification.",
            "agent_type": "Commercial platform integration (BlackRock sells Aladdin access).",
            "stages": "Idea Assessment, Monitoring, Stakeholder Management. CORRECTION: Gemini omitted Stakeholder — the paper explicitly lists 'stakeholder reporting' among the primary workflows supported."
            },
            "advantage": "analytical",
            "autonomy": "low",
            "agent_type": "commercial",
            "complexity": "white",
            "stages": [
            "idea-assess",
            "monitoring",
            "stakeholder"
            ],
            "status": "classified"
        },
        {
            "name": "BlackRock AlphaAgents",
            "url": "https://arxiv.org/abs/2408.01152",
            "description": "An academic research prototype using role-based multi-agent debate — Fundamental, Sentiment, and Valuation agents coordinated via Microsoft AutoGen on GPT-4o — to produce a consensus stock recommendation. Not a deployed BlackRock product: a research paper testing whether structured agent debate reduces single-LLM bias in stock assessment.",
            "key_features": [
            "Multi-agent debate architecture designed to surface disagreement across analytical lenses and reduce single-agent LLM groupthink",
            "Academic prototype only — validated on a small backtest with frozen GPT-4o weights (no online learning); not connected to live capital"
            ],
            "rationale": {
            "advantage": "Analytical. The debate mechanism aims to produce better-informed recommendations by forcing multi-perspective synthesis — the advantage type is analytical, not behavioral. The de-biasing intent is a design motivation, but the mechanism is information synthesis.",
            "complexity": "Light-Grey Swan. CORRECTION from Gemini (Dark-Grey → Light-Grey): the agents deliberate over standard fundamental, sentiment, and valuation data — non-stationary market inputs with theoretically known distributions, not deep structural uncertainty. Dark-Grey requires scarce information; this has well-structured (if noisy) inputs.",
            "autonomy": "Medium. Recommends a consensus decision for human review; does not act.",
            "agent_type": "Academic research prototype.",
            "stages": "Idea Assessment, Decision. Correctly classified by Gemini."
            },
            "advantage": "analytical",
            "autonomy": "medium",
            "agent_type": "academic",
            "complexity": "light-grey",
            "stages": [
            "idea-assess",
            "decision"
            ],
            "status": "classified"
        },
        {
            "name": "Academic Trading Agents (FinGPT / FinMem / TradingAgents)",
            "url": "https://github.com/AI4Finance-Foundation",
            "description": "A family of open-source LLM frameworks from the AI4Finance Foundation exploring layered memory (FinMem), multimodal foundation models (FinAgent), and game-theoretic debate architectures for fully autonomous trading agents. Performance is exclusively backtested — none have been deployed with live capital.",
            "key_features": [
            "Broadest architectural variety in this list: layered memory, multimodal inputs, and debate-driven decision-making explored as distinct research vectors",
            "Open-source and freely modifiable — the most accessible research-to-practitioner bridge in this list, but zero live deployment validation"
            ],
            "rationale": {
            "advantage": "Analytical. These systems optimize signal extraction and decision quality from market data — behavioral de-biasing through debate is a secondary mechanism, not the primary advantage type.",
            "complexity": "Light-Grey Swan. CORRECTION from Gemini (Dark-Grey → Light-Grey): these agents operate on market price data, news, and financial signals — non-stationary but with theoretically known uncertainty structures. Dark-Grey would imply scarce information and reliance on pure logic/heuristics, which contradicts the data-heavy ML approach used.",
            "autonomy": "High. Autonomous from signal generation to simulated trade execution in backtesting environments.",
            "agent_type": "Academic / open-source.",
            "stages": "Idea Assessment, Decision, Execution. Correctly classified by Gemini."
            },
            "advantage": "analytical",
            "autonomy": "high",
            "agent_type": "academic",
            "complexity": "light-grey",
            "stages": [
            "idea-assess",
            "decision",
            "execution"
            ],
            "status": "classified"
        },
        {
            "name": "Bloomberg ASKB",
            "url": "https://www.bloomberg.com/professional/ai/",
            "description": "An agentic interface embedded in the Bloomberg Terminal that coordinates search agents over Bloomberg's document and data universe with transparent BQL code exposure. The differentiator is the depth of proprietary data access and full analytical transparency through exposed BQL queries.",
            "key_features": [
            "ASKB exposes underlying BQL (Bloomberg Query Language) code for all generated answers — unique analytical transparency among terminal-integrated AIs"
            ],
            "rationale": {
            "advantage": "Informational. Bloomberg's proprietary terminal data (tick data, filings, news archive, pricing) is the competitive moat — others cannot replicate the training corpus. The LLM amplifies access to this data.",
            "complexity": "White Swan. CORRECTION from Gemini (Light-Grey → White): Bloomberg AI answers queries against Bloomberg's structured financial database — well-defined retrieval against known data, not probabilistic signal search in noisy markets.",
            "autonomy": "Low. Pure decision support with full source attribution. Human interprets all outputs.",
            "agent_type": "Commercial terminal product.",
            "stages": "Idea Generation, Idea Assessment. Correctly classified by Gemini."
            },
            "advantage": "informational",
            "autonomy": "low",
            "agent_type": "commercial",
            "complexity": "white",
            "stages": [
            "idea-gen",
            "idea-assess"
            ],
            "status": "classified"
        },
        {
            "name": "FactSet Mercury / Intelligent Platform",
            "url": "https://www.factset.com/solutions/mercury",
            "description": "An LLM-powered platform built on Databricks Mosaic AI that orchestrates multiple AI agents — Portfolio Assistant, Commentary Agent, Pitch Agent — to generate auditable portfolio insights and stakeholder-facing content over FactSet's data universe. Notable for never training on client data and providing sentence-level citations across all generated outputs.",
            "key_features": [
            "Multi-agent orchestration (Portfolio, Commentary, Pitch agents) — one of the most mature agentic workflow architectures among commercial investment platforms",
            "Zero client-data training policy with sentence-level citations — the strictest auditability-compliance combination in this list"
            ],
            "rationale": {
            "advantage": "Analytical. CORRECTION from Gemini (Informational → Analytical): FactSet's underlying data is available to all FactSet subscribers; the edge lies in Mercury's ability to synthesize portfolio insights, generate commentary, and produce pitch materials — active analytical synthesis, not exclusive data access.",
            "complexity": "White Swan. Operates over FactSet's structured financial data with deterministic portfolio metrics — well-defined domain, not noisy signal search.",
            "autonomy": "Low. CORRECTION from Gemini (Medium → Low): all generated drafts (commentaries, pitch books) are reviewed and approved by human investment professionals before use. The system supports, not supplants, analyst judgment.",
            "agent_type": "Commercial.",
            "stages": "Idea Assessment, Monitoring, Stakeholder Management. Correctly classified by Gemini."
            },
            "advantage": "analytical",
            "autonomy": "low",
            "agent_type": "commercial",
            "complexity": "white",
            "stages": [
            "idea-assess",
            "monitoring",
            "stakeholder"
            ],
            "status": "classified"
        },
        {
            "name": "Morningstar 'Mo' / Intelligence Engine",
            "url": "https://www.morningstar.com/products/intelligence-engine",
            "description": "An AI chatbot and API engine that makes Morningstar's proprietary independent investment research — star ratings, analyst reports, and fund data — conversationally accessible, deployable via Microsoft Copilot Studio. The unique value is the editorial independence of the underlying data: Morningstar's research is unaffiliated with sell-side incentive structures.",
            "key_features": [
            "Surfaces Morningstar's independent (non-sell-side) research — editorial independence from banking relationships is the core data differentiator",
            "Microsoft Copilot Studio deployment enables enterprise-ready governed agents with entitlement-aware access and no client-data training"
            ],
            "rationale": {
            "advantage": "Informational. Morningstar's proprietary independent ratings and research are the moat — the AI amplifies access to a unique knowledge base that cannot be replicated.",
            "complexity": "White Swan. Retrieval over Morningstar's structured research and ratings database — well-defined domain with stable schema.",
            "autonomy": "Low. Pure decision support; surfacing research for human analysts to act upon.",
            "agent_type": "Commercial.",
            "stages": "Idea Assessment, Stakeholder Management. Correctly classified by Gemini."
            },
            "advantage": "informational",
            "autonomy": "low",
            "agent_type": "commercial",
            "complexity": "white",
            "stages": [
            "idea-assess",
            "stakeholder"
            ],
            "status": "classified"
        },
        {
            "name": "Goldman Sachs GS AI Assistant",
            "url": "https://www.goldmansachs.com/our-firm/technology/",
            "description": "A firmwide generative AI assistant rolled out to ~46,500 Goldman Sachs employees, providing secure multi-provider LLM access for document summarization, content drafting, data analysis, and code generation within GS's data governance perimeter. It is a horizontal productivity platform — not an investment-specific tool — with a strategic roadmap toward multi-step agentic workflows.",
            "key_features": [
            "Broadest employee deployment in this list (~46,500 users) — operates as a firmwide productivity layer, not an investment-specialist tool",
            "Multi-provider LLM architecture prevents single-vendor dependency while maintaining GS's strict institutional data governance"
            ],
            "rationale": {
            "advantage": "Informational. Accelerates access to and structuring of GS's internal knowledge at scale — the edge is organizational productivity, not investment-specific synthesis.",
            "complexity": "White Swan. Document summarization, drafting, and code generation operate in well-defined, deterministic task domains.",
            "autonomy": "Low. Assistant-mode only; all outputs reviewed by employees before any action.",
            "agent_type": "In-house.",
            "stages": "Idea Assessment, Stakeholder Management. Correctly classified by Gemini."
            },
            "advantage": "informational",
            "autonomy": "low",
            "agent_type": "in-house",
            "complexity": "white",
            "stages": [
            "idea-assess",
            "stakeholder"
            ],
            "status": "classified"
        },
        {
            "name": "JPMorgan LLM Suite",
            "url": "https://www.jpmorgan.com/technology/technology-blog/jpmorgan-chase-llm-suite",
            "description": "JPMorgan's internal secure generative AI platform serving 230,000+ employees across divisions with drafting, summarization, and insight generation via multiple LLM providers — the largest internal AI deployment by user count in this list. Currently a pure productivity layer with a planned roadmap toward multi-step agentic workflow execution.",
            "key_features": [
            "Largest internal AI deployment in this list (230,000+ employees) — scales JPMorgan's human capital productivity across all divisions and geographies",
            "Multi-provider LLM environment prevents single-vendor lock-in while maintaining JPMorgan's stringent enterprise data security standards"
            ],
            "rationale": {
            "advantage": "Informational. Accelerates internal knowledge access and document processing at scale — a horizontal productivity tool, not an investment-specific analytical system.",
            "complexity": "White Swan. Drafting, summarization, and structured document tasks are well-defined and deterministic.",
            "autonomy": "Low. Pure assistant; all outputs require human review and action.",
            "agent_type": "In-house.",
            "stages": "Idea Assessment, Stakeholder Management. Correctly classified by Gemini."
            },
            "advantage": "informational",
            "autonomy": "low",
            "agent_type": "in-house",
            "complexity": "white",
            "stages": [
            "idea-assess",
            "stakeholder"
            ],
            "status": "classified"
        },
        {
            "name": "JPMorgan LOXM",
            "url": "https://www.jpmorgan.com/technology/technology-blog/equities-execution",
            "description": "JPMorgan's proprietary ML equity execution engine using deep reinforcement learning trained on billions of historical and simulated trades to optimize order placement and minimize market impact in real time. Unlike RBC's Aiden, LOXM is not commercialized — it is a purely internal competitive advantage for JPMorgan's equity desks.",
            "key_features": [
            "Trained on billions of real + simulated trades — the largest training corpus for an execution agent in this list",
            "Internal proprietary tool, not commercialized: a direct and exclusive competitive advantage for JPMorgan's equity execution desks"
            ],
            "rationale": {
            "advantage": "Analytical. Deep RL learns superior market microstructure dynamics from historical data — the edge is better pattern recognition in execution, not privileged information.",
            "complexity": "White Swan. Execution optimization has a well-defined, highly measurable objective function (minimize slippage vs. arrival price) with abundant historical data — the environment is competitive but epistemically well-characterized.",
            "autonomy": "High. Executes institutional orders autonomously within set parameters without per-trade human input.",
            "agent_type": "In-house.",
            "stages": "Execution. Correctly classified by Gemini."
            },
            "advantage": "analytical",
            "autonomy": "high",
            "agent_type": "in-house",
            "complexity": "white",
            "stages": [
            "execution"
            ],
            "status": "classified"
        },
        {
            "name": "Hebbia",
            "url": "https://www.hebbia.ai",
            "description": "An AI analyst platform using a 'Matrix' interface to run parallel multi-document queries across private market data rooms, legal filings, and financial documents simultaneously, structuring answers in an auditable tabular format for human review. Distinct from AlphaSense in targeting unstructured private documents (CIMs, legal filings, data rooms) rather than public financial databases.",
            "key_features": [
            "Matrix interface runs parallel LLM queries across an entire private data room simultaneously — critical for M&A and PE due diligence speed",
            "Specialized for private market unstructured documents (CIMs, legal filings) vs. AlphaSense's public data focus — complementary, not competitive"
            ],
            "rationale": {
            "advantage": "Analytical. Synthesizes fragmented, unstructured private documents into structured tabular insights — the value is reasoning quality over complex documents, not exclusive data access.",
            "complexity": "White Swan. Extraction over fixed private documents is a deterministic task — the system is not predicting markets or searching probabilistic signal spaces.",
            "autonomy": "Low. Advanced analyst co-pilot that structures data for human review; all outputs require human interpretation and decision.",
            "agent_type": "Commercial.",
            "stages": "Idea Assessment, Compliance, Stakeholder Management. Correctly classified by Gemini."
            },
            "advantage": "analytical",
            "autonomy": "low",
            "agent_type": "commercial",
            "complexity": "white",
            "stages": [
            "idea-assess",
            "compliance",
            "stakeholder"
            ],
            "status": "classified"
        },
        {
            "name": "Morgan Stanley AI Assistant / AskResearchGPT",
            "url": "https://www.morganstanley.com/about-us/technology/ai",
            "description": "A suite of AI tools co-developed with OpenAI that gives Morgan Stanley advisors instant natural language access to 100,000+ internal documents and synthesizes 70,000+ annual institutional research reports for investment insights. Unlike GS AI Assistant (general productivity), this is investment-research-specific with strict hallucination guardrails and citation requirements.",
            "key_features": [
            "Purpose-built for investment advisory: indexes 100,000+ proprietary MS research documents with mandatory hallucination guardrails and source citations",
            "AskResearchGPT synthesizes 70,000+ annual research reports — the most investment-research-specific retrieval system in this list"
            ],
            "rationale": {
            "advantage": "Informational. Unlocks vast silos of internal MS proprietary knowledge — the moat is access to Morgan Stanley's exclusive research archive, not synthesis methodology.",
            "complexity": "White Swan. Retrieval over structured internal research databases — deterministic domain with well-defined queries.",
            "autonomy": "Low. CORRECTION from Gemini (Medium → Low): retrieves and synthesizes documents for advisor interpretation; advisors make all client-facing investment decisions. No recommendation autonomy.",
            "agent_type": "In-house.",
            "stages": "Idea Assessment, Stakeholder Management. Correctly classified by Gemini."
            },
            "advantage": "informational",
            "autonomy": "low",
            "agent_type": "in-house",
            "complexity": "white",
            "stages": [
            "idea-assess",
            "stakeholder"
            ],
            "status": "classified"
        },
        {
            "name": "AI @ Morgan Stanley Debrief",
            "url": "https://www.morganstanley.com/about-us/technology/ai",
            "description": "An AI tool that automatically transcribes and summarizes Morgan Stanley advisor-client meetings, generates draft follow-up emails, and updates Salesforce records — all subject to mandatory advisor approval before sending. The only tool in this list that operates at the meeting-interaction layer, capturing and structuring relationship data rather than market data.",
            "key_features": [
            "Only tool in this list operating at the client-advisor meeting interface — captures relationship data in real time, not market or portfolio data",
            "Draft emails and CRM updates require explicit advisor approval before sending — zero client-facing autonomous communication"
            ],
            "rationale": {
            "advantage": "Informational. Structures unstructured meeting conversation data into actionable CRM inputs — organizing and capturing relationship information at speed.",
            "complexity": "White Swan. Transcription, summarization, and CRM data entry are deterministic, well-defined tasks in a stable linguistic domain.",
            "autonomy": "Low. Requires advisor approval for every client-facing output; pure productivity tool.",
            "agent_type": "In-house.",
            "stages": "Stakeholder Management, Compliance. Correctly classified by Gemini."
            },
            "advantage": "informational",
            "autonomy": "low",
            "agent_type": "in-house",
            "complexity": "white",
            "stages": [
            "stakeholder",
            "compliance"
            ],
            "status": "classified"
        },
        {
            "name": "Panthera Decision GPS",
            "url": "https://panthera.solutions",
            "description": "A decision-intelligence platform that integrates behavioral science, quantitative finance, and machine intelligence to structure and debias investment decisions at the Decision Point — not generating signals, not executing trades. The only tool in this list with a primary Behavioral advantage, targeting the cognitive layer of the investment process.",
            "key_features": [
            "The only system in this list with an explicit Behavioral advantage — designed to debias decision-makers, not to generate signals or execute",
            "Operates exclusively at the Decision Point: complementary to all other tools, which address signal generation, execution, or compliance"
            ],
            "rationale": {
            "advantage": "Behavioral. Explicitly designed around behavioral science and debiasing — the only tool in this list that targets cognitive biases in decision-makers rather than market data. Per the paper's framework, behavioral advantage is the most durable because knowing a bias doesn't mean overcoming it.",
            "complexity": "Dark-Grey Swan. Decision support for investment choices where information is scarce or ambiguous — the environment requiring hypothetico-deductive logic and expert judgment is precisely where Panthera intervenes. This is the correct range: not probabilistic signal search (Light-Grey), but structured reasoning under genuine uncertainty.",
            "autonomy": "Low. CORRECTION from Gemini (Medium → Low): the entire value proposition is augmenting, not replacing, human judgment. The system keeps humans in the loop by design.",
            "agent_type": "Commercial.",
            "stages": "Decision. Correctly classified by Gemini — exclusive focus on the Decision Point is what makes this tool unique in the taxonomy."
            },
            "advantage": "behavioral",
            "autonomy": "low",
            "agent_type": "commercial",
            "complexity": "dark-grey",
            "stages": [
            "decision"
            ],
            "status": "classified"
        },
        {
            "name": "Shavandi & Khedmati Multi-Agent DRL",
            "url": "https://doi.org/10.1016/j.eswa.2022.118124",
            "description": "A hierarchical multi-agent deep reinforcement learning framework for algorithmic trading in which specialized expert agents at higher timeframes pass knowledge downward to reduce noise and improve lower-timeframe trade signals. An academic prototype grounded in the fractal market hypothesis — validated only in backtesting, not deployed with live capital.",
            "key_features": [
            "Hierarchical cross-timeframe knowledge flow is the technical differentiator: higher-timeframe agents guide lower-timeframe trading agents to reduce noise",
            "Grounded in the fractal market hypothesis (not EMH) — embeds a distinct theoretical market structure assumption directly into the DRL architecture"
            ],
            "rationale": {
            "advantage": "Analytical. DRL learns superior execution and signal patterns from historical data — edge is better computational synthesis of market microstructure dynamics.",
            "complexity": "Light-Grey Swan. Searches for optimal trading signals in non-stationary price data — known uncertainty structures, computationally intensive signal search.",
            "autonomy": "High. Autonomous from signal to simulated execution in backtesting environments.",
            "agent_type": "Academic prototype.",
            "stages": "Decision, Execution. Correctly classified by Gemini."
            },
            "advantage": "analytical",
            "autonomy": "high",
            "agent_type": "academic",
            "complexity": "light-grey",
            "stages": [
            "decision",
            "execution"
            ],
            "status": "classified"
        },
        {
            "name": "MSCI AI Portfolio Insights",
            "url": "https://www.msci.com/our-solutions/analytics/ai-powered-portfolio-insights",
            "description": "A commercial platform combining GenAI with MSCI's proprietary factor risk models to automate portfolio anomaly detection, limits monitoring, and multi-asset macro scenario stress-testing. Distinctive in this list because a specialist risk model — not just an LLM — drives the AI outputs, giving depth unachievable by generic language-only tools.",
            "key_features": [
            "Integrates MSCI's proprietary factor risk models with GenAI — the only tool where a specialist quantitative risk engine drives AI outputs, not just LLM reasoning",
            "Macro Finance Analyzer for multi-asset scenario stress-testing extends coverage into decision-support territory, beyond pure monitoring"
            ],
            "rationale": {
            "advantage": "Analytical. Superior risk modeling using MSCI's proprietary factor models — the edge is model depth and synthesis quality, not exclusive data access.",
            "complexity": "Light-Grey Swan. Scenario stress-testing and anomaly detection involve non-stationary macro and market environments — known uncertainty structures requiring ML search heuristics.",
            "autonomy": "Low. CORRECTION from Gemini (Medium → Low): flags anomalies and generates scenarios for human review; no autonomous investment or rebalancing decisions.",
            "agent_type": "Commercial.",
            "stages": "Monitoring, Decision. CORRECTION: Gemini listed only [monitoring] — the Macro Finance Analyzer's scenario stress-testing is explicitly designed for Decision support, making Decision a primary stage."
            },
            "advantage": "analytical",
            "autonomy": "low",
            "agent_type": "commercial",
            "complexity": "light-grey",
            "stages": [
            "monitoring",
            "decision"
            ],
            "status": "classified"
        },
        {
            "name": "Clarity AI",
            "url": "https://clarity.ai",
            "description": "An AI-native sustainability intelligence platform that automatically scores ESG factors, detects controversies in real time, and generates SFDR / EU Taxonomy regulatory reports across 98,000+ public issuers and 2.3M private companies. The only tool in this list focused exclusively on sustainability intelligence that simultaneously bridges ESG analysis and automated regulatory compliance output.",
            "key_features": [
            "Covers 98k public issuers + 2.3M private companies — the largest ESG data coverage universe in this list",
            "Automates SFDR and EU Taxonomy regulatory reporting — rare among ESG tools in bridging analysis and compliance output within a single system"
            ],
            "rationale": {
            "advantage": "Analytical. CORRECTION from Gemini (Informational → Analytical): ESG raw data is increasingly commoditized and available from multiple providers; Clarity AI's edge lies in the scoring, synthesis, and controversy detection across a massive multi-source universe — active synthesis, not exclusive access.",
            "complexity": "Light-Grey Swan. ESG signals are uncertain, noisy, and derived from heterogeneous non-financial data sources — requires ML heuristics to distinguish signal from noise in a high-dimensional search space.",
            "autonomy": "Low. CORRECTION from Gemini (Medium → Low): generates ESG scores and regulatory reports for human compliance officers and investment managers to review; no autonomous investment decisions.",
            "agent_type": "Commercial.",
            "stages": "Idea Assessment, Compliance. Correctly classified by Gemini."
            },
            "advantage": "analytical",
            "autonomy": "low",
            "agent_type": "commercial",
            "complexity": "light-grey",
            "stages": [
            "idea-assess",
            "compliance"
            ],
            "status": "classified"
        },
        {
            "name": "NICE Actimize SURVEIL-X / Actimize Intelligence",
            "url": "https://www.niceactimize.com/compliance/",
            "description": "A holistic conduct and trade surveillance platform that monitors voice recordings, electronic communications, and trade data simultaneously using AI/ML/NLP to detect misconduct risk patterns and generate regulatory alerts. The only platform in this list with integrated voice surveillance alongside text and trade data — multimodal misconduct detection.",
            "key_features": [
            "Voice + text + trade data surveillance simultaneously — the only multimodal misconduct detection system in this list",
            "Purpose-built for MAR, MiFID II, and Reg BI compliance — the narrowest and deepest regulatory compliance focus in this list"
            ],
            "rationale": {
            "advantage": "Analytical. Detects complex misconduct patterns across heterogeneous multimodal data through sophisticated ML pattern recognition — analytical synthesis of behavioral and transactional signals.",
            "complexity": "Light-Grey Swan. The regulatory framework is known (White Swan structure), but identifying misconduct in complex, noisy multimodal streams requires ML heuristics — making the effective complexity Light-Grey.",
            "autonomy": "Medium. Flags alerts and generates risk scores for human compliance reviewers; humans make enforcement decisions.",
            "agent_type": "Commercial.",
            "stages": "Compliance. Correctly classified by Gemini."
            },
            "advantage": "analytical",
            "autonomy": "medium",
            "agent_type": "commercial",
            "complexity": "light-grey",
            "stages": [
            "compliance"
            ],
            "status": "classified"
        },
        {
            "name": "Behavox (Quantum / Polaris)",
            "url": "https://www.behavox.com",
            "description": "An AI-native compliance platform using Behavox LLM 2.0 — a proprietary model trained on financial compliance data — to monitor all communications (Quantum) and conduct cross-asset trade surveillance across 10 asset classes (Polaris). Key differentiator from NICE Actimize: a proprietary finance-domain LLM and customer-inspectable training data that directly addresses the 'black-box' regulatory concern.",
            "key_features": [
            "Proprietary Behavox LLM 2.0 trained on financial compliance data — domain-specialized at a level comparable to BloombergGPT, not a general-purpose model",
            "Customer-inspectable training data — unique in this list in allowing regulated institutions to audit the model's knowledge base for bias and gaps"
            ],
            "rationale": {
            "advantage": "Analytical. Detects intent, sentiment, and misconduct patterns in communications and trade data using a domain-trained LLM — the edge is analytical depth from a specialized model.",
            "complexity": "Light-Grey Swan. Identifying conduct violations in massive, noisy communication and trade streams requires ML heuristics — regulatory rules are known, but pattern detection in complex data is not trivial.",
            "autonomy": "Medium. Generates recommendations and risk scores for human compliance approval.",
            "agent_type": "Commercial. Used heavily by Global Systemically Important Banks (GSIBs).",
            "stages": "Compliance. Correctly classified by Gemini."
            },
            "advantage": "analytical",
            "autonomy": "medium",
            "agent_type": "commercial",
            "complexity": "light-grey",
            "stages": [
            "compliance"
            ],
            "status": "classified"
        },
        {
            "name": "Ayasdi (SymphonyAI)",
            "url": "https://www.symphonyai.com/financial-services/",
            "description": "A specialized financial crime intelligence platform using Topological Data Analysis (TDA) to map the geometric shape of transaction data and discover hidden non-linear patterns invisible to standard ML — primarily applied to AML detection. TDA is fundamentally different from regression or tree-based methods: it finds structure in the data's topology rather than fitting statistical models.",
            "key_features": [
            "Uses Topological Data Analysis (TDA) — maps data geometry rather than fitting statistical models, detecting relationship patterns invisible to all other tools in this list",
            "Narrow AML specialization: deeper than NICE Actimize or Behavox in financial crime detection, but narrower in scope (no conduct surveillance)"
            ],
            "rationale": {
            "advantage": "Analytical. TDA-based geometric pattern discovery is a distinctly different — and more powerful for certain non-linear relationships — analytical approach than standard ML.",
            "complexity": "Light-Grey Swan. Transaction pattern search involves high-dimensional, non-linear relationships in noisy financial data — ML heuristics (here TDA) are required to find valid signals.",
            "autonomy": "Medium. Flags anomalous topologies for human review; humans make investigation and escalation decisions.",
            "agent_type": "Commercial (acquired by SymphonyAI).",
            "stages": "Compliance, Monitoring. Correctly classified by Gemini."
            },
            "advantage": "analytical",
            "autonomy": "medium",
            "agent_type": "commercial",
            "complexity": "light-grey",
            "stages": [
            "compliance",
            "monitoring"
            ],
            "status": "classified"
        },
        {
            "name": "Blueflame AI",
            "url": "https://www.blueflame.ai",
            "description": "A generative AI workspace built exclusively for alternative investment managers (PE, hedge funds, VC) that connects siloed internal data — CRMs, pitchbooks, financial models — for unified search and workflow automation within a SOC2-compliant environment. Distinct from Hebbia in targeting internal workflow data silos (CRM, internal models) rather than external private document due diligence.",
            "key_features": [
            "Built exclusively for alternative asset managers — integrates with alt-specific CRMs (DealCloud, 4Front, Salesforce) unlike general enterprise AI tools",
            "Targets internal data silos (CRM, pitchbooks, financial models) rather than external data rooms — complementary to Hebbia, not competitive"
            ],
            "rationale": {
            "advantage": "Informational. Connects and retrieves across proprietary internal data silos that are inaccessible to generic tools — the edge is internal knowledge organization, not analytical synthesis.",
            "complexity": "White Swan. Enterprise search and structured process automation within deterministic internal data environments — no probabilistic market signal search.",
            "autonomy": "Low. Requires human prompt engineering for each query; a direct co-pilot.",
            "agent_type": "Commercial.",
            "stages": "Idea Assessment, Stakeholder Management. Correctly classified by Gemini."
            },
            "advantage": "informational",
            "autonomy": "low",
            "agent_type": "commercial",
            "complexity": "white",
            "stages": [
            "idea-assess",
            "stakeholder"
            ],
            "status": "classified"
        },
        {
            "name": "JPMorgan IndexGPT",
            "url": "https://www.jpmorgan.com/technology/technology-blog/indexgpt",
            "description": "An in-house AI system that uses NLP and GPT-4 to translate market narratives into algorithmic thematic investment index baskets, with rapid automated backtesting before launch — automating the full idea-to-tradable-product pipeline for structured products and ETFs. NOTE: Incorrectly grouped with COIN by Gemini — these are two distinct tools with different advantage types and complexity levels.",
            "key_features": [
            "Translates market narrative (NLP) into a backtested tradable index basket — automating the idea-to-product pipeline for structured products",
            "Rapid thematic basket generation enables JPMorgan to bring narrative-driven investment products to market faster than competitors relying on manual construction"
            ],
            "rationale": {
            "advantage": "Analytical. Synthesizing abstract market narratives into quantitatively defined, backtested index baskets requires sophisticated interpretation of non-structured language into financial structure.",
            "complexity": "Light-Grey Swan. Translating NLP concepts into functional indices that will generalize to future non-stationary market environments — optimal baskets must be searched across a large, uncertain signal space.",
            "autonomy": "Medium. Autonomously generates index baskets, but launch requires human oversight and approval.",
            "agent_type": "In-house.",
            "stages": "Idea Generation, Idea Assessment. CORRECTION: separated from COIN (see below), which has a distinct classification."
            },
            "advantage": "analytical",
            "autonomy": "medium",
            "agent_type": "in-house",
            "complexity": "light-grey",
            "stages": [
            "idea-gen",
            "idea-assess"
            ],
            "status": "classified"
        },
        {
            "name": "JPMorgan COIN",
            "url": "https://www.jpmorgan.com/technology/technology-blog/",
            "description": "An in-house ML system that automates the extraction and interpretation of data clauses from complex legal documents (commercial loan agreements, ISDA contracts) — processing in seconds work that previously required 360,000 hours of lawyer time annually. NOTE: Incorrectly grouped with IndexGPT by Gemini — COIN has a fundamentally different advantage type (Informational, not Analytical) and complexity level (White Swan, not Light-Grey).",
            "key_features": [
            "Automates extraction from complex legal contracts — replaces 360,000 hours/year of manual lawyer review with seconds of automated parsing",
            "Purely a document processing engine: no market signal generation, no investment recommendation — pure legal data extraction"
            ],
            "rationale": {
            "advantage": "Informational. CORRECTION from Gemini: COIN extracts and organizes information locked in legal documents — the edge is access to structured data from contracts, not analytical synthesis. This is categorically different from IndexGPT's Analytical advantage.",
            "complexity": "White Swan. CORRECTION from Gemini: Legal contract parsing operates on stable, rule-based linguistic structures with deterministic extraction targets — not probabilistic signal search.",
            "autonomy": "Low. Extracts data for human legal and compliance teams to review and act upon.",
            "agent_type": "In-house.",
            "stages": "Idea Assessment, Compliance. CORRECTION: IndexGPT/COIN were merged as [idea-gen, idea-assess] — COIN's primary stages are Compliance (contract obligation monitoring) and Idea Assessment (structuring deal terms for analysis)."
            },
            "advantage": "informational",
            "autonomy": "low",
            "agent_type": "in-house",
            "complexity": "white",
            "stages": [
            "idea-assess",
            "compliance"
            ],
            "status": "classified"
        },
        {
            "name": "ShareWorks / Equity Edge MCP (Morgan Stanley)",
            "url": "https://shareworks.morganstanley.com",
            "description": "Morgan Stanley AI integrations within its equity plan administration platform (ShareWorks) that allow advisors to resolve complex equity compensation queries — RSUs, ESPPs, stock options — and parse large grant datasets via natural language. Narrowly focused on the equity plan operational layer: not investment decision support, but structured data retrieval for a highly regulated compensation domain.",
            "key_features": [
            "Specialized for equity compensation plans (RSUs, ESPPs, stock options) — the narrowest operational focus of any tool in this list",
            "Helps advisors interpret complex multi-grant compensation structures in deterministic, highly regulated data — pure retrieval, no market judgment"
            ],
            "rationale": {
            "advantage": "Informational. Reduces friction and time to access complex, structured equity plan data — the edge is organized retrieval of proprietary compensation records, not synthesis.",
            "complexity": "White Swan. Equity plan data is deterministic, tabular, and strictly regulated — the most structured and rule-bound data environment in this list.",
            "autonomy": "Low. On-demand analytics for human advisors; advisors make all client-facing decisions.",
            "agent_type": "In-house. CORRECTION: Gemini's URL pointed to a Seeking Alpha article — corrected to the actual ShareWorks platform URL.",
            "stages": "Stakeholder Management, Monitoring. Correctly classified by Gemini."
            },
            "advantage": "informational",
            "autonomy": "low",
            "agent_type": "in-house",
            "complexity": "white",
            "stages": [
            "stakeholder",
            "monitoring"
            ],
            "status": "classified"
        },
        {
            "name": "Citi Sky / Arc Platform",
            "url": "https://www.citigroup.com/global/news/perspectives/2026/introducing-ai-agents-next-phase-citi-artificial-intelligence-journey",
            "description": "Citi's next-generation internal AI agent framework (Sky/Arc) designed to automate multi-step institutional client workflows, transaction data structuring, and client service delivery across Citi's banking platform. One of the most recent deployments in this list (2026), with an agentic — rather than chat-only — architecture targeting full workflow automation.",
            "key_features": [
            "Agentic framework (not chat-only) — automates multi-step institutional client service workflows, not just single-turn queries",
            "Among the most recent large-bank AI deployments in this list (2026 announcement) — reflects the current industry shift from copilot to agentic workflow automation"
            ],
            "rationale": {
            "advantage": "Informational. Accelerates structuring and delivery of institutional transaction data to clients — edge is operational speed and data organization, not analytical synthesis.",
            "complexity": "White Swan. Institutional transaction processing and client data retrieval are highly stable, rule-based environments with deterministic data structures.",
            "autonomy": "Low. Assistant layer with automated workflow execution, but within defined institutional guardrails and with human oversight.",
            "agent_type": "In-house.",
            "stages": "Execution, Stakeholder Management. Correctly classified by Gemini."
            },
            "advantage": "informational",
            "autonomy": "low",
            "agent_type": "in-house",
            "complexity": "white",
            "stages": [
            "execution",
            "stakeholder"
            ],
            "status": "classified"
        },
        {
            "name": "Aiden (VWAP & Arrival) — RBC Capital Markets",
            "url": "https://www.rbccm.com/en/expertise/electronic-trading/aiden",
            "description": "RBC Capital Markets' AI-powered electronic trading platform using deep reinforcement learning to adapt order execution dynamically to live market microstructure, targeting minimum slippage against VWAP and Arrival Price benchmarks. Unlike JPMorgan's LOXM (internal only), Aiden is offered as a commercial execution service to institutional clients — making high-autonomy AI execution accessible externally.",
            "key_features": [
            "Commercially available AI execution service — distinguishes it from LOXM (JPMorgan's internal competitive tool), making adaptive execution accessible to external institutional clients",
            "Real-time adaptive order routing via DRL, moving beyond static VWAP schedules to dynamic microstructure response"
            ],
            "rationale": {
            "advantage": "Analytical. Deep RL learns superior order routing patterns from live market data — the edge is better real-time pattern recognition in market microstructure.",
            "complexity": "White Swan. Execution optimization has a well-defined, highly measurable objective function (minimize slippage vs. arrival price) with abundant historical trade data.",
            "autonomy": "High. Executes institutional orders autonomously in real time without per-trade human input.",
            "agent_type": "In-house (RBC proprietary, offered commercially to clients).",
            "stages": "Execution. Correctly classified by Gemini."
            },
            "advantage": "analytical",
            "autonomy": "high",
            "agent_type": "in-house",
            "complexity": "white",
            "stages": [
            "execution"
            ],
            "status": "classified"
        },
        {
            "name": "TOGGLE Copilot / Pro",
            "url": "https://toggle.ai",
            "description": "An AI-powered investment dashboard that monitors global equities and generates natural language alerts on technical and fundamental anomalies, translating complex signals into plain-English insights for non-quant users. Positioned at the retail/professional crossover, democratizing hedge-fund-style analytics for individual investors and small funds without quant infrastructure.",
            "key_features": [
            "Natural language translation of technical and fundamental signals — makes systematic investing accessible to non-quant users without coding or model-building",
            "Covers 20+ asset classes including crypto and macro factors — broader coverage than most institutional tools in this list"
            ],
            "rationale": {
            "advantage": "Analytical. Synthesizes billions of data points into logic trees and actionable alerts — edge is interpretation and accessibility of complex signals, not exclusive data access.",
            "complexity": "Light-Grey Swan. Uses ML heuristics to search for valid signals in non-stationary market data across multiple asset classes.",
            "autonomy": "Low. Generates insights and alerts; execution is entirely at the user's discretion.",
            "agent_type": "Commercial.",
            "stages": "Idea Generation, Monitoring. Correctly classified by Gemini."
            },
            "advantage": "analytical",
            "autonomy": "low",
            "agent_type": "commercial",
            "complexity": "light-grey",
            "stages": [
            "idea-gen",
            "monitoring"
            ],
            "status": "classified"
        },
        {
            "name": "InvestGPT (Kavout)",
            "url": "https://www.kavout.com/investgpt",
            "description": "A conversational AI interface by Kavout that allows users to construct and backtest equity strategies entirely in natural language, drawing on K-Score ratings and fundamental data for integrated signal testing. Distinct from Kavout's standalone K-Score screener in adding the strategy construction and backtesting layer on top of the same analytical engine.",
            "key_features": [
            "Natural language to quantitative backtest — makes algorithmic strategy construction and testing accessible without coding or quant infrastructure",
            "Integrates K-Score as a first-class signal within strategy construction — unique to Kavout's ecosystem, not replicable by generic backtest tools"
            ],
            "rationale": {
            "advantage": "Analytical. Translates natural language strategy specifications into quantitative backtests — the edge is superior accessibility to analytical strategy construction.",
            "complexity": "Light-Grey Swan. Backtesting searches for strategies that will generalize to future non-stationary market conditions — a signal optimization problem under uncertainty.",
            "autonomy": "Low. Conversational screener and strategy builder; the human decides whether to act on backtested results.",
            "agent_type": "Commercial.",
            "stages": "Idea Generation, Idea Assessment. Correctly classified by Gemini."
            },
            "advantage": "analytical",
            "autonomy": "low",
            "agent_type": "commercial",
            "complexity": "light-grey",
            "stages": [
            "idea-gen",
            "idea-assess"
            ],
            "status": "classified"
        },
        {
            "name": "Pluto.fi (Robinhood)",
            "url": "https://robinhood.com/pluto",
            "description": "A retail-facing conversational AI platform (acquired by Robinhood) that uses a Thinker-Actor-Communicator agent architecture to let users build, backtest, and automate custom trading strategies entirely through natural language — then execute them automatically within Robinhood's brokerage. The highest-autonomy commercial retail tool in this list, with the largest potential user base via Robinhood integration.",
            "key_features": [
            "Thinker-Actor-Communicator architecture — the only explicitly multi-role agentic design among retail tools; strategies execute automatically post-approval",
            "Acquired by Robinhood: now accessible to Robinhood's tens of millions of retail users — the largest potential user base of any tool in this list"
            ],
            "rationale": {
            "advantage": "Analytical. Lowers the barrier to algorithmic strategy construction for retail investors — the edge is accessibility to analytical methods, not exclusive data.",
            "complexity": "Light-Grey Swan. Strategy construction requires searching for patterns in historical market data that will generalize to future non-stationary conditions.",
            "autonomy": "Medium. Users define the strategy in natural language; it then runs automatically under user supervision — not fully autonomous since the strategy logic originates from and is approved by the user.",
            "agent_type": "Commercial (Robinhood subsidiary).",
            "stages": "Idea Generation, Decision, Execution. Correctly classified by Gemini."
            },
            "advantage": "analytical",
            "autonomy": "medium",
            "agent_type": "commercial",
            "complexity": "light-grey",
            "stages": [
            "idea-gen",
            "decision",
            "execution"
            ],
            "status": "classified"
        }
    ]

    agents_data_new = [
        {
            "name": "Aiera",
            "url": "https://aiera.com",
            "description": "Real-time event intelligence platform that transcribes, indexes, and alerts on earnings calls, investor days, and corporate events as they happen, giving analysts structured access to management commentary before consensus digests it. Distinct from news platforms (RavenPack, Dataminr) in that the primary source is live corporate audio — not social media or news wires.",
            "key_features": [
            "Real-time earnings call transcription with speaker attribution and live search — the only tool in this list whose primary data source is live corporate audio",
            "Event-driven alerts and document structuring across a universe of scheduled corporate events — enables systematic monitoring of management communications at scale"
            ],
            "rationale": {
            "advantage": "Informational. Real-time access to management commentary during scheduled corporate events before it is widely processed or reported — speed and directness of the information channel is the edge.",
            "complexity": "White Swan. Earnings calls and investor days are scheduled, structured events with known formats (CEO/CFO Q&A, guidance language). The content is uncertain, but the event framework is deterministic.",
            "autonomy": "Low. Streams structured event intelligence to human analysts; humans interpret all implications and make investment decisions.",
            "agent_type": "Commercial.",
            "stages": "Idea Generation (early signal from earnings commentary), Idea Assessment (company-specific research), Monitoring (ongoing tracking of management communications)."
            },
            "advantage": "informational",
            "autonomy": "low",
            "agent_type": "commercial",
            "complexity": "white",
            "stages": ["idea-gen", "idea-assess", "monitoring"]
        },
        {
            "name": "ARKEN Finance",
            "url": "https://www.arkenfinance.com",
            "description": "AI-powered portfolio construction platform that generates optimized multi-asset portfolios from a defined investment universe using factor models and ML-driven risk-return estimation, then delivers model portfolios to discretionary managers for approval. Positioned between pure quant platforms (SigTech) and advisory tools (Vise AI) — aimed at multi-asset managers and DFMs.",
            "key_features": [
            "Generates fully specified model portfolios with risk attribution — goes beyond screening to produce actionable allocation recommendations ready for human approval",
            "Covers the full construction-to-monitoring loop: optimization, rebalancing triggers, and portfolio drift monitoring in one integrated platform"
            ],
            "rationale": {
            "advantage": "Analytical. Multi-factor portfolio optimization at scale — the edge is superior synthesis of risk-return signals into coherent allocations, not privileged data access.",
            "complexity": "Light-Grey Swan. Portfolio optimization requires searching for optimal weights in a non-stationary risk environment; probability distributions are theoretically known but computationally intractable to optimize exactly.",
            "autonomy": "Medium. Generates optimized portfolio recommendations with risk attribution; human discretionary manager approves and executes.",
            "agent_type": "Commercial.",
            "stages": "Idea Assessment (evaluating opportunities within universe), Decision (portfolio construction and rebalancing proposals), Monitoring (drift and risk monitoring)."
            },
            "advantage": "analytical",
            "autonomy": "medium",
            "agent_type": "commercial",
            "complexity": "light-grey",
            "stages": ["idea-assess", "decision", "monitoring"]
        },
        {
            "name": "Auquan",
            "url": "https://www.auquan.com",
            "description": "Investment research automation platform that deploys AI agents to generate analyst-grade research output — earnings analysis, sector deep dives, and thematic research — by synthesizing filings, news, transcripts, and alternative data. Distinctive in targeting the core analyst workflow (not just search or Q&A) with structured research deliverables.",
            "key_features": [
            "Generates structured investment research documents (not just summaries) — moves from search/retrieval to full analyst-grade output production",
            "Multi-source synthesis across filings, transcripts, news, and alternative data with source citations — designed to replace repetitive analyst prep work, not the investment judgment"
            ],
            "rationale": {
            "advantage": "Analytical. Synthesizes diverse data sources into research-grade deliverables — the value is superior quality of analytical output relative to manual analyst effort, not exclusive data access.",
            "complexity": "White Swan. The synthesis process operates over known financial document types (filings, transcripts, news) in a structured workflow — the production of research reports is a well-defined task, even if markets are uncertain.",
            "autonomy": "Low. Generates research for human analyst review and judgment; humans make investment decisions from the output.",
            "agent_type": "Commercial.",
            "stages": "Idea Generation (thematic and sector research), Idea Assessment (company-specific analysis), Stakeholder Management (generating client-ready research content)."
            },
            "advantage": "analytical",
            "autonomy": "low",
            "agent_type": "commercial",
            "complexity": "white",
            "stages": ["idea-gen", "idea-assess", "stakeholder"]
        },
        {
            "name": "Axyon AI",
            "url": "https://axyon.ai",
            "description": "Deep learning signal generation platform for asset managers, producing directional price forecasts and risk signals across asset classes based on 20+ years of historical market data without requiring feature engineering from users. Differentiator: fully managed ML model lifecycle — the asset manager consumes signals via API without maintaining the model infrastructure.",
            "key_features": [
            "Delivers pre-built directional signals via API without requiring in-house quant model development — lowers the barrier to systematic factor integration for traditional managers",
            "Fully managed model lifecycle (training, validation, production) — the only tool in the alpha-signal category where the manager consumes outputs without owning the models"
            ],
            "rationale": {
            "advantage": "Analytical. Deep learning extraction of predictive signals from historical market data — superior computational synthesis of market patterns is the edge.",
            "complexity": "Light-Grey Swan. Forecasting directional price movements in non-stationary market environments — probability distributions are theoretically defined but computationally intractable; ML search for robust signals is required.",
            "autonomy": "Low. Delivers signals for human portfolio managers to incorporate into their process; no autonomous allocation.",
            "agent_type": "Commercial.",
            "stages": "Idea Generation (signal-driven opportunity identification), Idea Assessment (incorporating ML signals into analysis), Monitoring (ongoing signal tracking)."
            },
            "advantage": "analytical",
            "autonomy": "low",
            "agent_type": "commercial",
            "complexity": "light-grey",
            "stages": ["idea-gen", "idea-assess", "monitoring"]
        },
        {
            "name": "Boosted.ai",
            "url": "https://www.boosted.ai",
            "description": "AI platform for equity portfolio management that combines fundamental, quantitative, and alternative data to generate factor-based investment signals and portfolio construction recommendations for institutional equity managers. Covers the full loop from signal generation to portfolio optimization, distinguishing it from pure data vendors.",
            "key_features": [
            "Integrates fundamental, quantitative, and alternative data signals into unified equity scores — broader signal integration than pure-factor quant tools",
            "Covers signal generation through portfolio construction in one workflow — not just a screener, but a full investment process support layer for active equity managers"
            ],
            "rationale": {
            "advantage": "Analytical. Superior synthesis of heterogeneous equity data (fundamental + quant + alternative) into unified investment signals — the edge is multi-source analytical integration, not data exclusivity.",
            "complexity": "Light-Grey Swan. Equity signal generation and portfolio optimization in non-stationary markets — ML heuristics are needed to search for robust predictive factors.",
            "autonomy": "Low. Generates signals and portfolio recommendations for human portfolio managers; managers retain full discretion.",
            "agent_type": "Commercial.",
            "stages": "Idea Generation (signal-driven equity screening), Idea Assessment (equity analysis and scoring)."
            },
            "advantage": "analytical",
            "autonomy": "low",
            "agent_type": "commercial",
            "complexity": "light-grey",
            "stages": ["idea-gen", "idea-assess"]
        },
        {
            "name": "EILLA AI",
            "url": "https://eilla.ai",
            "description": "Investment research automation platform specifically built for M&A, VC, and PE workflows — automatically generating deal memos, company tearsheets, and competitive analyses from structured deal inputs. Unlike general research tools, EILLA's entire workflow is calibrated to private market deal timelines and documentation conventions.",
            "key_features": [
            "M&A/VC/PE-specific output templates (deal memos, tearsheets, IC memos) — not generic research, but deal-process-ready deliverables",
            "Designed for private market workflows where deal velocity matters — faster preliminary analysis enables wider deal screening without proportional analyst headcount"
            ],
            "rationale": {
            "advantage": "Analytical. Synthesizes deal-relevant data (company info, market comps, financials) into investment-process-ready research — the edge is workflow-specific analytical output quality.",
            "complexity": "White Swan. Deal memo generation operates over known data types (company filings, CIMs, comparable transactions) with structured output templates — a deterministic synthesis environment.",
            "autonomy": "Low. Generates research deliverables for investment professional review; humans make all investment decisions.",
            "agent_type": "Commercial.",
            "stages": "Idea Generation (deal sourcing research), Idea Assessment (preliminary deal analysis), Stakeholder Management (IC presentation preparation)."
            },
            "advantage": "analytical",
            "autonomy": "low",
            "agent_type": "commercial",
            "complexity": "white",
            "stages": ["idea-gen", "idea-assess", "stakeholder"]
        },
        {
            "name": "MDOTM (Sei)",
            "url": "https://www.mdotm.ai",
            "description": "AI-driven systematic asset allocation platform (product: Sei) that uses ML to generate multi-asset portfolio recommendations, integrating macro signals, risk factor analysis, and portfolio optimization for institutional investors. Bridges the gap between pure quant funds and traditional discretionary multi-asset managers by making systematic allocation accessible without an in-house quant team.",
            "key_features": [
            "Generates systematic multi-asset allocation recommendations via ML — makes quant-grade portfolio construction available to discretionary institutional managers without in-house quant infrastructure",
            "Integrates macro factor analysis, risk attribution, and portfolio optimization in one output — goes beyond signal generation to full allocation proposal"
            ],
            "rationale": {
            "advantage": "Analytical. ML-driven multi-asset portfolio construction — the edge is computational synthesis of macro and risk signals into coherent allocation recommendations.",
            "complexity": "Light-Grey Swan. Multi-asset allocation in non-stationary macro environments — optimal allocations must be searched across uncertain, interdependent factor dynamics.",
            "autonomy": "Medium. Generates systematic portfolio recommendations with rationale; human portfolio managers review, adjust, and approve before execution.",
            "agent_type": "Commercial.",
            "stages": "Idea Assessment (evaluating allocation opportunities), Decision (portfolio construction proposals), Monitoring (ongoing factor and risk tracking)."
            },
            "advantage": "analytical",
            "autonomy": "medium",
            "agent_type": "commercial",
            "complexity": "light-grey",
            "stages": ["idea-assess", "decision", "monitoring"]
        },
        {
            "name": "Neural Alpha",
            "url": "https://www.neuralalpha.com",
            "description": "AI platform for systematic hedge funds providing deep learning-based alpha signal generation and strategy research tools, designed to integrate directly into existing quant workflows without replacing the fund's proprietary models. Positioned as an analytical layer for established systematic managers, not a standalone allocation system.",
            "key_features": [
            "Deep learning signal generation designed for integration into existing quant frameworks — not a standalone product but an analytical enhancement layer for systematic managers",
            "Covers strategy research through signal production without extending into execution — maintains clean separation between signal generation and trading decisions"
            ],
            "rationale": {
            "advantage": "Analytical. Deep learning extraction of alpha signals from market data — the edge is advanced pattern recognition in financial time series exceeding traditional factor models.",
            "complexity": "Light-Grey Swan. Alpha signal discovery in non-stationary markets — searching for patterns that are computationally intractable to optimize exactly using classical methods.",
            "autonomy": "Low. Produces signals for systematic portfolio managers to incorporate into their own models; no autonomous allocation or execution.",
            "agent_type": "Commercial.",
            "stages": "Idea Generation (signal-driven opportunity identification), Idea Assessment (signal validation and strategy research)."
            },
            "advantage": "analytical",
            "autonomy": "low",
            "agent_type": "commercial",
            "complexity": "light-grey",
            "stages": ["idea-gen", "idea-assess"]
        },
        {
            "name": "Rogo",
            "url": "https://www.rogo.ai",
            "description": "Natural language AI research assistant for investment banking and asset management that answers complex financial questions by retrieving and citing data from filings, research reports, financial databases, and news. Differentiates from general LLM tools through investment-specific data integrations and mandatory citation for every claim.",
            "key_features": [
            "Mandatory source citation for every answer — designed for professional investment contexts where claims must be auditable and defensible to clients or regulators",
            "Deep integration with financial data sources (SEC filings, earnings, market data) rather than general web — answers are drawn from investment-relevant databases, not open-web inference"
            ],
            "rationale": {
            "advantage": "Informational. Rapid, structured retrieval from financial databases with mandatory sourcing — the edge is access speed and citation quality, not synthesis depth.",
            "complexity": "White Swan. Q&A over structured financial documents and databases — well-defined retrieval over known document types with deterministic citation requirements.",
            "autonomy": "Low. Answers financial questions for human analysts; all investment decisions remain with the analyst.",
            "agent_type": "Commercial.",
            "stages": "Idea Assessment (researching companies, transactions, markets), Stakeholder Management (supporting client-facing research preparation)."
            },
            "advantage": "informational",
            "autonomy": "low",
            "agent_type": "commercial",
            "complexity": "white",
            "stages": ["idea-assess", "stakeholder"]
        },
        {
            "name": "SigTech",
            "url": "https://sigtech.com",
            "description": "Cloud-based systematic investment research and backtesting platform that provides quantitative managers with clean multi-asset data pipelines, strategy development environments, and portfolio analytics in a unified research infrastructure. Targets the full quant research lifecycle — from data to strategy to portfolio analysis — without requiring proprietary data infrastructure.",
            "key_features": [
            "Clean, production-ready multi-asset data pipelines eliminating data engineering overhead — allows quant researchers to focus on strategy logic rather than infrastructure",
            "Covers the full quant research lifecycle (data → signal → backtest → portfolio) in one environment — reduces the fragmented toolchain typical of systematic investing"
            ],
            "rationale": {
            "advantage": "Analytical. Systematic strategy development and backtesting infrastructure enabling superior signal discovery and validation — the edge is research efficiency and analytical rigor, not data exclusivity.",
            "complexity": "Light-Grey Swan. Systematic signal discovery and strategy validation in non-stationary markets — quant researchers use the platform to search for robust patterns in uncertain environments.",
            "autonomy": "Low. Provides research tools for human quant researchers; strategies require human decision to deploy.",
            "agent_type": "Commercial.",
            "stages": "Idea Generation (systematic signal discovery), Idea Assessment (strategy backtesting and validation), Decision (strategy selection and sizing)."
            },
            "advantage": "analytical",
            "autonomy": "low",
            "agent_type": "commercial",
            "complexity": "light-grey",
            "stages": ["idea-gen", "idea-assess", "decision"]
        },
        {
            "name": "Vise AI",
            "url": "https://www.vise.com",
            "description": "AI-powered portfolio construction and management platform for financial advisors and RIAs that automates personalized portfolio creation, tax-loss harvesting, and rebalancing across individual client accounts at scale. The core differentiator: enables true individualization at the account level rather than model-portfolio approximations, across hundreds of advisor clients simultaneously.",
            "key_features": [
            "Account-level individualization: each client gets a unique portfolio respecting their specific tax lot history, restrictions, and risk profile — impossible manually at scale",
            "Autonomous rebalancing and tax-loss harvesting within pre-approved mandates — the highest autonomy of any wealth management platform in this list"
            ],
            "rationale": {
            "advantage": "Analytical. Automated multi-constraint portfolio optimization across hundreds of individual accounts simultaneously — superior computational capability relative to manual advisor management.",
            "complexity": "Light-Grey Swan. Portfolio optimization across individual client constraints in non-stationary markets — optimal personalized solutions require ML heuristics to search across uncertain risk-return environments.",
            "autonomy": "Medium. Autonomously constructs, rebalances, and harvests tax losses within pre-approved client mandates; advisor reviews and approves the mandate parameters, not each trade.",
            "agent_type": "Commercial.",
            "stages": "Idea Assessment (evaluating allocations per client profile), Decision (portfolio construction), Execution (rebalancing and tax-loss harvesting), Monitoring (drift and performance tracking)."
            },
            "advantage": "analytical",
            "autonomy": "medium",
            "agent_type": "commercial",
            "complexity": "light-grey",
            "stages": ["idea-assess", "decision", "execution", "monitoring"]
        },
        {
            "name": "DiligenceSquared",
            "url": "https://www.diligencesquared.com",
            "description": "AI-powered operational due diligence automation platform for institutional investors, processing manager DDQs, regulatory filings, and operational data to generate structured ODD risk assessments and ongoing monitoring reports. Targets the systematic, repeatable part of operational due diligence — not investment merit assessment.",
            "key_features": [
            "Processes DDQs and operational data at scale — enables institutional allocators to conduct systematic ODD across a larger manager universe without proportional analyst headcount",
            "Ongoing monitoring module: re-runs ODD assessment on portfolio managers continuously, not just at onboarding — converting a point-in-time exercise into continuous oversight"
            ],
            "rationale": {
            "advantage": "Analytical. Synthesizes heterogeneous operational risk data (DDQs, regulatory filings, reference checks) into structured ODD risk assessments — superior synthesis of complex multi-source operational information.",
            "complexity": "White Swan. ODD operates against defined regulatory frameworks (SEC ADV, AIFMD filings) and structured DDQ templates — well-defined assessment criteria, not uncertain market signal search.",
            "autonomy": "Low. Generates ODD analysis and risk flags for human fund-of-fund or allocator teams to review and act upon.",
            "agent_type": "Commercial.",
            "stages": "Idea Assessment (operational risk assessment of target managers), Compliance (regulatory filing monitoring)."
            },
            "advantage": "analytical",
            "autonomy": "low",
            "agent_type": "commercial",
            "complexity": "white",
            "stages": ["idea-assess", "compliance"]
        },
        {
            "name": "Harmonic",
            "url": "https://harmonic.ai",
            "description": "AI deal-sourcing platform for VC and growth equity investors that scans real-time signals across company websites, LinkedIn, GitHub, job postings, and product databases to surface emerging companies before they appear in traditional deal flow channels. The edge is discovery velocity: identifying high-growth companies at Series A or earlier before they are widely covered.",
            "key_features": [
            "Scans 20M+ companies in real time across non-traditional signals (GitHub commits, job postings, product launches) — discovers companies before they appear in pitch books or traditional databases",
            "Relevance scoring and alerts for companies matching user-defined growth signals — converts a manual market scanning process into an automated early-warning system"
            ],
            "rationale": {
            "advantage": "Informational. Early-stage discovery from alternative signals (web activity, hiring, GitHub) before companies become widely known — pure informational edge through novel data source access.",
            "complexity": "Light-Grey Swan. Identifying valid high-growth signals amid very noisy, heterogeneous web data requires ML heuristics — probability distributions of company quality are theoretically defined but computationally hard to search.",
            "autonomy": "Low. Surfaces investment opportunities for human VC partners to evaluate; humans conduct all investment analysis and decisions.",
            "agent_type": "Commercial.",
            "stages": "Idea Generation (early-stage company discovery), Idea Assessment (qualifying surfaced opportunities)."
            },
            "advantage": "informational",
            "autonomy": "low",
            "agent_type": "commercial",
            "complexity": "light-grey",
            "stages": ["idea-gen", "idea-assess"]
        },
        {
            "name": "Wokelo Agentic Builder",
            "url": "https://wokelo.ai",
            "description": "Agentic AI research platform that autonomously generates comprehensive investment research deliverables — company profiles, competitive landscapes, M&A target analyses — from a single prompt, without step-by-step instructions. Differentiates from co-pilots (Finpilot, Rogo) through true agentic autonomy: the system plans, searches, retrieves, and writes the full report independently.",
            "key_features": [
            "Fully agentic: generates a complete research report from a single prompt — no per-step instructions, no iterative prompting required by the analyst",
            "Covers company profiling through to competitive landscape and M&A target analysis — the broadest autonomous research scope of any tool in this batch"
            ],
            "rationale": {
            "advantage": "Analytical. Agentic multi-source synthesis of investment research — the edge is the autonomous orchestration of search, retrieval, and synthesis into a complete deliverable.",
            "complexity": "White Swan. Research report generation operates over known financial document types and structured data sources — deterministic synthesis environment, even if markets are uncertain.",
            "autonomy": "Medium. The agent autonomously plans and executes the full research workflow from a single prompt, but the output is reviewed by a human analyst before any investment decision.",
            "agent_type": "Commercial.",
            "stages": "Idea Generation (generating new research coverage), Idea Assessment (producing company and sector analysis), Stakeholder Management (preparing client-facing research materials)."
            },
            "advantage": "analytical",
            "autonomy": "medium",
            "agent_type": "commercial",
            "complexity": "white",
            "stages": ["idea-gen", "idea-assess", "stakeholder"]
        },
        {
            "name": "SmartKarma",
            "url": "https://www.smartkarma.com",
            "description": "Independent investment research marketplace and analytics platform where specialist independent analysts publish insights for institutional investors, augmented by AI-powered research discovery, scoring, and portfolio analytics tools. The key differentiator: independent research free from sell-side conflict of interest, structured for professional institutional consumption.",
            "key_features": [
            "Independent research marketplace: access to non-sell-side specialist analysts covering markets and companies outside traditional broker coverage — editorial independence is the core informational moat",
            "AI-powered research relevance scoring and portfolio analytics layer sits atop the marketplace — helping analysts prioritize which research is most actionable for their positions"
            ],
            "rationale": {
            "advantage": "Informational. Access to differentiated, independent research perspectives — the moat is editorial independence and specialist coverage breadth, not AI synthesis capability.",
            "complexity": "Light-Grey Swan. The research covers non-stationary investment opportunities across global markets — human analysts on the platform operate in uncertain market environments.",
            "autonomy": "Low. Research discovery and analytics platform for human portfolio managers; humans make all investment decisions.",
            "agent_type": "Commercial.",
            "stages": "Idea Generation (discovering new investment opportunities from independent research), Idea Assessment (evaluating theses across analyst perspectives)."
            },
            "advantage": "informational",
            "autonomy": "low",
            "agent_type": "commercial",
            "complexity": "light-grey",
            "stages": ["idea-gen", "idea-assess"]
        },
        {
            "name": "Hadrius",
            "url": "https://www.hadrius.com",
            "description": "AI-powered compliance automation platform built specifically for RIAs, hedge funds, and fintech firms to automate SEC/FINRA compliance workflows, policy generation, regulatory filing preparation, and ongoing review monitoring. Unlike generic compliance tools, Hadrius is purpose-built for the specific regulatory environment of investment advisers.",
            "key_features": [
            "Automates the full SEC/FINRA compliance workflow from policy generation to filing preparation — not just flagging, but drafting and submitting required regulatory documents",
            "Built exclusively for investment adviser regulatory environments (Form ADV, compliance program reviews) — investment-specific regulatory depth that generic compliance tools lack"
            ],
            "rationale": {
            "advantage": "Analytical. Synthesizing regulatory requirements against firm-specific activities to identify gaps and generate compliant documents — superior analytical processing of complex regulatory frameworks.",
            "complexity": "White Swan. SEC and FINRA regulatory requirements are published and defined — compliance tasks operate against deterministic rule sets even if voluminous.",
            "autonomy": "Medium. Autonomously generates compliance documents, policies, and filing drafts; human compliance officers review and approve before submission.",
            "agent_type": "Commercial.",
            "stages": "Compliance."
            },
            "advantage": "analytical",
            "autonomy": "medium",
            "agent_type": "commercial",
            "complexity": "white",
            "stages": ["compliance"]
        },
        {
            "name": "Norm AI",
            "url": "https://www.norm.ai",
            "description": "AI agent platform that converts complex regulatory and policy text into executable compliance monitoring rules, enabling financial institutions to deploy agents that continuously monitor operations against formal regulatory requirements. The key innovation: bridging the gap between legal language and executable compliance logic without manual rule-coding.",
            "key_features": [
            "Converts regulatory text directly into executable monitoring rules — eliminates the manual translation from legal language to compliance code that is typically done by expensive legal-tech teams",
            "Continuous compliance monitoring agents update automatically as regulations change — the only tool in the compliance category with regulatory language as its primary AI input"
            ],
            "rationale": {
            "advantage": "Analytical. Translating unstructured regulatory language into structured, executable compliance logic — the edge is superior NLP comprehension of legal text for operational deployment.",
            "complexity": "White Swan. Regulatory frameworks are published, defined, and formally structured — the compliance environment is deterministic even if the text is complex.",
            "autonomy": "Medium. Agents continuously monitor and flag compliance violations; human compliance officers handle escalation and remediation decisions.",
            "agent_type": "Commercial.",
            "stages": "Compliance."
            },
            "advantage": "analytical",
            "autonomy": "medium",
            "agent_type": "commercial",
            "complexity": "white",
            "stages": ["compliance"]
        },
        {
            "name": "Holistic AI",
            "url": "https://www.holisticai.com",
            "description": "AI governance and risk management platform that audits, monitors, and documents AI models for bias, reliability, fairness, and regulatory compliance — a meta-AI tool governing other AI deployments within financial institutions. Directly relevant as investment firms deploy more AI agents (from this list): Holistic AI provides the governance layer required by EU AI Act and MiFID II obligations.",
            "key_features": [
            "Meta-AI function: governs and audits other AI systems rather than generating investment signals — the only tool in this list that operates on AI models as its primary subject",
            "Addresses EU AI Act and MiFID II model risk requirements — provides the documentation and monitoring layer regulators are beginning to require for AI in financial services"
            ],
            "rationale": {
            "advantage": "Analytical. Systematic assessment of AI model risks and biases using established auditing methodologies — the edge is rigorous analytical evaluation of model behavior across diverse deployment contexts.",
            "complexity": "Light-Grey Swan. AI model behavior is uncertain and context-dependent — identifying bias, reliability issues, and failure modes requires ML audit techniques applied to non-deterministic systems.",
            "autonomy": "Low. Generates audit reports and risk assessments for human governance and compliance teams to review and act upon.",
            "agent_type": "Commercial.",
            "stages": "Compliance (AI regulatory governance), Monitoring (ongoing model behavior surveillance)."
            },
            "advantage": "analytical",
            "autonomy": "low",
            "agent_type": "commercial",
            "complexity": "light-grey",
            "stages": ["compliance", "monitoring"]
        },
        {
            "name": "Riskspan",
            "url": "https://riskspan.com",
            "description": "AI-enhanced risk analytics platform specializing in structured finance (MBS, ABS, CLOs, GSE securities) with ML-augmented prepayment modeling, credit risk analysis, and portfolio stress testing. The specialization is what distinguishes it: structured product risk requires domain expertise (prepayment models, tranche waterfall analysis) that general risk platforms do not provide.",
            "key_features": [
            "ML-augmented prepayment and credit models for structured products — the deepest domain specialization of any risk tool in this list (MBS, CLO, ABS, GSE-specific models)",
            "Covers the full structured finance risk workflow from collateral analysis through portfolio stress testing — not a generic risk platform adapted to structured products"
            ],
            "rationale": {
            "advantage": "Analytical. Specialist ML modeling for structured product risks that require deep domain expertise — the edge is analytical depth in a complexity-intensive asset class.",
            "complexity": "Light-Grey Swan. Structured finance risk involves complex probabilistic modeling of prepayments and defaults in non-stationary economic environments — ML heuristics are required to search the solution space.",
            "autonomy": "Low. Generates risk analytics and stress test results for human structured finance portfolio managers and risk officers.",
            "agent_type": "Commercial.",
            "stages": "Idea Assessment (evaluating structured product investments), Monitoring (ongoing portfolio risk surveillance), Compliance (regulatory capital reporting)."
            },
            "advantage": "analytical",
            "autonomy": "low",
            "agent_type": "commercial",
            "complexity": "light-grey",
            "stages": ["idea-assess", "monitoring", "compliance"]
        },
        {
            "name": "QuantAgent",
            "url": "https://arxiv.org/abs/2402.06656",
            "description": "Academic self-improving LLM agent framework for quantitative investment research that autonomously generates, tests, and iterates on quantitative trading hypotheses through an agent loop — seeking strategies with genuine alpha rather than overfitting. Distinctive in the academic category for its self-correction mechanism: the agent reflects on backtesting failures and revises its own hypotheses.",
            "key_features": [
            "Self-improving agent loop: autonomously generates hypotheses, backtests them, analyzes failures, and revises — the first academic framework to implement genuine self-reflection in quant strategy discovery",
            "Targeted at the 'holy grail' problem of quant investing: strategies that generalize out-of-sample — self-correction is designed to reduce the overfitting that plagues pure ML backtesters"
            ],
            "rationale": {
            "advantage": "Analytical. Agentic self-improving framework for quantitative strategy discovery — the edge is autonomous hypothesis generation and revision through iterative analytical search.",
            "complexity": "Light-Grey Swan. Quantitative strategy discovery in non-stationary markets — searching for patterns that generalize is computationally intractable and requires iterative heuristic refinement.",
            "autonomy": "High. Autonomously generates, tests, and revises strategies through a full agent loop in backtesting environments — no human involvement in each iteration.",
            "agent_type": "Academic.",
            "stages": "Idea Generation (strategy hypothesis generation), Idea Assessment (backtesting and validation), Decision (strategy selection from evaluated candidates)."
            },
            "advantage": "analytical",
            "autonomy": "high",
            "agent_type": "academic",
            "complexity": "light-grey",
            "stages": ["idea-gen", "idea-assess", "decision"]
        },
        {
            "name": "FLAG-Trader",
            "url": "https://arxiv.org/abs/2312.04875",
            "description": "Academic multi-agent LLM trading framework that deploys specialized role-based agents (macro analyst, technical analyst, sentiment analyst) coordinated by a meta-agent to produce consensus trading signals and portfolio decisions. Distinct from AlphaAgents (BlackRock) by including execution in the agent loop and integrating macro-level analysis as a distinct agent role.",
            "key_features": [
            "Role-based agent specialization (macro, technical, sentiment) coordinated by a meta-agent — more granular division of analytical labor than BlackRock AlphaAgents' three-role architecture",
            "Includes execution in the agent loop (not just recommendation) — one of the few academic frameworks to span the full Decision-to-Execution chain autonomously in backtesting"
            ],
            "rationale": {
            "advantage": "Analytical. Structured multi-agent reasoning across macro, technical, and sentiment domains — the edge is wider analytical perspective coverage through role specialization.",
            "complexity": "Light-Grey Swan. Trading signal generation and execution in non-stationary market environments — known uncertainty structures requiring ML-based signal search.",
            "autonomy": "High. Autonomous from signal generation through trade execution in backtesting environments.",
            "agent_type": "Academic.",
            "stages": "Idea Assessment (multi-agent analytical deliberation), Decision (consensus investment decision), Execution (autonomous trade execution in backtesting)."
            },
            "advantage": "analytical",
            "autonomy": "high",
            "agent_type": "academic",
            "complexity": "light-grey",
            "stages": ["idea-assess", "decision", "execution"]
        },
        {
            "name": "Theia Insights",
            "url": "https://www.theiainsights.com",
            "description": "AI-powered investment decision intelligence platform that synthesizes macro data, fundamental analysis, and alternative signals into structured investment insights for institutional portfolio managers and family offices. Positions itself as an intelligence layer sitting above data vendors — not another data source, but a synthesis and interpretation engine.",
            "key_features": [
            "Cross-domain synthesis (macro + fundamental + alternative data) into unified investment insights — functions as an interpretation layer above raw data, not another data vendor",
            "Targeted at smaller institutional managers and family offices lacking dedicated research infrastructure — brings multi-source analytical synthesis to teams without full quant capability"
            ],
            "rationale": {
            "advantage": "Analytical. Multi-source investment signal synthesis — the edge is quality of cross-domain interpretation, not exclusive data access.",
            "complexity": "Light-Grey Swan. Synthesizing macro, fundamental, and alternative signals in non-stationary investment environments — multi-source signal integration requires ML heuristics.",
            "autonomy": "Low. Generates structured investment insights for human portfolio managers to act upon.",
            "agent_type": "Commercial.",
            "stages": "Idea Generation (multi-signal opportunity identification), Idea Assessment (structured investment analysis), Decision (decision-support insights for portfolio managers)."
            },
            "advantage": "analytical",
            "autonomy": "low",
            "agent_type": "commercial",
            "complexity": "light-grey",
            "stages": ["idea-gen", "idea-assess", "decision"]
        },
        {
            "name": "StockSnips",
            "url": "https://stocksnips.net",
            "description": "AI platform that generates per-stock structured news summaries and sentiment scores from financial news streams, reducing analyst time spent monitoring news by delivering pre-processed, ticker-tagged intelligence. Distinguished from RavenPack by human-readability focus: outputs are designed for analyst consumption as brief structured summaries, not for direct algorithmic pipeline integration.",
            "key_features": [
            "Human-readable structured summaries per ticker — designed for analyst workflows, not API pipeline integration (unlike RavenPack which targets quant systems)",
            "Automated financial news triage across a broad equity universe — converts continuous news monitoring from a full-time human task into a structured digest"
            ],
            "rationale": {
            "advantage": "Informational. Rapid structuring of financial news into ticker-level summaries and sentiment scores — speed and organization of information delivery is the edge.",
            "complexity": "Light-Grey Swan. Sentiment and event detection in noisy financial news streams — ML heuristics are required to identify relevant signals from continuous news flow.",
            "autonomy": "Low. Generates news summaries and sentiment for human analyst consumption; all investment decisions remain human.",
            "agent_type": "Commercial.",
            "stages": "Idea Generation (news-driven opportunity signals), Monitoring (ongoing news surveillance per holding)."
            },
            "advantage": "informational",
            "autonomy": "low",
            "agent_type": "commercial",
            "complexity": "light-grey",
            "stages": ["idea-gen", "monitoring"]
        },
        {
            "name": "Cognaize",
            "url": "https://cognaize.com",
            "description": "AI document intelligence platform for financial services that extracts, classifies, and structures data from complex unstructured financial documents — 10-Ks, credit agreements, earnings supplements, regulatory filings — into machine-readable formats. Designed for financial institutions that need to ingest large volumes of heterogeneous financial documents into their operational systems.",
            "key_features": [
            "Financial document-specific extraction: trained on financial document conventions (balance sheets, covenants, footnotes) with precision exceeding generic OCR or LLM extraction",
            "Operates as data infrastructure — extracts structured data that feeds downstream analytical systems, positioning it as foundational plumbing for other tools in this list"
            ],
            "rationale": {
            "advantage": "Informational. Unlocking structured data trapped in unstructured financial documents — the edge is speed and precision of information extraction, enabling downstream analytics.",
            "complexity": "White Swan. Financial document extraction operates on known document conventions and defined data fields — deterministic task with stable linguistic and structural patterns.",
            "autonomy": "Low. Structures document data for human analysts and downstream systems; no analytical decisions.",
            "agent_type": "Commercial.",
            "stages": "Idea Assessment (structuring company-level data for analysis), Compliance (extracting regulatory and legal data from filings)."
            },
            "advantage": "informational",
            "autonomy": "low",
            "agent_type": "commercial",
            "complexity": "white",
            "stages": ["idea-assess", "compliance"]
        },
        {
            "name": "Affinity AI",
            "url": "https://www.affinity.co",
            "description": "AI-powered relationship intelligence CRM for VC and PE firms that automatically captures and structures relationship data from emails, calendar activity, and meetings to track deal flow, warm introductions, and portfolio network signals. The core insight: most deal-relevant relationship data lives in unstructured inboxes and is never systematically captured without AI.",
            "key_features": [
            "Automatically captures relationship data from email and calendar without manual CRM entry — converts unstructured relationship activity into a searchable deal intelligence database",
            "Network-aware deal scoring: identifies which relationships in the fund's network have existing connections to target companies — the only tool in this list focused on relationship graph intelligence"
            ],
            "rationale": {
            "advantage": "Informational. Automatically structuring relationship and deal flow signals from communication activity — the edge is access to proprietary relationship intelligence that would otherwise be lost in inboxes.",
            "complexity": "White Swan. Relationship data capture from email and calendar is a deterministic extraction task — well-defined data sources with structured output targets.",
            "autonomy": "Low. Captures and organizes data; human deal professionals make all sourcing and investment decisions.",
            "agent_type": "Commercial.",
            "stages": "Idea Generation (relationship-driven deal sourcing signals), Stakeholder Management (tracking investor and LP relationship activity)."
            },
            "advantage": "informational",
            "autonomy": "low",
            "agent_type": "commercial",
            "complexity": "white",
            "stages": ["idea-gen", "stakeholder"]
        },
        {
            "name": "Arteria AI",
            "url": "https://www.arteriai.com",
            "description": "AI platform for contract intelligence and workflow automation in financial services, handling the generation, negotiation, and data extraction of complex financial contracts — ISDA, GMRA, credit agreements, and loan documentation. Distinct from generic legal AI: Arteria is specifically trained on financial contract conventions and integrates with industry-standard financial legal frameworks.",
            "key_features": [
            "Trained on financial contract conventions (ISDA, GMRA, LMA standards) — financial-law specificity distinguishes it from general legal AI tools like Harvey or ContractPodAi",
            "Covers contract generation through negotiation through data extraction in one platform — not just extraction (like COIN) but also drafting and redlining"
            ],
            "rationale": {
            "advantage": "Informational. Extracting and structuring obligations, terms, and risk data from complex financial contracts — the edge is organizing critical contractual information into structured, searchable form.",
            "complexity": "White Swan. Financial contracts have defined legal structures and standard frameworks (ISDA definitions, LMA standards) — deterministic extraction and drafting environment.",
            "autonomy": "Low. Generates contract drafts and extracts data for legal and compliance team review; no autonomous execution of contractual obligations.",
            "agent_type": "Commercial.",
            "stages": "Idea Assessment (extracting deal terms from contract data), Compliance (monitoring contractual obligations), Stakeholder Management (contract documentation for client agreements)."
            },
            "advantage": "informational",
            "autonomy": "low",
            "agent_type": "commercial",
            "complexity": "white",
            "stages": ["idea-assess", "compliance", "stakeholder"]
        },
        {
            "name": "Atlas AI",
            "url": "https://www.atlasai.co",
            "description": "Geospatial and supply chain intelligence platform that generates alternative data signals for investors from satellite imagery, shipping activity, foot traffic data, and global supply chain monitoring. The informational moat is the physical-world observability: data points that cannot be obtained from financial statements, news, or traditional data sources.",
            "key_features": [
            "Physical-world data signals (satellite, shipping, foot traffic) invisible to all financial statement or news-based analytical platforms — genuinely alternative in the strictest sense",
            "Supply chain intelligence: tracks real-time physical goods flows that can lead fundamental data by weeks or months — a predictive edge in commodity, retail, and manufacturing sectors"
            ],
            "rationale": {
            "advantage": "Informational. Unique geospatial and supply chain signals unavailable through any financial data source — exclusive access to physical-world observations is the informational moat.",
            "complexity": "Light-Grey Swan. Extracting valid predictive investment signals from geospatial and logistics noise requires ML heuristics — valid signals must be searched from a high-dimensional, noisy alternative data space.",
            "autonomy": "Low. Generates signals for human portfolio managers and analysts to incorporate into investment decisions.",
            "agent_type": "Commercial.",
            "stages": "Idea Generation (alternative signal-driven opportunity identification), Idea Assessment (validating investment theses with physical-world data)."
            },
            "advantage": "informational",
            "autonomy": "low",
            "agent_type": "commercial",
            "complexity": "light-grey",
            "stages": ["idea-gen", "idea-assess"]
        },
        {
            "name": "V7 Go (Due Diligence Agent)",
            "url": "https://www.v7labs.com/go",
            "description": "A general-purpose agentic AI product by V7 Labs that is particularly deployed for document-heavy investment due diligence workflows — autonomously reading through large document sets, extracting structured data, and generating comparative analyses with minimal human prompting. Unlike Hebbia (private markets specialist), V7 Go is domain-agnostic, making it deployable across public and private market DD contexts.",
            "key_features": [
            "Domain-agnostic agentic document analysis: deployable across public or private market due diligence without pre-configured financial document templates",
            "Minimal prompting agentic workflow: the agent plans its own reading, extraction, and synthesis steps — higher autonomy than copilot-style tools (Finpilot, Rogo) for document-intensive tasks"
            ],
            "rationale": {
            "advantage": "Analytical. Agentic document analysis and synthesis across heterogeneous document sets — the edge is the autonomous orchestration of multi-document reasoning without per-step instruction.",
            "complexity": "White Swan. Document extraction and synthesis in defined deal environments — deterministic task over known document types, even if the documents are complex.",
            "autonomy": "Medium. The agent autonomously plans and executes multi-step document analysis with minimal prompting, but a human reviews all outputs before any investment decision.",
            "agent_type": "Commercial.",
            "stages": "Idea Assessment (due diligence document analysis), Compliance (regulatory and legal document review)."
            },
            "advantage": "analytical",
            "autonomy": "medium",
            "agent_type": "commercial",
            "complexity": "white",
            "stages": ["idea-assess", "compliance"]
        },
        {
            "name": "Finpilot",
            "url": "https://www.finpilot.co",
            "description": "AI copilot for financial analysts that enables natural language extraction of data from filings, earnings transcripts, and financial databases, and generates structured comparative analyses across companies or time periods. Operates as an accelerator for the manual parts of analyst workflow — data retrieval and table construction — rather than replacing the analyst's judgment.",
            "key_features": [
            "Extracts structured data tables from filings and transcripts via natural language — reduces hours of manual data extraction to seconds for comparable company and historical analysis",
            "Explicitly designed as an accelerator, not a replacement — handles the mechanical research tasks (data pulling, table building) while leaving interpretation and judgment to the analyst"
            ],
            "rationale": {
            "advantage": "Analytical. Synthesizes and compares financial data from multiple document sources into structured outputs — the edge is quality and speed of analytical data preparation.",
            "complexity": "White Swan. Research over structured financial documents (10-Ks, earnings transcripts, financial databases) — deterministic extraction and comparison tasks with known document conventions.",
            "autonomy": "Low. Copilot requiring analyst prompts for each task; all interpretation and decisions remain with the human analyst.",
            "agent_type": "Commercial.",
            "stages": "Idea Assessment (comparative company and financial analysis)."
            },
            "advantage": "analytical",
            "autonomy": "low",
            "agent_type": "commercial",
            "complexity": "white",
            "stages": ["idea-assess"]
        },
        {
            "name": "Acuity (Acuity Trading)",
            "url": "https://acuitytrading.com",
            "description": "Financial news analytics platform delivering structured market sentiment scores, event signals, and news trend data via API to trading desks and investment systems, covering forex, equities, and commodities. Positioned as sentiment infrastructure: a data feed, not an interface — designed for integration into trading systems and quantitative workflows rather than analyst-facing use.",
            "key_features": [
            "API-delivered structured sentiment signals for FX, equities, and commodities — pure data-feed infrastructure for quant and systematic trading integration",
            "Covers sentiment trend analysis alongside event detection — distinguishes between one-off signals (events) and persistent sentiment shifts (trends) in the same feed"
            ],
            "rationale": {
            "advantage": "Informational. Rapid structuring of financial news into quantified market sentiment signals — the edge is speed and precision of sentiment quantification from continuous news flow.",
            "complexity": "Light-Grey Swan. Sentiment extraction from noisy, real-time financial news streams requires ML heuristics to separate signal from noise.",
            "autonomy": "Low. Generates structured signals for human traders and quant systems; no autonomous trading decisions.",
            "agent_type": "Commercial.",
            "stages": "Idea Generation (sentiment-driven trading signals), Monitoring (continuous sentiment tracking for positions)."
            },
            "advantage": "informational",
            "autonomy": "low",
            "agent_type": "commercial",
            "complexity": "light-grey",
            "stages": ["idea-gen", "monitoring"]
        },
        {
            "name": "YourStake",
            "url": "https://yourstake.org",
            "description": "AI platform for wealth managers that personalizes client portfolios based on individual ESG preferences, values, and exclusion screens — scoring portfolios against client-specific values profiles and enabling advisors to show clients exactly how their portfolio aligns with what matters to them. Focused on advisor-client engagement, not investment alpha generation.",
            "key_features": [
            "Client-level values personalization: each client gets a unique scoring of their portfolio against their specific preferences — not a fund-level ESG score but account-level alignment analysis",
            "Advisor engagement tool: generates visual client-facing reports showing values alignment — bridges ESG data into advisor-client conversations rather than quant pipelines"
            ],
            "rationale": {
            "advantage": "Informational. Structured ESG/values data enabling portfolio personalization against client-specific criteria — the edge is organization and presentation of values-relevant information, not market alpha generation.",
            "complexity": "White Swan. Values alignment assessment against defined ESG and exclusion frameworks — deterministic scoring against structured criteria without market uncertainty.",
            "autonomy": "Low. Generates portfolio alignment analysis for advisors to discuss with clients; advisors implement any changes.",
            "agent_type": "Commercial.",
            "stages": "Idea Assessment (evaluating portfolio alignment with values criteria), Stakeholder Management (client-facing values reporting)."
            },
            "advantage": "informational",
            "autonomy": "low",
            "agent_type": "commercial",
            "complexity": "white",
            "stages": ["idea-assess", "stakeholder"]
        },
        {
            "name": "Portrait Analytics",
            "url": "https://portraitanalytics.com",
            "description": "AI-powered investor relations intelligence platform that analyzes shareholder behavior, ownership changes, and institutional investor sentiment to help IR teams understand who holds their stock, why they hold it, and how to target new aligned investors. The only tool in this list exclusively dedicated to the sell-side of the investor relations function.",
            "key_features": [
            "Analyzes institutional investor behavior patterns to identify why shareholders buy and sell — goes beyond ownership data to model investor decision rationale",
            "Targeted outreach intelligence: identifies prospective investors with the highest alignment probability — converts a manual IR targeting process into a data-driven function"
            ],
            "rationale": {
            "advantage": "Informational. Structured intelligence about shareholder behavior and institutional investor sentiment — the edge is organized analysis of ownership and behavior data that IR teams cannot process manually.",
            "complexity": "White Swan. Shareholder registry, 13F filings, and trading behavior data are structured, regulated, and deterministic — well-defined data environment.",
            "autonomy": "Low. Provides intelligence for human IR professionals to act upon; no autonomous shareholder communication.",
            "agent_type": "Commercial.",
            "stages": "Stakeholder Management (this tool lives exclusively in Stakeholder Management — investor relations is its sole application)."
            },
            "advantage": "informational",
            "autonomy": "low",
            "agent_type": "commercial",
            "complexity": "white",
            "stages": ["stakeholder"]
        },
        {
            "name": "Holistic AI",
            "url": "https://www.holisticai.com",
            "description": "AI governance and risk management platform that audits, monitors, and documents AI models for bias, reliability, fairness, and EU AI Act/MiFID II regulatory compliance — governing other AI deployments rather than generating investment signals itself. As investment firms deploy more AI agents, Holistic AI provides the mandatory governance layer regulators require.",
            "key_features": [
            "Meta-AI function: governs other AI systems rather than generating investment signals — the only tool in this list whose subject is AI models, not markets or documents",
            "Directly addresses EU AI Act and MiFID II model risk management requirements — the governance infrastructure investment firms need to deploy any high-risk AI in production"
            ],
            "rationale": {
            "advantage": "Analytical. Systematic assessment of AI model risks, biases, and reliability using established auditing methodologies — the edge is rigorous analytical evaluation of model behavior.",
            "complexity": "Light-Grey Swan. AI model behavior is uncertain and context-dependent — identifying bias and failure modes requires ML audit techniques applied to probabilistic systems.",
            "autonomy": "Low. Generates audit reports and monitoring alerts for human governance and compliance teams.",
            "agent_type": "Commercial.",
            "stages": "Compliance (AI regulatory governance), Monitoring (ongoing model behavior surveillance)."
            },
            "advantage": "analytical",
            "autonomy": "low",
            "agent_type": "commercial",
            "complexity": "light-grey",
            "stages": ["compliance", "monitoring"]
        },
        {
            "name": "Investbanq Co-Pilot",
            "url": "https://investbanq.com",
            "description": "AI copilot designed specifically for investment banking workflows — supporting pitch deck preparation, comparable company analysis, financial modeling assistance, and client presentation creation using AI that understands investment banking conventions. Targets the analyst/associate layer of IBD where the bulk of presentation and analysis preparation time is spent.",
            "key_features": [
            "Investment banking-specific outputs: comps tables, precedent transactions, pitch deck slides — not generic document generation but IB-workflow-calibrated deliverables",
            "Designed for IBD analyst/associate workflows where preparation time is highest — the productivity impact is concentrated at the most time-intensive part of the IB value chain"
            ],
            "rationale": {
            "advantage": "Analytical. Synthesizes financial data into investment banking-specific deliverables (comps, pitch decks, deal analyses) — the edge is IB-workflow-specific synthesis quality.",
            "complexity": "White Swan. Investment banking workflows operate on structured financial data and established methodology frameworks (comparable analysis, DCF, precedent transactions) — deterministic analytical environment.",
            "autonomy": "Low. Copilot for human investment bankers; all deal judgments and client interactions remain human.",
            "agent_type": "Commercial.",
            "stages": "Idea Assessment (deal and company analysis), Decision (deal structuring support), Stakeholder Management (pitch and presentation preparation)."
            },
            "advantage": "analytical",
            "autonomy": "low",
            "agent_type": "commercial",
            "complexity": "white",
            "stages": ["idea-assess", "decision", "stakeholder"]
        },
        {
            "name": "Linedata",
            "url": "https://linedata.com",
            "description": "Investment management software suite (Longview, Beauchamp) that has integrated AI across its front-office platform for portfolio management, order management, and workflow automation — functioning as an AI-enhanced operational infrastructure layer for asset managers. Unlike point AI tools, Linedata covers the entire investment operations lifecycle within one connected platform.",
            "key_features": [
            "End-to-end investment management platform with integrated AI — covers portfolio management, order management, and compliance in one connected system rather than separate point solutions",
            "AI enhancements are embedded in operational workflows (order routing, compliance pre-trade checking) rather than offered as a standalone analytical tool"
            ],
            "rationale": {
            "advantage": "Analytical. AI-enhanced investment workflow analytics across portfolio management and trading operations — the edge is operational intelligence embedded in the investment management process.",
            "complexity": "White Swan. Investment management operations (portfolio management, order management, compliance checking) operate on structured, well-defined portfolio and order data.",
            "autonomy": "Low. AI-enhanced operational software requiring human portfolio managers and traders for all decisions — the AI improves workflow efficiency, not decision autonomy.",
            "agent_type": "Commercial.",
            "stages": "Idea Assessment (portfolio analytics), Decision (order management support), Execution (order routing analytics), Monitoring (position and risk monitoring), Compliance (pre-trade and post-trade compliance checking). NOTE: broadest stage coverage of any tool in this batch — reflects its nature as an end-to-end operations platform."
            },
            "advantage": "analytical",
            "autonomy": "low",
            "agent_type": "commercial",
            "complexity": "white",
            "stages": ["idea-assess", "decision", "execution", "monitoring", "compliance"]
        },
        {
            "name": "Altruist AI Agents",
            "url": "https://altruist.com",
            "description": "AI agents integrated into Altruist's RIA custodial platform that automate advisor operational workflows — account onboarding, compliance tasks, and client reporting — within a modern low-cost custodial infrastructure targeted at independent RIAs. Distinct from Morgan Stanley or Goldman in-house tools: Altruist serves independent advisors who lack institutional AI infrastructure.",
            "key_features": [
            "Serves independent RIAs (not wirehouse advisors) — delivers AI workflow automation to the long-tail of smaller advisors who lack institutional-grade operational infrastructure",
            "Embedded in custodial infrastructure: AI automates workflows that are native to the custodial platform (onboarding, account maintenance, reporting) rather than external tool integrations"
            ],
            "rationale": {
            "advantage": "Informational. Organizing and surfacing client and portfolio data for independent RIA advisors who lack dedicated operational staff — the edge is efficient data organization and task automation for lean advisory practices.",
            "complexity": "White Swan. RIA custodial operations (account onboarding, rebalancing, reporting) operate on structured, deterministic client and account data within defined regulatory frameworks.",
            "autonomy": "Medium. Agents automate specific operational steps (onboarding flows, compliance tasks, report generation) within defined parameters; advisors oversee client-facing outputs.",
            "agent_type": "Commercial.",
            "stages": "Stakeholder Management (client reporting), Monitoring (portfolio drift and compliance monitoring), Compliance (regulatory workflow automation)."
            },
            "advantage": "informational",
            "autonomy": "medium",
            "agent_type": "commercial",
            "complexity": "white",
            "stages": ["stakeholder", "monitoring", "compliance"]
        },
        {
            "name": "FinRobot",
            "url": "https://github.com/AI4Finance-Foundation/FinRobot",
            "description": "Open-source multi-agent AI framework from the AI4Finance Foundation providing modular, pre-built LLM agents for financial analysis, report generation, and trading strategy development — designed for academic and practitioner experimentation. From the same foundation as FinGPT and FinMem but with a different focus: orchestration and composability of multiple financial AI agents rather than a single model approach.",
            "key_features": [
            "Modular multi-agent architecture: researchers can compose specialized agents (data, analysis, strategy, report) rather than relying on a single monolithic model",
            "Open-source and production-composable: bridges academic research and practitioner deployment — the most practically oriented framework from the AI4Finance Foundation"
            ],
            "rationale": {
            "advantage": "Analytical. Modular multi-agent framework for financial analysis and strategy development — the edge is compositional flexibility enabling complex financial reasoning workflows.",
            "complexity": "Light-Grey Swan. Strategy development and financial analysis in non-stationary markets — ML heuristics required for signal discovery.",
            "autonomy": "High. Agents autonomously execute analysis and strategy pipelines in research and backtesting environments.",
            "agent_type": "Academic / open-source.",
            "stages": "Idea Generation (signal research), Idea Assessment (company and strategy analysis), Decision (strategy selection in backtesting)."
            },
            "advantage": "analytical",
            "autonomy": "high",
            "agent_type": "academic",
            "complexity": "light-grey",
            "stages": ["idea-gen", "idea-assess", "decision"]
        },
        {
            "name": "Xceptor",
            "url": "https://xceptor.com",
            "description": "AI-driven financial data transformation and automation platform that cleanses, reconciles, enriches, and routes financial data across institutional systems for operations, regulatory reporting, and compliance — not an analytical tool but the data plumbing enabling all other tools in this list. Widely used by global banks and asset managers for data quality at scale.",
            "key_features": [
            "Financial data transformation at institutional scale: handles the messy, exception-heavy reconciliation work between trading systems, custodians, and regulatory reporting",
            "Exception-handling workflow: flags data anomalies for human review rather than silently correcting — the human-in-the-loop design is appropriate for regulatory and audit contexts"
            ],
            "rationale": {
            "advantage": "Informational. Transforming, validating, and routing financial data across institutional systems — the edge is data quality and operational reliability, enabling downstream analytical tools.",
            "complexity": "White Swan. Financial data transformation operates on structured financial data (trades, positions, cash flows) with defined regulatory and system requirements — deterministic data engineering tasks.",
            "autonomy": "Medium. Automates data processing pipelines autonomously with exception-based escalation to human operators for anomalies.",
            "agent_type": "Commercial.",
            "stages": "Monitoring (position and data reconciliation), Compliance (regulatory data quality and reporting)."
            },
            "advantage": "informational",
            "autonomy": "medium",
            "agent_type": "commercial",
            "complexity": "white",
            "stages": ["monitoring", "compliance"]
        },
        {
            "name": "Terminal X",
            "url": "https://terminalx.com",
            "description": "AI-powered financial intelligence terminal combining multi-source data aggregation, LLM-driven research assistance, and portfolio analytics in a unified platform — positioned as an AI-native alternative to traditional financial data terminals for independent and institutional investors. Differentiates from Bloomberg/FactSet by leading with AI-native conversational interfaces rather than retrofitting AI onto legacy terminal architecture.",
            "key_features": [
            "AI-native terminal architecture: conversational interface is the primary UI, not a chatbot add-on to a legacy data terminal — fundamentally different UX paradigm from Bloomberg or FactSet",
            "Targets independent investors and smaller institutional teams who cannot justify Bloomberg terminal costs — accessibility at a fraction of terminal cost with AI-native design"
            ],
            "rationale": {
            "advantage": "Informational. Unified access to multi-source financial data and AI-driven research in a terminal interface — the edge is information access breadth and interface accessibility.",
            "complexity": "White Swan. Financial data retrieval and research assistance over structured financial databases — deterministic information access tasks.",
            "autonomy": "Low. Terminal assistant for human analysts; all investment decisions remain with the user.",
            "agent_type": "Commercial.",
            "stages": "Idea Generation (market and company screening), Idea Assessment (research and analytical queries)."
            },
            "advantage": "informational",
            "autonomy": "low",
            "agent_type": "commercial",
            "complexity": "white",
            "stages": ["idea-gen", "idea-assess"]
        },
        {
            "name": "StockBench",
            "url": "https://stockbench.net",
            "description": "Web-based systematic strategy backtesting and simulation platform that enables investors to test rule-based and indicator-driven trading strategies against historical market data with a visual interface requiring no coding. Targeted at systematic retail and semi-professional investors who lack the quant infrastructure to use platforms like SigTech.",
            "key_features": [
            "No-code backtesting with visual interface — makes systematic strategy testing accessible to non-quant investors without Python or quant programming skills",
            "Positioned between retail backtesting tools and institutional platforms (SigTech) — fills the gap for serious systematic investors who are not full quant funds"
            ],
            "rationale": {
            "advantage": "Analytical. Systematic strategy testing and validation — the edge is accessibility to rigorous quantitative backtesting methodology without requiring quant infrastructure.",
            "complexity": "Light-Grey Swan. Backtesting searches for strategies that will generalize to future non-stationary market conditions — signal robustness in uncertain environments is the core challenge.",
            "autonomy": "Low. Provides backtesting results for human strategy developers; no autonomous deployment or trading.",
            "agent_type": "Commercial.",
            "stages": "Idea Assessment (strategy validation through backtesting), Decision (strategy selection based on backtesting results)."
            },
            "advantage": "analytical",
            "autonomy": "low",
            "agent_type": "commercial",
            "complexity": "light-grey",
            "stages": ["idea-assess", "decision"]
        },
        {
            "name": "Bridget / ThemeWise",
            "url": "https://bridget.ai",
            "description": "AI-powered platform for identifying and tracking thematic investment trends, mapping company universes to investment themes (energy transition, AI infrastructure, aging demographics) using NLP on news, filings, and alternative data. Addresses the growing demand for thematic investment products by automating what is typically a manual narrative-to-portfolio construction process.",
            "key_features": [
            "Thematic universe construction: automatically maps companies to investment themes using NLP — converting narrative investment ideas into structured, backtestable equity universes",
            "Trend tracking: monitors how investment themes evolve over time as corporate positioning and market narratives shift — not a static basket but a dynamic thematic intelligence layer"
            ],
            "rationale": {
            "advantage": "Analytical. Identifying and mapping emerging investment themes from multi-source data — the edge is synthesis of narrative signals into structured, investable thematic universes.",
            "complexity": "Light-Grey Swan. Thematic investment identification requires ML search across heterogeneous data to find companies best-positioned for non-stationary macro and industry trends.",
            "autonomy": "Low. Surfaces thematic investment frameworks for human portfolio managers to evaluate and implement.",
            "agent_type": "Commercial.",
            "stages": "Idea Generation (thematic investment opportunity identification), Idea Assessment (mapping companies to themes and validating exposures)."
            },
            "advantage": "analytical",
            "autonomy": "low",
            "agent_type": "commercial",
            "complexity": "light-grey",
            "stages": ["idea-gen", "idea-assess"]
        },
        {
            "name": "Needl",
            "url": "https://needl.ai",
            "description": "AI-powered financial information search and intelligence platform that consolidates and searches across financial documents, alternative data, and news in a single interface with relevance-ranked results. Positioned as a research aggregator for investment professionals who currently waste significant time switching between multiple data platforms.",
            "key_features": [
            "Unified search across heterogeneous financial data sources in one interface — reduces the multi-platform research workflow to a single query environment",
            "Relevance ranking optimized for investment professionals — not generic web search but investment-context-aware prioritization of results"
            ],
            "rationale": {
            "advantage": "Informational. Unified, faster access to financial information across multiple sources — the edge is information retrieval efficiency across a consolidated source universe.",
            "complexity": "White Swan. Document and data retrieval over structured financial information sources — deterministic search and ranking task.",
            "autonomy": "Low. Research discovery tool for human analysts; humans interpret all results.",
            "agent_type": "Commercial.",
            "stages": "Idea Assessment (consolidated research search), Monitoring (tracking new information across coverage universe)."
            },
            "advantage": "informational",
            "autonomy": "low",
            "agent_type": "commercial",
            "complexity": "white",
            "stages": ["idea-assess", "monitoring"]
        },
        {
            "name": "BlackRock Aladdin",
            "url": "https://www.blackrock.com/aladdin/solutions/aladdin-copilot",
            "description": "BlackRock's Aladdin platform with integrated AI Copilot, enabling portfolio managers to query exposures, run scenario analyses, and generate risk summaries in natural language over Aladdin's structured system of record for public market assets (equities, fixed income, derivatives, multi-asset). The benchmark low-autonomy AI copilot for institutional public market risk and portfolio analytics — all outputs require human sign-off with no trading authority.",
            "key_features": [
            "Natural language interface over Aladdin's scoped portfolio and risk data — no open-web access or hallucination of data outside the system of record",
            "Formal human sign-off requirement on all outputs: no allocation or trading authority, making it the industry reference for a low-autonomy, high-control investment AI"
            ],
            "rationale": {
            "advantage": "Analytical. Synthesizes Aladdin's structured portfolio and risk data to answer complex queries across multi-asset exposures and scenario analyses — the edge is reasoning quality over a rich institutional data environment.",
            "complexity": "White Swan. Operates over structured, deterministic portfolio and risk data within Aladdin's system of record — not searching for signals in noisy market data.",
            "autonomy": "Low. No trading or allocation authority; all outputs are decision-support requiring human review and formal sign-off.",
            "agent_type": "Commercial. BlackRock sells Aladdin platform access to asset managers globally.",
            "stages": "Idea Assessment (portfolio exposure analysis), Monitoring (risk and performance monitoring), Stakeholder Management (portfolio reporting and scenario communication)."
            },
            "advantage": "analytical",
            "autonomy": "low",
            "agent_type": "commercial",
            "complexity": "white",
            "stages": ["idea-assess", "monitoring", "stakeholder"]
        },
        {
            "name": "BlackRock eFront",
            "url": "https://www.blackrock.com/aladdin/solutions/efront",
            "description": "BlackRock's eFront platform with integrated AI Copilot, purpose-built for private market investment management (PE, real estate, infrastructure, private debt) — enabling natural language queries over fund data, portfolio monitoring, cash flow analytics, and reporting for alternative asset managers. Distinct from Aladdin in covering illiquid private asset data structures (capital calls, distributions, NAV schedules) rather than public market risk.",
            "key_features": [
            "Private market-specific data model (PE, RE, infra, private debt) covering capital call schedules, distribution waterfalls, and NAV calculations — data structures absent from public market platforms",
            "AI Copilot for private market due diligence workflows: queries across fund documents, LP reports, and portfolio company data within eFront's governed environment"
            ],
            "rationale": {
            "advantage": "Analytical. Synthesizes heterogeneous private market data (fund documents, NAV schedules, cash flows) into structured analytics — the edge is reasoning quality over complex illiquid asset data.",
            "complexity": "White Swan. Private market portfolio analytics operate over structured, deterministic fund accounting and LP data — well-defined data environment even if asset values are uncertain.",
            "autonomy": "Low. Generates private market analytics and reports for human investment teams; no autonomous allocation or commitment authority.",
            "agent_type": "Commercial. Part of BlackRock's Aladdin ecosystem, sold to PE managers, real asset managers, and institutional allocators.",
            "stages": "Idea Assessment (private market due diligence and opportunity evaluation), Monitoring (portfolio company and fund performance tracking), Compliance (LP reporting and regulatory disclosure)."
            },
            "advantage": "analytical",
            "autonomy": "low",
            "agent_type": "commercial",
            "complexity": "white",
            "stages": ["idea-assess", "monitoring", "compliance"]
        },
        {
            "name": "FinGPT",
            "url": "https://github.com/AI4Finance-Foundation/FinGPT",
            "description": "Open-source financial LLM framework from the AI4Finance Foundation that fine-tunes large language models on financial news, filings, and social media using RLHF — enabling financial sentiment analysis, market report generation, and financial question-answering at a fraction of the cost of closed models like BloombergGPT. Designed to democratize access to finance-domain LLMs for researchers and practitioners without proprietary data infrastructure.",
            "key_features": [
            "Low-cost RLHF fine-tuning on financial data: researchers can adapt LLMs to finance tasks with minimal compute — the most accessible route to a domain-specific financial LLM",
            "Open-source and modifiable: bridges academic finance research and practitioner deployment without commercial API dependencies or proprietary training data requirements"
            ],
            "rationale": {
            "advantage": "Analytical. LLM fine-tuned on financial text to improve comprehension of financial sentiment, market narratives, and domain-specific language — the edge is analytical quality of financial language understanding.",
            "complexity": "Light-Grey Swan. Financial sentiment and market signal extraction from noisy, heterogeneous text sources requires ML heuristics — signal probability distributions are theoretically known but require search.",
            "autonomy": "Low. Generates financial text analysis and signals for human researchers and practitioners; not a standalone autonomous trading system.",
            "agent_type": "Academic / open-source. From the AI4Finance Foundation; freely available on GitHub.",
            "stages": "Idea Generation (sentiment-driven signal generation), Idea Assessment (financial text analysis and comprehension)."
            },
            "advantage": "analytical",
            "autonomy": "low",
            "agent_type": "academic",
            "complexity": "light-grey",
            "stages": ["idea-gen", "idea-assess"]
        },
        {
            "name": "FinMem",
            "url": "https://github.com/AI4Finance-Foundation/FinMem-LLM-StockTrading",
            "description": "Academic LLM trading agent from the AI4Finance Foundation that incorporates a layered memory architecture (working memory, short-term memory, long-term memory) to enable the agent to accumulate, prioritize, and retrieve financial experience across trading sessions — significantly outperforming memory-less LLM trading agents in backtesting on US equities.",
            "key_features": [
            "Layered memory architecture (working / short-term / long-term): the agent learns from prior trading outcomes and accumulates financial 'experience' — distinguishing it from stateless LLM trading agents",
            "Memory priority scoring: recent and high-impact financial events are weighted more heavily in agent decisions — mimicking how experienced traders internalize market lessons"
            ],
            "rationale": {
            "advantage": "Analytical. Layered memory enables progressive improvement in trading signal extraction — the edge is accumulated analytical experience improving decision quality over time.",
            "complexity": "Light-Grey Swan. Stock trading signal generation in non-stationary equity markets — known uncertainty structures requiring ML heuristics and adaptive learning.",
            "autonomy": "High. Autonomously generates signals and executes trading decisions in backtesting environments from raw market data.",
            "agent_type": "Academic. Research prototype validated in backtesting; not deployed with live capital.",
            "stages": "Idea Assessment (market signal analysis with accumulated memory context), Decision (trading decision generation), Execution (autonomous trade execution in backtesting)."
            },
            "advantage": "analytical",
            "autonomy": "high",
            "agent_type": "academic",
            "complexity": "light-grey",
            "stages": ["idea-assess", "decision", "execution"]
        },
        {
            "name": "TradingAgents",
            "url": "https://arxiv.org/abs/2412.20138",
            "description": "Multi-agent LLM trading framework where specialized role-based agents (bull analyst, bear analyst, researcher, risk manager) engage in structured debate coordinated by a trading manager agent to reach consensus trading decisions — validated against historical data with improved risk-adjusted returns over single-agent and baseline models.",
            "key_features": [
            "Bull/bear debate mechanism forces explicit articulation of opposing investment theses — reduces single-agent groupthink and surfaces asymmetric risk in trading decisions",
            "Integrated risk management agent participates in the debate loop: risk constraints are embedded in the decision process, not applied as an afterthought"
            ],
            "rationale": {
            "advantage": "Analytical. Structured multi-role debate architecture for generating consensus trading decisions — the edge is wider analytical perspective coverage through agent specialization and adversarial deliberation.",
            "complexity": "Light-Grey Swan. Trading signal generation in non-stationary markets — non-stationary uncertainty structures requiring ML-based heuristic search across market data.",
            "autonomy": "High. Autonomous from signal generation through trade execution in backtesting environments; no human involvement in each deliberation cycle.",
            "agent_type": "Academic. Research prototype validated in backtesting; not deployed with live capital.",
            "stages": "Idea Assessment (multi-agent analytical deliberation), Decision (consensus investment decision via debate), Execution (autonomous trade execution in backtesting)."
            },
            "advantage": "analytical",
            "autonomy": "high",
            "agent_type": "academic",
            "complexity": "light-grey",
            "stages": ["idea-assess", "decision", "execution"]
        },
        {
            "name": "FinRL-Trading",
            "url": "https://github.com/AI4Finance-Foundation/FinRL",
            "description": "The first open-source deep reinforcement learning framework for quantitative finance from the AI4Finance Foundation, training RL agents (DQN, PPO, SAC, A2C) to trade autonomously across equities, crypto, and futures — providing researchers and practitioners with a standardized benchmark environment for autonomous trading strategy development.",
            "key_features": [
            "First open-source DRL framework for finance: standardized benchmark enabling reproducible autonomous trading research without proprietary infrastructure",
            "Supports multiple asset classes (equities, crypto, futures) and multiple RL algorithms — the broadest DRL experimentation surface of any open-source trading framework in this list"
            ],
            "rationale": {
            "advantage": "Analytical. Deep RL learns optimal trading policies from historical market data — the edge is superior computational discovery of trading patterns via reward-maximizing reinforcement learning.",
            "complexity": "Light-Grey Swan. Autonomous trading policy discovery in non-stationary financial markets — optimal policies must be searched across uncertain, time-varying environments using DRL heuristics.",
            "autonomy": "High. RL agents autonomously generate and execute trading signals end-to-end in backtesting environments with no human in each decision loop.",
            "agent_type": "Academic / open-source. From the AI4Finance Foundation; widely used for DRL trading research.",
            "stages": "Idea Generation (signal discovery through RL exploration), Idea Assessment (strategy backtesting and policy evaluation), Decision (policy-driven trading decisions), Execution (autonomous trade execution in backtesting)."
            },
            "advantage": "analytical",
            "autonomy": "high",
            "agent_type": "academic",
            "complexity": "light-grey",
            "stages": ["idea-gen", "idea-assess", "decision", "execution"]
        }

    ]

    timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

    for agent in agents_data_new:
        cursor.execute("SELECT id FROM agents WHERE name = ?", (agent["name"],))
        if cursor.fetchone():
            continue
        cat_id = AGENT_CATEGORY_SEED.get(agent["name"])
        cursor.execute('''
            INSERT INTO agents (
                name, url, description, rationale, key_features,
                advantage, autonomy, agent_type, complexity, stages, category_id, status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            agent["name"],
            agent["url"],
            agent["description"],
            json.dumps(agent["rationale"]),
            json.dumps(agent["key_features"]),
            agent["advantage"],
            agent["autonomy"],
            agent["agent_type"],
            agent["complexity"],
            json.dumps(agent["stages"]),
            cat_id,
            "classified",
            timestamp,
        ))

    conn.commit()
    conn.close()
    print(f"Success: 'agents.db' created at {db_path} with {len(agents_data)} agents.")


if __name__ == '__main__':
    generate_database()
