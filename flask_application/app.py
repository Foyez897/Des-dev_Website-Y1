import pymysql
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_session import Session
# For password hashing
import bcrypt  
import datetime
from datetime import datetime
import uuid

# Configure the Flask app
app = Flask(__name__)

# Configure session secret (replace with a secure random string)
app.config['SECRET_KEY'] = 'your_secret_key'

# Specify the session type
app.config['SESSION_TYPE'] = 'filesystem'

# Initialize session
Session(app)

HOST = '127.0.0.1'
# Assuming 'root' is your username
USER = 'root'  
DATABASE = 'worldhotel'

# Function to connect to database
def get_db():
    connection = pymysql.connect(
        host=HOST,
        user=USER,
        password='Foyez369@',
        database=DATABASE,
    )
    return connection

# Route to handle user login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        # Display login form
        return render_template('login.html')  
    else:
        username = request.form['username']
        password = request.form['password']

        # Database query to check user credentials
        connection = get_db()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        connection.close()

        if user and bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            # Login successful, set session variable
            session['logged_in'] = True
            session['username'] = username
            flash('Login successful!', 'success')
            # Redirect to homepage
            return redirect(url_for('index')) 
        else:
            flash('Invalid username or password.', 'error')
            # Display login form again
            return render_template('login.html')  

# Route to handle admin login
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        # Handle the form submission
        # Example: Validate username and password
        username = request.form['username']
        password = request.form['password']
        # Authentication 
        return redirect(url_for('admindashboard'))
    else:
        # Render the login form
        return render_template('admin.html')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/hotels')
def hotels():
    return render_template('hotels.html')

@app.route('/bookings')
def bookings():
    return render_template('submitbooking.html')

@app.route('/contact_form')
def contact_form():
    print("Hello")

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/register')
def register():
    return render_template('registration.html')

@app.route('/admin-login')
def admin_login():
    return render_template('admin-login.html')

# Route for verify-login action
@app.route('/verify-login', methods = ['POST', 'GET'])
def verify_login():
    msg = ""
    print("verify-login")
    if request.method == 'POST':
        try:
            Username = request.form['Username']
            Password = request.form['Password']
            print(Username)
            print(Password)
            # chech database conection
            conn = get_db()
            if conn != None:
                dbcursor = conn.cursor()
                # check login data with database
                SQL_statement = 'SELECT * FROM worldhotel.user where Username = %s and Password = %s'
                args = (Username,Password,)
                dbcursor.execute(SQL_statement,args)
                rows = dbcursor.fetchall()

                if len(rows) > 0:
                    print("Authenticated")
                    # Return to Home page 
                    return render_template('index.html')
                else:
                    # Return to login page again
                    return render_template("login.html")

                dbcursor.close()
                conn.close()

        except Exception as e:
            print(e)
    return render_template('index.html')
# Route to hadle admindashboard
@app.route('/admindashboard')
def admindashboard():
    return render_template('admindashboard.html')


# Route to handle user logout
@app.route('/logout')
def logout():
    session.clear()  # Clear session data
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))  # Redirect to homepage

# Registration route
@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        # Form submission logic
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Check if passwords match
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('registration.html'))  # Redirect to registration page

        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Insert data into the database
        connection = get_db()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                       (username, email, hashed_password))
        # Commit changes to the database
        connection.commit()  
        cursor.close()
        connection.close()

        flash('Registration successful! You can now log in.', 'success')
        # Redirect to login page
        return redirect(url_for('index'))  
    return render_template('registration.html')

# Route to display booking form (login required)
@app.route('/make-booking')
def make_booking():
    if not session.get('logged_in'):
        # Redirect if not logged in
        return redirect(url_for('login'))  
    # Display booking form
    return render_template('bookings.html')  


# Main booking route
def calculate_price(check_in_date, check_out_date, room_type, advance_booking_days):
    # Sample room prices (you can replace this with data from your database)
    room_prices = {
        "standard_room": {
            "peak_season": 200,
            "off_peak_season": 100
        },
        "double_room": {
            "peak_season": 250,
            "off_peak_season": 150
        },
        "family_room": {
            "peak_season": 300,
            "off_peak_season": 200
        }
    }
   
    # Sample discount information
    discount_info = {
        "80-90": 30,
        "60-79": 20,
        "45-59": 10,
        "under_45": 0
    }

    # Calculate duration of stay in days
    check_in = datetime.strptime(check_in_date, '%Y-%m-%d')
    check_out = datetime.strptime(check_out_date, '%Y-%m-%d')
    duration_of_stay = (check_out - check_in).days

    # Determine season
    if check_in.month in [4, 5, 6, 7, 8, 11, 12]:  # Peak Season
        season = "peak_season"
    else:
        season = "off_peak_season"

    # Fetch room price from room_prices dictionary
    room_price = room_prices.get(room_type, {}).get(season)

    # Calculate total price
    if room_price is not None:
        total_price = room_price * duration_of_stay

        # Apply discount based on advance booking days
        if advance_booking_days >= 80:
            discount = discount_info["80-90"]
        elif 60 <= advance_booking_days <= 79:
            discount = discount_info["60-79"]
        elif 45 <= advance_booking_days <= 59:
            discount = discount_info["45-59"]
        else:
            discount = discount_info["under_45"]

        total_price -= (total_price * discount) / 100

        return total_price
    else:
        return None

# Example usage
check_in_date = "2024-06-15"
check_out_date = "2024-06-20"
room_type = "double_room"
advance_booking_days = 70

def generate_booking_id():
    return str(uuid.uuid4())

print(calculate_price(check_in_date, check_out_date, room_type, advance_booking_days))

# Route for the booking form page
# Route for submitting a booking
@app.route('/submitbooking', methods=['POST'])
def submitbooking():
    if request.method == 'POST':
        # Form submission logic
        hotel = request.form['hotel']
        check_in_date = request.form['check_in_date']
        check_out_date = request.form['check_out_date']
        room_type = request.form['room_type']
        email = request.form['email']
        card_number = request.form['card_number']
        expiration_date = request.form['expiration_date']
        cvv = request.form['cvv']
        card_holder_name = request.form['card_holder_name']
        total_price=request.form['total_price']
        
        # Generate a unique booking ID
        booking_id = generate_booking_id()

        # Hash sensitive information
        hashed_card_number = bcrypt.hashpw(card_number.encode('utf-8'), bcrypt.gensalt())
        hashed_expiration_date = bcrypt.hashpw(expiration_date.encode('utf-8'), bcrypt.gensalt())
        hashed_cvv = bcrypt.hashpw(cvv.encode('utf-8'), bcrypt.gensalt())

        # Convert bytes to string for database insertion
        hashed_card_number_str = hashed_card_number.decode('utf-8')
        hashed_expiration_date_str = hashed_expiration_date.decode('utf-8')
        hashed_cvv_str = hashed_cvv.decode('utf-8')

        # Insert data into the database
        connection = get_db()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO bookings ( hotel, check_in_date, check_out_date, room_type, email, card_number, expiration_date, cvv, card_holder_name,total_price,booking_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s)",
               ( hotel, check_in_date, check_out_date, room_type, email, hashed_card_number_str, hashed_expiration_date_str, hashed_cvv_str, card_holder_name,total_price,booking_id))
        # Commit changes to the database
        connection.commit()  
        cursor.close()
        connection.close()
        # Confirmation messege with booking details
        return render_template('confirmation.html',
                       hotel=hotel, 
                       check_in_date=check_in_date, 
                       check_out_date=check_out_date, 
                       room_type=room_type, 
                       email=email, 
                       total_price=total_price, 
                       card_number=card_number, 
                       expiration_date=expiration_date, 
                       cvv=cvv, 
                       card_holder_name=card_holder_name, 
                       booking_id=booking_id) 
    else:
        return render_template('bookings.html') 
# Define a route for the booking form page
@app.route('/booking_form')
def booking_form():
    return render_template('submitbooking.html')

if __name__ == '__main__':
    app.run(debug=True)

