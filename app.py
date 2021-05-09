from flask import Flask, escape, request, render_template,session

app = Flask(__name__)


# the home page
@app.route('/')
def home():
    return render_template('home.html', username=session.get('username'))


@app.route('/hello')
def hello():
    name = request.args.get("name", "World")
    return f'Hello, {escape(name)}!'


if __name__ == '__main__':
    app.run()
