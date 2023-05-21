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
from datetime import datetime

routes = Blueprint('routes', __name__)
keyid = None

@routes.route('/', methods=['GET'])
def home():
    return render_template('home.html', user=current_user)

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
                keyid = random.Random().randint(1, 999)
                return redirect(url_for("routes.home"))
            else:
                flash("Incorrect password!", category="error")
        else:
            flash("Username does not exist!", category="error")
    return render_template('login.html', user=current_user)

@routes.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out successfully!")
    return redirect(url_for("routes.home"))

@routes.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get("uname")
        password = request.form.get("pwd")
        confirm_password = request.form.get("cpwd")
        admin_confirmation = False

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
            staff_name = request.form.get("staff_name")
            staff_id = request.form.get("staff_id")
            if len(staff_name) > 0 or len(staff_id) > 0:
                csv = open("staff.csv", "r").readlines()
                details = f"{staff_name},{staff_id}\n"
                if details in csv:
                    admin_confirmation = True
                else:
                    flash("Incorrect admin credentials entered.", category="error")
                    return render_template('signup.html', user=current_user)
            salt = os.urandom(16)
            salt = b64encode(salt).decode()
            new_user = User(username=username, password=generate_password_hash(
                password + salt, method="sha256"), salt=salt, is_admin=admin_confirmation)
            db.session.add(new_user)
            db.session.commit()
            flash("Account created successfully. Log in to continue!", category="success")
            return redirect(url_for("routes.login"))
    return render_template('signup.html', user=current_user)

@routes.route('/chat-page')
@login_required
def chat_page():
    return render_template('chat_page.html', user=current_user, keyid=keyid)

@routes.route('/knowledge-hub', methods=['GET', 'POST'])
@login_required
def knowledge_hub():
    if request.method == 'POST':
        now = datetime.now()
        file = request.files['file']
        resource = Resource(filename=file.filename, data=file.read(), timestamp=now, title=request.form.get("title-box"), op=current_user.username)
        db.session.add(resource)
        db.session.commit()
        flash("Resource uploaded successfully.", category="success")
    all_resources = db.session.query(Resource).order_by(desc(Resource.timestamp)).all()
    return render_template('knowledge_hub.html', resources=all_resources, user=current_user)

@routes.route('/download/<upload_id>')
def download(upload_id):
    upload = Resource.query.filter_by(id=upload_id).first()
    return send_file(BytesIO(upload.data), download_name= upload.filename, as_attachment=True)

@routes.route('/admin-tools', methods=['GET', 'POST'])
@login_required
def admin_tools():
    if request.method == "POST":
        if request.form.get("uid"):
            uid = request.form.get("uid")
            User.query.filter(User.id == uid).delete()
            db.session.commit()
        elif request.form.get("rid"):
            rid = request.form.get("rid")
            Resource.query.filter(Resource.id == rid).delete()
            db.session.commit()
    all_resources = db.session.query(Resource).order_by(Resource.id).all()
    all_users = db.session.query(User).order_by(User.id).all()
    return render_template('admin_tools.html', user=current_user, resources=all_resources, users=all_users)
