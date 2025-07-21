import os

from flask import Blueprint, request, redirect, url_for, render_template, flash
from Form.Modules.db import db, DynamicForm, DynamicFormEntry, User
import json
from flask import render_template_string
from flask_login import current_user
from functools import wraps

forms_bp = Blueprint('forms', __name__, url_prefix='/forms')

template_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash("You need administrator privileges to access this page.", "error")
            return redirect(url_for('auth.signin'))
        return f(*args, **kwargs)
    return decorated_function

@forms_bp.route('/')
@admin_required
def list_forms():
    forms = DynamicForm.query.all()

    with open(template_path + "/list_forms.html", 'r', encoding='utf-8') as f:
        template_content = f.read()

    return render_template_string(template_content, forms=forms, name=current_user.username, user=current_user)

@forms_bp.route('/fill/<int:form_id>', methods=['GET', 'POST'])
def fill_form(form_id):
    form = DynamicForm.query.get_or_404(form_id)
    fields = json.loads(form.fields)

    if request.method == 'POST':
        data = {}

        # Process each field according to its type
        for field in fields:
            field_name = field['name']
            field_type = field.get('type', 'text')

            if field_type == 'checkbox' and field.get('options'):
                # Process multiple checkboxes
                checked_options = []
                for i, option in enumerate(field.get('options', [])):
                    checkbox_name = f"{field_name}_{i}"
                    if checkbox_name in request.form:
                        checked_options.append(option)
                data[field_name] = checked_options
            else:
                # Process regular fields
                data[field_name] = request.form.get(field_name, '')

        # Store the submission
        user_id = current_user.id if current_user.is_authenticated else None

        entry = DynamicFormEntry(
            form_id=form.id,
            user_id=user_id,
            data=json.dumps(data)
        )
        db.session.add(entry)
        db.session.commit()

        # Show success page
        with open(template_path + "/form_submitted.html", 'r', encoding='utf-8') as f:
            template_content = f.read()
        return render_template_string(template_content, user=current_user)

    # Display the form
    with open(template_path + "/fill_form.html", 'r', encoding='utf-8') as f:
        template_content = f.read()
    return render_template_string(template_content, form=form, fields=fields, user=current_user)
