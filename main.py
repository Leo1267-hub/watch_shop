


"""
My system has two kinds of user: regular ones, and administrators.
Choose Register on the main page in order to register as a regular user.
But to login as an administrator,the role should be 'admin', the user name is admin and the password is '1357'
"""



from flask import Flask,redirect,url_for
from app.database import close_db
from flask_session import Session
from config import Config
from app.auth.routes import auth_bp
from app.watches.routes import watches_bp
from app.seller.routes import seller_bp
from app.buyer.routes import buyer_bp
from app.admin.routes import admin_bp
from app.utils.context import load_logged_in_user

app = Flask(__name__)
app.config.from_object(Config)
app.teardown_appcontext(close_db)
Session(app)
app.register_blueprint(auth_bp)
app.register_blueprint(watches_bp)
app.register_blueprint(seller_bp)
app.register_blueprint(buyer_bp)
app.register_blueprint(admin_bp)

app.before_request(load_logged_in_user)

   
@app.errorhandler(404)
def page_not_found(error):
    return redirect(url_for('watches.main'))