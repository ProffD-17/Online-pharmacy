# imports
from flask import Flask, render_template, request, session, redirect # flask functinos
from flask_session import Session # for tracking if users are logged in
from cs50 import SQL # for interacting with databases
import bcrypt # for password hashing
from datetime import datetime, timedelta # for getting todays date

# configure app
app = Flask(__name__)
db = SQL("sqlite:///databases/pharmacy.db")

#configure session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# constansts
CHANGE_ROLE_PASSWORD = 'Terra' # this is secure to store this here ... right?

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


# return users role as str or false the account is inactive
def user_role(user_id):
    active = extract_data_single(db.execute('SELECT is_active FROM users WHERE user_id = ?', user_id), 'is_active')
    if not active:
        return False
    role_id = extract_data_single(db.execute('SELECT role_id FROM users WHERE user_id = ?', user_id), 'role_id')
    role = extract_data_single(db.execute('SELECT name FROM roles WHERE role_id = ?', role_id), 'name')
    return role



# USERS LOGGIN IN/OUT
# if user has logged in send to home else to login
@app.route('/')
def index():
    # check if user is logged in
    user_id = session.get('user_id')
    if user_id:
        user_info = db.execute('SELECT * FROM users WHERE user_id = ?', session['user_id'])
        if  user_info:
            # get users username and role
            username = extract_data_single(user_info, 'username')
            role = user_role(user_id)
            if not role:
                return render_template('error.html', message='Account is no longer active.')
        else:
            return redirect('/login')
        return render_template('home.html', username=username, role=role)
    
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
        active = db.execute('SELECT is_active FROM users WHERE user_id = ?', user_info['user_id'])
        active = extract_data_single(active, 'is_active')
        if active == 0:
            return render_template('error.html', message='Account is no longer active.')
        # user is correct
        # store id in session
        session['user_id'] = user_info['user_id']
        return redirect('/')
    # got here by link
    return render_template('login.html', logged_out=True)


# logout user and clear session
@app.route('/logout')
def logout():
    session.clear()
    return render_template('logout.html', logged_out=True)


# register new users in the db
@app.route('/register', methods=['POST', 'GET'])
def register():
    # return form if got here by link
    if request.method == 'GET':
        return render_template('register.html', logged_out=True)
    
    # get info from the form
    username = request.form.get('username')
    email = request.form.get('email')
    password_text = request.form.get('password')
    firstname = request.form.get('firstname')
    lastname = request.form.get('lastname')

    # check all info is there
    if (not username) or (not email) or (not password_text) or (not firstname) or (not lastname):
        return render_template('error.html', message='Not enough information provided.', logged_out=True)
    
    # check email and username are unique
    identical_email = db.execute('SELECT * FROM users WHERE email = ?', email)
    if identical_email:
        return render_template('error.html', message='Email already in use.', logged_out=True)
    identical_username = db.execute('SELECT * FROM users WHERE username = ?', username)
    if identical_username:
        return render_template('error.html', message='Username already in use.', logged_out=True)
    
    # hash password
    password_hash = bcrypt.hashpw(password=password_text.encode("utf-8"), salt=bcrypt.gensalt())

    # insert info into db
    success = db.execute('INSERT INTO users (username, email, password_hash, is_active, firstname, lastname) VALUES (?, ?, ?, ?, ?, ?)', username, email, password_hash, 1, firstname, lastname)
    if success:
        # store user id in session
        user_id = extract_data_single(db.execute('SELECT user_id FROM users WHERE email = ?', email), 'user_id')
        session['user_id'] = user_id
        return render_template('home.html', username=username)
    return render_template('error.html', message='Error inserting user into database.', logged_out=True)


# DISPLAY MEDICINE INFORMATION
# show medicines in db
@app.route('/medicines')
def show_medicines():
    # check for search and return results if any
    search = request.args.get('search')
    if search:
        # use LIKE to return search results containing the query
        search_resuslts = db.execute('SELECT * FROM generic WHERE name LIKE ?', '%' + search + '%')
        if not search_resuslts:
            return render_template('medicines.html', medicines=None, search_query=search)
        return render_template('medicines.html', medicines=search_resuslts, search_query=search)

    # if no search return all medicines
    medicines = db.execute('SELECT * FROM generic')
    return render_template('medicines.html', medicines=medicines)

# show information for a medicine
@app.route('/medicine_info')
def show_medicine_info():
    # check valid medicine id is given
    medicine_id = request.args.get('medicine_id')
    if not medicine_id:
        return render_template('error.html', message='No medicine ID provided')
    medicine_info = db.execute('SELECT * FROM generic WHERE medicine_id = ?', medicine_id)
    if not medicine_info:
        return render_template('error.html', message='Invlaid medicine ID')
    # get the info on the medicine
    medicine_info = medicine_info[0]
    # get pregnancy category
    pregnancy_category = medicine_info['pregnancy_category_id']
    pregnancy_category = db.execute('SELECT pregnancy_description FROM pregnancy_category WHERE pregnancy_id = ?', pregnancy_category)
    pregnancy_category = extract_data_single(pregnancy_category, 'pregnancy_description')
    
    
    return render_template('medicine_info.html', medicine_info=medicine_info, pregnancy_advice=pregnancy_category)


# DISPLAY ACCOUNT INFO
# display information about a users account: Role, username, email, delete account and allow them to edit it
@app.route('/account', methods=['POST', 'GET'])
def account():
    if request.method == 'GET':
        # GET USER INFO
        # get users id
        user_id = session.get('user_id')
        if not user_id:
            return redirect('/login')
        # get account info from users table
        account_info = db.execute('SELECT * FROM users WHERE user_id = ?', user_id)
        if not account_info:
            return render_template('error.html', message='Account could not be found')
        account_info = account_info[0]
        # get users role
        role = user_role(user_id).capitalize()
        # return edit form if requested
        if request.args.get('action') == 'edit':
            return render_template('account.html', account_info=account_info, action='edit', role=role)
        # GET USERS ORDERS
        users_orders = db.execute('SELECT * FROM orders JOIN prescriptions ON orders.prescription_id = prescriptions.prescription_id JOIN generic ON prescriptions.medicine_id = generic.medicine_id WHERE prescriptions.patient_id = ?', user_id)
        
        uncompleted_orders = []
        HOW_LONG_RECENT_IS = 7
        recently_completed_orders = []
        for order in users_orders:
            # UNCOMPLETED ORDERS
            if order['completed'] == 0:
                uncompleted_orders.append(order)
            else:
                # ORDERS COMPLETED IN THE PAST 7 DAYS
                current_date = datetime.today().date()
                order_completion_date = datetime.strptime(order['completion_date'], '%Y-%m-%d').date()
                if current_date < order_completion_date + timedelta(days=HOW_LONG_RECENT_IS):
                    recently_completed_orders.append(order)
            
        return render_template('account.html', account_info=account_info, action='view', role=role, uncompleted_orders=uncompleted_orders, recently_completed_orders=recently_completed_orders)

    # change account info
    # get user_id
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/login')
    # check what info is being requested to be changed
    # account info
    email = request.form.get('email')
    if email:
        # get info from form
        username = request.form.get('username')
        if (not email) or (not username):
            return render_template('error.html', message='Not enough information provided')
        
    
        success = db.execute('UPDATE users SET username = ?, email = ? WHERE user_id = ?', username, email, user_id)
        if not success:
            return render_template('error.html', message='Information could not be updated.')
        return redirect('/account')

    # role
    role = request.form.get('role')
    if role:
        # validate password
        role_password = request.form.get('role_password')
        if not role_password == CHANGE_ROLE_PASSWORD:
            return render_template('error.html', message='Incorrect password, If you are a reviewer check message I sent when submitting on Terra to reviewers for password.')
        # get id of requested role
        role_id = extract_data_single(db.execute('SELECT role_id FROM roles WHERE name = ?', role), 'role_id')
        if not role_id:
            return render_template('error.html', message='Role does not exist')
        # change info in db and return status
        success = db.execute('UPDATE users SET role_id = ? WHERE user_id = ?', role_id, user_id)
        if not success:
            return render_template('error.html', message='Could not update role.')
        return redirect('/account')
    # not get and none of the correct info passed in post
    return render_template('error.html', message='Please enter a value on one of the forms.')


# HANDLE PRESCRIPTONS BEING MADE, VIEWED AND REQUESTED
@app.route('/make_prescription', methods=['GET', 'POST'])
def make_prescription():
    # get user id and check user is logged in
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/login')   
    # return create prescription form if got here by link
    if request.method == 'GET':
        medicines = db.execute('SELECT * FROM generic')
        return render_template('make_prescription.html', medicines=medicines, user_id=user_id)
    # create a prescription with info from the form

    # VALIDATE FORM INPUT
    # get info from form
    patient_firstname = request.form.get('patient_firstname')
    patient_lastname = request.form.get('patient_lastname')
    repeating = request.form.get('repeating')
    repeating_start_date_str = request.form.get('repeating_start_date')
    repeating_end_date_str = request.form.get('repeating_end_date')
    repeat_interval = request.form.get('repeat_interval')
    medicine_id = request.form.get('medicine_id')
    creator_id = request.form.get('creator_id')

    # make sure creator is a doctor
    role = user_role(user_id)
    if role != 'doctor':
        return render_template('error.html', message='Need doctor privileges to create prescriptions.')
    # make sure doctor account is active
    active = extract_data_single(db.execute('SELECT is_active FROM users WHERE user_id = ?', creator_id), 'is_active')
    if active != 1:
        return render_template('error.html', message='Your account is no longer active.')

    # check patient is in db
    patient_info = db.execute('SELECT * FROM users WHERE firstname = ? AND lastname = ?', patient_firstname, patient_lastname)
    if not patient_info:
        return render_template('error.html', message='Patient does not exist.')
    # check patient is active
    active = extract_data_single(patient_info, 'is_active')
    if active != 1:
        return render_template('error.html', message='Patient account is no longer active.')

    # check start and end times are after current time
    if repeating:
        if (not repeating_end_date_str) or (not repeating_start_date_str) or (not repeat_interval):
            return render_template('error.html', message='Please provide start date, end date and repeat interval for repeating prescription.')
        # get current date in datetime.date type
        current_date = datetime.today().date()
        # convert date inputs from strings to datetime.date type
        if (len(repeating_start_date_str) > 10) or (len(repeating_end_date_str) > 10):
            return render_template('error.html', message='Latest valid date is 31/12/9999.')
        repeating_start_date = datetime.strptime(repeating_start_date_str, '%Y-%m-%d').date()
        repeating_end_date = datetime.strptime(repeating_end_date_str, '%Y-%m-%d').date()
        # check dates are after or equal to current day
        if repeating_start_date < current_date:
            return render_template('error.html', message='Repeating start date must be today or later.')
        if repeating_end_date < current_date:
            return render_template('error.html', message='Repeating end date must be today or later.')
        # check repeating interval is valid
        repeat_interval = int(repeat_interval)
        if not (repeat_interval >= 0):
            return render_template('error.html', message='Repeating interval must be 0(for no interval) or greater. Interval is in days.')

    # check medicine is valid 
    if not db.execute('SELECT * FROM generic WHERE medicine_id = ?', medicine_id):
        return render_template('error.html', message='Medicine does not exist.')

    # insert prescription into db
    # store true as 1 and false as 0
    if repeating == 'repeating':
        repeating = 1
    else:
        repeating = 0
    patient_id = extract_data_single(patient_info, 'user_id')
    doctor_id = creator_id
    print(medicine_id)
    print(type(medicine_id))
    success = db.execute('INSERT INTO prescriptions (patient_id, medicine_id, doctor_id, repeating, repeating_start, repeating_end, repeat_interval) VALUES (?, ?, ?, ?, ?, ?, ?)', patient_id, medicine_id, doctor_id, repeating, repeating_start_date_str, repeating_end_date_str, repeat_interval)
    if success:
        return redirect('/')
    return render_template('error.html', message='Could not create prescription.')


# let users view thier prescriptions
@app.route('/my_prescriptions')
def my_prescriptions():
    # get user info
    user_id = session.get('user_id')
    username = extract_data_single(db.execute('SELECT username FROM users WHERE user_id = ?', user_id), 'username')
    # get users prescriptions and add in user info with INNER JOIN
    prescriptions_info = db.execute('SELECT * FROM prescriptions INNER JOIN users ON prescriptions.patient_id = users.user_id WHERE patient_id = ?', user_id)
    # add doctor name, if prescription is valid to be ordered and medicine name into prescriptions info
    for prescription in prescriptions_info:
        # doctor name
        doctor_id = prescription['doctor_id']
        doctor_lastname = extract_data_single(db.execute('SELECT lastname FROM users WHERE user_id = ?', doctor_id), 'lastname')
        prescription['doctor_name'] = 'Dr. ' + doctor_lastname
        # medicine name
        medicine_id = prescription['medicine_id']
        medicine_name = extract_data_single(db.execute('SELECT name FROM generic WHERE medicine_id = ?', medicine_id), 'name')
        prescription['medicine_name'] = medicine_name
        # check if prescription is valid to be ordered
        # non repeating prescriptions
        if prescription['repeating'] == 0:
            # if has been ordered then valid else not valid
            if prescription['times_ordered'] != 0:
                prescription['valid'] = 0
            else:
                prescription['valid'] = 1
        # repeating prescriptions
        else:
            repeating_end_date = datetime.strptime(prescription['repeating_end'], '%Y-%m-%d').date()
            todays_date = datetime.today().date()
            # if prescription has passed the end date
            if repeating_end_date < todays_date:
                prescription['valid'] = 0
            else:
                # CALCULATE NEXT VALID ORDER DATE
                # get last order date
                last_ordered = prescription['last_ordered']
                # only check next valid order date if prescription has been ordered before
                if last_ordered:
                    last_ordered = datetime.strptime(last_ordered, '%Y-%m-%d').date()
                    # get order interval
                    repeat_interval = prescription['repeat_interval']
                    next_valid_order_date = last_ordered + timedelta(days=repeat_interval)
                    if next_valid_order_date < todays_date:
                        next_valid_order_date = todays_date
                else:
                    next_valid_order_date = todays_date
                
                # check if next valid order date is before end date
                if next_valid_order_date > repeating_end_date:
                    prescription['valid'] = 0
                else:
                    # get time until next valid order
                    days_until_next_valid_order = next_valid_order_date - todays_date
                    prescription['days_until_next_valid_order'] = days_until_next_valid_order.days
                    if days_until_next_valid_order.days == 0:
                        prescription['valid'] = 1
                    else:
                        # 2 means orderable in the futre
                        prescription['valid'] = 2
                

    # display template with users username and list of prescriptions
    return render_template('my_prescriptions.html', username=username, prescriptions=prescriptions_info)


# check users prescription requests and add them to the prescription requests table if valid
@app.route('/order_prescription', methods=['POST'])
def order_prescription():
    # VALIDATE PRESCRIPTION REQUEST
    # get prescripton id from form
    prescription_id = request.form.get('prescription_id')
    # get dict of prescription info
    print(prescription_id)
    prescription_info = db.execute('SELECT * FROM prescriptions WHERE prescription_id = ?', prescription_id)
    if not prescription_info:
        return render_template('error.html', message='Invalid prescription')
    prescription_info = prescription_info[0]

    # validate medicine exists
    medicine_id = prescription_info['medicine_id']
    if not db.execute('SELECT * FROM generic WHERE medicine_id = ?', medicine_id):
        return render_template('error.html', message='Medicine does not exist.')
    
    # validate date and repeat interval
    repeating = prescription_info['repeating']
    if repeating == 1:
        # get todays date
        current_date = datetime.today().date()
        # validate start date
        repeat_start_date = datetime.strptime(prescription_info['repeating_start'], '%Y-%m-%d').date()
        if repeat_start_date > current_date:
            return render_template('error.html', message='You cannot order this prescription before the start date.')
        # validate end date
        repeat_end_date = datetime.strptime(prescription_info['repeating_end'], '%Y-%m-%d').date()
        if repeat_end_date < current_date:
            return render_template('error.html', message='This prescription is past the end date. Please talk to your doctor to request a new one.')
        # validate if order has been ordered too recently to be ordered again
        repeat_interval = prescription_info['repeat_interval']
        last_ordered = prescription_info['last_ordered']
        if last_ordered:
            last_ordered = datetime.strptime(last_ordered, '%Y-%m-%d').date()
            next_valid_order_date = last_ordered + timedelta(days=repeat_interval)
            if next_valid_order_date > current_date:
                return render_template('error.html', message='You cannot order that yet. Please wait until ' + next_valid_order_date.strftime('%d/%m/%Y'))
    else:
        # is onetime use so check prescription has not been used before
        if prescription_info['last_ordered']:
            return render_template('error.html', message='This prescription has been ordered and is no longer valid. Please speak to your doctor if you require more medication.')
    # update last ordered date
    # change format to store in db
    last_ordered = datetime.today().date().strftime('%Y-%m-%d')
    # update last ordered to now
    db.execute('UPDATE prescriptions SET last_ordered = ? WHERE prescription_id = ?', last_ordered, prescription_id)
    # update times ordered
    db.execute('UPDATE prescriptions SET times_ordered = ? WHERE prescription_id = ?', extract_data_single(db.execute('SELECT times_ordered FROM prescriptions WHERE prescription_id = ?', prescription_id), 'times_ordered') + 1, prescription_id)
    # return status
    success = db.execute('INSERT INTO orders (prescription_id, completed, order_date) VALUES (?, ?, ?)', prescription_id, 0, datetime.today().date().strftime('%Y-%m-%d'))
    if success:
        return render_template('success.html', message='Ordered prescription. It will be ready to collect within 2 buisness days.')
    return render_template('error.html', message='Failed to order prescription.')


# allow pharmacists and doctors to manage patients ordering prescriptions
@app.route('/manage_orders', methods=['GET', 'POST'])
def manage_orders():
    # check user has sufficient role to access this route
    user_id = session.get('user_id')
    if not user_id:
        return render_template('error.html', message='Please log out and login again.')
    role = user_role(user_id)
    if role not in ['doctor', 'pharmacist']:
        return render_template('error.html', message='You do not have the privilage for this. You can change your privilages in the accounts page.')
    
    if request.method ==  'GET':
        # DISPLAY ORDERS    
        # show all orders sorted by completed and uncompleted
        # get list of all orders and relating info
        orders = db.execute('SELECT * FROM orders INNER JOIN prescriptions ON orders.prescription_id = prescriptions.prescription_id INNER JOIN generic ON prescriptions.medicine_id = generic.medicine_id INNER JOIN users ON prescriptions.patient_id = users.user_id')
        # add doctors name to the order
        for order in orders:
            prescription_id = order['prescription_id']
            doctor_id = extract_data_single(db.execute('SELECT doctor_id FROM prescriptions WHERE prescription_id = ?', prescription_id), 'doctor_id')
            doctor_lastname = extract_data_single(db.execute('SELECT lastname FROM users WHERE user_id = ?', doctor_id), 'lastname')
            order['prescribing_doctor'] = 'Dr. ' + doctor_lastname

        return render_template('orders.html', orders=orders)
    # CHANGE STATUS OF ORDER (COMPLETED <--> UNCOMPLETED)
    order_id = request.form.get('order_id')
    completed = extract_data_single(db.execute('SELECT completed FROM orders WHERE order_id = ?', order_id), 'completed')
    if completed == 0:
        db.execute('UPDATE orders SET completion_date = ? WHERE order_id = ?', datetime.today().date().strftime('%Y-%m-%d'), order_id)
        success = db.execute('UPDATE orders SET completed = 1 WHERE order_id = ?', order_id)
        if success:
                return render_template('success.html', message='Marked prescription as completed')
        return render_template('error.html', message='Could not update status of order')
        
    success = db.execute('UPDATE orders SET completed = 0 WHERE order_id = ?', order_id)
    if success:
            return render_template('success.html', message='Marked prescription as uncompleted')
    return render_template('error.html', message='Could not update status of order')


# ALLOW USERS TO VIEW ALL THIER PAST ORDERS AND DOCS/PHARMS TO VIEW USERS PAST ORDERS
@app.route('/order_history', methods=['GET', 'POST'])
def order_history():
    user_id = session.get('user_id')
    if request.method == 'GET':
        # check user has authorisation to view all past orders
        if not user_id:
            return redirect('/login')
        role = user_role(user_id)
        if not role:
            return render_template('error.html', message='Your account is inactive.')
        if role not in ['doctor', 'pharmacist']:
            return render_template('error.html', message='You do not have the privilege to view this. Change your privileges in the account page.')
        # show all past orders and search form
        orders = db.execute('SELECT * FROM orders JOIN prescriptions ON orders.prescription_id = prescriptions.prescription_id JOIN users ON prescriptions.patient_id = users.user_id JOIN generic ON prescriptions.medicine_id = generic.medicine_id')
        name = orders[0]['firstname'] + orders[0]['lastname']
        return render_template('order_history.html', orders=orders, mode='all')
    # show prescriptions for a specific patient
    # get firstname either from search input or with user id
    firstname = request.form.get('firstname')
    lastname = request.form.get('lastname')
    if not (firstname or lastname):
        # user accessing their own order history so already have person id or empty search
        if request.form.get('search'):
            # empty search form
            orders = db.execute('SELECT * FROM orders JOIN prescriptions ON orders.prescription_id = prescriptions.prescription_id JOIN generic ON generic.medicine_id = prescriptions.medicine_id')
            return render_template('order_history.html', orders=orders, mode='all')
        # user accessing thier own info
        orders_info = db.execute('SELECT * FROM orders JOIN prescriptions ON orders.prescription_id = prescriptions.prescription_id JOIN generic ON generic.medicine_id = prescriptions.medicine_id JOIN users ON prescriptions.patient_id = users.user_id WHERE patient_id = ?', user_id)
        name = orders_info[0]['firstname'] + ' ' + orders_info[0]['lastname']
        return render_template('order_history.html', orders=orders_info, name=name)
        
    person_id = db.execute('SELECT user_id FROM users WHERE firstname = ? AND lastname = ?', firstname, lastname)
    if not person_id:
        return render_template('error.html', message='Person not found')
    name = firstname + ' ' + lastname
    if len(person_id) > 1:
        # more than one person with the name searched for
        people_ids = extract_data_to_list(person_id, 'user_id')
        peoples_prescription_ids = extract_data_to_list(db.execute('SELECT prescription_id FROM prescriptions WHERE patient_id IN (?)', people_ids), 'prescription_id')
        orders = db.execute('SELECT * FROM orders JOIN prescriptions ON orders.prescription_id = prescriptions.prescription_id JOIN generic ON generic.medicine_id = prescription.medicine_id WHERE prescription_id IN (?)', peoples_prescription_ids)
        
        return render_template('order_history.html', orders=orders, name=name)
    # only one person
    orders = db.execute('SELECT * FROM orders JOIN prescriptions ON orders.prescription_id = prescriptions.prescription_id JOIN generic ON prescriptions.medicine_id = generic.medicine_id WHERE patient_id = ?', person_id[0]['user_id'])
    return render_template('order_history.html', orders=orders, name=name)