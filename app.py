import os
from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)

# Load configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///budget_tracker.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Set a default secret key, but allow it to be overridden by an environment variable
default_secret_key = 'dev_secret_key_change_this_in_production'
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', default_secret_key)

# Add a warning if using the default secret key
if app.config['SECRET_KEY'] == default_secret_key:
    app.logger.warning('WARNING: Using default secret key. This should be changed')

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    balance = db.Column(db.Float, default=0.0)  
    categories = db.relationship('Category', backref='user', lazy=True)
    transactions = db.relationship('Transaction', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def update_balance(self, amount, transaction_type):
        if transaction_type == 'income':
            self.balance += amount
        elif transaction_type == 'expense':
            self.balance -= amount
    
    def __repr__(self):
        return f'<User {self.username}>'

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    transactions = db.relationship('Transaction', backref='category', lazy=True)

    def __repr__(self):
        return f'<Category {self.name}>'

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200))
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    type = db.Column(db.String(10), nullable=False)  # 'income' or 'expense'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)

    def __repr__(self):
        return f'<Transaction {self.id}: {self.amount}>'

@login_manager.user_loader # this returns the user object by identifying it by user id. crucial for flask_login behind the scenes :D.
def load_user(user_id):
    return User.query.get(int(user_id))
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))
from flask import render_template, request, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if request.method == 'POST':
        if 'category_name' in request.form:
            # Handle new category creation
            category_name = request.form['category_name']
            new_category = Category(name=category_name, user_id=current_user.id)
            db.session.add(new_category)
            db.session.commit()
            return jsonify({
                'success': True,
                'message': 'Category added successfully',
                'category_id': new_category.id,
                'category_name': new_category.name
            })
        else:
            # Handle new transaction
            amount = float(request.form['amount'])
            transaction_type = request.form['type']
            description = request.form['description']
            category_id = int(request.form['category'])

            new_transaction = Transaction(
                amount=abs(amount),
                description=description,
                type=transaction_type,
                date=datetime.utcnow(),
                user_id=current_user.id,
                category_id=category_id
            )
            db.session.add(new_transaction)

            # Update user's balance
            current_user.update_balance(abs(amount), transaction_type)

            db.session.commit()

            return jsonify({
                'success': True, 
                'message': f'{transaction_type.capitalize()} added successfully',
                'new_balance': current_user.balance
            })

    # Get recent transactions
    recent_transactions = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.date.desc()).limit(5).all()

    # Get categories for the form
    categories = Category.query.filter_by(user_id=current_user.id).all()

    return render_template('dashboard.html', balance=current_user.balance, recent_transactions=recent_transactions, categories=categories)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        user = User.query.filter((User.username == username) | (User.email == email)).first()
        if user:
            flash('Username or email already exists')
        else:
            new_user = User(username=username, email=email)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            
            # Create default categories for the new user
            create_default_categories(new_user.id)
            
            flash('Registered successfully')
            return redirect(url_for('login'))
    return render_template('register.html')

if __name__ == '__main__':
    app.run(debug=True)

from app import db
from app.models import Category, User

DEFAULT_CATEGORIES = [
    # Income categories
    "Salary",
    "Freelance",
    "Investments",
    "Gifts",
    
    # Expense categories
    "Housing",
    "Utilities",
    "Groceries",
    "Transportation",
    "Healthcare",
    "Insurance",
    "Dining Out",
    "Entertainment",
    "Shopping",
    "Education",
    "Personal Care",
    "Debt Payments",
    "Savings",
    "Charity/Donations"
]

def create_default_categories(user_id):
    for category_name in DEFAULT_CATEGORIES:
        category = Category(name=category_name, user_id=user_id)
        db.session.add(category)
    db.session.commit()