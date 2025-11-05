# General utilities
import os
import re
import io
import json
import random

# Email handling
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

# Data manipulation and machine learning
import numpy as np
from keras.preprocessing.image import load_img, img_to_array
from keras.models import load_model

# Database-related
import psycopg2.extras
import psycopg2.pool

# Web application framework
from flask import Flask, redirect, render_template, request, jsonify, session, url_for, flash, send_from_directory

# Security-related
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

# Define the upload folder path
UPLOAD_FOLDER = 'uploads'

# Create a connection pool
db_pool = psycopg2.pool.SimpleConnectionPool(
    1,  # minconn: Minimum number of connections to create in the pool
    5,  # maxconn: Maximum number of connections in the pool
    # For local environment:
    # dbname="identree",
    # user="postgres",
    # password="Gamechanger",
    # host="localhost"

    # For Render deployemnt:
    dbname=os.environ.get("DB_NAME"),
    user=os.environ.get("DB_USER"),
    password=os.environ.get("DB_PASSWORD"),
    host=os.environ.get("DB_HOST"),
    port=os.environ.get("DB_PORT", 5432)
)

# Referred documentation for structure of app
app = Flask(__name__)
app.secret_key = 'dev-leicester'

# Configure the upload folder in your app
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.teardown_request
def close_db_connection(exception):
    """Close the database connection at the end of each request."""
    if db_pool:
        conn = db_pool.getconn()
        conn.close()
        db_pool.putconn(conn)

# Load the SavedModel
loaded_model = load_model('model/identree_model_cnn_resnet.h5')

# Custom error handler for 404 (Not Found) errors
@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html'), 404

# Reference of register and login functionality : Cairocoders. Link: https://youtu.be/xIiNYn0q1gs?si=XdjoqbbKD2vEd6FW
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('home.html', username=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))
 
@app.route('/login/', methods=['GET', 'POST'])
def login():
    # cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor = db_pool.getconn().cursor(cursor_factory=psycopg2.extras.DictCursor)
   
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
 
        # Check if account exists using MySQL
        cursor.execute('SELECT * FROM users WHERE username ILIKE %s', (username,))
        # Fetch one record and return result
        account = cursor.fetchone()
 
        if account:
            password_rs = account['password']
            # If account exists in users table in out database
            if check_password_hash(password_rs, password):
                # Create session data, we can access this data in other routes
                session['loggedin'] = True
                session['id'] = account['id']
                session['username'] = account['username']
                # Redirect to home page
                return redirect(url_for('home'))
            else:
                # Account doesnt exist or username/password incorrect
                flash('Incorrect username/password')
        else:
            # Account doesnt exist or username/password incorrect
            flash('Incorrect username/password')
    db_pool.putconn(cursor.connection)
    return render_template('login.html')
  
@app.route('/register', methods=['GET', 'POST'])
def register():
    # cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor = db_pool.getconn().cursor(cursor_factory=psycopg2.extras.DictCursor)
 
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        fullname = request.form['fullname'].title() #Convert to camel case
        username = request.form['username'].title()
        password = request.form['password']
        email = request.form['email']
    
        _hashed_password = generate_password_hash(password)
 
        #Check if account exists using MySQL
        cursor.execute('SELECT * FROM users WHERE username ILIKE %s', (username,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            flash('Account already exists!')
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash('Invalid email address!')
        elif not re.match(r'[A-Za-z0-9]+', username):
            flash('Username must contain only characters and numbers!')
        elif not username or not password or not email:
            flash('Please fill out the form!')
        else:
            # Account doesnt exists and the form data is valid, now insert new account into users table
            cursor.execute("INSERT INTO users (fullname, username, password, email) VALUES (%s,%s,%s,%s)", (fullname, username, _hashed_password, email))
             # After successful registration, commit changes to the database
            cursor.connection.commit()
            flash('You are successfully registered as a tree enthusiast!','alert-success')
            # After successful registration, redirect to the login page
            return redirect(url_for('login'))
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        flash('Please fill out the form!')
    # Show registration form with message (if any)
    db_pool.putconn(cursor.connection)
    return render_template('register.html')
     
@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))

# Self- developed
@app.route('/profile')
def profile(): 
    # cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor = db_pool.getconn().cursor(cursor_factory=psycopg2.extras.DictCursor)
   
    # Check if user is loggedin
    if 'loggedin' in session:
        cursor.execute('SELECT * FROM users WHERE id = %s', [session['id']])
        account = cursor.fetchone()
        # Show the profile page with account info
        db_pool.putconn(cursor.connection)
        return render_template('profile.html', account=account)
    # User is not loggedin redirect to login page
    db_pool.putconn(cursor.connection)
    return redirect(url_for('login'))

with open('class_info.json', 'r') as json_file:
    class_info = json.load(json_file)

with open('label_details.json', 'r') as json_file:
    label_details = json.load(json_file)


def allowed_file(filename, allowed_extensions):
    # Get the file extension from the filename
    file_extension = filename.rsplit('.', 1)[-1].lower()

    # Check if the file extension is in the set of allowed extensions
    return '.' in filename and file_extension in allowed_extensions

# Self- developed
# Routing for predict function
@app.route('/predict', methods=['POST'])
def predict():
    # Get the uploaded image file from the HTTP request
    imagefile = request.files['imagefile']

    # Check if the file has a valid filename
    if imagefile.filename == '':
        return jsonify({'error': 'No selected file'})

    # Check if the file is uploaded
    if 'imagefile' not in request.files:
        return jsonify({'error': 'No file part'})

    # Check if the file is allowed (you can add more allowed extensions if needed)
    allowed_extensions = {'jpg', 'jpeg', 'png'}
    if not allowed_file(imagefile.filename, allowed_extensions):
        return jsonify({'error': 'Invalid file extension'})

    # Generate a unique filename for the uploaded image
    unique_filename = secure_filename(imagefile.filename)

    # Save the uploaded image to the configured upload folder
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
    imagefile.save(image_path)

    # Load and preprocess the image
    image = load_img(image_path, target_size=(224, 224))
    image = img_to_array(image)
    image = image.reshape((1, image.shape[0], image.shape[1], image.shape[2]))

    # Make predictions using the loaded_model
    predictions = loaded_model.predict(image)

    # Determine the predicted class index with the highest confidence score
    predicted_class_index = np.argmax(predictions)

    predicted_class_label = class_info[str(predicted_class_index)]
    predicted_scientific_name = label_details[predicted_class_label]['scientific_name']
    predicted_other_info = label_details[predicted_class_label]['other_info']

    # Calculate the confidence score for the predicted class
    confidence_score = predictions[0][predicted_class_index] * 100

    # Format the confidence score as a percentage with two decimal places
    confidence_percentage = "{:.2f}%".format(confidence_score)

    # Construct the classification response with all the information
    response = {
        'class_label': predicted_class_label,
        'scientific_name': predicted_scientific_name,
        'other_info': predicted_other_info,
        'confidence_percentage': confidence_percentage
    }

    # Log the user's activity in the user_activity table
    if 'loggedin' in session:
        user_id = session['id']

        cursor = db_pool.getconn().cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute("INSERT INTO user_activity (user_id, image_path, result) VALUES (%s, %s, %s)",
                       (user_id, image_path, predicted_class_label))
        cursor.connection.commit()
        db_pool.putconn(cursor.connection)

    return jsonify(response)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Self- developed
@app.route('/mydiary')
def mydiary():
    cursor = db_pool.getconn().cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Check if the user is logged in
    if 'loggedin' in session:
        user_id = session['id']

        # Fetch user activity history from the database
        cursor.execute("SELECT * FROM user_activity WHERE user_id = %s ORDER BY timestamp DESC", (user_id,))
        activities = cursor.fetchall()
        empty_msg="There is no activity to display. Please identify a tree first!"
        
        # Close the database connection
        db_pool.putconn(cursor.connection)
        if(activities==[]):
            return render_template('mydiary.html', empty_msg=empty_msg)
        return render_template('mydiary.html', activities=activities)

    # If the user is not logged in, redirect to the login page
    db_pool.putconn(cursor.connection)
    return redirect(url_for('login'))

def get_activity_details(activity_id):
    cursor = db_pool.getconn().cursor(cursor_factory=psycopg2.extras.DictCursor)

    try:
        # Retrieve the activity details from the database
        cursor.execute("SELECT * FROM user_activity WHERE id = %s", (activity_id,))
        activity = cursor.fetchone()

        if activity:
            activity_details = {  
                'result': activity['result'],
                'image_path': activity['image_path']
            }
            return activity_details
        else:
            return None  # Activity not found
    except Exception as e:
        print(f"Error fetching activity details: {str(e)}")
        return None
    finally:
        db_pool.putconn(cursor.connection)


@app.route('/share_activity/<int:activity_id>', methods=['GET', 'POST'])
def share_activity(activity_id):
    if request.method == 'GET':
        # Fetch activity details and display them (if needed)
        activity_details = get_activity_details(activity_id)
        if activity_details:
            return jsonify(activity_details)
        else:
            return jsonify({'error': 'Activity not found'}), 404

    if request.method == 'POST':
        friend_email = request.form['friend_email']
        message = request.form['message']
        
        # Fetch activity details
        activity_details = get_activity_details(activity_id)

        # Compose the email content
        subject = "Identree activity"
        body = f"Hey, Identree helped me know that the tree to this leaf is:\n"
        
        for key, value in activity_details.items():
            body += f"{key}: {value}\n"
        
        body += f"\nMessage from the user:\n{message}"

        # Configure your SMTP server and credentials
        smtp_server = 'smtp.gmail.com'
        smtp_port = 587
        smtp_username = 'identree.leicester@gmail.com'
        smtp_password = 'uxoryzwmntonjvkw'

        try:
            # Create an SMTP connection
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(smtp_username, smtp_password)

            # Create an email message
            # msg = MIMEText(body)
            msg = MIMEMultipart()
            msg['Subject'] = subject
            msg['From'] = 'your_email@example.com'
            msg['To'] = friend_email

            # Attach the image
            image_path = activity_details['image_path']
            with open(image_path, 'rb') as image_file:
                img = MIMEImage(image_file.read())
                img.add_header('Content-Disposition', 'attachment', filename=os.path.basename(image_path))
                msg.attach(img)

            # Attach the text content
            msg.attach(MIMEText(body, 'plain'))

            # Send the email
            server.sendmail('your_email@example.com', friend_email, msg.as_string())
            server.quit()

            return "Email sent successfully!"
        except Exception as e:
            return f"Error sending email: {str(e)}"


@app.route('/trivia', methods=['GET', 'POST'])
def trivia():
    random_questions = []
    user_score = 0
    top_scores = []

    if request.method == 'POST':
        user_answers = {}
        correct_count = 0

        user_id = session.get('id')

        for key, value in request.form.items():
            if key.startswith('answer_'):
                question_id = int(key.split('_')[1])
                user_answers[question_id] = int(value)

        cursor = db_pool.getconn().cursor(cursor_factory=psycopg2.extras.DictCursor)

        for question_id, user_answer_index in user_answers.items():
            cursor.execute("SELECT correct_option, explanation FROM questions WHERE id = %s", (question_id,))
            row = cursor.fetchone()
            correct_option = row[0]
            explanation = row[1]

            is_correct = user_answer_index == correct_option

            if is_correct:
                correct_count += 1
                cursor.execute("UPDATE users SET score = score + 1 WHERE id = %s", (user_id,))
                cursor.connection.commit()

            cursor.execute("INSERT INTO answers (user_id, question_id, selected_option, is_correct) VALUES (%s, %s, %s, %s)",
                           (user_id, question_id, user_answer_index, is_correct))

            # Update the user_score
            user_score += 1 if is_correct else 0

        cursor.connection.commit()
        db_pool.putconn(cursor.connection)

        # Redirect the user to the /results page with query parameters
        return redirect(url_for('results', user_score=user_score, correct_count=correct_count, explanation=explanation))

    cursor = db_pool.getconn().cursor(cursor_factory=psycopg2.extras.DictCursor)
    user_id = session.get('id')
    cursor.execute("SELECT score FROM users WHERE id = %s", (user_id,))
    user_score = cursor.fetchone()[0]

    # Fetch the top 3 scores and usernames from the database
    cursor.execute("SELECT username, score FROM users ORDER BY score DESC LIMIT 3")
    top_scores = cursor.fetchall()
    cursor.execute("SELECT * FROM questions ORDER BY RANDOM() LIMIT 1;")
    random_questions = cursor.fetchall()

    for question in random_questions:
        question['options'] = json.loads(question['options'])

    db_pool.putconn(cursor.connection)

    return render_template('trivia.html', random_questions=random_questions, top_scores=top_scores, user_score=user_score)

@app.route('/results', methods=['GET'])
def results():
    cursor = db_pool.getconn().cursor(cursor_factory=psycopg2.extras.DictCursor)
    user_id = session.get('id')
    cursor.execute("SELECT score FROM users WHERE id = %s", (user_id,))
    user_score = cursor.fetchone()[0]
    correct_count = request.args.get('correct_count')
    if correct_count == '1':
        message = "Correct Answer!"
    else:
        message = "Incorrect Answer"
    explanation = request.args.get('explanation')
    db_pool.putconn(cursor.connection)
    return render_template('results.html', user_score=user_score, correct_count=correct_count, message=message, explanation=explanation)


# Referred documentation
if __name__ == '__main__':
#     app.run(port=9000, debug=True)
# Change for Render deployment
    port = int(os.environ.get("PORT", 9000))
    app.run(host="0.0.0.0", port=port, debug=True)
