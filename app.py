import os
import psycopg2
from dotenv import load_dotenv
from flask import Flask, request, render_template, session, redirect, url_for
from flask_mail import Mail, Message
from cryptography.fernet import Fernet
from datetime import datetime, timedelta


CREATE_TABLE = (
    "CREATE TABLE IF NOT EXISTS User_Data (id SERIAL PRIMARY KEY, first_name VARCHAR(60), last_name VARCHAR(60), phone_num VARCHAR(15), email_address VARCHAR(50), SSN VARCHAR(9), encMsg VARCHAR, is_activated BOOLEAN DEFAULT FALSE,email_date DATE);"
)

INSERT_DATA = "INSERT INTO User_Data (first_name, last_name,phone_num, email_address, SSN, encMsg, is_activated,email_date ) VALUES (%s,%s,%s,%s,%s,%s,%s, %s) RETURNING id;"


USER_INFO = (
    """SELECT * FROM User_Data;"""
)

app = Flask(__name__)
app.secret_key = 'secret_key'

app.config['SECRET_KEY'] = "Enter Secret Key here"

app.config['MAIL_SERVER'] = "smtp.googlemail.com"

app.config['MAIL_PORT'] = 465

app.config['MAIL_USE_TLS'] = False

app.config['MAIL_USE_SSL'] = True

app.config['MAIL_USERNAME'] = 'your@gmail.com'

app.config['MAIL_PASSWORD'] = "srdw hptt sxwy pklq"

mail = Mail(app)


# url = os.getenv("")
connection = psycopg2.connect(
    "postgres://goflhkmw:UcQZ1WFRf58uI4yslkvXS8ma0P5vLFCb@suleiman.db.elephantsql.com/goflhkmw")


@app.route('/', methods=['GET'])
def home():
    return render_template("index.html")


@app.route('/user/v1/createName', methods=['POST', 'GET'])
def createName():
    first_name = request.form["first_name"]
    last_name = request.form["last_name"]
    session["first_name"] = first_name
    session["last_name"] = last_name

    return redirect("/user/v1/loadDetails", code=302)


@app.route('/user/v1/loadDetails', methods=['GET', 'POST'])
def loadDetailsPage():
    return render_template("details.html")


@app.route('/user/v1/createDetails', methods=['POST', 'GET'])
def createDetails():
    phone_num = request.form["phone_num"]
    email_address = request.form["email_address"]
    ssn = request.form["ssn"]
    session["phone_num"] = phone_num
    session["email_address"] = email_address
    session["ssn"] = ssn
    return redirect("/user/v1/confirmCreation", code=302)


@app.route('/user/v1/confirmCreation', methods=['GET', 'POST'])
def confirmCreation():
    if request.method == 'POST':
        if request.form['action'] == 'Yes':
            return redirect("/user/v1/thankYou", code=302)
        elif request.form['action'] == 'No':
            return redirect("/", code=302)
    return render_template('confirmation.html')


@app.route('/user/v1/thankYou/', methods=['GET'])
def send_email():
    first_name = session["first_name"]
    last_name = session["last_name"]
    phone_num = session["phone_num"]
    email_address = session["email_address"]
    ssn = session["ssn"]

    msg_title = "Please confirm your email for account activation "
    sender = "kduddugunta@gmail.com"
    msg = Message(msg_title, sender=sender,
                  recipients=[email_address])
    msg_body = f"Dear {first_name},\nYou have recently registered with us using this email address.We are delighted to have you as a registered user. In order to complete the account setup, we request you to activate your newly created user account.\n To activate your account, click on the the link below."
    data = {
        'app_name': "KD Coding",
        'title': msg_title,
        'body': msg_body,
    }
    # Generate fn
    key = Fernet.generate_key()
    fernet = Fernet(key)
    global encMessage
    encMessage = fernet.encrypt(email_address.encode())
    # Store this encMessage in to database by creating new column.
    # Create new colum type boolean activated and set initially false.
    # create new column for the current time.
    # create one more route for activation
    # Verify if it is with in 24 hours by getting from database.
    # Decode the argument received for the route and compare with

    msg.html = render_template("email.html", data=data)
    try:
        mail.send(msg)
        global date_sent
        date_sent = datetime.now().date()
        global expiration_date
        expiration_date = date_sent + timedelta(days=1)
        return render_template('thank_you.html')
    except Exception as e:
        return f"The email was not sent. Check if you entered a valid email address.\nError:{e}"


@app.route('/user/v1/accountActivation')
def account_activation():
    current_time = datetime.now().date()
    if current_time < expiration_date:
        is_activated = True
    else:
        pass
    first_name = session["first_name"]
    last_name = session["last_name"]
    phone_num = session["phone_num"]
    email_address = session["email_address"]
    ssn = session["ssn"]

    with connection:
        with connection.cursor() as cursor:
            cursor.execute(CREATE_TABLE)
            cursor.execute(INSERT_DATA, (first_name, last_name,
                           phone_num, email_address, ssn, encMessage, is_activated, date_sent))

    return render_template('activation.html')

@app.route("/<usr>", methods=["GET"])
def user(usr):
    return f"<h1>{usr}</h1>"
