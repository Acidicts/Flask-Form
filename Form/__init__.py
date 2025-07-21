from flask import Flask
import os
from flask_login import LoginManager, AnonymousUserMixin
import sqlalchemy.exc

from flask_sqlalchemy import SQLAlchemy
from Form.Modules.db import db

# Create a custom anonymous user class with is_admin attribute
class CustomAnonymousUser(AnonymousUserMixin):
    @property
    def is_admin(self):
        return False

class App:
    def __init__(self, app=None):
        template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
        if app is None:
            app = Flask(__name__, template_folder=template_dir)
        self.app = app

        # Set secret key for session support
        self.app.secret_key = "asdfghj"
        # Set up database URI
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        # Initialize login manager
        self.login_manager = LoginManager()
        self.login_manager.init_app(self.app)
        self.login_manager.login_view = 'auth.signin'
        self.login_manager.login_message = "Please log in to access this page."
        self.login_manager.anonymous_user = CustomAnonymousUser

        db.init_app(self.app)

        self.load()
        self.create_tables()
        self.setup_login()
        self.run()

    def load(self):
        from Form.Modules.views import views
        from Form.Modules.auth import auth
        from Form.Modules.admin import admin
        from Form.Modules.forms import forms_bp
        from Form.Modules.user import user
        from Form.Modules.users import users
        self.app.register_blueprint(user)
        self.app.register_blueprint(users)
        self.app.register_blueprint(views)
        self.app.register_blueprint(auth)
        self.app.register_blueprint(admin)
        self.app.register_blueprint(forms_bp)

    def create_tables(self):
        with self.app.app_context():
            # Try to query from tables to check if schema is valid
            # If there's a new column, it will raise an OperationalError
            schema_changed = False

            try:
                # Test each model by querying it
                from Form.Modules.db import User, DynamicForm, DynamicFormEntry, FormEntry
                User.query.first()
                DynamicForm.query.first()
                DynamicFormEntry.query.first()
                FormEntry.query.first()
            except sqlalchemy.exc.OperationalError:
                # If there's an error (like "no such column"), schema has changed
                print("Schema change detected. Rebuilding database...")
                schema_changed = True

            # Drop and recreate all tables if schema changed
            if schema_changed:
                db.drop_all()

            # Create tables that don't exist
            db.create_all()

            # Create an admin user if no users exist
            from Form.Modules.db import User
            try:
                if not User.query.first():
                    admin = User(username="admin", password="admin", is_admin=True)
                    db.session.add(admin)
                    db.session.commit()
                    print("Created default admin user: username='admin', password='admin'")
            except Exception as e:
                print(f"Error creating admin user: {e}")
                db.session.rollback()

    def setup_login(self):
        from Form.Modules.db import User

        @self.login_manager.user_loader
        def load_user(user_id):
            return User.query.get(int(user_id))

    def run(self):
        self.app.run(debug=True, host='0.0.0.0')
