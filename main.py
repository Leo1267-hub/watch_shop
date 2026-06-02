


"""
My system has two kinds of user: regular ones, and administrators.
Choose Register on the main page in order to register as a regular user.
But to login as an administrator,the role should be 'admin', the user name is admin and the password is '0621'
"""






from flask import Flask,render_template,redirect,url_for,session,flash,get_flashed_messages,g,request
from app.database import get_db,close_db
from app.forms import EditBudget,EditPassword,BasketForm,MessageForm,QuestionForm
from werkzeug.security import generate_password_hash,check_password_hash
from flask_session import Session
from datetime import datetime
from config import Config
from app.utils.auth import login_required_buyer
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

@app.route('/basket',methods = ['GET','POST'])
@login_required_buyer
def basket():
    form = BasketForm()
    message = get_flashed_messages()
    message_to_pay = ''
    if 'basket' not in session:
        session['basket'] = {}#creating empty dictionary with key 'basket'
    names = {}
    db = get_db()
    for watch_id in session['basket']:
        watch = db.execute('''SELECT * FROM watches
                           WHERE watch_id = ?;''',(watch_id,)).fetchone()
        name = watch['title'] #getting from the database dictionary the name of the title and store to variable name
        # user = watch['user_id']
        names[watch_id] = name#store the title of the watch to the dictionary called names with key called watch_id(eg 1,2....)
        
        # names[user] = user
    total_cost = sum(_['price'] for _ in session['basket'].values())
    total_cost = round(total_cost,2)
    # session['total_cost'] = total_cost
    if form.validate_on_submit():
        budget_sql = db.execute('''SELECT budget FROM buyer
                            WHERE user_id = ?''',(session['buyer'],)).fetchone()
        budget = budget_sql['budget']
        if total_cost > budget:
            money_needed = total_cost - budget
            message_to_pay = f"you need {money_needed}€ more to complete purchase"
        else:
            budget -= total_cost
            db.execute('''UPDATE buyer SET budget = ?
                       WHERE user_id = ?''',(budget,session['buyer']))
            watch_ids_to_remove = [watch_id for watch_id in session['basket']]
            for watch_id in watch_ids_to_remove:
                watch = db.execute('''SELECT * FROM watches
                           WHERE watch_id = ?;''',(watch_id,)).fetchone()
                quantity = watch['quantity']
                seller_id = watch['user_id']
                title = watch['title']
                size = watch['size']
                material = watch['material']
                weight = watch['weight']
                # price = watch['price']
                description = watch['description']
                watch_picture =  watch['watch_picture']
                date = send_current_time()
                quantity_in_basket = session['basket'][watch_id]['quantity']
                new_quantity = quantity - quantity_in_basket
                seller_id = watch['user_id']
                price_for_watch_id = session['basket'][watch_id]['price']
                
                db.execute('''INSERT INTO selling_history
                           VALUES(?,?,?,?,?,?,?,?,?,?,?,?)''',
                           (seller_id,session['buyer'],watch_id,title,price_for_watch_id,
                            size,material,weight,description,quantity_in_basket,watch_picture,date))
                if  new_quantity== 0:
                    db.execute('''DELETE FROM watches
                               WHERE watch_id = ?''',(watch_id,))
                else:
                    db.execute('''UPDATE watches SET quantity = ? WHERE watch_id = ?''',(new_quantity,watch_id))
                db.execute('''UPDATE seller SET income = income + ? WHERE user_id = ?''',(price_for_watch_id,seller_id))
                session['basket'].pop(watch_id) 
            db.commit()
            return redirect(url_for('auth.logout'))
            
    session.modified = True  #gets dictionary 
    return render_template('basket.html',basket=session['basket'],title = 'Basket',message=message,total_cost=total_cost,names=names,form=form,message_to_pay=message_to_pay)




@app.route('/add_to_basket/<int:watch_id>')
@login_required_buyer
def add_to_basket(watch_id):
    db = get_db()
    watch= db.execute('''SELECT quantity,price FROM watches 
                          WHERE watch_id = ?;''',(watch_id,)).fetchone()
    if 'basket' not in session:
        session['basket'] = {}
    
    if watch_id not in session['basket']:
        session['basket'][watch_id] = {'quantity':1,'price':watch['price']}
    else:
        if session['basket'][watch_id]['quantity'] >= watch['quantity']:
        # print(session['basket'][watch_id])
            message = f"Only {watch['quantity']} left in stock"
            flash(message)
            return redirect(url_for('watches.main'))
        else:
            session['basket'][watch_id]['quantity'] +=1
            session['basket'][watch_id]['price'] +=watch['price']
            

    session.modified = True
    
    
    return redirect(url_for('basket'))

@app.route('/profile',methods = ['GET','POST'])
@login_required_buyer
def profile():
    message = ''
    form_budget = EditBudget()
    form_password = EditPassword()
    user_id = session['buyer']
    db = get_db()
    #dictionary
    user = db.execute('''SELECT * FROM buyer
                      WHERE user_id = ?''',(session['buyer'],)).fetchone()
    budget = round(user['budget'],2)
    # responded_messages = db.execute('''SELECT * FROM responded_messages_buyer
    #     WHERE buyer_id = ?''',(user_id,)).fetchall()
    
    
    if form_budget.validate_on_submit():
        budget = form_budget.new_budget.data
        db.execute('''UPDATE buyer SET budget = ?
                    WHERE user_id = ?''',(budget,user_id))
        db.commit()
    
    
    return render_template('profile.html',title='Profile',budget = budget,form_budget=form_budget, form_password=form_password,message=message)



@app.route('/add_one_to_basket/<int:watch_id>')
@login_required_buyer
def add_one_to_basket(watch_id):
    db = get_db()
    watch = db.execute('''SELECT quantity,price FROM watches 
                          WHERE watch_id = ?;''',(watch_id,)).fetchone()
    if session['basket'][watch_id]['quantity'] >= watch['quantity']:
        # print(session['basket'][watch_id])
        message = f"Only {watch['quantity']} left in stock"
        flash(message)
    else:
        session['basket'][watch_id]['quantity'] += 1
        session['basket'][watch_id]['price'] +=watch['price']
    session.modified = True
    return redirect(url_for('basket'))


@app.route('/remove_from_basket/<int:watch_id>')
@login_required_buyer
def remove_from_basket(watch_id):
    db = get_db()
    watch = db.execute('''SELECT quantity,price FROM watches 
                          WHERE watch_id = ?;''',(watch_id,)).fetchone()
    
    if session['basket'][watch_id]['quantity'] > 1:
        session['basket'][watch_id]['quantity'] -= 1
        session['basket'][watch_id]['price'] -=watch['price']
    else:
        session['basket'].pop(watch_id)
    session.modified = True
    return redirect(url_for('basket'))



@app.route('/remove_all/<int:watch_id>')
@login_required_buyer
def remove_all(watch_id):
    session['basket'].pop(watch_id)
    session.modified = True
    return redirect(url_for('basket'))

@app.route('/change_password',methods = ['GET','POST'])
@login_required_buyer
def change_password():
    message = ''
    form_budget = EditBudget()
    form_password = EditPassword()
    db = get_db()
    #dictionary
    user = db.execute('''SELECT * FROM buyer
                      WHERE user_id = ?''',(session['buyer'],)).fetchone()
    budget = user['budget']
    user_id = session['buyer']
    if form_password.validate_on_submit(): 
        password = user['password']
        password_to_check = form_password.password_to_check.data
        if not check_password_hash(password,password_to_check):
            form_password.password_to_check.errors.append('wrong password')
        else:
            new_password = form_password.new_password.data
            new_password = generate_password_hash(new_password)
            db.execute('''UPDATE buyer SET password = ?
                        WHERE user_id = ?''',(new_password,user_id))
            db.commit()
            message = 'successful!'
            return redirect(url_for('profile'))
            
    
    return render_template('profile.html',title='Profile',budget = budget,form_password=form_password,message=message, form_budget=form_budget)


@app.route('/add_to_favourite/<int:watch_id>')
@login_required_buyer
def add_to_favourite(watch_id):
    user_id = session['buyer']
    db = get_db()
    check = db.execute('''SELECT * FROM favourite
                       WHERE watch_id = ? AND user_id = ?''',(watch_id,user_id)).fetchone()
    if check:
        flash('You already have this watch in favourite')
        return redirect(url_for('watches.main'))
    db.execute('''INSERT INTO favourite(user_id,watch_id)
               VALUES (?,?);''',(user_id,watch_id))
    db.commit()
                
    return redirect(url_for('favourite'))


@app.route('/favourite',methods = ['GET','POST'])
@login_required_buyer
def favourite():
    user_id = session['buyer']
    db = get_db()
    favourite_to_check_if_exists = db.execute('''SELECT * FROM favourite WHERE user_id = ?''',(user_id,)).fetchall()
    
    favourite_that_exists = []

    names = {}
    for watch_dic in favourite_to_check_if_exists:
        watch_id = watch_dic['watch_id']
        watch = db.execute('''SELECT * FROM watches
                             WHERE watch_id = ?''',(watch_id,)).fetchone()
        if watch:
            favourite_that_exists.append(watch_id)
            name = watch['title'] 
            seller = watch['user_id']
            # session['basket'][watch_id] = {'quantity':1,'price':watch['price']}
            names[watch_id] = {'title':name,'seller':seller,'watch_id':watch_id}
            

            
        session.modified = True
    return render_template('favourite.html',title = 'favourite',names=names,favourite_that_exists=favourite_that_exists)


@app.route('/remove_from_favourite/<int:watch_id>')
@login_required_buyer
def remove_from_favourite(watch_id):
    db = get_db()
    user_id = session['buyer']
    db.execute('''DELETE FROM favourite 
               WHERE watch_id = ? AND user_id = ?''',(watch_id,user_id))
    db.commit()
    
    return redirect(url_for('favourite'))



@app.route('/seller_profile/<user_id>',methods = ['POST','GET'])
@login_required_buyer
def seller_profile(user_id):
    form = MessageForm()
    buyer_id = session['buyer']
    db = get_db()
    check_if_user_exists = db.execute('''SELECT * FROM seller 
                            WHERE user_id = ?''',(user_id,)).fetchone()
    blocked_sellers = db.execute('''SELECT * FROM blocked_sellers
                                 WHERE buyer_id = ? AND seller_id = ?''',(buyer_id,user_id)).fetchone()
    if check_if_user_exists is not None:
        seller_watches = db.execute('''SELECT * FROM watches WHERE user_id = ?''',(user_id,)).fetchall()
        reviews = db.execute('''SELECT * FROM reviews 
                             WHERE seller_id = ?''',(user_id,)).fetchall()
        if form.validate_on_submit():
            review = form.message.data
            date = send_current_time()
            db.execute('''INSERT INTO reviews(seller_id,buyer_id,review,date)
                VALUES (?,?,?,?)''',(user_id,buyer_id,review,date))
            db.commit()
            flash('Message was successfully sent!')
            return redirect(url_for('watches.main'))
    else:
        flash(f"there is no such user {user_id}")
        return redirect(url_for('watches.main'))
    return render_template('seller_profile.html',seller_watches=seller_watches,user_id=user_id,form=form,reviews=reviews,blocked_sellers=blocked_sellers,title = 'Seller Profile')

@app.route('/help_buyer',methods = ['POST','GET'])
@login_required_buyer
def help_buyer():
    form = QuestionForm()
    db = get_db()
    user_id = session['buyer']
    responded_messages_buyer = db.execute('''SELECT * FROM responded_messages_buyer
                                          WHERE buyer_id = ?
                                          ORDER BY date DESC;''',(user_id,)).fetchall()
    if form.validate_on_submit():
            message = form.message.data
            date = send_current_time()
            db.execute('''INSERT INTO messages_to_response_buyer(buyer_id,message,date)
                VALUES (?,?,?)''',(user_id,message,date))
            db.commit()
            flash('Message was successfully sent!')
            return redirect(url_for('watches.main'))
    return render_template('help.html',form=form,responded_messages_buyer=responded_messages_buyer,title='Help')

@app.route('/block_seller/<seller_id>')
@login_required_buyer
def block_seller(seller_id):
    buyer_id = session['buyer']
    db = get_db()
    already_blocked = db.execute('''SELECT * FROM blocked_sellers
                                 WHERE seller_id = ?
                                 AND buyer_id = ?''',(seller_id,buyer_id)).fetchone()
    if not already_blocked:
        db.execute('''INSERT INTO blocked_sellers
                VALUES (?,?)''',(buyer_id,seller_id))
        db.commit()
        return redirect(url_for('seller_profile',user_id=seller_id))
    else:
        flash(f"{seller_id} is already blocked!")
        return redirect(url_for('watches.main'))


@app.route('/unblock_seller/<seller_id>')
@login_required_buyer
def unblock_seller(seller_id):
    db = get_db()
    buyer_id = session['buyer']
    already_blocked = db.execute('''SELECT * FROM blocked_sellers
                                 WHERE seller_id = ?
                                 AND buyer_id = ?''',(seller_id,buyer_id)).fetchone()
    if already_blocked:
        db.execute('''DELETE FROM blocked_sellers
                WHERE seller_id = ? AND buyer_id = ?''',(seller_id,buyer_id))
        db.commit()
        return redirect(url_for('seller_profile',user_id=seller_id))
    else:
        flash(f"{seller_id} isn't blocked")
        return redirect(url_for('watches.main'))
    

@app.route('/blocked_sellers')
@login_required_buyer
def blocked_sellers():
    db = get_db()
    buyer_id = session['buyer']
    blocked_sellers = db.execute('''SELECT * FROM blocked_sellers
                                 WHERE buyer_id = ?''',(buyer_id,)).fetchall()
    return render_template('blocked_sellers.html',blocked_sellers=blocked_sellers,title= 'blocked sellers')


@app.errorhandler(404)
def page_not_found(error):
    return redirect(url_for('watches.main'))

def send_current_time():
    return datetime.today().date()