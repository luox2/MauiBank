from flask import Flask, request, render_template, session, redirect, url_for
import sqlite3
import hashlib

app = Flask(__name__)
app.secret_key = '\xc9ixnRb\xe40\xd4\xa5\x7f\x03\xd0y6\x01\x1f\x96\xeao+\x8a\x9f\xe4'


# To check the password in database with input password after md5 conversion
def check_password(hashed_password, user_password):
    return hashed_password == hashlib.md5(user_password.encode()).hexdigest()


def valid_login(username, password):
    con = sqlite3.connect('database/bank.db')
    completion = False
    result_user_name = ""
    with con:
        cur = con.cursor()
        # without SQL injection
        # cur.execute("SELECT * FROM USER")
        # rows = cur.fetchall()
        # for row in rows:
        #     db_user = row[0]
        #     db_pass = row[1]
        #     if db_user == username:
        #         completion = check_password(db_pass, password)
        # with SQL injection
        sql = "SELECT * FROM USER WHERE USERNAME = '" + username + "' AND PASSWORD = '" + \
              hashlib.md5(password.encode()).hexdigest()+"'"
        cur.execute(sql)
        row = cur.fetchone()
        if row:
            result_user_name = row[0]
            completion = True
        cur.close()
    con.close()
    return completion, result_user_name


# judge whether a String is a number
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
    # try:
    #     import unicodedata
    #     unicodedata.numeric(s)
    #     return True
    # except (TypeError, ValueError):
    #     pass
    return False


def get_account_balance(username):
    con = sqlite3.connect('database/bank.db')
    balance = 0
    with con:
        cur = con.cursor()
        cur.execute("SELECT BALANCE FROM USER WHERE USERNAME = ?", (username,))
        row = cur.fetchone()
        balance = row[0]
        cur.close()
    con.close()
    return balance


def update_account_balance(username, operation, amount):
    con = sqlite3.connect('database/bank.db')
    response = ""
    with con:
        cur = con.cursor()
        cur.execute("SELECT BALANCE FROM USER WHERE USERNAME = ?", (username,))
        balance = cur.fetchone()[0]
        print("1", balance)
        if operation == 'withdrawal':
            balance -= int(amount)
        elif operation == 'deposit':
            balance += int(amount)
        if balance < 0:

            response = "Failed to process your request, please check the amount you entered and retry later."
        else:
            try:
                cur.execute("UPDATE USER SET BALANCE = ? WHERE USERNAME = ?", (balance, username))
                con.commit()
            except Exception as e:
                print(e)
                con.rollback()
                response = "Failed to process your request, please retry later."
        cur.close()
    con.close()
    return response


def get_account_info(username):
    con = sqlite3.connect('database/bank.db')
    with con:
        cur = con.cursor()
        cur.execute("SELECT BALANCE FROM USER WHERE USERNAME = ?", username)
        row = cur.fetchone()
        return row[0]


app.config['SECRET_KEY'] = 'maui bank'


def valid_register(username):
    con = sqlite3.connect('database/bank.db')
    with con:
        cur = con.cursor()
        cur.execute("SELECT * FROM USER")
        rows = cur.fetchall()
        for row in rows:
            db_user = row[0]
            if db_user == username:
                cur.close()
                con.close()
                return False
        cur.close()
    con.close()
    return True


def add_user(username, password, balance):
    con = sqlite3.connect('database/bank.db')
    with con:
        cur = con.cursor()
        md5_password = hashlib.md5(password.encode()).hexdigest()
        try:
            cur.execute("INSERT INTO USER (USERNAME, PASSWORD, BALANCE) VALUES (?, ?, ?)",
                        (username, md5_password, balance))
            con.commit()
        except Exception as e:
            print(e)
            con.rollback()
        cur.close()
    con.close()


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
        if valid_login(request.form['username'], request.form['password'])[0]:
            # SQL injection
            session['username'] = valid_login(request.form['username'], request.form['password'])[1]
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
        elif request.form['input_balance'] == '' or float(request.form['input_balance']) < 0.0:
            error = 'the input balance cannot be negative or null'
        elif valid_register(request.form['username']):
            add_user(request.form['username'], request.form['password1'], request.form['input_balance'])
            return redirect(url_for('login'))
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
        operation = request.form['operation']
        amount = request.form['amount']
        balance = get_account_balance(name)
        if not is_number(amount):
            return render_template("account.html", username=name, balance=balance, error="The amount must be a number.")
        elif float(amount) <= 0.0:
            return render_template("account.html", username=name, balance=balance, error="The amount has to be larger than 0.")
        else:
            response = update_account_balance(name, operation, amount)
            if not response:
                return redirect("/hello")
            else:
                return render_template("account.html", username=name, balance=balance, error=response)


if __name__ == '__main__':
    app.run(debug=True)
