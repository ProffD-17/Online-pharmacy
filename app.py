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


@app.route('/')
def index():
    # if user has logged in send to home else to login
    user_id = session.get('id')
    if user_id:
        name = db.execute('SELECT name FROM users WHERE id = ?', session['id'])
        name = extract_data_single(name, 'name')
        if not name:
            name = ''
        return render_template('home.html', name=name)
    
    return redirect('/login')


@app.route('/login', methods=['GET', 'POST'])
def login():
    # has submited the login form
    if request.method == 'POST':
        email = request.form.get('email')
        password_text = request.form.get('password')
        if (not email) or (not password_text):
            return render_template('error.html', message='Email or Password not entered')
        # check if user is in db
        user_info = db.execute('SELECT * FROM users WHERE email = ?', email)
        if not user_info:
            # nothing returned so user doesnt exist
            return render_template('error.html', message='Invalid email, please use a person that already exists. For example check README')
        # check users password
        password_hash = user_info[0]['password_hash']
        if not bcrypt.checkpw(password_text.encode("utf-8"), password_hash.encode("utf-8")):
            # password incorect
            return render_template('error.html', message='Incorrect password, check README example user')
        # user is correct
        return render_template('home.html')


        
    return render_template('login.html')