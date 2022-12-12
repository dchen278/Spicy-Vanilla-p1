# Spicy Vanilla: David Chen, Jing Feng, Jeremy Kwok, and Matthew Yee
# SoftDev

from flask import Flask, jsonify  # facilitate flask webserving
from flask import render_template  # facilitate jinja templating
from flask import request  # facilitate form submission
from flask import session
import sqlite3
import requests
import json
from db import get_user_by_username, add_user, check_username, get_orders, get_order, get_users

app = Flask(__name__)  # create Flask object
# Set the secret key to some random bytes. Keep this really secret!
app.secret_key = b'v9y$B&E)H+MbQeThWmZq4t7w!z%C*F-J'

bestBuyKey = open("keys/key_bestbuy.txt", "r").read()
radarKey = open("keys/key_radar.txt", "r").read()
mailChimpKey = open("keys/key_mailchimp.txt", "r").read()

USER_DB_FILE = "users.db"


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return app.redirect("/")
    # both the database and the cursor need to be connected in the function it is used in because they must run in the same thread
    users_db = sqlite3.connect(USER_DB_FILE)
    users_c = users_db.cursor()

    try:
        users_c.execute("SELECT * FROM users")
    except:
        users_c.execute(
            "CREATE TABLE users(username TEXT PRIMARY KEY, password TEXT)")

    error = ""
    username = ""
    users_c.execute("SELECT * FROM users")
    user_list = users_c.fetchall()
    print("valid accounts are :" + str(user_list))

    # the following code will only run if the user submits the form on the login page
    if request.method == "POST":
        # diagnostic prints
        print("inputted username is " + request.form['username'])
        print("inputted password is " + request.form['password'])

        # to catch an incomplete operation exception that occurs if the username field is
        try:
            username = request.form['username']
            # inserts username as a tuple containing one item because the ? substitution requires a tuple
            # looks in the database to see if the username entered exists in the users database
            print(
                "executing: SELECT * FROM users GROUP BY username HAVING username=?", (username,))
            users_c.execute(
                "SELECT * FROM users GROUP BY username HAVING username=?", (username,))
        except:
            # print error message if username is not found in database
            error = "username not found"
            print("user with username: " +
                  request.form['username'] + " was not found in database")
            return render_template('login.html', error_message=error)
        # if username is found, get the corresponding record from the database
        credentials = users_c.fetchall()
        print(f"Found the following record for user {username}: {credentials}")

        # since we got the record as a list of tuples, we can check the length of the list to see if the query had any matches
        # username is a primary key, so there will be at most one record
        if len(credentials) > 0:
            username = credentials[0][0]
            password = credentials[0][1]

            if request.form['password'] == password:
                # if password is correct, let the user login with that username
                session['username'] = username
                return app.redirect('/')
            else:
                error = "incorrect password"
        else:
            error = "username not found"

    return render_template('login.html', error_message=error)


@app.route('/logout', methods=["GET", "POST"])
def logout():
    # Checks if there is a username and password in session before popping to prevent a key error
    if 'username' in session:
        print("attempting to pop username")
        session.pop('username')  # removes the username from the session
    # Sends the user back to the login page
    return app.redirect(app.url_for('login'))


@app.route('/goingbacktologin', methods=["GET", "POST"])
def tologin():
    # Sends the user back to the login page
    return app.redirect(app.url_for('login'))

def getip():
    ip = requests.get('https://api.ipify.org').text
    return ip


@app.route('/register', methods=["GET", "POST"])
def register():
    if 'username' in session:
        return app.redirect("/")
    error = ''
    if request.method == 'POST':
        # check for an empty username
        if request.form['username'].strip() == '':
            error = 'No username submitted'
            return render_template('register.html', error_message=error)
        # check for an empty password
        if request.form['password'].strip() == '':
            error = 'No password submitted'
            return render_template('register.html', error_message=error)
        # prevent whitespaces to prevent usernames and passwords like "         e"
        if ' ' in request.form['username'] or ' ' in request.form['password']:
            error = 'Spaces are not permitted in the username or password'
            return render_template('register.html', error_message=error)

        users_db = sqlite3.connect(USER_DB_FILE)
        users_c = users_db.cursor()
        # get the record with the username entered
        username = request.form['username']
        users_c.execute(
            "SELECT * FROM users GROUP BY username HAVING username=?", (username,))
        user_list = users_c.fetchall()

        # if the record / username exists
        if len(user_list) > 0:
            error = 'Username already exists'
            return render_template('register.html', error_message=error)
        else:
            password = request.form['password']
            # add the user into the user database
            command = "INSERT INTO users values(?, ?);"
            users_c.execute(command, (username, password))
            users_db.commit()

            # diagnostic print
            users_c.execute("SELECT * FROM users")
            user_list = users_c.fetchall()
            print(user_list)

            error = 'Account Created, Navigate to Login'
            return render_template('register.html', error_message=error)
            # confirmation message

    return render_template('register.html')



if __name__ == "__main__":  # false if this file imported as module
    # enable debugging, auto-restarting of server when this file is modified
    app.debug = True
    app.run()
