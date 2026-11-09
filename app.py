# imports
from flask import Flask, render_template, request, session, redirect # flask functinos
from flask_session import Session # for tracking if users are logged in
from cs50 import SQL # for interacting with databases
import bcrypt # for password hashing

# configure app
app = Flask(__name__)
db = SQL("sqlite:///pharmacy.db")

#configure session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# the db.execute() function returns the info as a list of dicts and this takes that and turns it
# into just the information with the key provided.
# assumes only one dict is in the list.
def extract_data_single(query_result, key):
    if query_result:
        dictionary = query_result[0]
        return dictionary[key]
    return None

@app.route('/test')
def test():
    return 'test worked!'


@app.route('/')
def index():
    user_id = session['id']
    if user_id:
        name = db.execute('SELECT name FROM users WHERE id = ?', session['id'])
        name = extract_data_single(name, 'name')
        if not name:
            name = ''
        return render_template('home.html', name=name)
    
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')