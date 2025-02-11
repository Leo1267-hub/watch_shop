from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,RadioField,PasswordField
from wtforms.validators import InputRequired,NumberRange,length,EqualTo


class RegistrationForm(FlaskForm):
    username = StringField('',validators=[InputRequired()],render_kw={'placeholder':'Enter your username: ','class':'user_input'})
    password = PasswordField('',validators=[InputRequired(),length(min=5)],render_kw={'placeholder':'Create password','class':'user_input'})
    password_confirm = PasswordField('',validators=[InputRequired(),EqualTo("password")],render_kw={'placeholder':'Confirm password','class':'user_input'})
    submit = SubmitField('Sign in',render_kw={'class':'btn'})
    
    
class LoginForm(FlaskForm):
    username = StringField('',validators=[InputRequired()],render_kw={'placeholder':'Enter your password','class':'user_input'})
    password =PasswordField('',validators=[InputRequired()],render_kw={'placeholder':'Enter your password','class':'user_input'})
    submit = SubmitField('Login',render_kw={'placeholder','btn'})