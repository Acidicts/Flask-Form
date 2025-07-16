from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)  # Add admin flag

class FormEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    data = db.Column(db.Text, nullable=False)

class DynamicForm(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    image = db.Column(db.String(500), nullable=True)  # Link to image
    display_image = db.Column(db.Boolean, default=False)  # Whether to display the image in the form
    image_display_type = db.Column(db.String(20), default="banner")  # "banner" or "logo"
    fields = db.Column(db.Text, nullable=False)  # JSON string describing fields

    # Form styling
    text_color = db.Column(db.String(20), default="#000000")
    bg_color = db.Column(db.String(20), default="#f8f8f8")
    field_bg_color = db.Column(db.String(20), default="#ffffff")
    button_color = db.Column(db.String(20), default="#007bff")
    button_text_color = db.Column(db.String(20), default="#ffffff")
    heading_color = db.Column(db.String(20), default="#000000")

class DynamicFormEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    form_id = db.Column(db.Integer, db.ForeignKey('dynamic_form.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    data = db.Column(db.Text, nullable=False)  # JSON string of submitted data
