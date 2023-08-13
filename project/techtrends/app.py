import logging
import sqlite3
import sys


from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort

conn_count = 0

log = logging.getLogger()

handler_stdout = logging.StreamHandler(sys.stdout)
handler_stdout = logging.StreamHandler(sys.stderr)
handlers = [handler_stdout, handler_stdout]

datefmt="%d/%m/%Y, %H:%M:%S"
level=logging.DEBUG
format = '%(levelname)s:%(name)s:%(asctime)s, %(message)s'

logging.basicConfig(datefmt=datefmt, handlers=handlers, level=level, format=format)
log.setLevel(logging.DEBUG)

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    global conn_count

    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    conn_count += 1

    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
#    import pdb; pdb.set_trace()
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'
app.logger.setLevel(logging.DEBUG)


def get_posts():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return posts

def create_post(title, content):
    connection = get_db_connection()
    try:
        connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                        (title, content))
        connection.commit()
        connection.close()
        app.logger.info(f"Article {title} was added successfully.")
    except sqlite3.Error:
        pass
    

# Define the main route of the web application 
@app.route('/')
def index():
    posts = get_posts()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    article = get_post(post_id)
    if article is None:
        log.warning(f"Article not found!")
        return render_template('404.html'), 404
    else:
        log.info(f"Article {list(article)[2]} retrieved!")
        return render_template('post.html', post=article)

# Define the About Us page
@app.route('/about')
def about():
    log.debug(f"About me was called.")
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
            create_post(title, content)
            return redirect(url_for('index'))

    return render_template('create.html')


# Define the About Us page
@app.route('/healthz')
def healthz():
    response = app.response_class(
            response=json.dumps({"result":"OK - healthy"}),
            status=200,
            mimetype='application/json'
    )
    app.logger.info('Status request successfull')
    app.logger.debug('DEBUG message')
    return response


@app.route('/metrics')
def metrics():
    posts = get_posts()
    response = app.response_class(
            response=json.dumps({"status":"success","code":0,"data":{"db_connection_count": conn_count, "post_count": len(posts)}}),
            status=200,
            mimetype='application/json'
    )
    app.logger.info('Metrics request successfull')
    return response


# start the application on port 3111
if __name__ == "__main__":
   app.run(host='0.0.0.0', port='3111')
