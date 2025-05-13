from flask import Flask, render_template, request, jsonify, redirect, url_for,session, flash

from datetime import date
from datetime import datetime
import mysql.connector
import os

app = Flask(__name__)

app.secret_key = '1234'

# Database Configuration
db_config = {
   "host":os.getenv("DB_HOST"),
    "user":os.getenv("DB_USER"),
    "password":os.getenv("DB_PASSWORD"),
    "database":os.getenv("DB_NAME"),
    "port":int(os.getenv("DB_PORT", 3306))
}

def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")
        return None

def initialize_database():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            with open('schema.sql', 'r') as f:
                sql_script = f.read()
            
            # Execute each statement separately
            for statement in sql_script.strip().split(';'):
                if statement.strip():
                    cursor.execute(statement + ';')
            conn.commit()
            print("Database initialized successfully.")
        except mysql.connector.Error as err:
            print(f"Error executing SQL script: {err}")
        finally:
            cursor.close()
            conn.close()
    else:
        print("Could not establish database connection.")
       
initialize_database()  # Only for setup; remove in production

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/home')
def home():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Fetch the carousel items
    cursor.execute("SELECT * FROM carousel_item")
    carousel_items = cursor.fetchall()

    # Fetch the 5 most recent resources
    cursor.execute("""
        SELECT r.Resource_id, rt.ResourceType_name AS type, r.Link, c.Name AS contributor
        FROM resources r
        JOIN resourcetypes rt ON r.ResourceType_id = rt.ResourceType_id
        JOIN contributors c ON r.Contributor_id = c.Contributor_id
        LIMIT 5
    """)
    resources = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template('index.html', carousel_items=carousel_items, resources=resources)

from flask import session  # Add this import if not already


@app.route('/submit', methods=['POST'])
def submit_news():
    try:
        title = request.form.get('title')
        description = request.form.get('description')
        category = request.form.get('category')
       

        if not title or not description or not category:
            return jsonify({'error': 'Title, Description, Category, and Requested By are required!'}), 400

        user_id = session.get('user_id')  # Fetch logged-in user's ID
        username = session.get('username')

        if not user_id:
            return jsonify({'error': 'User not authenticated'}), 403

        conn = get_db_connection()
        cursor = conn.cursor()

        # Insert the news request
        cursor.execute("""
            INSERT INTO news_requests (title, content, category, requested_by, status)
            VALUES (%s, %s, %s, %s,'pending')
        """, (title, description, category, user_id))

        news_request_id = cursor.lastrowid

        # Log the activity with actual user ID
        cursor.execute("""
            INSERT INTO activity_log (user_id, action_type, target_table, target_id, details)
            VALUES (%s, 'request', 'news_requests', %s, %s)
        """, (user_id, news_request_id, f"News request submitted by user_id={user_id}"))

        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for('home'))

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    except Exception as e:
        return jsonify({'error': f"Something went wrong: {str(e)}"}), 500

@app.route('/get-news', methods=['GET'])  # Changed from /get_news
def get_news():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM news ORDER BY created_at DESC LIMIT 20")  # Fixed column name
        news_items = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify(news_items), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/news')
def news_page():
    return render_template('news.html')

@app.route('/admin/news_requests')
def view_news_requests():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM news_requests WHERE status = 'pending'")  # Only get 'pending' news requests
    requests = cursor.fetchall()

    # Get the latest 20 approved news
    cursor.execute("SELECT title, content, category, DATE_FORMAT(created_at, '%Y-%m-%d %H:%i:%s') AS created_at FROM news ORDER BY created_at DESC LIMIT 20")
    approved_news = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('admin_news.html', requests=requests, approved_news=approved_news)
from flask import session  # Ensure session is imported
from datetime import datetime

@app.route('/admin/handle_news/<int:request_id>', methods=['POST'])
def handle_news_request(request_id):
    action = request.form.get('action')

    if not action:
        return redirect(url_for('admin_news', status='error'))

    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Admin not authenticated'}), 403

    conn = get_db_connection()
    cursor = conn.cursor()

    if action == 'approve':
        cursor.execute("SELECT title, content, category, requested_by FROM news_requests WHERE request_id = %s", (request_id,))
        news = cursor.fetchone()
        if news:
            title, content, category, requested_by = news
            cursor.execute("""
                INSERT INTO news (title, content, category, created_at)
                VALUES (%s, %s, %s, %s)
            """, (title, content, category, date.today()))

            # Get the new news ID
            news_id = cursor.lastrowid

            # Update the request status
            cursor.execute("UPDATE news_requests SET status = 'accepted' WHERE request_id = %s", (request_id,))

            # Log the activity
            cursor.execute("""
                INSERT INTO activity_log (user_id, action_type, target_table, target_id, details)
                VALUES (%s, 'create', 'news', %s, %s)
            """, (user_id, news_id, f"News approved from request {request_id}: '{title}' by {requested_by}"))

    elif action == 'reject':
        cursor.execute("SELECT title, requested_by FROM news_requests WHERE request_id = %s", (request_id,))
        result = cursor.fetchone()
        if result:
            title, requested_by = result
            cursor.execute("UPDATE news_requests SET status = 'rejected' WHERE request_id = %s", (request_id,))

            # Log the activity as an 'update'
            cursor.execute("""
                INSERT INTO activity_log (user_id, action_type, target_table, target_id, details)
                VALUES (%s, 'update', 'news_requests', %s, %s)
            """, (user_id, request_id, f"News request rejected: '{title}' by {requested_by}"))

    else:
        conn.close()
        return redirect(url_for('admin_news', status='error'))

    conn.commit()
    conn.close()

    return redirect(url_for('admin_news', status='accepted' if action == 'approve' else 'rejected'))

@app.route('/admin/news')
def admin_news():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Get pending requests (only if there are any)
    cursor.execute("SELECT * FROM news_requests WHERE status = 'pending'")
    requests = cursor.fetchall()

    # Get the latest 20 approved news
    cursor.execute("SELECT title, content, category, DATE_FORMAT(created_at, '%Y-%m-%d %H:%i:%s') AS created_at FROM news ORDER BY created_at DESC LIMIT 20")
    approved_news = cursor.fetchall()

    conn.close()

    # Render the page with both pending requests and approved news
    return render_template('admin_news.html', requests=requests, approved_news=approved_news)

@app.route('/get-events')
def get_events():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT b.name AS building, b.latitude, b.longitude, e.event_name
        FROM buildings b
        LEFT JOIN events e ON b.id = e.building_id
    """)
    rows = cursor.fetchall()

    # Group events by building
    buildings = {}
    for row in rows:
        key = row['building']
        if key not in buildings:
            buildings[key] = {
                'name': key,
                'coord': [row['latitude'], row['longitude']],
                'events': []
            }
        if row['event_name']:
            buildings[key]['events'].append(row['event_name'])

    return jsonify(list(buildings.values()))

@app.route('/add-event', methods=['GET', 'POST'])
def add_event():
    db = get_db_connection()
    cursor = db.cursor()

    if request.method == 'POST':
        event_name = request.form['event_name']
        building_id = request.form.get('building_id') or None

        sql = "INSERT INTO events (event_name, building_id) VALUES (%s, %s)"
        values = (event_name, building_id if building_id else None)

        try:
            cursor.execute(sql, values)
            db.commit()

            event_id = cursor.lastrowid  # Get the inserted event ID

            user_id = session.get('user_id')
            if not user_id:
                flash("User not authenticated. Event was added but not logged.")
            else:
                # Log the activity
                cursor.execute("""
                    INSERT INTO activity_log (user_id, action_type, target_table, target_id, details)
                    VALUES (%s, 'create', 'events', %s, %s)
                """, (
                    user_id,
                    event_id,
                    f"Event '{event_name}' added by user_id={user_id}"
                ))
                db.commit()

            flash('Event added successfully!')

        except mysql.connector.Error as err:
            db.rollback()
            flash(f"Error: {err}")

        return redirect(url_for('add_event'))

    # Fetch buildings for dropdown
    cursor.execute("SELECT id, name FROM buildings")
    buildings = cursor.fetchall()

    return render_template('add_event.html', buildings=buildings)

@app.route('/activity_log')
def activity_log():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM activity_log ORDER BY timestamp DESC")

        activity_logs = cursor.fetchall()
        return render_template('activity_log.html', activity_logs=activity_logs)
    except Exception as e:
        print(f"Error fetching activity logs: {e}")
        return render_template('activity_log.html', activity_logs=[])

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', role=session.get('role'))


#Reema's app.py

@app.route('/login')
def login():
    return render_template("SignIn.html")

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json(force=True)
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    passing_date = data.get('passing_date')
    branch = data.get('branch')
    role = data.get('role')

    if not all([name, email, password, passing_date, branch, role]):
        return jsonify({'error': 'All fields are required'}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT email FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            return jsonify({'error': 'Email already registered'}), 409
            
        cursor.execute(
            "INSERT INTO users (username, email, password, passing_date, branch, role) VALUES (%s, %s, %s, %s, %s, %s)",
            (name, email, password, passing_date, branch, role)
        )
        conn.commit()
        return jsonify({'message': 'Signup successful!'}), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/signin', methods=['POST'])
def signin():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    is_guest = data.get('is_guest', False)

    if not email or not password:
        return jsonify({'error': 'Email and Password required'}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        if is_guest:
            # Create a guest session without database checks
            session['user_id'] = 0
            session['username'] = 'Guest'
            session['role'] = 'guest'
            session['is_guest'] = True
            return jsonify({'message': 'Welcome guest!', 'is_guest': True}), 200

        # Check current users first
        cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
        user = cursor.fetchone()

        if user:
            # Check if user has graduated
            if user['passing_date']:
                user_passing_date = user['passing_date']
                if isinstance(user_passing_date, str):
                    user_passing_date = datetime.strptime(user_passing_date, '%Y-%m-%d').date()
    
                if user_passing_date <= date.today():
                # Move to Alumnae table
                    cursor.execute("""  
                        INSERT INTO alumnae 
                        (id, name, email, password, passing_date, branch, role)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (
                        user['user_id'], user['username'], user['email'], user['password'],
                        user['passing_date'], user['branch'], user['role']
                    ))
                    cursor.execute("DELETE FROM users WHERE id = %s", (user['user_id'],))
                    conn.commit()
                
                    session['user_id'] = user['user_id']
                    session['name'] = user['username']
                    session['role'] = 'guest'
                    session['is_guest'] = True
                    return jsonify({
                    'error': 'Your account has expired. Please use Guest Login.'
                    }), 403

            
            # Current active student
            session['user_id'] = user['user_id']
            session['name'] = user['username']
            session['role'] = user['role']
            session['is_guest'] = False
            # In the successful login block (around line 200), modify the return statement:
            return jsonify({
                'message': f"Welcome {user['username']}!",
                'is_guest': False,
                'user': {
                    'name': user['username'],
                    'role': user['role'],
                    'branch': user.get('branch', ''),
                    'year': user.get('year', '')
                }
            }), 200

        # Check if user is in Alumnae table
        cursor.execute("SELECT * FROM alumnae WHERE email = %s AND password = %s", (email, password))
        alum = cursor.fetchone()
        
        if alum:
            session['user_id'] = alum['id']
            session['name'] = alum['name']
            session['role'] = 'guest'
            session['is_guest'] = True
            return jsonify({
                'message': f"Welcome {alum['name']}! (Guest access)",
                'is_guest': True
            }), 200

        return jsonify({'error': 'Invalid credentials'}), 401

    except Exception as e:
        print(f"Login error: {str(e)}")  # Debug logging
        return jsonify({'error': 'Login failed. Please try again.'}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/resource', methods=['GET'])
def resources():
    return render_template('Resources.html')  # or jsonify() if returning JSON


@app.route('/search_resource', methods=['POST'])
def search_resource():
    try:
        data = request.get_json()
        if not data:
            print("No JSON data received")
            return jsonify({'error': 'No data received'}), 400

        year = data.get('year')
        domain = data.get('domain')

        print(f"Received search request - Year: {year}, Domain: {domain}")  # Debug log

        if not year or not domain:
            print("Missing year or domain")
            return jsonify({'error': 'Year and Domain are required!'}), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT rt.ResourceType_name AS ResourceType, r.Link
            FROM resources r
            JOIN contributors c ON r.Contributor_id = c.Contributor_id
            JOIN domains d ON r.Domain_id = d.Domain_id
            JOIN resourcetypes rt ON r.ResourceType_id = rt.ResourceType_id
            WHERE c.Year = %s AND d.Domain_name = %s
        """, (year, domain))

        rows = cursor.fetchall()
        print(f"Found {len(rows)} resources")  # Debug log
        
        formatted_results = [
            {'ResourceType': row['ResourceType'], 'Link': row['Link']}
            for row in rows
        ]

        return jsonify(formatted_results), 200

    except Exception as e:
        print(f"Search error: {str(e)}")
        return jsonify({'error': "Failed to fetch resources. Please try again later."}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

@app.route('/add_resource', methods=['POST'])
def add_resource():
    if session.get('is_guest'):
        return jsonify({'error': 'Guests are not allowed to contribute resources.'}), 403

    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Please login to contribute resources.'}), 401

    try:
        data = request.get_json()
        name = data.get('name')
        year = data.get('year')
        domain = data.get('domain')
        resources = data.get('resources', [])

        if not name or not year or not domain or not resources:
            return jsonify({'error': 'Missing required fields!'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Verify domain is approved
        cursor.execute("""
            SELECT d.Domain_id 
            FROM domains d
            LEFT JOIN domain_requests dr ON d.Domain_name = dr.domain_name
            WHERE d.Domain_name = %s AND (dr.status IS NULL OR dr.status = 'approved')
        """, (domain,))
        domain_result = cursor.fetchone()

        if not domain_result:
            return jsonify({
                'error': 'This domain is not yet approved. Please wait for admin approval.',
                'requires_approval': True
            }), 400

        # Handle contributor
        cursor.execute("SELECT Contributor_id FROM contributors WHERE Name=%s AND Year=%s", (name, year))
        contributor = cursor.fetchone()
        if contributor:
            contributor_id = contributor[0]
        else:
            cursor.execute("INSERT INTO contributors (Name, Year) VALUES (%s, %s)", (name, year))
            contributor_id = cursor.lastrowid

        # Handle domain
        cursor.execute("SELECT Domain_id FROM domains WHERE Domain_name=%s", (domain,))
        domain_result = cursor.fetchone()
        if domain_result:
            domain_id = domain_result[0]
        else:
            cursor.execute("INSERT INTO domains (Domain_name) VALUES (%s)", (domain,))
            domain_id = cursor.lastrowid

        # Process each resource
        for resource in resources:
            r_type = resource.get('type')
            r_link = resource.get('link')
            if not r_type or not r_link:
                continue

            # Handle resource type
            cursor.execute("SELECT ResourceType_id FROM resourcetypes WHERE ResourceType_name=%s", (r_type,))
            type_result = cursor.fetchone()
            if type_result:
                type_id = type_result[0]
            else:
                cursor.execute("INSERT INTO resourcetypes (ResourceType_name) VALUES (%s)", (r_type,))
                type_id = cursor.lastrowid

            # Insert resource
            cursor.execute(
                "INSERT INTO resources (Contributor_id, Domain_id, ResourceType_id, Link) VALUES (%s, %s, %s, %s)",
                (contributor_id, domain_id, type_id, r_link)
            )
            resource_id = cursor.lastrowid

            # Log activity for each resource added
            cursor.execute("""
                INSERT INTO activity_log (user_id, action_type, target_table, target_id, details)
                VALUES (%s, 'create', 'Resources', %s, %s)
            """, (
                user_id,
                resource_id,
                f"Resource added by user_id={user_id} (Contributor: {name}, Year: {year}, Domain: {domain}, Type: {r_type})"
            ))

        conn.commit()
        return jsonify({'message': 'Resources added successfully!'}), 200

    except Exception as e:
        conn.rollback()
        print(f"Resource addition error: {str(e)}")
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/check_session')
def check_session():
    if 'user_id' in session:
        return jsonify({
            'logged_in': True,
            'user': {
                'name': session.get('name'),
                'role': session.get('role'),
                'branch': session.get('branch', ''),
                'year': session.get('year', '')
            }
        })
    return jsonify({'logged_in': False})

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('home'))

@app.route('/get_domains')
def get_domains():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT Domain_name FROM domains")
        domains = [row[0] for row in cursor.fetchall()]
        return jsonify(domains)
    except Exception as e:
        print(f"Error fetching domains: {str(e)}")
        return jsonify([])
    finally:
        cursor.close()
        conn.close()

@app.route('/add_domain', methods=['POST'])
def add_domain():
    if session.get('is_guest'):
        return jsonify({'error': 'Guests cannot add domains'}), 403

    data = request.get_json()
    domain = data.get('domain')
    user_id = session.get('user_id')
    user_role = session.get('role')

    if not domain:
        return jsonify({'error': 'Domain name required'}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        if user_role == 'admin':
            # Admin directly adds domain
            cursor.execute("INSERT INTO domains (Domain_name) VALUES (%s)", (domain,))
            domain_id = cursor.lastrowid

            # Log the creation activity
            cursor.execute("""
                INSERT INTO activity_log (user_id, action_type, target_table, target_id, details)
                VALUES (%s, 'create', 'Domains', %s, %s)
            """, (user_id, domain_id, f"Admin added domain '{domain}'"))

            conn.commit()
            return jsonify({'message': 'Domain added successfully'}), 200

        else:
            # Non-admin submits a domain request
            cursor.execute("""
                INSERT INTO domain_requests (domain_name, requested_by) VALUES (%s, %s)
            """, (domain, user_id))
            request_id = cursor.lastrowid

            # Log the request activity
            cursor.execute("""
                INSERT INTO activity_log (user_id, action_type, target_table, target_id, details)
                VALUES (%s, 'request', 'domain_requests', %s, %s)
            """, (user_id, request_id, f"User requested domain '{domain}'"))

            conn.commit()
            return jsonify({'message': 'Your request has been sent to admin'}), 200

    except mysql.connector.IntegrityError:
        return jsonify({'message': 'Domain already exists'}), 200
    except Exception as e:
        print(f"Error handling domain request: {str(e)}")
        return jsonify({'error': 'Failed to process request'}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/admin/handle_domain/<int:request_id>', methods=['POST'])
def handle_domain_request(request_id):
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    user_id = session.get('user_id')  # Admin's user ID for logging

    if not user_id:
        return jsonify({'error': 'User not authenticated'}), 403

    action = request.form.get('action')

    if not action:
        return jsonify({'error': 'Action required'}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT domain_name FROM domain_requests WHERE request_id = %s", (request_id,))
        request_data = cursor.fetchone()
        
        if not request_data:
            return jsonify({'error': 'Request not found'}), 404

        domain_name = request_data['domain_name']

        if action == 'approve':
            # Add to domains table if not exists
            cursor.execute("""
                INSERT INTO domains (Domain_name)
                SELECT %s FROM DUAL
                WHERE NOT EXISTS (
                    SELECT 1 FROM domains WHERE Domain_name = %s
                )
            """, (domain_name, domain_name))
            
            # Update any resources waiting for this domain
            cursor.execute("""
                UPDATE resources r
                JOIN domains d ON r.Domain_id = d.Domain_id
                SET r.Domain_id = (
                    SELECT Domain_id FROM domains WHERE Domain_name = %s LIMIT 1
                )
                WHERE d.Domain_name = %s
            """, (domain_name, domain_name))
            
            cursor.execute("UPDATE domain_requests SET status = 'approved' WHERE request_id = %s", (request_id,))

            # Log activity
            cursor.execute("""
                INSERT INTO activity_log (user_id, action_type, target_table, target_id, details)
                VALUES (%s, 'update', 'domain_requests', %s, %s)
            """, (user_id, request_id, f"Domain request '{domain_name}' approved by admin (user_id={user_id})"))

        elif action == 'reject':
            cursor.execute("UPDATE domain_requests SET status = 'rejected' WHERE request_id = %s", (request_id,))
            
            cursor.execute("""
                DELETE r FROM resources r
                JOIN domains d ON r.Domain_id = d.Domain_id
                WHERE d.Domain_name = %s
            """, (domain_name,))

            # Log activity
            cursor.execute("""
                INSERT INTO activity_log (user_id, action_type, target_table, target_id, details)
                VALUES (%s, 'update', 'domain_requests', %s, %s)
            """, (user_id, request_id, f"Domain request '{domain_name}' rejected by admin (user_id={user_id})"))

        conn.commit()
        return jsonify({'message': f'Request {action}d successfully'}), 200

    except Exception as e:
        conn.rollback()
        print(f"Error handling domain request: {str(e)}")
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/cleanup_pending_domains', methods=['POST'])
def cleanup_pending_domains():
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    user_id = session.get('user_id')  # Fetch the admin's user ID

    if not user_id:
        return jsonify({'error': 'User not authenticated'}), 403

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Delete resources associated with rejected domains
        cursor.execute("""
            DELETE r FROM resources r
            JOIN domains d ON r.Domain_id = d.Domain_id
            JOIN domain_requests dr ON d.Domain_name = dr.domain_name
            WHERE dr.status = 'rejected'
        """)
        
        affected_rows = cursor.rowcount  # Count how many rows were deleted

        # Log the cleanup activity
        cursor.execute("""
            INSERT INTO activity_log (user_id, action_type, target_table, target_id, details)
            VALUES (%s, 'delete', 'Resources', 0, %s)
        """, (
            user_id,
            f"Deleted {affected_rows} resource(s) linked to rejected domain requests by admin user_id={user_id}"
        ))

        conn.commit()
        return jsonify({'message': f'Cleanup completed: {affected_rows} resource(s) deleted'}), 200

    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500

    finally:
        cursor.close()
        conn.close()

@app.route('/request-status')
def request_status():
    # Debug session data
    print(f"Session data in /request-status: {dict(session)}")
    
    if not session.get('user_id'):
        print("No user_id in session - redirecting to login")
        return redirect(url_for('login'))
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        if session.get('role') == 'admin':
            cursor.execute("""
                SELECT dr.*, u.username as requester_name 
                FROM domain_requests dr
                JOIN users u ON dr.requested_by = u.user_id
                WHERE dr.status = 'pending'
                ORDER BY request_date DESC
            """)
        else:
            cursor.execute("""
                SELECT domain_name, status, request_date 
                FROM domain_requests 
                WHERE requested_by = %s
                ORDER BY request_date DESC
            """, (session['user_id'],))
        
        requests = cursor.fetchall()
        return render_template('Request.html', 
                            requests=requests, 
                            is_admin=(session.get('role') == 'admin'))
    
    except Exception as e:
        print(f"Error in request_status: {str(e)}")
        return redirect(url_for('login'))
    finally:
        cursor.close()
        conn.close()

@app.route('/admin/requests')
def admin_requests():
    if not session.get('user_id') or session.get('role') != 'admin':
        return redirect('/login')
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT dr.*, u.username as requester_name 
        FROM domain_requests dr
        JOIN users u ON dr.requested_by = u.user_id
        WHERE dr.status = 'pending'
        ORDER BY dr.request_date DESC
    """)
    
    requests = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('Request.html', requests=requests, is_admin=True)

#ishwari's app.py
@app.route('/add_opportunity', methods=['POST'])
def add_opportunity():
    if session.get('is_guest'):
        return jsonify({'error': 'Guests are not allowed to contribute resources.'}), 403

    print("Adding opportunity request")
    title = request.form.get('title')
    link = request.form.get('link')
    opportunity_type = request.form.get('type')
    user_id = session.get('id')  # Corrected column name

    print("Opportunity Type:", opportunity_type)
    print("Opportunity Title:", title)
    print("Opportunity Link:", link)

    if not title or not opportunity_type:
        flash('Title and Type are required', 'danger')
        return redirect(url_for('home'))

    if not user_id:
        flash('User not authenticated', 'danger')
        return redirect(url_for('home'))

    conn = get_db_connection()
    if not conn:
        flash('Database connection failed', 'danger')
        return redirect(url_for('home'))

    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO opportunity_requests (title, description, opportunity_type, requested_by, status)
            VALUES (%s, %s, %s, %s, 'pending')
        """, (title, link, opportunity_type, user_id))

        request_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO activity_log (user_id, action_table, target_table, target_id, details)
            VALUES (%s, 'opportunities', 'opportunity_requests', %s, %s)
        """, (user_id, request_id, f"Opportunity request '{title}' submitted by user_id={user_id}"))

        conn.commit()
        flash('Opportunity request submitted successfully! Awaiting admin approval.', 'success')
    except mysql.connector.Error as err:
        flash(f'Error submitting opportunity request: {err}', 'danger')
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('home'))


@app.route('/admin/handle_opportunity/<int:request_id>', methods=['POST'])
def handle_opportunity_request(request_id):
    if session.get('role') != 'admin':
        flash('Unauthorized access', 'danger')
        return redirect(url_for('home'))

    admin_id = session.get('id')
    if not admin_id:
        flash('Admin not authenticated', 'danger')
        return redirect(url_for('home'))

    action = request.form.get('action')
    if not action:
        flash('Action required', 'danger')
        return redirect(url_for('home'))

    conn = get_db_connection()
    if not conn:
        flash('Database connection failed', 'danger')
        return redirect(url_for('home'))

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT title, description, opportunity_type, requested_by FROM opportunity_requests WHERE request_id = %s", (request_id,))
        request_data = cursor.fetchone()

        if not request_data:
            flash('Request not found', 'danger')
            return redirect(url_for('home'))

        title = request_data['title']
        link = request_data['description']
        opportunity_type = request_data['opportunity_type']
        requested_by = request_data['requested_by']

        if action == 'approve':
            cursor.execute("SELECT type_id FROM opportunitytypes WHERE type_name = %s", (opportunity_type,))
            type_result = cursor.fetchone()
            if not type_result:
                flash(f'Invalid opportunity type: {opportunity_type}', 'danger')
                return redirect(url_for('home'))
            type_id = type_result['type_id']

            cursor.execute("""
                INSERT INTO opportunities (title, description, link, posted_by, type_id)
                VALUES (%s, %s, %s, %s, %s)
            """, (title, title, link, requested_by, type_id))  # description is title fallback

            opportunity_id = cursor.lastrowid

            cursor.execute("UPDATE opportunity_requests SET status = 'approved' WHERE request_id = %s", (request_id,))

            cursor.execute("""
                INSERT INTO activity_log (user_id, action_table, target_table, target_id, details)
                VALUES (%s, 'opportunities', 'opportunities', %s, %s)
            """, (admin_id, opportunity_id, f"Opportunity '{title}' approved from request {request_id} by admin user_id={admin_id}"))

        elif action == 'reject':
            cursor.execute("UPDATE opportunity_requests SET status = 'rejected' WHERE request_id = %s", (request_id,))
            cursor.execute("""
                INSERT INTO activity_log (user_id, action_table, target_table, target_id, details)
                VALUES (%s, 'opportunities', 'opportunity_requests', %s, %s)
            """, (admin_id, request_id, f"Opportunity request '{title}' rejected by admin user_id={admin_id}"))

        else:
            flash('Invalid action', 'danger')
            return redirect(url_for('home'))

        conn.commit()
        flash(f'Opportunity request {action}d successfully', 'success')
    except mysql.connector.Error as err:
        flash(f'Error handling request: {err}', 'danger')
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('home'))


@app.route('/admin/opportunities')
def admin_opportunities():
    print("Entering /admin/opportunities route")
    if not session.get('user_id') or session.get('role') != 'admin':
        print("Unauthorized: user_id=%s, role=%s" % (session.get('user_id'), session.get('role')))
        flash('Unauthorized access', 'danger')
        return redirect(url_for('home'))

    conn = get_db_connection()
    if not conn:
        print("Database connection failed")
        flash('Database connection failed', 'danger')
        return redirect(url_for('home'))

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT orq.*, u.username as requester_name 
            FROM opportunity_requests orq
            JOIN users u ON orq.requested_by = u.user_id
            WHERE orq.status = 'pending'
            ORDER BY orq.submitted_at DESC
        """)
        requests = cursor.fetchall()
        print("Pending Requests:", requests)

        cursor.execute("""
            SELECT o.title, o.link, ot.type_name, u.username as poster_name
            FROM opportunities o
            JOIN users u ON o.posted_by = u.user_id
            LEFT JOIN opportunitytypes ot ON o.type_id = ot.type_id
            ORDER BY o.opp_id DESC
            LIMIT 20
        """)
       
        approved_opportunities = cursor.fetchall()
        print("Approved Opportunities:", approved_opportunities)

    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
        flash(f'Error fetching data: {err}', 'danger')
        requests = []
        approved_opportunities = []
    finally:
        cursor.close()
        conn.close()

    print("Rendering opp_approval.html with %d requests" % len(requests))
    return render_template('opp_approval.html', requests=requests, approved_opportunities=approved_opportunities)

   
@app.route('/add_collaboration', methods=['POST'])
def add_collaboration():
    if 'user_id' not in session:
        flash('Please login first', 'danger')
        return redirect(url_for('signin'))

    title = request.form.get('title')
    description = request.form.get('description')
    collaboration_type = request.form.get('collaboration_type')
    contact_link = request.form.get('contact_link')
    deadline = request.form.get('deadline')
    
    if not title or not description or not collaboration_type:
        flash('Title, description and type are required', 'danger')
        return redirect(url_for('home'))

    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            # Insert into collaborations table
            cursor.execute("""
                INSERT INTO collaborations (title, description, collaboration_type, posted_by, contact_link, deadline)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (title, description, collaboration_type, session['user_id'], contact_link, deadline))
            
            collaboration_id = cursor.lastrowid  # Get the ID of the inserted collaboration

            # Log activity
            cursor.execute("""
                INSERT INTO activity_log (user_id, action_type, target_table, target_id, details)
                VALUES (%s, 'create', 'collaborations', %s, %s)
            """, (
                session['user_id'],
                collaboration_id,
                f"Collaboration '{title}' added by user_id={session['user_id']}"
            ))

            conn.commit()
            flash('Collaboration added successfully!', 'success')
        except mysql.connector.Error as err:
            flash(f'Error adding collaboration: {err}', 'danger')
        finally:
            cursor.close()
            conn.close()

    return redirect(url_for('home'))


@app.route('/get_opportunity_types')
def get_opportunity_types():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM opportunitytypes")
        types = cursor.fetchall()
        cursor.close()
        conn.close()
        return {'types': types}
    return {'types': []}

@app.route('/explore')
def explore():
    search_query = request.args.get('search', '')
    print("Search query:", search_query)
    
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        
        # Search opportunities with the query
        cursor.execute("""
        SELECT o.*, u.username as poster_name, ot.type_name
        FROM opportunities o
        LEFT JOIN users u ON o.posted_by = u.user_id
        LEFT JOIN opportunitytypes ot ON o.type_id = ot.type_id
        WHERE o.title LIKE %s OR COALESCE(ot.type_name, '') LIKE %s OR COALESCE(o.description, '') LIKE %s
        ORDER BY o.opp_id DESC
        """, (f'%{search_query}%', f'%{search_query}%', f'%{search_query}%'))
        opportunities = cursor.fetchall()
        print("Opportunities fetched:", opportunities)
        
        cursor.close()
        conn.close()
        
        return render_template('explore.html', 
                            opportunities=opportunities,
                            search_query=search_query)
    print("Database connection failed")
    return render_template('explore.html', opportunities=[], search_query=search_query)

@app.route('/collaborate')
def collaborate():
    search_query = request.args.get('search', '')
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        
        # Search collaborations with the query
        cursor.execute("""
        SELECT c.*, u.username as poster_name
        FROM collaborations c
        LEFT JOIN users u ON c.posted_by = u.user_id
        WHERE c.title LIKE %s OR c.collaboration_type LIKE %s OR c.description LIKE %s
        ORDER BY c.created_at DESC
        """, (f'%{search_query}%', f'%{search_query}%', f'%{search_query}%'))
        collaborations = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return render_template('/', 
                            collaborations=collaborations,
                            search_query=search_query,
                            active_tab='collaborate')  # Set Collaborate tab as active
    return render_template('opportunities.html', 
                         collaborations=[],
                         opportunities=[],
                         opportunity_types=[],
                         search_query=search_query,
                         active_tab='collaborate')

    # New routes for Contact Us and About Us pages
@app.route('/contact')
def contact_us():
    return render_template('contactus.html')

@app.route('/about')
def about_us():
    return render_template('aboutus.html')
   
@app.route('/opportunities')
def opportunities():
    search_query = request.args.get('search', '')
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        
        # Get opportunities with search
        cursor.execute("""
        SELECT o.*, u.username as poster_name, ot.type_name
        FROM opportunities o
        JOIN users u ON o.posted_by = u.user_id
        LEFT JOIN opportunitytypes ot ON o.opp_id = ot.type_id
        WHERE o.title LIKE %s OR ot.type_name LIKE %s
        ORDER BY o.opp_id DESC
        """, (f'%{search_query}%', f'%{search_query}%'))
        opportunities = cursor.fetchall()
        
        # Get collaborations with search
        cursor.execute("""
        SELECT c.*, u.username as poster_name
        FROM collaborations c
        LEFT JOIN users u ON c.posted_by = u.user_id
        WHERE c.title LIKE %s OR c.collaboration_type LIKE %s OR c.description LIKE %s
        ORDER BY c.created_at DESC
        """, (f'%{search_query}%', f'%{search_query}%', f'%{search_query}%'))
        collaborations = cursor.fetchall()
        
        # Get opportunity types
        cursor.execute("SELECT * FROM opportunitytypes")
        opportunity_types = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return render_template('opportunities.html', 
                            opportunities=opportunities,
                            collaborations=collaborations,
                            search_query=search_query,
                            opportunity_types=opportunity_types)  # Pass opportunity_types
    return render_template('opportunities.html', 
                         opportunities=[], 
                         collaborations=[],
                         search_query=search_query,
                         opportunity_types=[])  # Pass empty list if DB fails

#ishwari's code ends
if __name__ == '__main__':
    app.run(debug=True)

