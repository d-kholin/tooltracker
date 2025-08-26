import os
import sqlite3
import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
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
                name TEXT NOT NULL UNIQUE,
                contact_info TEXT
            )
            """
        )
        # Ensure contact_info column exists for older databases
        try:
            c.execute("ALTER TABLE people ADD COLUMN contact_info TEXT")
        except sqlite3.OperationalError:
            pass
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
    return render_template('index.html')


@app.route('/api/tools', methods=['GET', 'POST'])
def api_tools():
    if request.method == 'POST':
        data = request.get_json(force=True)
        name = data.get('name', '').strip()
        if not name:
            return jsonify({'error': 'name required'}), 400
        with get_conn() as conn:
            c = conn.cursor()
            c.execute(
                "INSERT INTO tools (name, description, value, image_path) VALUES (?, '', 0, NULL)",
                (name,),
            )
            tool_id = c.lastrowid
            conn.commit()
            c.execute("SELECT id, name FROM tools WHERE id=?", (tool_id,))
            tool = dict(c.fetchone())
        return jsonify(tool), 201

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
        tools = [dict(row) for row in c.fetchall()]
    return jsonify(tools)


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
        person_id = request.form.get('person_id')
        with get_conn() as conn:
            c = conn.cursor()
            c.execute(
                "SELECT COUNT(*) FROM loans WHERE tool_id=? AND returned_on IS NULL",
                (tool_id,),
            )
            if c.fetchone()[0] > 0:
                flash('Tool already lent out')
            else:
                c.execute("SELECT id FROM people WHERE id=?", (person_id,))
                row = c.fetchone()
                if not row:
                    flash('Person not found')
                else:
                    lent_on = datetime.date.today().isoformat()
                    c.execute(
                        "INSERT INTO loans (tool_id, person_id, lent_on) VALUES (?, ?, ?)",
                        (tool_id, person_id, lent_on),
                    )
                    conn.commit()
        return redirect(url_for('index'))
    with get_conn() as conn:
        c = conn.cursor()
        c.execute("SELECT id, name FROM people ORDER BY name")
        people = [dict(row) for row in c.fetchall()]
        if not people:
            flash('No people available. Add a person first.')
            return redirect(url_for('people'))
    return render_template('lend_tool.html', tool_id=tool_id, people=people)


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


@app.route('/people', methods=['GET', 'POST'])
def people():
    if request.method == 'POST':
        name = request.form['name']
        contact_info = request.form.get('contact_info', '')
        with get_conn() as conn:
            c = conn.cursor()
            try:
                c.execute(
                    "INSERT INTO people (name, contact_info) VALUES (?, ?)",
                    (name, contact_info),
                )
                conn.commit()
            except sqlite3.IntegrityError:
                flash('Person already exists')
        return redirect(url_for('people'))
    with get_conn() as conn:
        c = conn.cursor()
        c.execute("SELECT id, name, contact_info FROM people ORDER BY name")
        people = c.fetchall()
    return render_template('people.html', people=people)


@app.route('/people/<int:person_id>/delete', methods=['POST'])
def delete_person(person_id):
    with get_conn() as conn:
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM loans WHERE person_id=?", (person_id,))
        if c.fetchone()[0] > 0:
            flash('Cannot delete person: existing loan records')
        else:
            c.execute("DELETE FROM people WHERE id=?", (person_id,))
            conn.commit()
    return redirect(url_for('people'))


@app.route('/people/<int:person_id>')
def person_detail(person_id):
    with get_conn() as conn:
        c = conn.cursor()
        c.execute("SELECT name, contact_info FROM people WHERE id=?", (person_id,))
        person = c.fetchone()
        if not person:
            return redirect(url_for('people'))
        c.execute(
            """
            SELECT t.name AS tool_name, l.lent_on, l.returned_on
            FROM loans l
            JOIN tools t ON l.tool_id = t.id
            WHERE l.person_id=?
            ORDER BY l.lent_on DESC
            """,
            (person_id,),
        )
        loans = c.fetchall()
    return render_template('person_loans.html', person=person, loans=loans)


@app.route('/people/<int:person_id>/edit', methods=['GET', 'POST'])
def edit_person(person_id):
    with get_conn() as conn:
        c = conn.cursor()
        if request.method == 'POST':
            name = request.form['name']
            contact_info = request.form.get('contact_info', '')
            try:
                c.execute(
                    "UPDATE people SET name=?, contact_info=? WHERE id=?",
                    (name, contact_info, person_id),
                )
                conn.commit()
                return redirect(url_for('people'))
            except sqlite3.IntegrityError:
                flash('Person already exists')
        c.execute("SELECT id, name, contact_info FROM people WHERE id=?", (person_id,))
        person = c.fetchone()
        if not person:
            return redirect(url_for('people'))
    return render_template('edit_person.html', person=person)


@app.route('/report')
def report():
    with get_conn() as conn:
        c = conn.cursor()
        c.execute(
            """
            SELECT p.id AS person_id, p.name, COUNT(l.id) AS count
            FROM people p
            LEFT JOIN loans l ON p.id = l.person_id AND l.returned_on IS NULL
            GROUP BY p.id, p.name
            ORDER BY p.name
            """
        )
        rows = c.fetchall()
    return render_template('report.html', rows=rows)


@app.route('/tool/<int:tool_id>')
def tool_detail(tool_id):
    with get_conn() as conn:
        c = conn.cursor()
        # Get tool details
        c.execute(
            """
            SELECT t.id, t.name, t.description, t.value, t.image_path, p.name AS borrower, l.lent_on
            FROM tools t
            LEFT JOIN loans l ON t.id = l.tool_id AND l.returned_on IS NULL
            LEFT JOIN people p ON l.person_id = p.id
            WHERE t.id = ?
            """,
            (tool_id,),
        )
        tool = c.fetchone()
        if not tool:
            return redirect(url_for('index'))
        
        # Get lending history
        c.execute(
            """
            SELECT l.lent_on, l.returned_on, p.name AS person_name, p.contact_info
            FROM loans l
            JOIN people p ON l.person_id = p.id
            WHERE l.tool_id = ?
            ORDER BY l.lent_on DESC
            """,
            (tool_id,),
        )
        loans = c.fetchall()
    
    return render_template('tool_detail.html', tool=tool, loans=loans)


@app.route('/edit/<int:tool_id>', methods=['GET', 'POST'])
def edit_tool(tool_id):
    with get_conn() as conn:
        c = conn.cursor()
        if request.method == 'POST':
            name = request.form['name']
            description = request.form.get('description', '')
            value_raw = request.form.get('value')
            value = float(value_raw) if value_raw else 0
            image_file = request.files.get('image')
            if image_file and image_file.filename:
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                filename = secure_filename(image_file.filename)
                save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                image_file.save(save_path)
                image_path = os.path.join('images', filename)
                c.execute(
                    "UPDATE tools SET name=?, description=?, value=?, image_path=? WHERE id=?",
                    (name, description, value, image_path, tool_id),
                )
            else:
                c.execute(
                    "UPDATE tools SET name=?, description=?, value=? WHERE id=?",
                    (name, description, value, tool_id),
                )
            conn.commit()
            return redirect(url_for('index'))
        c.execute("SELECT * FROM tools WHERE id=?", (tool_id,))
        tool = c.fetchone()
    return render_template('edit_tool.html', tool=tool)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
