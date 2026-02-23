"""
Authentication routes for user registration and login.
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from Personal_Expense_Tracker import db, bcrypt
from Personal_Expense_Tracker.models import User
from Personal_Expense_Tracker.forms import RegistrationForm, LoginForm

# Create blueprint
auth = Blueprint('auth', __name__, url_prefix='/auth')


@auth.route('/register', methods=['GET', 'POST'])
def register():
    """
    User registration route.
    
    GET: Display registration form
    POST: Process registration data
    
    Returns:
        rendered template or redirect
    """
    # Redirect if already logged in
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if username or email exists
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already exists!', 'danger')
            return render_template('auth/register.html', title='Register', form=form)
        
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already registered!', 'danger')
            return render_template('auth/register.html', title='Register', form=form)
        
        # Create new user
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, 
                   email=form.email.data, 
                   password_hash=hashed_password)
        
        # First user becomes admin
        if User.query.count() == 0:
            user.role = 'admin'
        
        db.session.add(user)
        db.session.commit()
        
        flash('Account created! You can now login.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', title='Register', form=form)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    """
    User login route.
    
    GET: Display login form
    POST: Process login credentials
    
    Returns:
        rendered template or redirect
    """
    # Redirect if already logged in
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and bcrypt.check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash('Login successful!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('dashboard.index'))
        else:
            flash('Login failed! Check email and password.', 'danger')
    
    return render_template('auth/login.html', title='Login', form=form)


@auth.route('/logout')
def logout():
    """
    User logout route.
    
    Returns:
        redirect: To login page
    """
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))