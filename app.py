from flask import Flask, escape, request, render_template,session
from flask_bootstrap import Bootstrap
app = Flask(__name__)

app.config['SECRET_KEY'] = 'maui bank'
bootstrap = Bootstrap(app)


# the home page
@app.route('/')
def home():
    print(session.get('username'))
    return render_template('home.html', username=session.get('username'))


@app.route('/hello', methods=['GET', 'POST'])
def hello():
    # todo
    # show account information
    if request.method == 'GET':
        # query data from db
        return render_template("account.html", username=session.get('username'))

    name = request.args.get("name", "World")
    return f'Hello, {escape(name)}!'


if __name__ == '__main__':
    app.run()
