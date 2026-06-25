# Panthera Insights — Commercialization Plan

**Status:** Planning (no code changes yet)
**Date:** 2026-06-25
**Source brief:** *Notes — AI agents Classification Framework in Action* (18 June 2026)

This document specifies how to evolve the existing internal **AI Agent Classifier** (Flask app) into **Panthera Insights** — a neutral, two-sided discovery & classification SaaS for the investment-management AI-agent market.

---

## 1. Strategic summary

The classification engine is already the moat and **does not need rebuilding**. The four taxonomy dimensions in the brief map 1:1 onto existing fields:

| Brief dimension | Existing field | Source |
|---|---|---|
| D1 — Investment Process Stage | `Agent.stages` (7 stages) | `app.py` `STAGES` |
| D2 — Autonomy Level | `Agent.autonomy` (low/medium/high/full) | `app.py` |
| D3 — Comparative Advantage Type | `Agent.advantage` (informational/analytical/behavioral) | `app.py` |
| D4 — Swan Complexity | `Agent.complexity` (white/light-grey/dark-grey/black) | README Swan Theory |

The commercialization work is therefore an **access-control + two-audience layer on top of the existing matrix, guide, wizard, pipeline, and export code** — not a rewrite.

### Decisions locked (2026-06-25)
- **Freemium split:** explicit `premium` boolean column on `Agent` (manual control).
- **Decision GPS:** kept in catalogue **with a visible "Panthera-affiliated" disclosure** on its profile.
- **Output:** written plan first (this document); implementation to follow in phases.

---

## 2. Current-state gap analysis

| Business requirement | Today | Gap to close |
|---|---|---|
| Buyer self-serve discovery (CIO shortlists in <10 min) | `/guide`, `/matrix` | No compare/shortlist; no accounts |
| Freemium — 50% free, rest gated | All public | No auth, no paywall, no tiering |
| Supplier listings + self-serve updates | `/pipeline`, `/add` open to anyone | No supplier accounts; no submission/review separation |
| Listing fees + subscriptions | None | No billing, no roles |
| Neutral positioning (independent of Decision GPS) | Decision GPS listed as a plain agent | Add disclosure label |
| Periodic reports | Excel/Word/PDF export of full DB | Exists but ungated; not productized |

**Security-critical finding:** `/pipeline`, `/add`, `/edit`, `/delete`, `/quick-add`, `/agents/<id>/classify*`, `/api/agents`, and the entire `/admin` Flask-Admin panel currently have **no authentication**. Anyone can edit or delete the whole catalogue. This must be fixed first, independent of monetization.

---

## 3. Target architecture

### Audiences & roles
- **Visitor** (anonymous) — sees landing page, matrix positioning (badges), free agent profiles, framework page.
- **Subscriber** (paying buyer / CIO) — full profiles, compare, shortlist, exports/reports.
- **Supplier** (AI vendor) — own dashboard; submit & edit their own agent profile (goes to review queue).
- **Admin** (Panthera staff) — pipeline, wizard, auto-classifier, Flask-Admin, API; the neutral classifier role.

### Route map (target)

| Route | Audience | Change |
|---|---|---|
| `/` (landing) | Visitor | **New** marketing entry; product value prop + 4 dimensions |
| `/matrix` | Visitor (positioning) | Premium badges visible, detail gated |
| `/guide` | Visitor | Feeds shortlist instead of just linking |
| `/framework` | Visitor | Keep |
| `/agents/<id>` | Visitor (free) / Subscriber (premium) | Teaser template when `premium` & not subscribed |
| `/compare?ids=` | Subscriber | **New** side-by-side of 2–4 agents |
| `/shortlist` | Visitor/Subscriber | **New** session/user-backed list |
| `/export/*` | Subscriber | Gate (becomes "periodic reports") |
| `/supplier/register`, `/supplier/dashboard` | Supplier | **New** |
| `/pipeline`, `/add*`, `/edit*`, `/delete`, `/quick-add`, `/agents/<id>/classify*` | Admin | **Lock down** |
| `/admin/*` (Flask-Admin) | Admin | **Lock down** (`is_accessible`) |
| `/api/agents` | Admin (or API-key) | **Lock down** |
| `/account/billing`, `/stripe/webhook` | Subscriber | **New** (Phase 5) |

---

## 4. Data-model changes (`models.py`)

### New `User` model
```
id, email (unique), password_hash, role  # visitor|subscriber|supplier|admin
company (nullable, suppliers), subscription_active (bool, default False)
stripe_customer_id (nullable), created_at
```
Use `werkzeug.security` for hashing; Flask-Login for sessions.

### `Agent` additions
- `premium` — Boolean, default False. Drives freemium gating (manual control).
- `submitted_by` — FK → `User.id`, nullable. Set when a supplier submits.
- `verified_at` / `last_reviewed` — DateTime, nullable. Powers the "audited / current as of" trust signal (addresses the brief's *database maintenance* mitigation).

### Status lifecycle
Reuse existing `status` field; add a `submitted` value:
`submitted` (supplier-created, not yet audited) → `pending` → `classified` (live) / `rejected`.
Supplier submissions never hit the public matrix until an admin classifies them — preserving Panthera's neutral-classifier role.

**Migration:** extend the existing `_migrate_db()` in `app.py` (already does `ALTER TABLE ... ADD COLUMN` for `category_id`) to add the new columns. Note: production is now PostgreSQL (commit `c94bbda`) — the `PRAGMA table_info` path in `_migrate_db()` is SQLite-only and must be made dialect-aware or replaced with a proper migration (consider Flask-Migrate/Alembic at this point).

---

## 5. Freemium gating (the 50% rule)

- Mark ~50% of the 77 agents `premium = True` (admin choice via Flask-Admin).
- **Matrix & guide still display premium agents** (badges + positioning) so value is visible.
- `/agents/<id>` ([app.py](../ai_agent_classifier/app.py) `agent_detail`): if `agent.premium and not current_user.subscription_active`, render a **teaser** — name, category, the 4 dimension badges, but rationale & key features blurred/omitted, plus an upgrade CTA.
- Gate `/export/*` behind `subscription_active`. These become the productized "periodic reports."

---

## 6. Buyer experience — Compare & Shortlist (the "<10 minutes" goal)

- **Shortlist:** session-backed for visitors, user-backed for logged-in. "Add to shortlist" button on matrix hover cards, guide result cards, and detail pages. `/shortlist` renders the set.
- **Compare:** `/compare?ids=a,b,c` — side-by-side table across all four dimensions + category + key features (2–4 agents).
- Wire `/guide` questionnaire results into the shortlist rather than dead-ending at profiles.

---

## 7. Supplier portal (supply side + listing fees)

- `/supplier/register` → creates `role='supplier'` user.
- `/supplier/dashboard` → lists the supplier's own agents; "Submit new agent" and "Edit" reuse the **existing wizard**, scoped to `submitted_by == current_user.id`, writing `status='submitted'`.
- Submitted agents surface in the admin `/pipeline` for audit → admin runs wizard / `auto_classify.py` → `classified` → live.
- Per the brief, **offer free listing during initial phase** — gate the listing fee behind a flag so launch can be free.

---

## 8. Billing (Stripe) — Phase 5, deferrable

- `stripe` package; one subscription product (buyer) + one listing product (supplier).
- `/account/billing` (Checkout session) + `/stripe/webhook` to flip `subscription_active` / role.
- **MVP shortcut:** skip real billing at launch; let admin toggle `subscription_active` manually. The brief explicitly endorses a free initial phase, so launch gated-but-free and switch Stripe on later.

---

## 9. Positioning & neutrality

- Rebrand product surface to **Panthera Insights**; new `/` landing becomes the marketing entry, matrix becomes the *product* (not the homepage). Update `base.html` brand link (currently → `matrix`).
- **Decision GPS:** keep listed, add a visible "Panthera-affiliated product" disclosure label on its detail page (`agent_detail.html`). It is currently in `UNCATEGORIZED_AGENTS` (`app.py`).

---

## 10. Phased roadmap

| Phase | Scope | Why this order |
|---|---|---|
| **1. Auth & lockdown** | `User` model, Flask-Login, protect back-office routes + Flask-Admin + API | Security-critical; unblocks everything |
| **2. Freemium + landing** | `premium` column, teaser template, gated exports, `/` landing | Makes it a sellable product |
| **3. Compare & shortlist** | `/shortlist`, `/compare`, buttons, guide wiring | The demo-able buyer value |
| **4. Supplier portal** | supplier role, register/dashboard, `submitted` lifecycle | Supply side |
| **5. Billing** | Stripe subscription + listing, webhook | Monetization; can pilot free first |

Each phase reuses existing matrix / guide / wizard / pipeline / export code; the net new work is the access-control layer plus two new audience surfaces.

---

## 11. New dependencies

`flask-login`, `flask-migrate` (recommended over hand-rolled `_migrate_db`), `stripe` (Phase 5). Add to `requirements.txt` per phase.

---

## 12. Messaging & clarity (goals · targets · methodology · offer)

**Design principle:** a CIO should grasp *what this is, who it's for, how it works, and what they get* in **one scroll, under 30 seconds** — before reading a single line of documentation. The deep framework page stays as the proof; the product surface leads with plain language and punchlines.

### The one-line product punchline (master tagline)
> **Panthera Insights — the reference map of AI agents in investment management.**

Supporting line:
> *Every AI agent, classified on one rigorous framework. Filter, compare, and shortlist in under ten minutes — neutrally, with no tools to sell you.*

### Punchline library (drop-in, reusable)
| Use | Punchline |
|---|---|
| Hero | **Stop drowning in AI vendor decks. Start with the map.** |
| Neutrality | **We don't sell the tools. We make sense of them.** |
| Methodology | **Four questions locate any AI agent: where it works, how independently it acts, what edge it brings, and how well it handles the unknown.** |
| Speed-to-value | **From 200 AI tools to your shortlist — in ten minutes.** |
| Swan / risk angle | **Know which AI belongs in a crisis, and which one causes it.** |
| For suppliers | **Get classified. Get found. Get chosen.** |
| Credibility | **Built on a peer-reviewed taxonomy. Trusted by allocators.** |
| Network-effect / standard | **The common language for AI in investing.** |

### Goals — stated plainly (for an "About / Why" block)
1. **Cut the noise.** One neutral catalogue instead of a hundred vendor pitches.
2. **Make AI legible.** Every agent positioned on the same four dimensions — comparable at a glance.
3. **De-risk adoption.** Show which tool fits which decision, and where autonomy is appropriate.
4. **Become the standard.** The reference taxonomy buyers and suppliers both rally to.

### Targets — say who it's for, in their words
| Audience | One-line "job to be done" |
|---|---|
| **CIOs & Heads of Investment** | "Show me the AI landscape for my process — and what's worth a meeting." |
| **PMs & Analysts** | "Find the right tool for *this* stage of *my* workflow, fast." |
| **Risk & Compliance** | "Tell me how autonomous a tool is before it touches live capital." |
| **AI Suppliers (sellers)** | "Get classified credibly and found by the buyers who matter." |

### Methodology — the framework in one breath
Present the four dimensions as **four plain questions**, each with its icon/colour from the existing design system:

| # | Plain-language question | Dimension | Field |
|---|---|---|---|
| 1 | **Where does it work?** | Investment Process Stage (7) | `stages` |
| 2 | **How independently does it act?** | Autonomy (low → fully autonomous) | `autonomy` |
| 3 | **What kind of edge does it give?** | Comparative Advantage (informational / analytical / behavioral) | `advantage` |
| 4 | **How well does it handle the unknown?** | Swan Complexity (white → black) | `complexity` |

Tagline for this block: *"Four questions. One coordinate. Any agent, instantly placed."*

### Solutions offered — what you actually get (3-card "offer" block)
1. **The Map** — the live classification matrix: ~77 agents (growing) across stage × complexity, colour-coded by edge, type, and autonomy.
2. **The Finder** — answer four questions, get a ranked shortlist for your exact workflow (the `/guide` questionnaire, productized).
3. **The Briefings** — exportable, board-ready reports and periodic market intelligence (the gated Excel/Word/PDF engine).

---

## 13. Navigation & information architecture redesign

**Problem today:** the navbar (`base.html`) exposes the *internal tool* mental model — `Matrix · Pipeline · Guide · Framework · Exports`. `Pipeline` and `Exports` are back-office/ gated concepts that confuse a first-time buyer, and there is no landing page.

**Target primary nav (buyer-first, max 5 items):**

| Label | Route | Replaces / note |
|---|---|---|
| **Explore the Map** | `/matrix` | renamed from "Matrix" — verb-led, obvious |
| **Find an Agent** | `/guide` | renamed from "Guide" — outcome-led |
| **Compare** | `/compare` (+ `/shortlist`) | new buyer feature (Phase 3) |
| **How it works** | `/framework` | renamed from "Framework" — lower barrier; deep methodology lives here |
| **For Suppliers** | `/supplier` | new supply-side entry (Phase 4) |

Right-aligned: **Log in / Subscribe** (Phase 1–2). `Pipeline`, `Exports`, and `/admin` move **out of the public navbar** into an authenticated staff/account area. Exports resurface as "Download report" CTAs inside `/compare` and `/shortlist`, gated for subscribers.

**Navigation principles to apply:**
- **Verb-led labels** ("Explore", "Find", "Compare") over nouns — they tell the user what they'll *do*.
- **One primary CTA per page**, reusing the existing pulsing `.fw-cta-btn` style so the eye always knows the next step.
- **Persistent shortlist affordance** (a counter chip in the navbar) so a CIO can collect candidates while browsing and check out in one place — the backbone of the "<10 minutes" promise.
- **Progressive disclosure:** landing → map/finder (free positioning) → full profile (gated). Never show a wall of methodology before the value.

---

## 14. Landing page copy (new `/` — drop-in draft)

Reuse the framework page's existing component styles (`.fw-hero`, `.fw-axis-card`, `.fw-cta-wrap`, the four advantage/complexity colours). Sections, top to bottom:

**1 — Hero**
- Eyebrow: `NEUTRAL AI-AGENT INTELLIGENCE FOR INVESTMENT MANAGEMENT`
- H1: **The reference map of AI agents in investment management.**
- Sub: *Stop drowning in vendor decks. Filter, compare, and shortlist the right AI tools for your investment process — on one rigorous, peer-reviewed framework. No tools to sell you.*
- Primary CTA: **Explore the Map →**  ·  Secondary: *Find an agent by criteria →*
- Trust strip: *Built on Schuller, Wierckx, Kuhn & Zilic (2025) · ~77 agents classified & audited · 10 functional archetypes.*

**2 — The problem (one line + three pills)**
- Line: **There are hundreds of AI agents and no neutral way to compare them.** Panthera Insights fixes that.
- Pills: *Information overload · No common language · No idea which tool fits which decision.*

**3 — Methodology ("Four questions. One coordinate.")** — the four plain-language question cards from §12.

**4 — What you get (the three solution cards from §12: Map · Finder · Briefings).**

**5 — Who it's for** — the four target rows from §12 as audience cards (CIOs · PMs/Analysts · Risk & Compliance · Suppliers).

**6 — Neutrality statement** — **We don't sell the tools. We make sense of them.** *An independent infrastructure layer between investment firms and AI suppliers — including a transparently-flagged listing for Panthera's own Decision GPS (see §9).*

**7 — Final CTA** — reuse `.fw-cta-wrap`: **See every AI agent mapped in multi-dimensional space → Explore the Map.**

---

## 15. Impact on phasing

Clarity is now a **first-class workstream folded into Phase 2**, not an afterthought:

- **Phase 2 (Freemium + landing)** expands to: build the new `/` landing (§14), the navbar/IA redesign (§13), and apply the punchlines/methodology framing (§12). This is what makes the product *legible and attractive*, so it ships alongside gating.
- **Phase 3** delivers the `Compare`/`Shortlist` nav items the new IA promises.
- Copy in §12–§14 is drop-in: it reuses existing `framework.html` component styles and the design system, so the build is mostly templating, not new CSS.
