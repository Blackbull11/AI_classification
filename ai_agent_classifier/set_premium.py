"""
set_premium.py — Curate which classified agents are premium (freemium gating).

Rules (per docs/PANTHERA_INSIGHTS_PLAN.md §5, refined by business decision):
  1. Only commercial agents may be marked premium (in-house / academic always stay free).
  2. For every investment-process stage, at least 40% of the agents tagged with that
     stage must stay free (i.e. premium agents are capped at 60% of each stage's total).
  3. Subject to (1) and (2), mark as close to 50% of all classified agents premium as possible.

Selection is a greedy set-packing: cheapest agents (fewest stage tags) are placed first,
so scarce per-stage capacity is spent efficiently. Re-running is idempotent and safe to
do after adding new agents — it recomputes the whole assignment from scratch.

Usage (run from ai_agent_classifier/ directory):
  python set_premium.py            # apply
  python set_premium.py --dry-run  # report only, no DB writes
"""

import math
import sys
from collections import Counter

from app import app
from models import db, Agent

PREMIUM_TARGET_RATIO = 0.5
MIN_FREE_PER_STAGE_RATIO = 0.4


def compute_selection(agents):
    stage_total = Counter()
    for a in agents:
        for s in a.stages_list:
            stage_total[s] += 1

    premium_max = {
        s: math.floor((1 - MIN_FREE_PER_STAGE_RATIO) * total)
        for s, total in stage_total.items()
    }
    remaining_cap = dict(premium_max)

    eligible = [a for a in agents if a.agent_type == "commercial"]
    eligible.sort(key=lambda a: (len(a.stages_list), a.name))

    target = round(PREMIUM_TARGET_RATIO * len(agents))
    selected = []
    for a in eligible:
        if len(selected) >= target:
            break
        stages = a.stages_list
        if all(remaining_cap.get(s, 0) >= 1 for s in stages):
            selected.append(a)
            for s in stages:
                remaining_cap[s] -= 1

    return selected, stage_total, premium_max


def main():
    dry_run = "--dry-run" in sys.argv

    with app.app_context():
        agents = Agent.query.filter_by(status="classified").all()
        selected, stage_total, premium_max = compute_selection(agents)
        selected_ids = {a.id for a in selected}

        print(f"Classified agents: {len(agents)}")
        print(f"Selected premium:  {len(selected)} ({len(selected) / len(agents):.0%})")
        print()
        print(f"{'stage':14s} {'total':>6s} {'premium':>8s} {'free %':>8s}")
        premium_by_stage = Counter()
        for a in selected:
            for s in a.stages_list:
                premium_by_stage[s] += 1
        for s, total in sorted(stage_total.items()):
            p = premium_by_stage.get(s, 0)
            free_pct = (total - p) / total
            print(f"{s:14s} {total:6d} {p:8d} {free_pct:7.0%}  (cap {premium_max[s]})")

        if dry_run:
            print("\n--dry-run: no changes written.")
            return

        for a in agents:
            a.premium = a.id in selected_ids
        db.session.commit()
        print("\nDone. Premium flags written.")


if __name__ == "__main__":
    main()
