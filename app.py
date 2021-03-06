from flask import Flask, request, render_template, session, redirect, url_for
import sqlite3
import hashlib
import random
import string

app = Flask(__name__)
app.secret_key = '\xc9ixnRb\xe40\xd4\xa5\x7f\x03\xd0y6\x01\x1f\x96\xeao+\x8a\x9f\xe4'

def valid_login(username, password):
    con = sqlite3.connect('database/bank.db')
    completion = False
    result_user_name = ""
    with con:
        cur = con.cursor()
        # without SQL injection
        cur.execute("SELECT * FROM USER")
        rows = cur.fetchall()
        for row in rows:
            db_user = row[0]
            db_pass = row[1]
            db_salt = row[2]
            if db_user == username:
                completion = db_pass == hashlib.md5((password+db_salt).encode()).hexdigest()
                result_user_name = row[0]
        # with SQL injection
        # sql = "SELECT * FROM USER WHERE USERNAME = '" + username + "' AND PASSWORD = '" + \
        #       hashlib.md5(password.encode()).hexdigest()+"'"
        # cur.execute(sql)
        # row = cur.fetchone()
        # if row:
        #     result_user_name = row[0]
        #     completion = True
        cur.close()
    con.close()
    return completion, result_user_name


# judge whether a String is a number
def is_number(s):
    if str(s) == 'nan':
        return False
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
    # balance = 0
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
        # print("1", balance)
        if operation == 'withdrawal':
            balance -= float(amount)
        elif operation == 'deposit':
            balance += float(amount)
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


def valid_register(username, password):
    # verify the validation of the password
    contain_low = False
    contain_cap = False
    contain_num = False
    length = 0
    password
    for c in password:
        length += 1
        if c.islower():
            contain_low = True
        elif c.isupper():
            contain_cap = True
        elif c.isdigit():
            contain_num = True

    if not (contain_low and contain_cap and contain_num):
        return 1
    elif length < 8:
        return 2
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
                return 3
        cur.close()
    con.close()
    return 0


def add_user(username, password, balance):
    con = sqlite3.connect('database/bank.db')
    with con:
        cur = con.cursor()
        salt = generate_rand_str()
        md5_password = hashlib.md5((password+salt).encode()).hexdigest()
        try:
            cur.execute("INSERT INTO USER (USERNAME, PASSWORD, SALT, BALANCE) VALUES (?, ?, ?, ?)",
                        (username, md5_password, salt, balance))
            con.commit()
        except Exception as e:
            print(e)
            con.rollback()
        cur.close()
    con.close()


def generate_rand_str(random_length=6):
    rand_list = [random.choice(string.digits + string.ascii_letters) for i in range(random_length)]
    rand_str = ''.join(rand_list)
    return rand_str


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
        else:
            error_code = valid_register(request.form['username'], request.form['password1'])
            if error_code == 0:
                add_user(request.form['username'], request.form['password1'], request.form['input_balance'])
                return redirect(url_for('login'))
            elif error_code == 1:
                error = 'the password is too simple, set again'
            elif error_code == 2:
                error = 'the password is too short, set again'
            elif error_code == 3:
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
        # print(session)
        balance = get_account_balance(name)

        return render_template("account.html", username=name, balance=balance)

    if request.method == 'POST':
        operation = request.form['operation']
        amount = request.form['amount']
        balance = get_account_balance(name)
        if not is_number(amount):
            return render_template("account.html", username=name, balance=balance, error="The amount must be a number.")
        elif float(amount) <= 0.0:
            return render_template("account.html", username=name, balance=balance,
                                   error="The amount has to be larger than 0.")
        else:
            response = update_account_balance(name, operation, amount)
            if not response:
                return redirect("/hello")
            else:
                return render_template("account.html", username=name, balance=balance, error=response)


if __name__ == '__main__':
    app.run(debug=True)
