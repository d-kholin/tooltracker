import os
import sqlite3
import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename

DB_PATH = os.environ.get('TOOLTRACKER_DB', 'tooltracker.db')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'images')
app.config['SECRET_KEY'] = 'dev'


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_conn() as conn:
        c = conn.cursor()
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS tools (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                value REAL,
                image_path TEXT
            )
            """
        )
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS people (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
            """
        )
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS loans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tool_id INTEGER NOT NULL,
                person_id INTEGER NOT NULL,
                lent_on TEXT NOT NULL,
                returned_on TEXT,
                FOREIGN KEY(tool_id) REFERENCES tools(id),
                FOREIGN KEY(person_id) REFERENCES people(id)
            )
            """
        )
        conn.commit()


init_db()


@app.route('/')
def index():
    with get_conn() as conn:
        c = conn.cursor()
        c.execute(
            """
            SELECT t.id, t.name, t.value, t.image_path, p.name AS borrower, l.lent_on
            FROM tools t
            LEFT JOIN loans l ON t.id = l.tool_id AND l.returned_on IS NULL
            LEFT JOIN people p ON l.person_id = p.id
            ORDER BY t.id
            """
        )
        tools = c.fetchall()
    return render_template('index.html', tools=tools)


@app.route('/add', methods=['GET', 'POST'])
def add_tool():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form.get('description', '')
        value_raw = request.form.get('value')
        value = float(value_raw) if value_raw else 0
        image_file = request.files.get('image')
        image_path = None
        if image_file and image_file.filename:
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            filename = secure_filename(image_file.filename)
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image_file.save(save_path)
            image_path = os.path.join('images', filename)
        with get_conn() as conn:
            c = conn.cursor()
            c.execute(
                "INSERT INTO tools (name, description, value, image_path) VALUES (?, ?, ?, ?)",
                (name, description, value, image_path),
            )
            conn.commit()
        return redirect(url_for('index'))
    return render_template('add_tool.html')


@app.route('/delete/<int:tool_id>', methods=['POST'])
def delete_tool(tool_id):
    with get_conn() as conn:
        c = conn.cursor()
        c.execute(
            "SELECT COUNT(*) FROM loans WHERE tool_id=? AND returned_on IS NULL",
            (tool_id,),
        )
        if c.fetchone()[0] > 0:
            flash('Cannot delete tool: it is currently lent out')
        else:
            c.execute("DELETE FROM tools WHERE id=?", (tool_id,))
            conn.commit()
    return redirect(url_for('index'))


@app.route('/lend/<int:tool_id>', methods=['GET', 'POST'])
def lend_tool(tool_id):
    if request.method == 'POST':
        person = request.form['person']
        with get_conn() as conn:
            c = conn.cursor()
            c.execute(
                "SELECT COUNT(*) FROM loans WHERE tool_id=? AND returned_on IS NULL",
                (tool_id,),
            )
            if c.fetchone()[0] > 0:
                flash('Tool already lent out')
            else:
                c.execute("SELECT id FROM people WHERE name=?", (person,))
                row = c.fetchone()
                if row:
                    person_id = row[0]
                else:
                    c.execute("INSERT INTO people (name) VALUES (?)", (person,))
                    person_id = c.lastrowid
                lent_on = datetime.date.today().isoformat()
                c.execute(
                    "INSERT INTO loans (tool_id, person_id, lent_on) VALUES (?, ?, ?)",
                    (tool_id, person_id, lent_on),
                )
                conn.commit()
        return redirect(url_for('index'))
    return render_template('lend_tool.html', tool_id=tool_id)


@app.route('/return/<int:tool_id>', methods=['POST'])
def return_tool(tool_id):
    with get_conn() as conn:
        c = conn.cursor()
        c.execute(
            "SELECT id FROM loans WHERE tool_id=? AND returned_on IS NULL",
            (tool_id,),
        )
        row = c.fetchone()
        if row:
            returned_on = datetime.date.today().isoformat()
            c.execute(
                "UPDATE loans SET returned_on=? WHERE id=?",
                (returned_on, row[0]),
            )
            conn.commit()
    return redirect(url_for('index'))


@app.route('/report')
def report():
    with get_conn() as conn:
        c = conn.cursor()
        c.execute(
            """
            SELECT p.name, COUNT(l.id) AS count
            FROM people p
            LEFT JOIN loans l ON p.id = l.person_id AND l.returned_on IS NULL
            GROUP BY p.id
            ORDER BY p.name
            """
        )
        rows = c.fetchall()
    return render_template('report.html', rows=rows)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
