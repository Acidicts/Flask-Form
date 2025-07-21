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

@users.route('/delete/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)

    # Prevent deleting the last admin user
    if user.is_admin:
        admin_count = User.query.filter_by(is_admin=True).count()
        if admin_count <= 1:
            flash("Cannot delete the last administrator user.", "error")
            return redirect(url_for('users.index'))

    # Prevent users from deleting themselves
    if current_user.id == user.id:
        flash("You cannot delete your own account.", "error")
        return redirect(url_for('users.index'))

    username = user.username  # Store username before deletion
    db.session.delete(user)
    db.session.commit()

    flash(f"User '{username}' has been deleted successfully.", "success")
    return redirect(url_for('users.index'))

@users.route('/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    """
    Edit a user's details.
    """
    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        is_admin = 'is_admin' in request.form

        if username:
            user.username = username
        if password:
            user.password = password
        user.is_admin = is_admin

        db.session.commit()
        flash(f"User {user.username} has been updated.", "success")
        return redirect(url_for('users.index'))

    return render_temp('edit_user', user=user, title="Edit User")
