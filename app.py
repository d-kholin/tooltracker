import os
import sqlite3
import datetime
import uuid
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename
from PIL import Image
import io

DB_PATH = os.environ.get('TOOLTRACKER_DB', 'tooltracker.db')
UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', os.path.join('static', 'images'))

# Image optimization constants
MAX_IMAGE_DIMENSION = 1024  # Maximum dimension for image resizing
JPEG_QUALITY = 85  # JPEG compression quality
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB maximum file size

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(24).hex())


def generate_unique_filename(original_filename):
    """Generate a unique filename to prevent conflicts"""
    if not original_filename:
        return None
    
    # Get file extension
    _, ext = os.path.splitext(original_filename)
    ext = ext.lower()  # Normalize extension
    
    # Validate file extension (only allow common image formats)
    allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
    if ext not in allowed_extensions:
        ext = '.jpg'  # Default to jpg if extension is not recognized
    
    # Generate unique filename with timestamp and UUID
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    unique_id = str(uuid.uuid4())[:8]  # Use first 8 characters of UUID
    
    # Create new filename
    new_filename = f"tool_{timestamp}_{unique_id}{ext}"
    
    return new_filename


def optimize_image(image_file):
    """
    Optimize uploaded image by resizing and compressing
    Returns the optimized image as bytes and the file extension
    """
    try:
        # Open the image
        img = Image.open(image_file)
        
        # Convert to RGB if necessary (for JPEG compatibility)
        if img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGB')
        
        # Get original dimensions
        original_width, original_height = img.size
        
        # Calculate new dimensions while maintaining aspect ratio
        if original_width > MAX_IMAGE_DIMENSION or original_height > MAX_IMAGE_DIMENSION:
            if original_width > original_height:
                new_width = MAX_IMAGE_DIMENSION
                new_height = int(original_height * (MAX_IMAGE_DIMENSION / original_width))
            else:
                new_height = MAX_IMAGE_DIMENSION
                new_width = int(original_width * (MAX_IMAGE_DIMENSION / original_height))
            
            # Resize the image
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            print(f"Resized image from {original_width}x{original_height} to {new_width}x{new_height}")
        
        # Save optimized image to bytes
        output = io.BytesIO()
        
        # Determine output format and save with optimization
        if img.format in ('JPEG', 'JPG') or img.mode == 'RGB':
            # Save as JPEG with compression
            img.save(output, format='JPEG', quality=JPEG_QUALITY, optimize=True)
            extension = '.jpg'
        else:
            # Save as PNG for transparency support
            img.save(output, format='PNG', optimize=True)
            extension = '.png'
        
        output.seek(0)
        return output, extension
        
    except Exception as e:
        print(f"Error optimizing image: {e}")
        return None, None


def validate_image_file(image_file):
    """
    Validate image file size and type
    Returns (is_valid, error_message)
    """
    if not image_file or not image_file.filename:
        return False, "No image file provided"
    
    # Check file size
    image_file.seek(0, 2)  # Seek to end
    file_size = image_file.tell()
    image_file.seek(0)  # Reset to beginning
    
    if file_size > MAX_FILE_SIZE:
        return False, f"Image file too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB"
    
    # Check file extension
    _, ext = os.path.splitext(image_file.filename)
    allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
    if ext.lower() not in allowed_extensions:
        return False, "Invalid image format. Allowed formats: JPG, PNG, GIF, BMP, WebP"
    
    return True, None


def get_conn():
    # Ensure the directory for the database exists
    db_dir = os.path.dirname(DB_PATH)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    # Ensure the upload folder exists and has proper permissions
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        print(f"Created upload folder: {UPLOAD_FOLDER}")
    
    # Ensure the folder is writable
    if not os.access(UPLOAD_FOLDER, os.W_OK):
        print(f"Warning: Upload folder {UPLOAD_FOLDER} is not writable")
    
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
            # Validate image file
            is_valid, error_message = validate_image_file(image_file)
            if not is_valid:
                flash(error_message)
                return render_template('add_tool.html')
            
            try:
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                
                # Optimize the image
                optimized_image, extension = optimize_image(image_file)
                if not optimized_image:
                    flash('Error processing image. Please try again.')
                    return render_template('add_tool.html')
                
                # Generate unique filename with correct extension
                unique_filename = generate_unique_filename(f"image{extension}")
                save_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                
                # Save the optimized image
                with open(save_path, 'wb') as f:
                    f.write(optimized_image.getvalue())
                
                # Store relative path for database
                image_path = os.path.join('images', unique_filename)
                print(f"Optimized image uploaded successfully: {unique_filename}")
                
            except Exception as e:
                print(f"Error uploading image: {e}")
                image_path = None
                flash('Error uploading image. Please try again.')
        with get_conn() as conn:
            c = conn.cursor()
            c.execute(
                "INSERT INTO tools (name, description, value, image_path) VALUES (?, ?, ?, ?)",
                (name, description, value, image_path),
            )
            conn.commit()
        return redirect(url_for('index'))
    return render_template('add_tool.html')


def delete_tool_image(image_path):
    """Delete the image file if it exists"""
    if image_path:
        try:
            # Convert relative path to absolute path
            full_path = os.path.join(app.config['UPLOAD_FOLDER'], os.path.basename(image_path))
            if os.path.exists(full_path):
                os.remove(full_path)
                print(f"Deleted image file: {full_path}")
        except Exception as e:
            print(f"Error deleting image file: {e}")


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
            # Get the image path before deleting the tool
            c.execute("SELECT image_path FROM tools WHERE id=?", (tool_id,))
            tool = c.fetchone()
            if tool and tool['image_path']:
                delete_tool_image(tool['image_path'])
            
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
        loans_raw = c.fetchall()
        
        # Calculate duration for each loan
        loans = []
        for loan in loans_raw:
            loan_dict = dict(loan)
            if loan_dict['returned_on'] and loan_dict['lent_on']:
                try:
                    lent_date = datetime.datetime.strptime(loan_dict['lent_on'], '%Y-%m-%d').date()
                    returned_date = datetime.datetime.strptime(loan_dict['returned_on'], '%Y-%m-%d').date()
                    duration_days = (returned_date - lent_date).days
                    if duration_days == 0:
                        loan_dict['duration'] = '1 day'
                    else:
                        loan_dict['duration'] = f'{duration_days + 1} days'
                except (ValueError, TypeError):
                    loan_dict['duration'] = 'Unknown'
            else:
                loan_dict['duration'] = '-'
            loans.append(loan_dict)
    
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
                # Validate image file
                is_valid, error_message = validate_image_file(image_file)
                if not is_valid:
                    flash(error_message)
                    return redirect(url_for('edit_tool', tool_id=tool_id))
                
                try:
                    # Get the old image path before updating
                    c.execute("SELECT image_path FROM tools WHERE id=?", (tool_id,))
                    old_tool = c.fetchone()
                    old_image_path = old_tool['image_path'] if old_tool else None
                    
                    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                    
                    # Optimize the image
                    optimized_image, extension = optimize_image(image_file)
                    if not optimized_image:
                        flash('Error processing image. Please try again.')
                        return redirect(url_for('edit_tool', tool_id=tool_id))
                    
                    # Generate unique filename with correct extension
                    unique_filename = generate_unique_filename(f"image{extension}")
                    save_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                    
                    # Save the optimized image
                    with open(save_path, 'wb') as f:
                        f.write(optimized_image.getvalue())
                    
                    # Store relative path for database
                    image_path = os.path.join('images', unique_filename)
                    print(f"Optimized image updated successfully: {unique_filename}")
                    
                    # Delete the old image if it exists
                    if old_image_path:
                        delete_tool_image(old_image_path)
                        
                except Exception as e:
                    print(f"Error updating image: {e}")
                    image_path = None
                    flash('Error updating image. Please try again.')
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


@app.route('/data/images/<filename>')
def serve_image(filename):
    """Serve images from the data directory"""
    from flask import send_from_directory
    data_dir = os.path.dirname(UPLOAD_FOLDER)
    return send_from_directory(data_dir, f'images/{filename}')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
