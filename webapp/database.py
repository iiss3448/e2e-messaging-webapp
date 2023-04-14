#!/usr/bin/env python3
from . import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    session_id = db.Column(db.Integer)
    salt = db.Column(db.String(16))