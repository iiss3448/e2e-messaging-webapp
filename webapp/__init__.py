#!/usr/bin/env python3
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
DB_NAME = "database.db"

def initialise():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = "lndoiwbhf9012hr9riupfchi"  # Encryption
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DB_NAME}"
    db.init_app(app)

    from .routes import routes
    app.register_blueprint(routes, url_prefix="/")

    from .database import User
    with app.app_context():
        db.create_all()
    
    login_manager = LoginManager()
    login_manager.login_view = "routes.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app
