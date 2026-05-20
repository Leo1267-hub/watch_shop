from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,RadioField,PasswordField,FileField,IntegerField,SelectField,DecimalField, FloatField,TextAreaField
from wtforms.validators import InputRequired,NumberRange,length,EqualTo,Optional #the validator 'Optional' is taken from https://wtforms.readthedocs.io/en/2.3.x/validators/
from flask_wtf.file import FileAllowed,FileRequired


class RegistrationForm(FlaskForm):
    user_id = StringField('',validators=[InputRequired(),length(max=10)],render_kw={'placeholder':'Enter your username: ','class':'user_input'})
    password = PasswordField('',validators=[InputRequired(),length(min=5,max=15)],render_kw={'placeholder':'Create password:','class':'user_input'})
    password_confirm = PasswordField('',validators=[InputRequired(),EqualTo("password")],render_kw={'placeholder':'Confirm password:','class':'user_input'})
    role = RadioField("Who are you registering for? ", choices=['Seller','Buyer'] ,
                          default='Buyer',render_kw={'class':'radio_btn'})
    submit = SubmitField('Sign up',render_kw={'class':'btn'})
    
    
class LoginForm(FlaskForm):
    user_id = StringField('',validators=[InputRequired()],render_kw={'placeholder':'Enter your username: ','class':'user_input'})
    password =PasswordField('',validators=[InputRequired()],render_kw={'placeholder':'Enter password:','class':'user_input'})
    role = RadioField("Who are you?", choices=['Seller','Buyer','Admin'] ,
                          default='Buyer',render_kw={'class':'radio_btn'})
    submit = SubmitField('Login',render_kw={'class':'btn'})


class SellerForm(FlaskForm):
    title = StringField('',validators=[InputRequired(),length(max=10)],render_kw={'placeholder':'Enter the title: ','class':'user_input'})
    price = FloatField('',validators=[InputRequired(),NumberRange(min=0,max=10000)],render_kw={'placeholder':'Enter the price: ','class':'user_input'})
    size = FloatField('',validators=[InputRequired(),NumberRange(min=1,max=63)],render_kw={'placeholder':'Enter the size(mm): ','class':'user_input'})
    material = StringField('',validators=[InputRequired(),length(max=15)],render_kw={'placeholder':'Enter the material: ','class':'user_input'})
    weight = FloatField('',validators=[InputRequired(),NumberRange(min=1,max=120)],render_kw={'placeholder':'Enter the weight(grams): ','class':'user_input'})
    description = TextAreaField('',validators=[InputRequired(),length(max=50)],render_kw={'placeholder':'Enter the description: ','class':'user_input'})
    quantity = IntegerField('How many watches you want to sell?:',validators=[InputRequired(),NumberRange(min=1,max=20)],
                            default=1,render_kw={'class':'user_input'})
    # the filefield allows to upload files, for my web site it allows to upload the images a small bit of code is taken from:
    # https://flask-wtf.readthedocs.io/en/0.15.x/form/
    file = FileField('Upload the image of the watch:',      validators=[
        FileRequired(),
        FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField('Submit',render_kw={'class':'btn'})
    
    
    
class EditBudget(FlaskForm):
    new_budget = FloatField('New Budget',validators=[InputRequired(),NumberRange(min=0,max=100000)],render_kw={'placeholder':'Enter new budget: ','class':'user_input'})
    submit = SubmitField('Submit',render_kw={'class':'btn'})
    
class EditPassword(FlaskForm):
    password_to_check = PasswordField('Current Password',validators=[InputRequired()],render_kw={'placeholder':'Enter old password: ','class':'user_input'})
    new_password = PasswordField('New Password',validators=[InputRequired(),length(min=5,max=15)],render_kw={'placeholder':'Enter new password: ','class':'user_input'})
    change = SubmitField('Change',render_kw={'class':'btn'})
    
class BasketForm(FlaskForm):
    submit = SubmitField('Purchase',render_kw={'class':'btn'})
    
class EditWatch(FlaskForm):
    title = StringField('Enter The Title:',validators=[length(max=10)],render_kw={'placeholder':'Enter the title: ','class':'user_input'})
    price = FloatField('Enter The Price:',validators=[Optional(),NumberRange(min=0,max=10000)],render_kw={'placeholder':'Enter the price: ','class':'user_input'})
    size = FloatField('Enter the Size:',validators=[Optional(),NumberRange(min=1,max=63)],render_kw={'placeholder':'Enter the size(mm): ','class':'user_input'})
    material = StringField('Enter The Material:',render_kw={'placeholder':'Enter the material: ','class':'user_input'})
    weight = FloatField('Enter The Weight:',validators=[Optional(),NumberRange(min=1,max=120)],render_kw={'placeholder':'Enter the weight(grams): ','class':'user_input'})
    description = TextAreaField('',validators=[length(max=50)],render_kw={'placeholder':'Enter the description: ','class':'user_input'})
    quantity = IntegerField('How many watches you want to sell?:',validators=[Optional(),NumberRange(min=1,max=20)],render_kw={'class':'user_input'})
    # the filefield allows to upload files, for my web site it allows to upload the images a small bit of code is taken from:
    # https://flask-wtf.readthedocs.io/en/0.15.x/form/
    file = FileField('Upload the image of the watch:',      validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField('Submit',render_kw={'class':'btn'})
    
    
    
class FilterForm(FlaskForm):
    watch = SelectField('our catalog:',validators=[Optional()],choices=['all'],default='all')
    min_price = FloatField('Enter the minimum price',validators=[NumberRange(min=0,max=10000),Optional()],render_kw={'class':'user_input'})
    max_price = FloatField('Enter the maximum price',validators=[NumberRange(min=0,max=10000),Optional()],render_kw={'class':'user_input'})
    sort = SelectField('Sort',validators=[Optional()],choices=['Price low to high','Price high to low','all'],
                       default='all',render_kw={'class':'user_input'})
    submit = SubmitField('Submit',render_kw={'class':'btn'})
    
    
class MessageForm(FlaskForm):
    message = TextAreaField('',validators=[InputRequired(),length(max=50)],render_kw={'placeholder':'Leave message for seller: ','class':'user_input'})
    submit = SubmitField('Submit',render_kw={'class':'btn'})


class QuestionForm(FlaskForm):
    message = TextAreaField('',validators=[InputRequired(),length(max=50)],render_kw={'placeholder':'Leave your question:','class':'user_input'})
    submit = SubmitField('Submit',render_kw={'class':'btn'})


class CompareForm(FlaskForm):
    submit = SubmitField('Clear',render_kw={'class':'btn'})
        