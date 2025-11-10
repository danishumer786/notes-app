import os
import pyodbc
from flask import Flask, g, redirect, render_template, request, url_for

app = Flask(__name__)


def get_db():
    if "db" not in g:
        conn_str = os.environ.get("AZURE_SQL_CONNECTIONSTRING")
        if not conn_str:
            raise RuntimeError("AZURE_SQL_CONNECTIONSTRING env var is not set")
        g.db = pyodbc.connect(conn_str, autocommit=False)
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


@app.before_request
def ensure_db():
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
