import json
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Agent(db.Model):
    __tablename__ = "agents"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    url = db.Column(db.String(500))
    description = db.Column(db.Text)
    rationale = db.Column(db.Text)
    key_features = db.Column(db.Text)
    advantage = db.Column(db.String(20))
    autonomy = db.Column(db.String(10))
    agent_type = db.Column(db.String(20))
    complexity = db.Column(db.String(20))
    stages = db.Column(db.Text)
    category_id = db.Column(db.String(50))
    status = db.Column(db.String(20), default="pending")
    in_stack = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def rationale_dict(self):
        """Parse rationale as JSON dict; fall back to {'general': value} for legacy plain text."""
        if not self.rationale:
            return {}
        try:
            data = json.loads(self.rationale)
            return data if isinstance(data, dict) else {"general": str(data)}
        except (json.JSONDecodeError, TypeError):
            return {"general": self.rationale}

    @property
    def stages_list(self):
        if not self.stages:
            return []
        try:
            return json.loads(self.stages)
        except (json.JSONDecodeError, TypeError):
            return []

    @property
    def features_list(self):
        if not self.key_features:
            return []
        try:
            return json.loads(self.key_features)
        except (json.JSONDecodeError, TypeError):
            return []
