from flask_bootstrap import Bootstrap
from flask import Flask, escape, request, render_template, session, redirect, url_for
import sqlite3
import hashlib

app = Flask(__name__)
app.secret_key = '\xc9ixnRb\xe40\xd4\xa5\x7f\x03\xd0y6\x01\x1f\x96\xeao+\x8a\x9f\xe4'


# TODO for MD5 CONVERSION
def check_password(hashed_password, user_password):
    return hashed_password == user_password


def valid_login(username, password):
    con = sqlite3.connect('database/bank.db')
    completion = False
    with con:
        cur = con.cursor()
        cur.execute("SELECT * FROM USER")
        rows = cur.fetchall()
        for row in rows:
            db_user = row[0]
            db_pass = row[1]
            # TODO SQL INJECTION
            if db_user == username:
                completion = check_password(db_pass, password)
    return completion


def get_account_balance(username):
    con = sqlite3.connect('database/bank.db')
    with con:
        cur = con.cursor()
        print(username)
        cur.execute("SELECT BALANCE FROM USER WHERE USERNAME = ?", (username,))
        row = cur.fetchone()
        print(row[0])
        return row[0]

def get_account_info(username):
    con = sqlite3.connect('database/bank.db')
    with con:
        cur = con.cursor()
        cur.execute("SELECT BALANCE FROM USER WHERE USERNAME = ?", username)
        row = cur.fetchone()
        return row[0]


app.config['SECRET_KEY'] = 'maui bank'
bootstrap = Bootstrap(app)


def valid_register(username):
    con = sqlite3.connect('database/bank.db')
    with con:
        cur = con.cursor()
        cur.execute("SELECT * FROM USER")
        rows = cur.fetchall()
        for row in rows:
            db_user = row[0]
            if db_user == username:
                return False
    return True


def add_user(username, password, balance):
    con = sqlite3.connect('database/bank.db')
    with con:
        cur = con.cursor()
        cur.execute("INSERT INTO USER (USERNAME, PASSWORD, BALANCE) VALUES (?, ?, ?)", (username, password, balance))
        con.commit()


# the home page
@app.route('/')
def home():
    print(session.get('username'))
    return render_template('home.html', username=session.get('username'))


# login
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if valid_login(request.form['username'], request.form['password']):
            session['username'] = request.form.get('username')
            return redirect(url_for('hello'))
        else:
            error = 'wrong username or password'

    return render_template('login.html', error=error)


# logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))


# register
@app.route('/register', methods=['GET', 'POST', 'PUT'])
def register():
    error = None
    if request.method == 'POST':
        if request.form['password1'] != request.form['password2']:
            error = 'the two passwords are not the same'
        elif float(request.form['input_balance']) < 0.0:
            error = 'the input balance cannot be negative'
        elif valid_register(request.form['username']):
            add_user(request.form['username'], request.form['password1'], request.form['input_balance'])
            # TODO
            return redirect(url_for('hello'))
        else:
            error = 'this username has been registered'
    return render_template('register.html', error=error)


@app.route('/hello', methods=['GET', 'POST'])
def hello():
    # todo
    # show account information
    name = session.get('username')
    balance = 0
    if request.method == 'GET':
        # query data from db
        print(session)
        balance = get_account_balance(name)

        return render_template("account.html", username=name, balance=balance)

    if request.method == 'POST':
        print(request)
        operation = request.form['operation']
        print(operation)





if __name__ == '__main__':
    app.run(debug=True)
