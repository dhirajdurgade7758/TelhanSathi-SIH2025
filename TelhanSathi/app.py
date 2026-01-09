from datetime import datetime
from flask import Flask, render_template, send_from_directory, url_for, redirect, session, request, g
from flask_cors import CORS
import os
from dotenv import load_dotenv

from extensions import db
from flask_migrate import Migrate  # ✅ Added
from models_marketplace_keep import *

load_dotenv()

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

# ----------------------- SESSION CONFIG -----------------------
app.config['SESSION_COOKIE_SECURE'] = False  # True only in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# ----------------------- DATABASE CONFIG -----------------------
import re

database_url = os.getenv('DATABASE_URL', 'sqlite:///telhan_sathi.db')

# Handle internal Render PostgreSQL URL conversion
# Input:  postgresql://user:pass@dpg-xxxxx-a/dbname
# Output: postgresql+psycopg://user:pass@dpg-xxxxx-a.oregon-postgres.render.com/dbname
if database_url.startswith('postgresql://') and '@dpg-' in database_url:
    # Extract components
    match = re.match(r'postgresql://(.+)@dpg-([a-z0-9]+)/(.+)', database_url)
    if match:
        credentials = match.group(1)
        dpg_id = match.group(2)
        dbname = match.group(3)
        # Reconstruct with external endpoint
        database_url = f'postgresql+psycopg://{credentials}@dpg-{dpg_id}.oregon-postgres.render.com/{dbname}'
    else:
        # Fallback: just convert dialect
        database_url = database_url.replace('postgresql://', 'postgresql+psycopg://', 1)
elif database_url.startswith('postgresql://'):
    # Non-Render PostgreSQL - just convert dialect
    database_url = database_url.replace('postgresql://', 'postgresql+psycopg://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
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
from routes.subsidies import subsidies_bp
from routes.admin import admin_bp
from routes.notifications import notifications_bp
from routes.crop_economics import crop_economics_bp
from routes.profit_simulator import profit_bp
from routes.field_monitoring import iot
from routes.bidding import bidding_bp
app.register_blueprint(iot)



from routes.weather import weather_bp
from routes.redemption_store import redemption_bp
from routes.buyer_auth import buyer_auth_bp

app.register_blueprint(auth_bp)
app.register_blueprint(onboarding_bp)
app.register_blueprint(sahayak_bp)
app.register_blueprint(subsidies_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(notifications_bp)
app.register_blueprint(crop_economics_bp)   
app.register_blueprint(profit_bp)
app.register_blueprint(bidding_bp)


app.register_blueprint(weather_bp)
app.register_blueprint(redemption_bp)
app.register_blueprint(buyer_auth_bp)

# ----------------------- ROOT-LEVEL ESP32 ENDPOINTS -----------------------
# Import the handler function from field_monitoring
from routes.field_monitoring import handle_esp32_update

@app.route("/api/update", methods=["POST"])
@app.route("/api/push", methods=["POST"])
def root_esp32_update():
    """Root-level endpoints for ESP32 compatibility (bypasses blueprint prefix)"""
    return handle_esp32_update(request.json)

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

@app.context_processor
def inject_now():
    return {'now': datetime.utcnow}


@app.before_request
def set_language_context():
    """Set language context before each request (static English only)"""
    g.language = 'en'


# ----------------------- APP RUN -----------------------
if __name__ == '__main__':
    # ❗️IMPORTANT: Do NOT use db.create_all() when using Flask-Migrate
    # Migrations now handle schema updates.
    
    app.run(debug=True, host='0.0.0.0', port=5000)

