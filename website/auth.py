from flask import Blueprint, render_template, redirect, url_for, request, flash
from .models import User, Img, db
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in!')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Wrong password!', category='error')
        else:
            flash('Email does not exist', category='error')

    return render_template('login.html', user=current_user)

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        pic = request.files['pic']
        if not pic:
            flash('No pic uploaded!', category='error')
        filename = secure_filename(pic.filename)
        mimetype = pic.mimetype    
        if not filename or not mimetype:
            flash('Bad upload', category='error')
        img = Img(img=pic.read(), name=filename, mimetype=mimetype, username=username)
        email_exists = User.query.filter_by(email=email).first()
        username_exists = User.query.filter_by(username=username).first()


        if email_exists:
            flash('Email already exists', category='error')
        elif username_exists:
            flash('Username already exists', category='error')
        elif password1 != password2:
            flash('Passwords do not match', category='error')
        elif len(username) < 3:
            flash('Username must be at least 3 characters long', category='error')
        elif len(password1) < 4:
            flash('Password must be at least 4 characters long', category='error')   
        else:
            new_user = User(email=email, username=username, password=generate_password_hash(password1, method='sha256'))
            db.session.add(new_user)
            db.session.add(img)
            db.session.commit()
            login_user(new_user, remember=True)
            return redirect(url_for('views.home'))
            

    return render_template('sign_up.html', user=current_user)

@auth.route('/logout')
@login_required # This is a decorator that requires the user to be logged in to access this route
def logout():
    logout_user()
    return redirect(url_for('views.home'))
