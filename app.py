import os
import pyodbc
import logging
from flask import Flask, g, redirect, render_template, request, url_for

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)


def get_db():
    if "db" not in g:
        # Try multiple environment variable formats (Azure prefixes connection strings)
        conn_str = (
            os.environ.get("AZURE_SQL_CONNECTIONSTRING") or 
            os.environ.get("SQLAZURECONNSTR_AZURE_SQL_CONNECTIONSTRING")
        )
        if not conn_str:
            logging.error("Available env vars: %s", list(os.environ.keys()))
            raise RuntimeError("AZURE_SQL_CONNECTIONSTRING env var is not set")
        
        try:
            g.db = pyodbc.connect(conn_str, autocommit=False)
            logging.info("Database connection successful")
        except Exception as e:
            logging.error("Database connection failed: %s", e)
            raise
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        if exception is not None:
            db.rollback()
        else:
            db.commit()
        db.close()


def init_db():
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute(
            """
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'notes')
            BEGIN
                CREATE TABLE notes (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    content NVARCHAR(MAX) NOT NULL,
                    created_at DATETIME2 DEFAULT SYSUTCDATETIME()
                )
            END
            """
        )
    db.commit()


@app.route('/health')
def health():
    return "App is running! No database connection needed."


@app.before_request
def ensure_db():
    # Only initialize DB for non-health routes
    if request.endpoint != 'health':
        init_db()


@app.route("/", methods=["GET", "POST"])
def index():
    db = get_db()
    if request.method == "POST":
        content = request.form.get("content", "").strip()
        if content:
            with db.cursor() as cursor:
                cursor.execute("INSERT INTO notes (content) VALUES (?)", content)
            db.commit()
        return redirect(url_for("index"))

    with db.cursor() as cursor:
        cursor.execute(
            "SELECT id, content, created_at FROM notes ORDER BY created_at DESC"
        )
        columns = [col[0] for col in cursor.description]
        notes = [dict(zip(columns, row)) for row in cursor.fetchall()]
    return render_template("index.html", notes=notes)


if __name__ == "__main__":
    app.run(debug=True)
