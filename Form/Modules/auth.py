import os

from flask import Blueprint, request, redirect, url_for, render_template, session, flash
from Form.Modules.db import User, db
from flask import render_template_string
from flask_login import login_user, logout_user, login_required, current_user

auth = Blueprint('auth', __name__, url_prefix='/auth')

template_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('views.index'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            with open(template_path + "/signup.html", 'r', encoding='utf-8') as f:
                template_content = f.read()
            return render_template_string(template_content, error="Username already exists.")

        # Create a regular user (not admin) by default
        user = User(username=username, password=password, is_admin=False)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash('Account created successfully!', 'success')
        return redirect(url_for('views.index'))

    with open(template_path + "/signup.html", 'r', encoding='utf-8') as f:
        template_content = f.read()
    return render_template_string(template_content, error=None, user=current_user)

@auth.route('/signin', methods=['GET', 'POST'])
def signin():
    if current_user.is_authenticated:
        return redirect(url_for('views.index'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page if next_page else url_for('views.index'))

        with open(template_path + "/signin.html", 'r', encoding='utf-8') as f:
            template_content = f.read()
        return render_template_string(template_content, error="Invalid credentials.", user=current_user)

    with open(template_path + "/signin.html", 'r', encoding='utf-8') as f:
        template_content = f.read()
    return render_template_string(template_content, error=None, user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.signin'))

# Add a route to make a user an admin (for development purposes)
@auth.route('/make_admin/<username>')
@login_required
def make_admin(username):
    # Only allow existing admins to create other admins
    if not current_user.is_admin:
        flash("You don't have permission to perform this action.", "error")
        return redirect(url_for('views.index'))

    user = User.query.filter_by(username=username).first()
    if not user:
        flash(f"User {username} not found.", "error")
        return redirect(url_for('views.index'))

    user.is_admin = True
    db.session.commit()
    flash(f"User {username} is now an admin.", "success")
