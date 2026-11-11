# imports
from flask import Flask, render_template, request, session, redirect # flask functinos
from flask_session import Session # for tracking if users are logged in
from cs50 import SQL # for interacting with databases
import bcrypt # for password hashing

# configure app
app = Flask(__name__)
db = SQL("sqlite:///medicine.db")

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


# databases often store string data like 'this_with_underscores' but I cant display that to the user so this 
# function turns that format to 'This without underscores'
def format_string_data(data_string):
    # replace underscores
    formated_string = ''
    for char in data_string:
        if char == '_':
            formated_string += ' '
        else:
            formated_string += char
    # capatilize first letter
    formated_string = formated_string[0].upper() + formated_string[1:]
    return formated_string


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
        # check if account is active
        active = db.execute('SELECT is_active FROM users WHERE id = ?', user_info['id'])
        active = extract_data_single(active, 'is_active')
        if active == 0:
            return render_template('error.html', message='Account is no longer active.')
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
    # check for search and return results if any
    search = request.args.get('search')
    if search:
        # use LIKE to return search results containing the query
        search_resuslts = db.execute('SELECT * FROM medicines WHERE name LIKE ?', '%' + search + '%')
        if not search_resuslts:
            return render_template('medicines.html', medicines=None, search_query=search)
        return render_template('medicines.html', medicines=search_resuslts, search_query=search)

    # if no search return all medicines
    medicines = db.execute('SELECT * FROM medicines')
    return render_template('medicines.html', medicines=medicines)

# show information for a medicine
@app.route('/medicine_info')
def show_medicine_info():
    # check valid medicine id is given
    medicine_id = request.args.get('medicine_id')
    if not medicine_id:
        return render_template('error.html', message='No medicine ID provided')
    medicine_info = db.execute('SELECT * FROM medicines WHERE id = ?', medicine_id)
    if not medicine_info:
        return render_template('error.html', message='Invlaid medicine ID')
    # get the info on the medicine
    medicine_info = medicine_info[0]
    # get the dosage info
    dosage_info = db.execute('SELECT * FROM dosage_forms WHERE id = ?', medicine_info['dosage_form_id'])
    if dosage_info:
        dosage_info = dosage_info[0]
    else: dosage_info = None
    # check if prescription is required
    prescription_required = 'unknown'
    prescription_needed = db.execute('SELECT requires_prescription FROM medicines WHERE id = ?', medicine_id)
    prescription_needed = extract_data_single(prescription_needed, 'requires_prescription')
    if prescription_needed == 1:
        prescription_required = True
        print('prescription needed')
    elif prescription_needed == 0:
        prescription_required = False
        print('prescription not needed')

    # check prescription category
    category_id = db.execute('SELECT category_id FROM medicines WHERE id = ?', medicine_id)
    category_id = extract_data_single(category_id, 'category_id')
    category_name = db.execute('SELECT name FROM medicine_categories WHERE id = ?', category_id)
    category_name = extract_data_single(category_name, 'name')
    category_name = format_string_data(category_name)
    
    return render_template('medicine_info.html', medicine_info=medicine_info, dosage_info=dosage_info, prescription_required=prescription_required, category=category_name)