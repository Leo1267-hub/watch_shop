from functools import wraps
from flask import g, redirect, url_for, request

def login_required_seller(view):
    @wraps(view)
    def wrapped_view(*args,**kwargs):
        if g.seller is None: #if user from above function is none then it goes to login and go back where you were by adding it to url
            return redirect(url_for('login',next = request.url))
        return view(*args,**kwargs)
    return wrapped_view

def login_required_admin(view):
    @wraps(view)
    def wrapped_view(*args,**kwargs):
        if g.admin is None: #if user from above function is none then it goes to login and go back where you were by adding it to url
            return redirect(url_for('login',next = request.url))
        return view(*args,**kwargs)
    return wrapped_view

def login_required_buyer(view):
    @wraps(view)
    def wrapped_view(*args,**kwargs):
        if g.buyer is None: #if user from above function is none then it goes to login and go back where you were by adding it to url
            return redirect(url_for('auth.login',next = request.url))
        return view(*args,**kwargs)
    return wrapped_view