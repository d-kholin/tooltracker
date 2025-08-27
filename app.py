import os
import sqlite3
import datetime
import uuid
import secrets
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from PIL import Image
import io
from config import config
from auth import User, OIDCAuth, init_auth_db, create_or_update_user, auth_required

# Get configuration
config_name = os.environ.get('FLASK_ENV', 'default')
app_config = config[config_name]

app = Flask(__name__)
app.config.from_object(app_config)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

# Initialize OIDC authentication
oidc_auth = OIDCAuth(app)

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# Database initialization will be done after functions are defined

# Initialize databases
def get_conn():
    # Ensure the directory for the database exists
    db_dir = os.path.dirname(app.config['TOOLTRACKER_DB'])
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
    
    conn = sqlite3.connect(app.config['TOOLTRACKER_DB'])
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    # Ensure the upload folder exists and has proper permissions
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        print(f"Created upload folder: {app.config['UPLOAD_FOLDER']}")
    
    # Ensure the folder is writable
    if not os.access(app.config['UPLOAD_FOLDER'], os.W_OK):
        print(f"Warning: Upload folder {app.config['UPLOAD_FOLDER']} is not writable")
    
    with get_conn() as conn:
        c = conn.cursor()
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS tools (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                value REAL,
                image_path TEXT,
                created_by TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(created_by) REFERENCES users(id)
            )
            """
        )
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS people (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                contact_info TEXT,
                created_by TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(created_by) REFERENCES users(id)
            )
            """
        )
        # Ensure contact_info column exists for older databases
        try:
            c.execute("ALTER TABLE people ADD COLUMN contact_info TEXT")
        except sqlite3.OperationalError:
            pass
        
        # Ensure created_by columns exist for older databases
        try:
            c.execute("ALTER TABLE tools ADD COLUMN created_by TEXT")
        except sqlite3.OperationalError:
            pass
        try:
            c.execute("ALTER TABLE people ADD COLUMN created_by TEXT")
        except sqlite3.OperationalError:
            pass
        
        # Add composite unique constraint for people (name + created_by) to allow same names across different users
        try:
            c.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_people_name_user ON people (name, created_by)")
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
                lent_by TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(tool_id) REFERENCES tools(id),
                FOREIGN KEY(person_id) REFERENCES people(id),
                FOREIGN KEY(lent_by) REFERENCES users(id)
            )
            """
        )
        
        # Ensure lent_by column exists for older databases
        try:
            c.execute("ALTER TABLE loans ADD COLUMN lent_by TEXT")
        except sqlite3.OperationalError:
            pass
        
        conn.commit()

# Database initialization will be done in app context

# Add missing utility functions
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
        if original_width > app.config['MAX_IMAGE_DIMENSION'] or original_height > app.config['MAX_IMAGE_DIMENSION']:
            if original_width > original_height:
                new_width = app.config['MAX_IMAGE_DIMENSION']
                new_height = int(original_height * (app.config['MAX_IMAGE_DIMENSION'] / original_width))
            else:
                new_height = app.config['MAX_IMAGE_DIMENSION']
                new_width = int(original_width * (app.config['MAX_IMAGE_DIMENSION'] / original_height))
            
            # Resize the image
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            print(f"Resized image from {original_width}x{original_height} to {new_width}x{new_height}")
        
        # Save optimized image to bytes
        output = io.BytesIO()
        
        # Determine output format and save with optimization
        if img.format in ('JPEG', 'JPG') or img.mode == 'RGB':
            # Save as JPEG with compression
            img.save(output, format='JPEG', quality=app.config['JPEG_QUALITY'], optimize=True)
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
    
    if file_size > app.config['MAX_FILE_SIZE']:
        return False, f"Image file too large. Maximum size is {app.config['MAX_FILE_SIZE'] // (1024*1024)}MB"
    
    # Check file size
    _, ext = os.path.splitext(image_file.filename)
    allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
    if ext.lower() not in allowed_extensions:
        return False, "Invalid image format. Allowed formats: JPG, PNG, GIF, BMP, WebP"
    
    return True, None

# Authentication routes
@app.route('/login')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    # Generate state for CSRF protection
    state = secrets.token_urlsafe(32)
    session['oauth_state'] = state
    
    # Get authorization URL
    redirect_uri = url_for('oidc_callback', _external=True)
    auth_url = oidc_auth.get_authorization_url(redirect_uri, state)
    
    if not auth_url:
        flash('OIDC authentication not configured properly')
        return render_template('login.html', error='Authentication not configured')
    
    return redirect(auth_url)

@app.route('/oidc/callback')
def oidc_callback():
    # Verify state parameter
    state = session.get('oauth_state')
    if not state or state != request.args.get('state'):
        app.logger.error(f'Invalid state parameter. Expected: {state}, Got: {request.args.get("state")}')
        flash('Invalid state parameter')
        return redirect(url_for('login'))
    
    # Clear state from session
    session.pop('oauth_state', None)
    
    # Handle authorization response
    try:
        redirect_uri = url_for('oidc_callback', _external=True)
        app.logger.info(f'OIDC callback - redirect_uri: {redirect_uri}')
        app.logger.info(f'OIDC callback - request.url: {request.url}')
        
        token_data = oidc_auth.get_token(request.url, redirect_uri)
        
        if not token_data or 'access_token' not in token_data:
            app.logger.error(f'Token data missing access_token: {token_data}')
            flash('Failed to obtain access token')
            return redirect(url_for('login'))
        
        app.logger.info('Successfully obtained access token')
        
        # Get user information
        userinfo = oidc_auth.get_userinfo(token_data['access_token'])
        if not userinfo:
            app.logger.error('Failed to get user information from OIDC provider')
            flash('Failed to get user information')
            return redirect(url_for('login'))
        
        app.logger.info(f'User info received: {userinfo}')
        
        # Create or update user in database
        user = create_or_update_user(userinfo)
        if not user:
            app.logger.error('Failed to create user account in database')
            flash('Failed to create user account')
            return redirect(url_for('login'))
        
        # Log in the user
        login_user(user)
        flash(f'Welcome, {user.name}!')
        return redirect(url_for('index'))
        
    except Exception as e:
        app.logger.error(f'OIDC callback error: {e}')
        app.logger.error(f'Error type: {type(e).__name__}')
        import traceback
        app.logger.error(f'Traceback: {traceback.format_exc()}')
        flash('Authentication failed')
        return redirect(url_for('login'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out')
    return redirect(url_for('index'))

@app.route('/')
@auth_required
def index():
    return render_template('index.html')


@app.route('/api/tools', methods=['GET', 'POST'])
@auth_required
def api_tools():
    if request.method == 'POST':
        data = request.get_json(force=True)
        name = data.get('name', '').strip()
        if not name:
            return jsonify({'error': 'name required'}), 400
        with get_conn() as conn:
            c = conn.cursor()
            c.execute(
                "INSERT INTO tools (name, description, value, image_path, created_by) VALUES (?, '', 0, NULL, ?)",
                (name, current_user.id),
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
            SELECT t.id, t.name, t.description, t.value, t.image_path, p.name AS borrower, l.lent_on
            FROM tools t
            LEFT JOIN loans l ON t.id = l.tool_id AND l.returned_on IS NULL
            LEFT JOIN people p ON l.person_id = p.id
            WHERE t.created_by = ?
            ORDER BY t.id
            """,
            (current_user.id,)
        )
        tools = [dict(row) for row in c.fetchall()]
    return jsonify(tools)


@app.route('/add', methods=['GET', 'POST'])
@auth_required
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
                "INSERT INTO tools (name, description, value, image_path, created_by) VALUES (?, ?, ?, ?, ?)",
                (name, description, value, image_path, current_user.id),
            )
            conn.commit()
        return redirect(url_for('index'))
    return render_template('add_tool.html')


@app.route('/add_person', methods=['GET', 'POST'])
@auth_required
def add_person():
    if request.method == 'POST':
        name = request.form['name']
        contact_info = request.form.get('contact_info', '')
        
        # Debug: Print current user info
        print(f"Adding person: {name}, contact: {contact_info}, user: {current_user.id if current_user.is_authenticated else 'Not authenticated'}")
        
        with get_conn() as conn:
            c = conn.cursor()
            
            # Debug: Check what people already exist for this user
            c.execute("SELECT id, name FROM people WHERE created_by = ?", (current_user.id,))
            existing_people = c.fetchall()
            print(f"Existing people for user {current_user.id}: {[p['name'] for p in existing_people]}")
            
            try:
                c.execute(
                    "INSERT INTO people (name, contact_info, created_by) VALUES (?, ?, ?)",
                    (name, contact_info, current_user.id),
                )
                conn.commit()
                flash('Person added successfully!')
                print(f"Successfully added person: {name}")
                return redirect(url_for('people'))
            except sqlite3.IntegrityError as e:
                print(f"IntegrityError when adding person: {e}")
                flash('Person already exists')
            except Exception as e:
                print(f"Unexpected error when adding person: {e}")
                flash(f'Error adding person: {str(e)}')
        return render_template('add_person.html')
    return render_template('add_person.html')


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
@auth_required
def delete_tool(tool_id):
    with get_conn() as conn:
        c = conn.cursor()
        # Check if tool belongs to current user
        c.execute("SELECT id FROM tools WHERE id=? AND created_by=?", (tool_id, current_user.id))
        if not c.fetchone():
            flash('Tool not found or access denied')
            return redirect(url_for('index'))
        
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
@auth_required
def lend_tool(tool_id):
    if request.method == 'POST':
        person_id = request.form.get('person_id')
        lent_date = request.form.get('lent_date')
        
        # Validate date input
        if not lent_date:
            lent_date = datetime.date.today().isoformat()
        else:
            try:
                # Validate the date format
                datetime.datetime.strptime(lent_date, '%Y-%m-%d')
            except ValueError:
                flash('Invalid date format. Please use YYYY-MM-DD format.')
                return redirect(url_for('lend_tool', tool_id=tool_id))
        
        with get_conn() as conn:
            c = conn.cursor()
            # Check if tool belongs to current user
            c.execute("SELECT id FROM tools WHERE id=? AND created_by=?", (tool_id, current_user.id))
            if not c.fetchone():
                flash('Tool not found or access denied')
                return redirect(url_for('index'))
            
            c.execute(
                "SELECT COUNT(*) FROM loans WHERE tool_id=? AND returned_on IS NULL",
                (tool_id,),
            )
            if c.fetchone()[0] > 0:
                flash('Tool already lent out')
            else:
                c.execute("SELECT id FROM people WHERE id=? AND created_by=?", (person_id, current_user.id))
                row = c.fetchone()
                if not row:
                    flash('Person not found or access denied')
                else:
                    c.execute(
                        "INSERT INTO loans (tool_id, person_id, lent_on, lent_by) VALUES (?, ?, ?, ?)",
                        (tool_id, person_id, lent_date, current_user.id),
                    )
                    conn.commit()
                    flash('Tool lent successfully!')
        return redirect(url_for('index'))
    with get_conn() as conn:
        c = conn.cursor()
        c.execute("SELECT id, name FROM people WHERE created_by = ? ORDER BY name", (current_user.id,))
        people = [dict(row) for row in c.fetchall()]
        if not people:
            flash('No people available. Add a person first.')
            return redirect(url_for('people'))
    return render_template('lend_tool.html', tool_id=tool_id, people=people, today_date=datetime.date.today().isoformat())


@app.route('/return/<int:tool_id>', methods=['POST'])
@auth_required
def return_tool(tool_id):
    with get_conn() as conn:
        c = conn.cursor()
        # Check if tool belongs to current user
        c.execute("SELECT id FROM tools WHERE id=? AND created_by=?", (tool_id, current_user.id))
        if not c.fetchone():
            flash('Tool not found or access denied')
            return redirect(url_for('index'))
        
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


@app.route('/edit_loan/<int:loan_id>', methods=['GET', 'POST'])
@auth_required
def edit_loan(loan_id):
    if request.method == 'POST':
        lent_date = request.form.get('lent_date')
        returned_date = request.form.get('returned_date')
        
        # Validate date inputs
        try:
            if lent_date:
                datetime.datetime.strptime(lent_date, '%Y-%m-%d')
            if returned_date:
                datetime.datetime.strptime(returned_date, '%Y-%m-%d')
        except ValueError:
            flash('Invalid date format. Please use YYYY-MM-DD format.')
            return redirect(url_for('edit_loan', loan_id=loan_id))
        
        with get_conn() as conn:
            c = conn.cursor()
            # Check if loan belongs to current user's tools
            c.execute(
                """
                SELECT l.id, l.tool_id, t.name as tool_name 
                FROM loans l 
                JOIN tools t ON l.tool_id = t.id 
                WHERE l.id=? AND t.created_by=?
                """,
                (loan_id, current_user.id)
            )
            loan = c.fetchone()
            if not loan:
                flash('Loan not found or access denied')
                return redirect(url_for('index'))
            
            # Update the loan dates
            if lent_date and returned_date:
                c.execute(
                    "UPDATE loans SET lent_on=?, returned_on=? WHERE id=?",
                    (lent_date, returned_date, loan_id)
                )
            elif lent_date:
                c.execute(
                    "UPDATE loans SET lent_on=? WHERE id=?",
                    (lent_date, loan_id)
                )
            elif returned_date:
                c.execute(
                    "UPDATE loans SET returned_on=? WHERE id=?",
                    (returned_date, loan_id)
                )
            
            conn.commit()
            flash('Loan updated successfully!')
            return redirect(url_for('tool_detail', tool_id=loan['tool_id']))
    
    # GET request - show edit form
    with get_conn() as conn:
        c = conn.cursor()
        c.execute(
            """
            SELECT l.id, l.lent_on, l.returned_on, l.tool_id, t.name as tool_name, p.name as person_name
            FROM loans l 
            JOIN tools t ON l.tool_id = t.id 
            JOIN people p ON l.person_id = p.id
            WHERE l.id=? AND t.created_by=?
            """,
            (loan_id, current_user.id)
        )
        loan = c.fetchone()
        if not loan:
            flash('Loan not found or access denied')
            return redirect(url_for('index'))
    
    return render_template('edit_loan.html', loan=loan)


@app.route('/people', methods=['GET'])
@auth_required
def people():
    # Debug: Print current user info
    print(f"Fetching people for user: {current_user.id if current_user.is_authenticated else 'Not authenticated'}")
    
    with get_conn() as conn:
        c = conn.cursor()
        c.execute("SELECT id, name, contact_info FROM people WHERE created_by = ? ORDER BY name", (current_user.id,))
        people = c.fetchall()
        print(f"Found {len(people)} people for user {current_user.id}")
        for person in people:
            print(f"  - {person['name']} (ID: {person['id']})")
    
    return render_template('people.html', people=people)


@app.route('/people/<int:person_id>/delete', methods=['POST'])
@auth_required
def delete_person(person_id):
    with get_conn() as conn:
        c = conn.cursor()
        # Check if person belongs to current user
        c.execute("SELECT id FROM people WHERE id=? AND created_by=?", (person_id, current_user.id))
        if not c.fetchone():
            flash('Person not found or access denied')
            return redirect(url_for('people'))
        
        c.execute("SELECT COUNT(*) FROM loans WHERE person_id=?", (person_id,))
        if c.fetchone()[0] > 0:
            flash('Cannot delete person: existing loan records')
        else:
            c.execute("DELETE FROM people WHERE id=?", (person_id,))
            conn.commit()
    return redirect(url_for('people'))


@app.route('/people/<int:person_id>')
@auth_required
def person_detail(person_id):
    with get_conn() as conn:
        c = conn.cursor()
        c.execute("SELECT id, name, contact_info FROM people WHERE id=? AND created_by=?", (person_id, current_user.id))
        person = c.fetchone()
        if not person:
            return redirect(url_for('people'))
        
        # Get all loans for this person
        c.execute(
            """
            SELECT t.name AS tool_name, l.lent_on, l.returned_on,
                   t.id as tool_id, t.description, t.value
            FROM loans l
            JOIN tools t ON l.tool_id = t.id
            WHERE l.person_id=?
            ORDER BY l.lent_on DESC
            """,
            (person_id,),
        )
        loans_raw = c.fetchall()
        
        # Calculate duration for each loan
        loans = []
        for loan in loans_raw:
            loan_dict = dict(loan)
            if loan_dict['lent_on']:
                try:
                    lent_date = datetime.datetime.strptime(loan_dict['lent_on'], '%Y-%m-%d').date()
                    if loan_dict['returned_on']:
                        # Calculate duration for returned tools
                        returned_date = datetime.datetime.strptime(loan_dict['returned_on'], '%Y-%m-%d').date()
                        duration_days = (returned_date - lent_date).days
                        if duration_days == 0:
                            loan_dict['duration'] = '1 day'
                        else:
                            loan_dict['duration'] = f'{duration_days + 1} days'
                    else:
                        # Calculate current duration for tools still out
                        current_date = datetime.date.today()
                        duration_days = (current_date - lent_date).days
                        if duration_days == 0:
                            loan_dict['duration'] = '1 day (currently out)'
                        else:
                            loan_dict['duration'] = f'{duration_days + 1} days (currently out)'
                except (ValueError, TypeError):
                    loan_dict['duration'] = 'Unknown'
            else:
                loan_dict['duration'] = '-'
            loans.append(loan_dict)
        
    return render_template('person_loans.html', person=person, loans=loans)


@app.route('/people/<int:person_id>/edit', methods=['GET', 'POST'])
@auth_required
def edit_person(person_id):
    with get_conn() as conn:
        c = conn.cursor()
        # Check if person belongs to current user
        c.execute("SELECT id FROM people WHERE id=? AND created_by=?", (person_id, current_user.id))
        if not c.fetchone():
            flash('Person not found or access denied')
            return redirect(url_for('people'))
        
        if request.method == 'POST':
            name = request.form['name']
            contact_info = request.form.get('contact_info', '')
            try:
                c.execute(
                    "UPDATE people SET name=?, contact_info=? WHERE id=? AND created_by=?",
                    (name, contact_info, person_id, current_user.id),
                )
                conn.commit()
                return redirect(url_for('people'))
            except sqlite3.IntegrityError:
                flash('Person already exists')
        c.execute("SELECT id, name, contact_info FROM people WHERE id=? AND created_by=?", (person_id, current_user.id))
        person = c.fetchone()
        if not person:
            return redirect(url_for('people'))
    return render_template('edit_person.html', person=person)


@app.route('/report')
@auth_required
def report():
    with get_conn() as conn:
        c = conn.cursor()
        c.execute(
            """
            SELECT p.id AS person_id, p.name, COUNT(l.id) AS count
            FROM people p
            LEFT JOIN loans l ON p.id = l.person_id AND l.returned_on IS NULL
            WHERE p.created_by = ?
            GROUP BY p.id, p.name
            ORDER BY p.name
            """,
            (current_user.id,)
        )
        rows = c.fetchall()
    return render_template('report.html', rows=rows)


@app.route('/report/overdue')
@auth_required
def overdue_report():
    with get_conn() as conn:
        c = conn.cursor()
        # Get tools out longer than 30 days
        c.execute(
            """
            SELECT t.id, t.name, t.description, t.value, t.image_path, 
                   p.name AS borrower, p.contact_info, l.lent_on,
                   (julianday('now') - julianday(l.lent_on)) AS days_out
            FROM tools t
            JOIN loans l ON t.id = l.tool_id AND l.returned_on IS NULL
            JOIN people p ON l.person_id = p.id
            WHERE t.created_by = ? AND (julianday('now') - julianday(l.lent_on)) > 30
            ORDER BY days_out DESC
            """,
            (current_user.id,)
        )
        overdue_tools = c.fetchall()
        
        # Calculate summary statistics
        total_overdue = len(overdue_tools)
        total_value_overdue = sum(tool['value'] or 0 for tool in overdue_tools)
        avg_days_overdue = sum(tool['days_out'] for tool in overdue_tools) / total_overdue if total_overdue > 0 else 0
        
    return render_template('overdue_report.html', 
                         overdue_tools=overdue_tools,
                         total_overdue=total_overdue,
                         total_value_overdue=total_value_overdue,
                         avg_days_overdue=round(avg_days_overdue, 1))


@app.route('/report/financial')
@auth_required
def financial_report():
    with get_conn() as conn:
        c = conn.cursor()
        
        # Get total inventory value
        c.execute(
            """
            SELECT COUNT(*) as total_tools, 
                   COALESCE(SUM(value), 0) as total_value,
                   COALESCE(AVG(value), 0) as avg_value
            FROM tools 
            WHERE created_by = ?
            """,
            (current_user.id,)
        )
        inventory_stats = c.fetchone()
        
        # Get value of tools currently lent out
        c.execute(
            """
            SELECT COUNT(*) as tools_lent_out,
                   COALESCE(SUM(t.value), 0) as value_lent_out
            FROM tools t
            JOIN loans l ON t.id = l.tool_id AND l.returned_on IS NULL
            WHERE t.created_by = ?
            """,
            (current_user.id,)
        )
        lent_stats = c.fetchone()
        
        # Get value of tools available (not lent out)
        available_value = inventory_stats['total_value'] - lent_stats['value_lent_out']
        available_tools = inventory_stats['total_tools'] - lent_stats['tools_lent_out']
        
        # Get tools by value ranges for distribution analysis
        c.execute(
            """
            SELECT 
                CASE 
                    WHEN value IS NULL OR value = 0 THEN 'No Value Set'
                    WHEN value <= 50 THEN '$0 - $50'
                    WHEN value <= 100 THEN '$51 - $100'
                    WHEN value <= 250 THEN '$101 - $250'
                    WHEN value <= 500 THEN '$251 - $500'
                    WHEN value <= 1000 THEN '$501 - $1000'
                    ELSE '$1000+'
                END as value_range,
                COUNT(*) as count,
                COALESCE(SUM(value), 0) as total_value
            FROM tools 
            WHERE created_by = ?
            GROUP BY 
                CASE 
                    WHEN value IS NULL OR value = 0 THEN 'No Value Set'
                    WHEN value <= 50 THEN '$0 - $50'
                    WHEN value <= 100 THEN '$51 - $100'
                    WHEN value <= 250 THEN '$101 - $250'
                    WHEN value <= 500 THEN '$251 - $500'
                    WHEN value <= 1000 THEN '$501 - $1000'
                    ELSE '$1000+'
                END
            ORDER BY 
                CASE value_range
                    WHEN 'No Value Set' THEN 0
                    WHEN '$0 - $50' THEN 1
                    WHEN '$51 - $100' THEN 2
                    WHEN '$101 - $250' THEN 3
                    WHEN '$251 - $500' THEN 4
                    WHEN '$501 - $1000' THEN 5
                    ELSE 6
                END
            """,
            (current_user.id,)
        )
        value_distribution = c.fetchall()
        
    return render_template('financial_report.html',
                         inventory_stats=inventory_stats,
                         lent_stats=lent_stats,
                         available_value=available_value,
                         available_tools=available_tools,
                         value_distribution=value_distribution)





@app.route('/tool/<int:tool_id>')
@auth_required
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
            WHERE t.id = ? AND t.created_by = ?
            """,
            (tool_id, current_user.id),
        )
        tool = c.fetchone()
        if not tool:
            return redirect(url_for('index'))
        
        # Get lending history
        c.execute(
            """
            SELECT l.id, l.lent_on, l.returned_on, p.name AS person_name, p.contact_info
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
            if loan_dict['lent_on']:
                try:
                    lent_date = datetime.datetime.strptime(loan_dict['lent_on'], '%Y-%m-%d').date()
                    if loan_dict['returned_on']:
                        # Calculate duration for returned tools
                        returned_date = datetime.datetime.strptime(loan_dict['returned_on'], '%Y-%m-%d').date()
                        duration_days = (returned_date - lent_date).days
                        if duration_days == 0:
                            loan_dict['duration'] = '1 day'
                        else:
                            loan_dict['duration'] = f'{duration_days + 1} days'
                    else:
                        # Calculate current duration for tools still out
                        current_date = datetime.date.today()
                        duration_days = (current_date - lent_date).days
                        if duration_days == 0:
                            loan_dict['duration'] = '1 day (currently out)'
                        else:
                            loan_dict['duration'] = f'{duration_days + 1} days (currently out)'
                except (ValueError, TypeError):
                    loan_dict['duration'] = 'Unknown'
            else:
                loan_dict['duration'] = '-'
            loans.append(loan_dict)
    
    return render_template('tool_detail.html', tool=tool, loans=loans)


@app.route('/edit/<int:tool_id>', methods=['GET', 'POST'])
@auth_required
def edit_tool(tool_id):
    with get_conn() as conn:
        c = conn.cursor()
        # Check if tool belongs to current user
        c.execute("SELECT id FROM tools WHERE id=? AND created_by=?", (tool_id, current_user.id))
        if not c.fetchone():
            flash('Tool not found or access denied')
            return redirect(url_for('index'))
        
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
        c.execute("SELECT * FROM tools WHERE id=? AND created_by=?", (tool_id, current_user.id))
        tool = c.fetchone()
        if not tool:
            flash('Tool not found or access denied')
            return redirect(url_for('index'))
    return render_template('edit_tool.html', tool=tool)


@app.route('/data/images/<filename>')
@auth_required
def serve_image(filename):
    """Serve images from the data directory"""
    from flask import send_from_directory
    data_dir = os.path.dirname(app.config['UPLOAD_FOLDER'])
    return send_from_directory(data_dir, f'images/{filename}')


if __name__ == '__main__':
    # Initialize databases within app context
    with app.app_context():
        init_auth_db(app)
        init_db()
    
    app.run(host='0.0.0.0', port=5000)
