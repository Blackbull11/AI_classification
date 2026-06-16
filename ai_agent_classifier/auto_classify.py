"""
auto_classify.py — Classify pending AI agents via Claude.

Usage (run from ai_agent_classifier/ directory):
  python auto_classify.py                          # classify all pending agents
  python auto_classify.py add "Agent Name"         # add + classify a new agent
  python auto_classify.py add "Agent Name" --url URL
"""

import json
import sys
import os
import argparse
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import anthropic
from app import app
from models import db, Agent


SYSTEM_PROMPT = """You are a specialist classifying AI agents for institutional investment management firms
using the Panthera Group Swan Theory framework. Research the given agent thoroughly, then classify it.

FRAMEWORK REFERENCE
===================

1. COMPLEXITY (Swan Theory tier)
   "white"      — White Swan: well-defined, deterministic objective. Abundant representative data.
                  Probability distribution is well-characterized. Pure optimization.
                  Examples: execution algorithms, compliance rule checkers.
   "light-grey" — Light Grey Swan: distribution theoretically exists but is non-stationary, fat-tailed,
                  or hard to fit. Requires ML/heuristics to find signal.
                  Examples: news sentiment, quant signal generation.
   "dark-grey"  — Dark Grey Swan: causal identification problem. We know the drivers but cannot fully
                  model the causal chain. Scenario analysis needed.
                  Examples: behavioral bias detection, macro forecasting.
   "black"      — Black Swan: fundamentally unknowable distribution. Novel, unprecedented situations.

2. INVESTMENT ADVANTAGE
   "informational" — Edge from data access speed, coverage breadth, or exclusive/proprietary data.
   "analytical"    — Edge from superior computation/synthesis over the same data others also have.
   "behavioral"    — Edge from overcoming cognitive biases or exploiting others' behavioral patterns.

3. AUTONOMY
   "low"    — Human-in-the-loop: agent recommends, human decides.
   "medium" — Semi-autonomous: acts within defined parameters with ongoing human oversight.
   "high"   — Fully autonomous within pre-set parameters.

4. AGENT TYPE
   "commercial" — SaaS / vendor product available commercially.
   "in-house"   — Built internally by the investment firm.
   "academic"   — Research prototype from an academic institution.

5. INVESTMENT PROCESS STAGES (select ALL that apply)
   "idea-gen"    — Idea Generation: generating investment signals, alpha sources, new ideas.
   "idea-assess" — Idea Assessment: screening and evaluating investment ideas.
   "decision"    — Decision Point: making buy/sell/hold decisions.
   "execution"   — Execution: implementing trades, order management, transaction cost optimization.
   "monitoring"  — Monitoring: ongoing portfolio and risk monitoring.
   "compliance"  — Compliance: regulatory compliance, risk controls, reporting obligations.
   "stakeholder" — Stakeholder Management: investor reporting, client communication, governance."""


def _build_tool() -> dict:
    return {
        "name": "classify_agent",
        "description": "Submit the complete classification for an AI investment agent.",
        "input_schema": {
            "type": "object",
            "properties": {
                "description": {
                    "type": "string",
                    "description": "2-3 sentence technical description of what the agent does and its key capabilities.",
                },
                "advantage": {
                    "type": "string",
                    "enum": ["behavioral", "analytical", "informational"],
                    "description": "Primary investment advantage type.",
                },
                "complexity": {
                    "type": "string",
                    "enum": ["black", "dark-grey", "light-grey", "white"],
                    "description": "Swan Theory complexity tier.",
                },
                "autonomy": {
                    "type": "string",
                    "enum": ["low", "medium", "high", "full"],
                    "description": "Level of agent autonomy. Use 'full' only for live-deployed systems with no human veto on individual decisions (e.g. fully algorithmic ETFs, live hedge fund meta-models).",
                },
                "agent_type": {
                    "type": "string",
                    "enum": ["commercial", "in-house", "academic"],
                    "description": "Product type.",
                },
                "stages": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": [
                            "idea-gen", "idea-assess", "decision",
                            "execution", "monitoring", "compliance", "stakeholder",
                        ],
                    },
                    "description": "Investment process stages this agent supports (all that apply).",
                    "minItems": 1,
                },
                "key_features": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "3-6 bullet points describing key features or notable facts.",
                    "minItems": 3,
                    "maxItems": 6,
                },
                "rationale": {
                    "type": "string",
                    "description": (
                        "2-4 sentences explaining WHY these classifications were assigned, "
                        "referencing the Panthera framework criteria."
                    ),
                },
            },
            "required": [
                "description", "advantage", "complexity", "autonomy",
                "agent_type", "stages", "key_features", "rationale",
            ],
        },
    }


def classify_with_claude(name: str, url: Optional[str] = None) -> dict:
    """Call Claude to research and classify a single agent. Returns the tool input dict."""
    client = anthropic.Anthropic()

    user_message = f"Please research and classify this AI agent:\n\nName: {name}"
    if url:
        user_message += f"\nURL: {url}"
    user_message += "\n\nProvide a complete classification using the classify_agent tool."

    with client.messages.stream(
        model="claude-opus-4-8",
        max_tokens=4096,
        thinking={"type": "adaptive"},
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
        tools=[_build_tool()],
        tool_choice={"type": "tool", "name": "classify_agent"},
    ) as stream:
        response = stream.get_final_message()

    for block in response.content:
        if block.type == "tool_use" and block.name == "classify_agent":
            return block.input

    raise RuntimeError("Claude did not return a classification tool call.")


def _apply_classification(agent: Agent, result: dict) -> None:
    agent.description = result["description"]
    agent.advantage = result["advantage"]
    agent.complexity = result["complexity"]
    agent.autonomy = result["autonomy"]
    agent.agent_type = result["agent_type"]
    agent.stages = json.dumps(result["stages"])
    agent.key_features = json.dumps(result["key_features"])
    agent.rationale = result["rationale"]
    agent.status = "classified"


def classify_pending() -> None:
    """Classify every agent currently in 'pending' status."""
    with app.app_context():
        pending = Agent.query.filter_by(status="pending").all()

        if not pending:
            print("No pending agents found.")
            return

        print(f"Found {len(pending)} pending agent(s).\n")

        for agent in pending:
            print(f"Classifying: {agent.name}")
            if agent.url:
                print(f"  URL: {agent.url}")

            try:
                result = classify_with_claude(agent.name, agent.url)
                _apply_classification(agent, result)
                db.session.commit()

                print(f"  complexity : {result['complexity']}")
                print(f"  advantage  : {result['advantage']}")
                print(f"  autonomy   : {result['autonomy']}")
                print(f"  stages     : {', '.join(result['stages'])}")
                print(f"  Done.\n")

            except Exception as exc:
                db.session.rollback()
                print(f"  ERROR: {exc}\n")


def add_and_classify(name: str, url: Optional[str] = None) -> None:
    """Add a new agent record and immediately classify it."""
    with app.app_context():
        existing = Agent.query.filter_by(name=name).first()
        if existing:
            print(f"Agent '{name}' already exists (id={existing.id}, status={existing.status}).")
            return

        print(f"Adding and classifying: {name}")
        if url:
            print(f"  URL: {url}")

        try:
            result = classify_with_claude(name, url)

            agent = Agent(
                name=name,
                url=url,
                description=result["description"],
                advantage=result["advantage"],
                complexity=result["complexity"],
                autonomy=result["autonomy"],
                agent_type=result["agent_type"],
                stages=json.dumps(result["stages"]),
                key_features=json.dumps(result["key_features"]),
                rationale=result["rationale"],
                status="classified",
            )
            db.session.add(agent)
            db.session.commit()

            print(f"  id         : {agent.id}")
            print(f"  complexity : {result['complexity']}")
            print(f"  advantage  : {result['advantage']}")
            print(f"  autonomy   : {result['autonomy']}")
            print(f"  stages     : {', '.join(result['stages'])}")
            print(f"  Done.\n")

        except Exception as exc:
            db.session.rollback()
            print(f"  ERROR: {exc}\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Auto-classify AI agents using Claude (claude-opus-4-8)."
    )
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("pending", help="Classify all pending agents (default).")

    add_p = subparsers.add_parser("add", help="Add a new agent and classify it immediately.")
    add_p.add_argument("name", help="Agent name")
    add_p.add_argument("--url", default=None, help="Agent URL (optional)")

    args = parser.parse_args()

    if args.command == "add":
        add_and_classify(args.name, args.url)
    else:
        classify_pending()


if __name__ == "__main__":
    main()
