from flask_login import logout_user, current_user, login_required
from flask import Blueprint, render_template_string, redirect, url_for, flash, request
import os
from Form.Modules.db import db, User

user = Blueprint('user', __name__, url_prefix='/user')

template_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))

@user.route('/profile')
@login_required
def profile():
    if not current_user.is_authenticated:
        flash("You need to be logged in to view your profile.", "error")
        return redirect(url_for('auth.signin'))

    with open(template_path + "/profile.html", 'r', encoding='utf-8') as f:
        template_content = f.read()

    return render_template_string(template_content, name=current_user.username, user=current_user, psw="*" * len(current_user.password))

@user.route('/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():

    if request.method == 'GET':
        if not current_user.is_authenticated:
            flash("You need to be logged in to edit your profile.", "error")

        with open(template_path + "/profile_edit.html", 'r', encoding='utf-8') as f:
            template_content = f.read()

        return render_template_string(template_content, user=current_user)
    elif request.method == 'POST':
        if not current_user.is_authenticated:
            flash("You need to be logged in to edit your profile.", "error")
            return redirect(url_for('auth.signin'))

        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if not username or not password:
            flash("Username and password cannot be empty.", "error")
            return redirect(url_for('user.edit_profile'))

        # Check if username already exists (for someone else)
        existing_user = User.query.filter_by(username=username).first()
        if existing_user and existing_user.id != current_user.id:
            flash("Username already taken. Please choose another.", "error")
            return redirect(url_for('user.edit_profile'))

        # Update user information
        current_user.username = username
        current_user.password = password

        # Save changes to database
        db.session.commit()

        flash("Profile updated successfully!", "success")
        return redirect(url_for('user.profile'))
    return redirect(url_for('views.index'))
