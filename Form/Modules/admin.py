import os
from ctypes import create_string_buffer

from flask import Blueprint, request, redirect, url_for, render_template, render_template_string, flash
from Form.Modules.db import db, DynamicForm, DynamicFormEntry
import json
from flask_login import login_required, current_user
from functools import wraps

admin = Blueprint('admin', __name__, url_prefix='/admin')

template_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))

# Custom decorator for admin-only routes
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash("You need administrator privileges to access this page.", "error")
            return redirect(url_for('auth.signin'))
        return f(*args, **kwargs)
    return decorated_function

@admin.route('/create_form', methods=['GET', 'POST'])
@login_required
@admin_required
def create_form():
    if request.method == 'POST':
        name = request.form['name']
        fields = request.form['fields']
        image_url = request.form.get('image', '')
        display_image = 'display_image' in request.form  # Check if checkbox is checked
        image_display_type = request.form.get('image_display_type', 'banner')

        # Get styling options
        text_color = request.form.get('text_color', '#000000')
        bg_color = request.form.get('bg_color', '#f8f8f8')
        field_bg_color = request.form.get('field_bg_color', '#ffffff')
        button_color = request.form.get('button_color', '#007bff')
        button_text_color = request.form.get('button_text_color', '#ffffff')
        heading_color = request.form.get('heading_color', '#000000')

        # Validate form data
        if not name:
            with open(template_path + "/create_form.html", 'r', encoding='utf-8') as f:
                template_content = f.read()
            return render_template_string(template_content, error="Form name is required.", user=current_user)

        # Validate JSON
        try:
            parsed_fields = json.loads(fields)
            if not isinstance(parsed_fields, list) or len(parsed_fields) == 0:
                raise ValueError("Fields must be a non-empty array.")

            # Validate each field has required properties
            for field in parsed_fields:
                if not all(key in field for key in ['name', 'label', 'type']):
                    raise ValueError("Each field must have name, label, and type properties.")

                # Validate field types that need options
                if field['type'] in ['select', 'radio', 'checkbox'] and ('options' not in field or not field['options']):
                    raise ValueError(f"Field '{field['label']}' requires options.")
        except Exception as e:
            with open(template_path + "/create_form.html", 'r', encoding='utf-8') as f:
                template_content = f.read()
            return render_template_string(template_content, error=f"Invalid form structure: {str(e)}", user=current_user)

        # Check for existing form with same name
        if DynamicForm.query.filter_by(name=name).first():
            with open(template_path + "/create_form.html", 'r', encoding='utf-8') as f:
                template_content = f.read()
            return render_template_string(template_content, error="A form with this name already exists.", user=current_user)

        # Create new form
        form = DynamicForm(
            name=name,
            fields=fields,
            image=image_url,
            display_image=display_image,
            image_display_type=image_display_type,
            text_color=text_color,
            bg_color=bg_color,
            field_bg_color=field_bg_color,
            button_color=button_color,
            button_text_color=button_text_color,
            heading_color=heading_color
        )
        db.session.add(form)
        db.session.commit()

        return redirect(url_for('admin.list_forms'))

    # GET request - show form builder
    with open(template_path + "/create_form.html", 'r', encoding='utf-8') as f:
        template_content = f.read()
    return render_template_string(template_content, error=None, user=current_user, name=current_user.username)

@admin.route('/delete_form/<int:form_id>', methods=['POST'])
@login_required
@admin_required
def delete_form(form_id):
    form = DynamicForm.query.get_or_404(form_id)
    # Delete all responses for this form
    DynamicFormEntry.query.filter_by(form_id=form.id).delete()
    db.session.delete(form)
    db.session.commit()
    return redirect(url_for('admin.list_forms'))

@admin.route('/edit_form/<int:form_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_form(form_id):
    form = DynamicForm.query.get_or_404(form_id)

    if request.method == 'POST':
        name = request.form['name']
        fields = request.form['fields']
        image_url = request.form.get('image', '')
        display_image = 'display_image' in request.form
        image_display_type = request.form.get('image_display_type', 'banner')

        # Get styling options
        text_color = request.form.get('text_color', '#000000')
        bg_color = request.form.get('bg_color', '#f8f8f8')
        field_bg_color = request.form.get('field_bg_color', '#ffffff')
        button_color = request.form.get('button_color', '#007bff')
        button_text_color = request.form.get('button_text_color', '#ffffff')
        heading_color = request.form.get('heading_color', '#000000')

        # Validate form data
        if not name:
            with open(template_path + "/edit_form.html", 'r', encoding='utf-8') as f:
                template_content = f.read()
            return render_template_string(template_content, form=form, error="Form name is required.", user=current_user, name=current_user.username)

        # Validate JSON
        try:
            parsed_fields = json.loads(fields)
            if not isinstance(parsed_fields, list) or len(parsed_fields) == 0:
                raise ValueError("Fields must be a non-empty array.")

            # Validate each field has required properties
            for field in parsed_fields:
                if not all(key in field for key in ['name', 'label', 'type']):
                    raise ValueError("Each field must have name, label, and type properties.")

                # Validate field types that need options
                if field['type'] in ['select', 'radio', 'checkbox'] and ('options' not in field or not field['options']):
                    raise ValueError(f"Field '{field['label']}' requires options.")
        except Exception as e:
            with open(template_path + "/edit_form.html", 'r', encoding='utf-8') as f:
                template_content = f.read()
            return render_template_string(template_content, form=form, error=f"Invalid form structure: {str(e)}", user=current_user, name=current_user.username)

        # Check for name conflict with other forms
        existing = DynamicForm.query.filter_by(name=name).first()
        if existing and existing.id != form.id:
            with open(template_path + "/edit_form.html", 'r', encoding='utf-8') as f:
                template_content = f.read()
            return render_template_string(template_content, form=form, error="A form with this name already exists.", user=current_user, name=current_user.username)

        # Update form
        form.name = name
        form.fields = fields
        form.image = image_url
        form.display_image = display_image
        form.image_display_type = image_display_type
        form.text_color = text_color
        form.bg_color = bg_color
        form.field_bg_color = field_bg_color
        form.button_color = button_color
        form.button_text_color = button_text_color
        form.heading_color = heading_color

        db.session.commit()
        return redirect(url_for('admin.list_forms'))

    # GET request
    with open(template_path + "/edit_form.html", 'r', encoding='utf-8') as f:
        template_content = f.read()
    return render_template_string(template_content, form=form, error=None, name=current_user.username, user=current_user)

@admin.route('/forms')
@login_required
@admin_required
def list_forms():
    forms = DynamicForm.query.all()
    with open(template_path + "/list_forms.html", 'r', encoding='utf-8') as f:
        template_content = f.read()
    return render_template_string(template_content, forms=forms, name=current_user.username, user=current_user)

@admin.route('/responses/<int:form_id>')
@login_required
@admin_required
def view_responses(form_id):
    form = DynamicForm.query.get_or_404(form_id)
    responses = DynamicFormEntry.query.filter_by(form_id=form.id).all()
    fields = json.loads(form.fields)
    field_names = [field['name'] for field in fields]
    field_labels = {field['name']: field['label'] for field in fields}
    field_types = {field['name']: field.get('type', 'text') for field in fields}

    # Prepare response data for display
    response_data = []
    for entry in responses:
        data = json.loads(entry.data)
        formatted_data = []

        for name in field_names:
            value = data.get(name, '')
            field_type = field_types.get(name)

            # Format value based on field type
            if isinstance(value, list):
                formatted_value = ", ".join(value) if value else "-"
            elif field_type == 'checkbox' and value == 'yes':
                formatted_value = "✓"
            elif not value:
                formatted_value = "-"
            else:
                formatted_value = value

            formatted_data.append(formatted_value)

        response_data.append(formatted_data)

    with open(template_path + "/responses.html", 'r', encoding='utf-8') as f:
        html = f.read()
    return render_template_string(html, form=form, field_names=field_names, field_labels=field_labels, user=current_user, response_data=response_data, name=current_user.username)
