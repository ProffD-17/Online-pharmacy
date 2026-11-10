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


# takes a query(list of dicts) and turns it to a list of values from the dicts of the key specified
def extract_data_to_list(query_result, key):
    # check if there is anything in the query result
    if not query_result:
        return None
    
    values = []
    # loop through and add to a list
    for dictionary in query_result:
        values.append(dictionary[key])
    return values


# if user has logged in send to home else to login
@app.route('/')
def index():
    user_id = session.get('id')
    if user_id:
        username = db.execute('SELECT username FROM users WHERE id = ?', session['id'])
        if  username:
            username = extract_data_single(username, 'username')
            print(username)
        else:
            username = ''
            print('no username')
        return render_template('home.html', username=username)
    
    return redirect('/login')


# login existing users 
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
            return render_template('register.html', email=email, password=password_text)
        user_info = user_info[0]
        # check users password
        password_hash = user_info['password_hash']
        if not bcrypt.checkpw(password_text.encode("utf-8"), password_hash):
            # password incorect
            return render_template('error.html', message='Incorrect password')
        # user is correct
        # store id in session
        session['id'] = user_info['id']
        return redirect('/')
    # got here by link
    return render_template('login.html')


# logout user and clear session
@app.route('/logout')
def logout():
    session.clear()
    return render_template('logout.html')


# register new users in the db
@app.route('/register', methods=['POST', 'GET'])
def register():
    # return form if got here by link
    if request.method == 'GET':
        return render_template('register.html')
    
    # get info from the form
    username = request.form.get('username')
    email = request.form.get('email')
    password_text = request.form.get('password')

    # check all info is there
    if (not username) or (not email) or (not password_text):
        return render_template('error.html', message='Not enough information provided.')
    
    # check email and username are unique
    identical_email = db.execute('SELECT * FROM users WHERE email = ?', email)
    if identical_email:
        return render_template('error.html', message='Email already in use.')
    identical_username = db.execute('SELECT * FROM users WHERE username = ?', username)
    if identical_username:
        return render_template('error.html', message='Username already in use.')
    
    # hash password
    password_hash = bcrypt.hashpw(password=password_text.encode("utf-8"), salt=bcrypt.gensalt())

    # insert info into db
    success = db.execute('INSERT INTO users (username, email, password_hash, is_active) VALUES (?, ?, ?, ?)', username, email, password_hash, 1)
    if success:
        return render_template('home.html', username=username)
    return render_template('error.html', message='Error inserting user into database.')


# show medicines in db
@app.route('/medicines')
def medicines():
    medicines = db.execute('SELECT * FROM medicines')
    return render_template('medicines.html', medicines=medicines)