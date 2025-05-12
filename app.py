from flask import Flask, render_template, request, jsonify, redirect, url_for,session, flash

from datetime import date
from datetime import datetime
import mysql.connector

app = Flask(__name__)

app.secret_key = '1234'

# Database Configuration
db_config = {
   host:os.getenv("DB_HOST"),
    user:os.getenv("DB_USER"),
    password:os.getenv("DB_PASSWORD"),
    database:os.getenv("DB_NAME"),
    port:int(os.getenv("DB_PORT", 3306))
}

def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")
        return None


@app.route('/')
def index():
    return render_template("index.html")


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
        FROM Resources r
        JOIN ResourceTypes rt ON r.ResourceType_id = rt.ResourceType_id
        JOIN Contributors c ON r.Contributor_id = c.Contributor_id
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
        requested_by = request.form.get('requested_by')

        if not title or not description or not category or not requested_by:
            return jsonify({'error': 'Title, Description, Category, and Requested By are required!'}), 400

        user_id = session.get('user_id')  # Fetch logged-in user's ID

        if not user_id:
            return jsonify({'error': 'User not authenticated'}), 403

        conn = get_db_connection()
        cursor = conn.cursor()

        # Insert the news request
        cursor.execute("""
            INSERT INTO news_requests (title, content, category, requested_by, status)
            VALUES (%s, %s, %s, %s, 'pending')
        """, (title, description, category, requested_by))

        news_request_id = cursor.lastrowid

        # Log the activity with actual user ID
        cursor.execute("""
            INSERT INTO activity_log (user_id, action_type, target_table, target_id, details)
            VALUES (%s, 'request', 'news_requests', %s, %s)
        """, (user_id, news_request_id, f"News request submitted by user_id={user_id}, name={requested_by}"))

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
        conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='admin123',
        database='campus_portal',
        )
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
    
if __name__ == '__main__':
    app.run(debug=True)
