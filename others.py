from flask import request,session,redirect,url_for
from functools import wraps
def valid(func):
    @wraps(func)
    def inner(*args,**kwargs):
        user=session.get('user_id')
        if user:
            return func(*args,**kwargs)
        else:
            return redirect(url_for('login'))
    return inner