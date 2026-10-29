
import os
import sqlite3
from datetime import datetime
from functools import wraps
from pathlib import Path

import click
from dotenv import load_dotenv
from flask import (
    Flask, abort, flash, redirect, render_template,
    request, session, url_for
)
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import check_password_hash, generate_password_hash

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

secret_key = os.environ.get("MTAFFIX_SECRET_KEY")
if not secret_key:
    raise RuntimeError(
        "MTAFFIX_SECRET_KEY is missing. Add it to your .env file."
    )

app = Flask(__name__)
app.config.update(
    SECRET_KEY=secret_key,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.environ.get("MTAFFIX_HTTPS", "0") == "1",
    WTF_CSRF_TIME_LIMIT=3600,
)

csrf = CSRFProtect(app)
DB_PATH = BASE_DIR / "mtaafix.db"

CATEGORIES = [
    "Road damage",
    "Garbage",
    "Water problem",
    "Broken streetlight",
    "Other",
]
STATUSES = ["Reported", "In Progress", "Resolved"]


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    # These statements preserve existing tables and reports.
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                category TEXT NOT NULL,
                location TEXT NOT NULL,
                description TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Reported',
                created_at TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS coordinators (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        conn.commit()


def current_coordinator():
    coordinator_id = session.get("coordinator_id")

    if not coordinator_id:
        return None

    with get_db() as conn:
        return conn.execute(
            "SELECT id, username FROM coordinators WHERE id = ?",
            (coordinator_id,),
        ).fetchone()


def coordinator_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if current_coordinator() is None:
            flash("Please log in as a coordinator to do that.", "error")
            return redirect(
                url_for("login", next=request.path)
            )

        return view(*args, **kwargs)

    return wrapped


@app.context_processor
def inject_coordinator():
    return {"logged_in_coordinator": current_coordinator()}


@app.cli.command("create-coordinator")
@click.argument("username")
def create_coordinator(username):
    """Create a coordinator account securely from the terminal."""
    username = username.strip()

    if not username or len(username) > 80:
        raise click.ClickException(
            "Username must be between 1 and 80 characters."
        )

    password = click.prompt(
        "Password",
        hide_input=True,
        confirmation_prompt=True,
    )

    if len(password) < 12:
        raise click.ClickException(
            "Use a password with at least 12 characters."
        )

    init_db()

    try:
        with get_db() as conn:
            conn.execute(
                """
                INSERT INTO coordinators
                    (username, password_hash, created_at)
                VALUES (?, ?, ?)
                """,
                (
                    username,
                    generate_password_hash(password),
                    datetime.now().strftime("%Y-%m-%d %H:%M"),
                ),
            )
            conn.commit()
    except sqlite3.IntegrityError:
        raise click.ClickException(
            "That username already exists. Choose another username."
        )

    click.echo(f"Coordinator account '{username}' created.")


@app.route("/")
def index():
    category = request.args.get("category", "").strip()

    with get_db() as conn:
        if category and category in CATEGORIES:
            reports = conn.execute(
                """
                SELECT * FROM reports
                WHERE category = ?
                ORDER BY id DESC
                """,
                (category,),
            ).fetchall()
        else:
            reports = conn.execute(
                "SELECT * FROM reports ORDER BY id DESC"
            ).fetchall()

        total = conn.execute(
            "SELECT COUNT(*) FROM reports"
        ).fetchone()[0]

        active = conn.execute(
            "SELECT COUNT(*) FROM reports WHERE status != 'Resolved'"
        ).fetchone()[0]

        resolved = conn.execute(
            "SELECT COUNT(*) FROM reports WHERE status = 'Resolved'"
        ).fetchone()[0]

    return render_template(
        "index.html",
        reports=reports,
        categories=CATEGORIES,
        selected_category=category,
        total=total,
        active=active,
        resolved=resolved,
    )


@app.route("/report", methods=["GET", "POST"])
def report():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        category = request.form.get("category", "").strip()
        location = request.form.get("location", "").strip()
        description = request.form.get("description", "").strip()

        valid = (
            bool(title)
            and len(title) <= 100
            and category in CATEGORIES
            and bool(location)
            and len(location) <= 160
            and bool(description)
            and len(description) <= 1200
        )

        if not valid:
            flash(
                "Please complete every field and choose a valid category.",
                "error",
            )
            return render_template(
                "report.html", categories=CATEGORIES
            ), 400

        with get_db() as conn:
            conn.execute(
                """
                INSERT INTO reports
                    (title, category, location, description, status, created_at)
                VALUES (?, ?, ?, ?, 'Reported', ?)
                """,
                (
                    title,
                    category,
                    location,
                    description,
                    datetime.now().strftime("%Y-%m-%d %H:%M"),
                ),
            )
            conn.commit()

        flash(
            "Your report was submitted. Thank you for helping your community!",
            "success",
        )
        return redirect(url_for("index"))

    return render_template("report.html", categories=CATEGORIES)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_coordinator() is not None:
        return redirect(url_for("index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        with get_db() as conn:
            coordinator = conn.execute(
                """
                SELECT id, username, password_hash
                FROM coordinators
                WHERE username = ?
                """,
                (username,),
            ).fetchone()

        if (
            coordinator
            and check_password_hash(
                coordinator["password_hash"], password
            )
        ):
            session.clear()
            session["coordinator_id"] = coordinator["id"]
            flash("You are now logged in.", "success")

            next_path = request.args.get("next", "")

            # Accept only local paths to prevent open redirects.
            if (
                next_path.startswith("/")
                and not next_path.startswith("//")
                and "\\" not in next_path
            ):
                return redirect(next_path)

            return redirect(url_for("index"))

        flash("Invalid username or password.", "error")

    return render_template("login.html")


@app.route("/logout", methods=["POST"])
@coordinator_required
def logout():
    session.clear()
    flash("You have logged out.", "success")
    return redirect(url_for("index"))


@app.route("/report/<int:report_id>/status", methods=["POST"])
@coordinator_required
def update_status(report_id):
    status = request.form.get("status", "")

    if status not in STATUSES:
        flash("That status is not valid.", "error")
        return redirect(url_for("index"))

    with get_db() as conn:
        cursor = conn.execute(
            "UPDATE reports SET status = ? WHERE id = ?",
            (status, report_id),
        )
        conn.commit()

    if cursor.rowcount == 0:
        abort(404)

    flash("Report status updated.", "success")
    return redirect(url_for("index"))


@app.route("/health")
def health():
    return {"status": "ok", "app": "MtaaFix"}


init_db()

if __name__ == "__main__":
    app.run(
        debug=os.environ.get("MTAFFIX_DEBUG", "0") == "1"
    )
