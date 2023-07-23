import sqlite3 
import logging


from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort


# Configure the logging format
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(asctime)s: %(message)s',
    datefmt='%d/%b/%Y %H:%M:%S'
)

# Create a logger for the Werkzeug module
werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.setLevel(logging.INFO)

# Create a logger for the app module
app_logger = logging.getLogger('app')
app_logger.setLevel(logging.INFO)

# Example log statements
werkzeug_logger.info('127.0.0.1 - - [08/Jan/2021 22:40:06] "GET /metrics HTTP/1.1" 200 -')
werkzeug_logger.info('127.0.0.1 - - [08/Jan/2021 22:40:09] "GET / HTTP/1.1" 200 -')
app_logger.info('01/08/2021, 22:40:10, Article "2020 CNCF Annual Report" retrieved!')


#Establish a connection to the database
conn = sqlite3.connect('database.db')

# Create a connection to the database
conn = sqlite3.connect('database.db')

# Create a cursor object to execute SQL queries
cursor = conn.cursor()

# Create the "articles" table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS articles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        author TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

# Commit the changes and close the connection
conn.commit()
conn.close()

#Function to get a database connection.
#This function connects to database with the name `database.db`
def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      return render_template('404.html'), 404
    else:
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()

            return redirect(url_for('index'))

    return render_template('create.html')

@app.route('/articles', methods=['POST'])
def create_article():
    data = request.get_json()
    title = data['title']
    author = data['author']
    content = data['content']
    conn.execute('INSERT INTO articles (title, author, content) VALUES (?, ?, ?)', (title, author, content))
    conn.commit()
    log_message = f'New article created: {title} by {author}'
    conn.execute('INSERT INTO logs (log_message) VALUES (?)', (log_message,))
    conn.commit()
    logger.info(log_message)
    return jsonify(message="Article created successfully"), 201

@app.route('/healthz')
def healthcheck():
    return jsonify(message="OK - healthy"), 200

@app.route('/metrics')
def metrics():
    conn = None
    try:
        # Create a new connection object within the metrics function
        conn = sqlite3.connect('database.db')
        conn.row_factory = sqlite3.Row

        # Get the total count of posts from the database
        total_posts = conn.execute('SELECT COUNT(*) FROM articles').fetchone()[0]

        # Get the total count of connections (queries to the database)
        total_connections = conn.total_changes

        # Create the metrics dictionary
        metrics = {
            'db_connection_count': total_connections,
            'post_count': total_posts
        }

        # Return the metrics as JSON response
        return metrics
    except sqlite3.Error as e:
        # Handle any potential database errors
        print(f"Error accessing database: {e}")
        return render_template('error.html')
    finally:
        # Close the connection after using it
        if conn:
            conn.close()


# start the application on port 3111
if __name__ == "__main__":
   app.run(host='0.0.0.0', port='3111')