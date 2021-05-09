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


# the home page
@app.route('/')
def home():
    return render_template('home.html', username=session.get('username'))


# the login page
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


@app.route('/hello')
def hello():
    name = request.args.get("name", "World")
    return f'Hello, {escape(name)}!'


if __name__ == '__main__':
    app.run(debug=True)
