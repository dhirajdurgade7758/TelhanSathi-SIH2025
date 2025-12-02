from flask import Flask, render_template, send_from_directory, url_for, redirect, session
from flask_cors import CORS
import os
from dotenv import load_dotenv

from extensions import db
from flask_migrate import Migrate  # ✅ Added

load_dotenv()

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

# ----------------------- SESSION CONFIG -----------------------
app.config['SESSION_COOKIE_SECURE'] = False  # True only in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# ----------------------- DATABASE CONFIG -----------------------
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///telhan_sathi.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Initialize the database
db.init_app(app)

# Initialize migrations
migrate = Migrate(app, db)     # ✅ Added (Important for flask db migrate/upgrade)


# ----------------------- BLUEPRINTS -----------------------
from routes.auth import auth_bp
from routes.onboarding import onboarding_bp
from routes.sahayak import sahayak_bp

app.register_blueprint(auth_bp)
app.register_blueprint(onboarding_bp)
app.register_blueprint(sahayak_bp)


# ----------------------- ROUTES -----------------------

@app.route('/')
def home():
    """If authenticated → go to profile, else → login."""
    if 'farmer_id_verified' in session:
        return redirect(url_for('auth.profile'))
    return redirect(url_for('auth.login'))


@app.route('/index')
def index():
    """Redirect to login."""
    return redirect(url_for('auth.login'))


@app.route('/dashboard')
def dashboard():
    """Basic placeholder dashboard."""
    if 'farmer_id_verified' not in session:
        return redirect(url_for('auth.login'))
    return render_template('dashboard.html')


@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files."""
    return send_from_directory('static', filename)


# ----------------------- APP RUN -----------------------
if __name__ == '__main__':
    # ❗️IMPORTANT: Do NOT use db.create_all() when using Flask-Migrate
    # Migrations now handle schema updates.
    
    app.run(debug=True, host='0.0.0.0', port=5000)
        # ----------------------- CUSTOM CLI COMMANDS -----------------------

