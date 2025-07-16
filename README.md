# Flask Dynamic Form Builder

A web application that allows administrators to create, manage, and collect responses from dynamic forms. Built with Flask, SQLAlchemy, and Flask-Login.

## Features

- User authentication and role-based access control
- Dynamic form creation with various field types
- Customizable form styling
- Form response collection and viewing
- Admin dashboard for form management

## Project Structure

- `main.py` - Application entry point
- `Form/__init__.py` - Main application setup
- `Form/Modules/` - Contains blueprint modules:
  - `admin.py` - Admin functionality for form management
  - `auth.py` - User authentication
  - `db.py` - Database models
  - `forms.py` - Form display and submission handling
  - `views.py` - Main site views

## Installation

1. Clone the repository
```bash
git clone https://github.com/Acidicts/Flask-Form.git
cd Flask-Form
```

2. Create a virtual environment
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
# OR
source .venv/bin/activate  # Unix/Mac
```

3. Install dependencies
```bash
pip install flask flask-sqlalchemy flask-login
```

4. Run the application
```bash
python main.py
```

5. Access the application at http://127.0.0.1:5000

## Usage

1. Log in with the default admin account:
   - Username: `admin`
   - Password: `admin`

2. Create forms via the admin interface at `/admin/create_form`

3. View and manage forms at `/admin/forms`

4. Users can fill out forms at `/forms/fill/<form_id>`

5. View form responses at `/admin/responses/<form_id>`

## Security Notes

This is a development version and includes several security considerations:
- Default admin credentials should be changed
- Passwords are stored in plaintext (use a proper hashing solution in production)
- Secret key is hardcoded (should be environment variable in production)

## License

[MIT License](LICENSE)