from functools import wraps
from flask import session, redirect, url_for

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin.admin_login'))
        return f(*args, **kwargs)
    return decorated
