#!/usr/bin/env python3
from flask import *
from .database import *
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
import random

routes = Blueprint('routes', __name__)

@routes.route('/', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form.get("uname")
        pwd = request.form.get("pwd")
        user = User.query.filter_by(username=username).first()
        if user:
            if check_password_hash(user.password, pwd):
                flash("Logged in successfully!", category="success")
                login_user(user, remember=True)
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
    return redirect(url_for("routes.login"))

@routes.route('/home')
@login_required
def home():
    keyid = random.Random().randint(1, 999)
    return render_template('home.html', user=current_user, keyid=keyid)

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
            new_user = User(username=username, password=generate_password_hash(password, method="sha256"))
            db.session.add(new_user)
            db.session.commit()
            flash("Account created successfully.", category="success")
            return redirect(url_for("routes.login"))
    return render_template('signup.html', user=current_user)