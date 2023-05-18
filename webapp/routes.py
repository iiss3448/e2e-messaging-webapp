#!/usr/bin/env python3
from io import BytesIO
from flask import *
from .database import *
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
import random
import os
from base64 import b64encode
from sqlalchemy import desc

routes = Blueprint('routes', __name__)

@routes.route('/', methods=['GET'])
def home():
    return render_template('home.html')

@routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form.get("uname")
        pwd = request.form.get("pwd")
        user = User.query.filter_by(username=username).first()
        if user:
            if check_password_hash(user.password, pwd + user.salt):
                flash("Logged in successfully!", category="success")
                login_user(user, remember=True)
                return redirect(url_for("routes.chat_page"))
            else:
                flash("Incorrect password!", category="error")
        else:
            flash("Username does not exist!", category="error")
    return render_template('login.html', user=current_user)

@routes.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for("routes.login"))

@routes.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get("uname")
        password = request.form.get("pwd")
        confirm_password = request.form.get("cpwd")

        user = User.query.filter_by(username=username).first()
        if user:
            flash("Username is taken!", category="error")
        
        if len(username) < 3:
            flash("Username must be at least 3 characters long.", category="error")
        elif len(password) < 5:
            flash("Password must be at least 5 characters long.", category="error")
        elif password != confirm_password:
            flash("Passwords do not match.", category="error")
        else:
            salt = os.urandom(16)
            salt = b64encode(salt).decode()
            new_user = User(username=username, password=generate_password_hash(password + salt, method="sha256"), salt=salt)
            db.session.add(new_user)
            db.session.commit()
            flash("Account created successfully.", category="success")
            return redirect(url_for("routes.login"))
    return render_template('signup.html', user=current_user)

@routes.route('/chat-page')
@login_required
def chat_page():
    keyid = random.Random().randint(1, 999)
    return render_template('chat_page.html', user=current_user, keyid=keyid)

@routes.route('/knowledge-hub', methods=['GET', 'POST'])
@login_required
def knowledge_hub():
    all_resources = db.session.query(Resource).order_by(desc(Resource.timestamp)).all()
    if request.method == 'POST' and not resources is None:
        file = request.files['file']
        resource = Resource(filename=file.filename, data=file.read())
        db.session.add(resource)
        db.commit()
        flash("Resource uploaded successfully.", category="success")
    if resources is None:
        resources = []
    return render_template('knowledge_hub.html', resources=all_resources, user=current_user)

@routes.route('/download/<upload_id>')
def download(upload_id):
    upload = Resource.query.filter_by(id=upload_id).first()
    return send_file(BytesIO(upload.data), attachment_filename=upload.filename, as_attachment=True)
