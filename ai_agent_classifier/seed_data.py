import json


def seed_database(app, db, Agent):
    return  # seeding disabled — use build_agents_db.py to populate
    with app.app_context():
        if Agent.query.count() > 0:
            return

        agents = [
            {
                "name": "BlackRock Aladdin Copilot",
                "url": "https://www.blackrock.com/aladdin/solutions/aladdin-copilot",
                "status": "classified",
                "advantage": "analytical",
                "complexity": "light-grey",
                "stages": json.dumps(["idea-assess", "monitoring"]),
                "autonomy": "medium",
                "agent_type": "commercial",
                "description": (
                    "LangGraph-orchestrated generative-AI copilot embedded across 100+ Aladdin "
                    "apps. Surfaces portfolio/risk context instantly. Strict guardrails and daily CI/CD "
                    "evaluation pipeline."
                ),
                "rationale": (
                    "Classified Light Grey because portfolio risk synthesis involves complex, "
                    "high-dimensional factor interactions not fully captured by a single known probability "
                    "distribution. Analytical advantage: superior synthesis of portfolio exposures, not "
                    "mere data retrieval. Won't advise outside Aladdin data boundaries."
                ),
                "key_features": json.dumps([
                    "NL queries over full Aladdin portfolio context",
                    "LangGraph multi-agent orchestration with guardrails",
                    "Daily CI/CD evaluation pipeline",
                    "100+ front-end app integrations",
                    "Won't advise outside Aladdin data boundaries",
                ]),
            },
            {
                "name": "RavenPack News Analytics",
                "url": "https://www.ravenpack.com",
                "status": "classified",
                "advantage": "informational",
                "complexity": "light-grey",
                "stages": json.dumps(["idea-gen"]),
                "autonomy": "low",
                "agent_type": "commercial",
                "description": (
                    "Converts 40,000+ news sources into structured sentiment and event scores "
                    "for 13M+ named entities in real-time. Core perception-layer agent for quant signal "
                    "generation."
                ),
                "rationale": (
                    "Light Grey: data is abundant but finding stable price-relevant signals in "
                    "noisy multilingual news streams requires heuristic filtering and ML. The probability "
                    "distribution of sentiment impact is theoretically estimable but highly noisy in "
                    "practice. Informational advantage: the edge is in data access speed and coverage "
                    "breadth, not analytical synthesis."
                ),
                "key_features": json.dumps([
                    "40,000+ news sources across 13 languages",
                    "13M+ named entity coverage",
                    "Real-time delivery + historical archive",
                    "API / data-feed integration",
                    "Timestamped auditability for model governance",
                ]),
            },
            {
                "name": "Essentia Analytics",
                "url": "https://www.essentia-analytics.com",
                "status": "classified",
                "advantage": "behavioral",
                "complexity": "dark-grey",
                "stages": json.dumps(["decision", "monitoring"]),
                "autonomy": "low",
                "agent_type": "commercial",
                "description": (
                    "Behavioral analytics platform detecting cognitive biases in portfolio "
                    "managers' own trade histories. Delivers ex-ante nudges when detrimental patterns "
                    "emerge. $430B+ AUM covered. Northern Trust strategic investor."
                ),
                "rationale": (
                    "Dark Grey Swan: the causal chain from an observed behavioral pattern to "
                    "future performance impact is a causal identification problem, not an optimization "
                    "problem. Per Dawes and Corrigan (1974, cited in the Panthera paper): identifying "
                    "correct causal directions matters more than optimizing weights. Behavioral advantage: "
                    "targets the most durable edge — overcoming one's own cognitive biases. Nudge-engaged "
                    "managers outperform by +160 bps/year on average (Essentia internal data)."
                ),
                "key_features": json.dumps([
                    "AI detection of 20+ behavioral bias types in trade history",
                    "Ex-ante nudges before critical decision points",
                    "Former fund manager coaching (Insight Partners)",
                    "Behavioral Alpha Benchmark peer comparison",
                    "Research published in Journal of Investing (2022)",
                ]),
            },
            {
                "name": "JPMorgan LOXM",
                "url": "https://www.jpmorgan.com",
                "status": "classified",
                "advantage": "analytical",
                "complexity": "white",
                "stages": json.dumps(["execution"]),
                "autonomy": "high",
                "agent_type": "in-house",
                "description": (
                    "Deep reinforcement-learning equity execution engine trained on billions "
                    "of historical trades. Optimizes order placement to minimize market impact and "
                    "transaction costs. First disclosed 2017."
                ),
                "rationale": (
                    "White Swan: the objective function (minimize execution cost) is "
                    "well-defined and stable. Microstructure data is abundant and representative. "
                    "The probability distribution of price impact is well-characterized by established "
                    "market microstructure models. RL optimizes over a known distribution — pure "
                    "optimization, not causal inference. Analytical advantage: superior use of "
                    "computing power over the same data available to all participants."
                ),
                "key_features": json.dumps([
                    "Deep RL trained on billions of historical trades",
                    "Minimizes market impact and transaction costs",
                    "~15% reported improvement in execution efficiency",
                    "Autonomous execution within pre-set parameters",
                    "Presented at QuantMinds Lisbon 2018",
                ]),
            },
            {
                "name": "Numerai Meta Model",
                "url": "https://numer.ai",
                "status": "classified",
                "advantage": "analytical",
                "complexity": "light-grey",
                "stages": json.dumps(["idea-gen"]),
                "autonomy": "high",
                "agent_type": "commercial",
                "description": (
                    "Crowdsourced ML hedge fund aggregating thousands of encrypted "
                    "stock-prediction models into a Meta Model trading a global equity market-neutral "
                    "book. ~$1B AUM; +25.45% net 2024. J.P. Morgan AM committed $500M."
                ),
                "rationale": (
                    "Light Grey Swan: equity return distributions exist in theory but are "
                    "non-stationary and fat-tailed — the true probability distribution cannot be read "
                    "off directly, it must be searched. The crowdsourcing of thousands of diverse models "
                    "is itself evidence of computational intractability: no single model reliably finds "
                    "the true distribution. Analytical advantage: superior ensemble synthesis through "
                    "the staking mechanism, which aligns incentives to surface genuine signal."
                ),
                "key_features": json.dumps([
                    "Crowdsourced from thousands of anonymous ML scientists",
                    "NMR cryptocurrency staking aligns incentives toward real signal",
                    "Meta Model ensemble of best-performing submissions",
                    "Global equity market-neutral strategy",
                    "+25.45% net return 2024; ~$1B AUM",
                ]),
            },
            {
                "name": "Snowflake Cortex AI",
                "url": "https://www.snowflake.com/en/blog/cortex-ai-financial-services/",
                "status": "pending",
            },
            {
                "name": "Kavout K Score",
                "url": "https://www.kavout.com/k-score/",
                "status": "pending",
            },
        ]

        for data in agents:
            agent = Agent(
                name=data["name"],
                url=data.get("url"),
                status=data.get("status", "pending"),
                advantage=data.get("advantage"),
                complexity=data.get("complexity"),
                stages=data.get("stages"),
                autonomy=data.get("autonomy"),
                agent_type=data.get("agent_type"),
                description=data.get("description"),
                rationale=data.get("rationale"),
                key_features=data.get("key_features"),
            )
            db.session.add(agent)

        db.session.commit()
