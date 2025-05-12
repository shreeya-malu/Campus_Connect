from flask import Flask, render_template, request, jsonify
from flask import Flask, request, redirect, url_for, jsonify

from datetime import date
import mysql.connector

app = Flask(__name__)

app.secret_key = '1234'

# Database Configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'admin123',
    'database': 'campus_portal'
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

@app.route('/')
def index():
    return redirect(url_for('home'))

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

@app.route('/submit', methods=['POST'])
def submit_news():
    try:
        title = request.form.get('title')
        description = request.form.get('description')
        category = request.form.get('category')  # Enum value ('fy', 'sy', 'ty', 'btech', 'other','all')
        requested_by = request.form.get('requested_by')  # Name of the person submitting the request

        # Check if title, description, and category are provided
        if not title or not description or not category or not requested_by:
            return jsonify({'error': 'Title, Description, Category, and Requested By are required!'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("INSERT INTO news_requests (title, content, category, requested_by, status) VALUES (%s, %s, %s, %s, 'pending')",(title, description, category, requested_by))


        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for('home'))  # Redirect to the home page after submitting

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

@app.route('/admin/handle_news/<int:request_id>', methods=['POST'])
def handle_news_request(request_id):
    action = request.form.get('action')

    if not action:
        return redirect(url_for('admin_news', status='error'))

    conn = get_db_connection()
    cursor = conn.cursor()

    if action == 'approve':
        cursor.execute("SELECT title, content, category, requested_by FROM news_requests WHERE request_id = %s", (request_id,))
        news = cursor.fetchone()
        if news:
            title, content, category, requested_by = news
            cursor.execute("INSERT INTO news (title, content, category, created_at) VALUES (%s, %s, %s, %s)", (title, content, category, date.today()))
            cursor.execute("UPDATE news_requests SET status = 'accepted' WHERE request_id = %s", (request_id,))
    elif action == 'reject':
        cursor.execute("UPDATE news_requests SET status = 'rejected' WHERE request_id = %s", (request_id,))
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

@app.route('/resources')
def resources():
    return render_template('resources.html')

@app.route('/add_resource', methods=['POST'])
def add_resource():
    try:
        data = request.get_json()
        name = data.get('name')
        year = data.get('year')
        domain = data.get('domain')
        resources = data.get('resources', [])

        if not name or not year or not domain or not resources:
            return jsonify({'error': 'Missing data in request!'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # --- Contributor ---
        cursor.execute("SELECT Contributor_id FROM Contributors WHERE Name=%s AND Year=%s", (name, year))
        contributor = cursor.fetchone()
        if contributor:
            contributor_id = contributor[0]
        else:
            cursor.execute("INSERT INTO Contributors (Name, Year) VALUES (%s, %s)", (name, year))
            contributor_id = cursor.lastrowid

        # --- Domain ---
        cursor.execute("SELECT Domain_id FROM Domains WHERE Domain_name=%s", (domain,))
        domain_result = cursor.fetchone()
        if domain_result:
            domain_id = domain_result[0]
        else:
            cursor.execute("INSERT INTO Domains (Domain_name) VALUES (%s)", (domain,))
            domain_id = cursor.lastrowid

        for resource in resources:
            r_type = resource.get('type')
            r_link = resource.get('link')
            if not r_type or not r_link:
                continue  # skip incomplete entries

            # --- Resource Type ---
            cursor.execute("SELECT ResourceType_id FROM ResourceTypes WHERE ResourceType_name=%s", (r_type,))
            type_result = cursor.fetchone()
            if type_result:
                type_id = type_result[0]
            else:
                cursor.execute("INSERT INTO ResourceTypes (ResourceType_name) VALUES (%s)", (r_type,))
                type_id = cursor.lastrowid

            # --- Insert Resource ---
            cursor.execute(
                "INSERT INTO Resources (Contributor_id, Domain_id, ResourceType_id, Link) VALUES (%s, %s, %s, %s)",
                (contributor_id, domain_id, type_id, r_link)
            )

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'message': 'Resources added successfully!'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/search_resource', methods=['POST'])
def search_resource():
    try:
        data = request.get_json()
        year = data.get('year')
        domain = data.get('domain')

        if not year or not domain:
            return jsonify({'error': 'Year and Domain are required!'}), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            '''
            SELECT rt.ResourceType_name AS type, r.Link
            FROM Resources r
            JOIN Contributors c ON r.Contributor_id = c.Contributor_id
            JOIN Domains d ON r.Domain_id = d.Domain_id
            JOIN ResourceTypes rt ON r.ResourceType_id = rt.ResourceType_id
            WHERE c.Year = %s AND d.Domain_name = %s
            ''',
            (year, domain)
        )

        rows = cursor.fetchall()

        cursor.close()
        conn.close()

        if not rows:
            return jsonify([])

        results = [{'ResourceType': row['type'], 'Link': row['Link']} for row in rows]
        return jsonify(results), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
  

if __name__ == '__main__':
    app.run(debug=True)
