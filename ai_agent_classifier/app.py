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

from models import Agent, db
from seed_data import seed_database
from exports import build_excel, build_word, build_pdf

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///agents.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

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


@app.context_processor
def inject_globals():
    pending_count = Agent.query.filter_by(status="pending").count()
    return {"pending_count": pending_count, "today": date.today()}


# ─── Matrix ───────────────────────────────────────────────────────────────────

@app.route("/")
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
    )


@app.route("/quick-add", methods=["POST"])
def quick_add():
    name = request.form.get("name", "").strip()
    url  = request.form.get("url",  "").strip()
    if not name:
        flash("Agent name is required.", "warning")
        return redirect(url_for("pipeline"))
    agent = Agent(name=name, url=url or None, status="pending")
    db.session.add(agent)
    db.session.commit()
    flash(f"'{name}' added to the pipeline.", "success")
    return redirect(url_for("pipeline"))


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
        }
        for a in classified
    ])
    return render_template(
        "guide.html",
        agents_json=agents_json,
        stages=STAGES,
        complexities=COMPLEXITIES,
        advantages=ADVANTAGES,
    )


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

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        seed_database(app, db, Agent)
    app.run(debug=True, port=5000)
