from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask import redirect, url_for

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'login'

@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for('login'))
