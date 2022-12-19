# Spicy Vanilla: David Chen, Jing Feng, Jeremy Kwok, and Matthew Yee
# SoftDev

from flask import Flask, jsonify  # facilitate flask webserving
from flask import render_template  # facilitate jinja templating
from flask import request  # facilitate form submission
from flask import session
import sqlite3
import requests
import os
import json
from db import get_user_by_username, add_user, check_username, get_orders, get_order, get_users

app = Flask(__name__)  # create Flask object
# Set the secret key to some random bytes. Keep this really secret!
app.secret_key = b'v9y$B&E)H+MbQeThWmZq4t7w!z%C*F-J'

dirname = os.path.dirname(__file__)
# qhqws47nyvgze2mq3qx4jadt
bestBuyKey = open(os.path.join(dirname, "keys/key_bestbuy.txt")).read()
radarKey = open(os.path.join(dirname, "keys/key_radar.txt")).read()
mailChimpKey = open(os.path.join(dirname, "keys/key_mailchimp.txt")).read()

USER_DB_FILE = "users.db"


@app.route('/', methods=['GET', 'POST'])
def index():
    # get the user's username from the session
    username = session.get('username', None)
    return render_template('index.html', username=username)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return app.redirect("/")
    # both the database and the cursor need to be connected in the function it is used in because they must run in the same thread
    users_db = sqlite3.connect(USER_DB_FILE)
    users_c = users_db.cursor()

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


def getip():
    ip = requests.get('https://api.ipify.org').text
    return ip


@app.route("/api/products/trending", methods=["GET"])
def trending():
    response = requests.get(
        f"https://api.bestbuy.com/v1/products/trendingViewed?apiKey={bestBuyKey}&format=json&show=sku,name,salePrice,image&pageSize=20"
    )
    data = response.json()
    return data

@app.route("/api/products/search", methods=["GET"])
def search():
    query = request.args.get("query")
    # handle pagination
    page = request.args.get("page")
    if page is None:
        page = 1
    else:
        page = int(page)
    response = requests.get(
        f"https://api.bestbuy.com/v1/products((search={query}))?apiKey={bestBuyKey}&format=json&show=sku,name,salePrice,image&pageSize=20&page={str(page)}"
    )
    data = response.json()
    return data


@app.route("/search", methods=["GET"])
def search_page():
    # dont error out if there is no username key in the session
    username = session.get('username', None)
    query = request.args.get("query")
    # handle pagination
    page = request.args.get("page")
    if query is None:
        return app.redirect("/")
    if page is None:
        page = 1
    else:
        page = int(page)
    response = requests.get(
        f"https://api.bestbuy.com/v1/products((search={query}))?apiKey={bestBuyKey}&format=json&show=sku,name,salePrice,image,customerReviewCount,customerReviewAverage&pageSize=20&page={str(page)}"
    )
    if response.status_code != 200:
        return app.redirect("/")
    data = response.json()["products"]
    return render_template("results.html", data=data, query=query, page=page, username=username)


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

            # add the user into the order_history table
            command = "INSERT INTO order_history values(?, ?, ?);"
            users_c.execute(command, (username, None, None))
            users_db.commit()

            # diagnostic print
            users_c.execute("SELECT * FROM users")
            user_list = users_c.fetchall()
            print(user_list)

            error = 'Account Created, Navigate to Login'
            return render_template('register.html', error_message=error)
            # confirmation message

    return render_template('register.html')


@app.route('/cart', methods=["GET", "POST"])
def cart_display():
    username = session.get('username', None)
    users_db = sqlite3.connect(USER_DB_FILE)
    users_c = users_db.cursor()
    users_c.execute(
        "SELECT cart FROM order_history WHERE username=?", (username,))
    full_cart = users_c.fetchone()[0]

    if 'username' in session:
        response = requests.get(
            f"https://api.bestbuy.com/v1/products(sku in ({full_cart}))?apiKey={bestBuyKey}&format=json"
        )
        data = response.json()["products"]
        error = 'You have no items in your cart.'
    else:
        error = 'Please log in to add items to your cart.'
    return render_template('cart.html', error=error, data=data, username=username)


@app.route('/searchbycategory/categoryID=<variable>', methods=['GET', 'POST'])
def searchbycategory(variable):
    response = requests.get(
        # pageSize=[number] allows you to change how many products you want in the json file returned
        f"https://api.bestbuy.com/v1/products(categoryPath.id={variable})?apiKey={bestBuyKey}&format=json&pageSize=40")
    data = response.json()["products"]
    #products = data["products"]
    # print(data)
    # print(products)

    return render_template("results.html", data=data)

@app.route('/searchbysku/sku=<variable>', methods=['GET', 'POST'])
def searchbysku(variable):
    response = request.get(
        f"https://api.bestbuy.com/v1/products((search={variable}))?apiKey={bestBuyKey}&format=json"
    )
    data = response.json()["products"]
    return render_template("products.html", data=data)

@app.route('/add_cart', methods=["GET", "POST"])
def add_to_cart():
    if request.method == "POST" and 'username' in session:

        users_db = sqlite3.connect(USER_DB_FILE)
        users_c = users_db.cursor()

        username = ""
        username = session['username']
        print("Username is: " + username)

        users_c.execute(
            "SELECT cart FROM order_history WHERE username=?", (username,))
        full_cart = users_c.fetchone()[0]

        if (full_cart == None):
            full_cart = request.form['SKU']
        else:
            full_cart += "," + request.form['SKU']

        users_c.execute(
            "UPDATE order_history SET cart=? WHERE username=?", (full_cart, username,))
        users_db.commit()

    return app.redirect(app.url_for('cart_display'))


if __name__ == "__main__":  # false if this file imported as module
    # enable debugging, auto-restarting of server when this file is modified
    app.debug = True
    app.run()
