"""
create_admin.py — Bootstrap or promote an admin user.

Usage (run from ai_agent_classifier/ directory):
  python create_admin.py you@panthera.design "a-strong-password"
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from models import db, User


def main():
    if len(sys.argv) != 3:
        print('Usage: python create_admin.py <email> "<password>"')
        sys.exit(1)

    email = sys.argv[1].strip().lower()
    password = sys.argv[2]

    with app.app_context():
        db.create_all()
        user = User.query.filter_by(email=email).first()
        if user is None:
            user = User(email=email, role="admin")
            db.session.add(user)
            print(f"Creating new admin user: {email}")
        else:
            user.role = "admin"
            print(f"Promoting existing user to admin: {email}")
        user.set_password(password)
        db.session.commit()
        print("Done.")


if __name__ == "__main__":
    main()
