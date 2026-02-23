"""
Personal Expense Tracker Application Factory.
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from config import config

# Initialize extensions
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'


def create_app(config_name='default'):
    """
    Application factory pattern.
    
    Args:
        config_name (str): Configuration name to use
    
    Returns:
        Flask: Configured Flask application
    """
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions with app
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    
    # Register blueprints
    from Personal_Expense_Tracker.routes.auth import auth
    from Personal_Expense_Tracker.routes.dashboard import dashboard
    from Personal_Expense_Tracker.routes.expenses import expenses
    from Personal_Expense_Tracker.routes.admin import admin
    
    app.register_blueprint(auth)
    app.register_blueprint(dashboard)
    app.register_blueprint(expenses)
    app.register_blueprint(admin)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app