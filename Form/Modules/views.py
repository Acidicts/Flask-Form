from flask import Flask, render_template, request, redirect, url_for, abort, flash, Blueprint
import os
from flask import render_template_string
from flask_login import current_user

views = Blueprint('views', __name__, url_prefix=None)

template_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))

@views.route('/')
def index():
    with open(template_path + "/index.html", 'r', encoding='utf-8') as f:
        template_content = f.read()

    # Check if user is authenticated before accessing is_admin
    is_admin = current_user.is_admin if current_user.is_authenticated else False
    username = current_user.username if current_user.is_authenticated else 'Guest'
    is_authenticated = current_user.is_authenticated

    return render_template_string(template_content, is_admin=is_admin, name=username, is_authenticated=is_authenticated)

@views.route('/about')
def about():

    with open(template_path + "/about.html", 'r', encoding='utf-8') as f:
        template_content = f.read()

    return render_template_string(template_content)