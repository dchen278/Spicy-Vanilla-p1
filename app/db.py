import sqlite3
DB_FILE = "users.db"

db = sqlite3.connect(DB_FILE, check_same_thread=False)
c = db.cursor()  # facilitate db ops -- you will use cursor to trigger db events

# three tables: users, orders
c.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)")
c.execute("CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY, user_id INTEGER, FOREIGN KEY (user_id) REFERENCES users(id), SKU TEXT, quantity INTEGER, price REAL, date TEXT, status TEXT, notes TEXT)")
# TODO work this out later
# c.execute("CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY, SKU TEXT, name TEXT, price REAL, description TEXT, image TEXT)")

# insert a user
c.execute("INSERT INTO users (username, password) VALUES ('admin', 'admin')")
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


def add_order(user_id, SKU, quantity, price, date, status, notes):
    c.execute("INSERT INTO orders (user_id, SKU, quantity, price, date, status, notes) VALUES (?, ?, ?, ?, ?, ?, ?)",
              (user_id, SKU, quantity, price, date, status, notes))
    db.commit()


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
