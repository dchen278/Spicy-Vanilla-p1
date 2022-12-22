import sqlite3
DB_FILE = "users.db"

db = sqlite3.connect(DB_FILE, check_same_thread=False)
c = db.cursor()  # facilitate db ops -- you will use cursor to trigger db events

# three tables: users, orders in cart, order history
c.execute(
    "CREATE TABLE IF NOT EXISTS users(username TEXT PRIMARY KEY, password TEXT)")
# execute with relation to users table
c.execute(
    "CREATE TABLE IF NOT EXISTS order_history(username TEXT PRIMARY KEY, cart, history)")

c.execute("CREATE TABLE IF NOT EXISTS orders(username TEXT, productName TEXT, date TEXT, quantity INT, productSKU TEXT, productPrice REAL, orderID INT PRIMARY KEY)")
# TODO work this out later

# c.execute("CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY, SKU TEXT, name TEXT, price REAL, description TEXT, image TEXT)")

db.commit()  # save changes


def get_users():
    c.execute("SELECT * FROM users")
    return c.fetchall()


def get_user(id):
    c.execute("SELECT * FROM users WHERE id = ?", (id,))
    return c.fetchone()


def get_user_by_username(username):
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    return c.fetchone()


def get_orders():
    c.execute("SELECT * FROM orders")
    return c.fetchall()


def get_order(id):
    c.execute("SELECT * FROM orders WHERE id = ?", (id,))
    return c.fetchone()


def get_cart(username):
    c.execute("SELECT * FROM order_history WHERE username = ?", (username,))
    return c.fetchall()


# def add_order(user_id, SKU, quantity, price, date, status, notes, user_id):
#     c.execute("INSERT INTO orders (user_id, SKU, quantity, price, date, status, notes, user_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
#               (user_id, SKU, quantity, price, date, status, notes, user_id))
#     db.commit()


def add_user(username, password):
    c.execute("INSERT INTO users (username, password) VALUES (?, ?)",
              (username, password))
    db.commit()


def check_username(username):
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    if c.fetchone():
        return True
    else:
        return False
