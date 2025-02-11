from flask import Flask,render_template,redirect,url_for
from database import get_db,close_db
from forms import RegistrationForm,LoginForm
from datetime import timedelta


app = Flask(__name__)
app.config['SECRET_KEY'] = 'brovski'
# app.permanent_session_lifetime = timedelta(minutes=5)
app.teardown_appcontext(close_db)


@app.route('/login',methods=['GET','POST'])
def login():
    
    
    
    return render_template('login.html')