pip install virtualenv
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
export FLASK_APP=app.py
flask run
#python app.python