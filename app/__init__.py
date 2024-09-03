import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///budget_tracker.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Set a default secret key, but allow it to be overridden by an environment variable
default_secret_key = 'dev_secret_key_change_this_in_production'
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', default_secret_key)

# Add a warning if using the default secret key
if app.config['SECRET_KEY'] == default_secret_key:
    app.logger.warning('WARNING: Using default secret key. This should be changed in production.')

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

from app import routes, models