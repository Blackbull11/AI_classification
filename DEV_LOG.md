# Development Log

Append-only. Newest entries at the bottom.

---

## 2026-06-19 — Authors/tutor presentation deck

**Summary:** Built a 15-slide professional PowerPoint deck presenting the platform to the paper's four authors and the internship tutor. Top-down narrative (goal → problem → framework → methodology → platform tour → results → reflections → limitations → conclusions), styled to the platform's dark/copper design system, embedding the six `docs/screenshots`. Includes per-slide speaker notes and personal design-decision commentary.

**Files created:**
- `presentation/build_deck.py` — python-pptx generator (palette, layout helpers, image-fit, speaker notes).
- `presentation/Panthera_AI_Agent_Classifier.pptx` — the rendered 15-slide deck.
- `DEV_LOG.md` — this log (was referenced in memory but did not exist yet).

**Notes / data used:** Pulled live stats from `instance/agents.db` — 78 classified agents; complexity skew to white (39) / light-grey (40), dark-grey 1, black 0; advantage analytical 49 / informational 30 / behavioral 1; autonomy low 54 / medium 14 / high 10 / full 2; stage coverage led by idea-assess (56) and idea-gen (31). These drive the "Results / market view" slide.

**Open items:**
- Presenter name/date on title + closing slides are placeholders (Andrea Signoretti, June 2026) — confirm/edit.
- "~99%" and "63%" stat-card figures are rounded from the classified set; re-confirm if the DB changes before the talk.
- Deck regenerates via `python presentation/build_deck.py`; PowerPoint COM was used only for visual QA (temp `_render/` removed).
