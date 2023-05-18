#!/usr/bin/env python3
from . import db
from flask_login import UserMixin
from datetime import datetime
from sqlalchemy import desc

now = datetime.now()
tm = datetime.timestamp(now)
formatted_tm = datetime.fromtimestamp(tm).strftime('%Y-%m-%d-%H:%M:%S')

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    session_id = db.Column(db.Integer)
    salt = db.Column(db.String(16))

class Resource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255))
    op = db.Column(db.String(255), db.ForeignKey('user.username'))
    title = db.Column(db.String(255))
    data = db.Column(db.LargeBinary)
    timestamp = db.Column(db.DateTime, default=formatted_tm)