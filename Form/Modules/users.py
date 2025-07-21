from flask import *
from flask_login import *
from Form.Modules.db import db, User
from flask_sqlalchemy import *
from functools import wraps
from Form.Modules.utils import render_temp

users = Blueprint('users', __name__, url_prefix='/admin/users')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash("You need administrator privileges to access this page.", "error")
            return redirect(url_for('auth.signin'))
        return f(*args, **kwargs)
    return decorated_function


@users.route('/')
@login_required
@admin_required
def index():
    """
    Display the list of users.
    """
    users = User.query.all()
    return render_temp('users', users=users, title="Users List")


