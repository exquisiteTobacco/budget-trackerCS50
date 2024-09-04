from flask import render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_user, login_required, logout_user, current_user
from app import app, db
from app.models import User, Category, Transaction 
from app.premade_categories import create_default_categories
from datetime import datetime , timedelta
from sqlalchemy import func
from werkzeug.security import generate_password_hash, check_password_hash
import re
from calendar import monthrange


def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def is_strong_password(password):
    # At least 8 characters, 1 uppercase, 1 lowercase, 1 digit, 1 special character
    pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
    return re.match(pattern, password) is not None

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Please provide both username and password.')
            return render_template('login.html')
        
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if request.method == 'POST':
        if 'category_name' in request.form:
            category_name = request.form.get('category_name')
            category_type = request.form.get('category_type')
            
            if not category_name or not category_type:
                return jsonify({'success': False, 'message': 'Category name and type are required.'})
            
            if category_type not in ['income', 'expense']:
                return jsonify({'success': False, 'message': 'Invalid category type.'})
            
            new_category = Category(name=category_name, type=category_type, user_id=current_user.id)
            db.session.add(new_category)
            db.session.commit()
            return jsonify({
                'success': True,
                'message': 'Category added successfully',
                'category_id': new_category.id,
                'category_name': new_category.name
            })
        else:
            amount = request.form.get('amount')
            transaction_type = request.form.get('type')
            description = request.form.get('description')
            category_id = request.form.get('category')
            
            if not amount or not transaction_type or not description or not category_id:
                return jsonify({'success': False, 'message': 'All fields are required.'})
            
            try:
                amount = float(amount)
                if amount <= 0:
                    raise ValueError
            except ValueError:
                return jsonify({'success': False, 'message': 'Amount must be a positive number.'})
            
            if transaction_type not in ['income', 'expense']:
                return jsonify({'success': False, 'message': 'Invalid transaction type.'})
            
            category = Category.query.get(category_id)
            if not category or category.user_id != current_user.id:
                return jsonify({'success': False, 'message': 'Invalid category.'})
            
            new_transaction = Transaction(
                amount=abs(amount),
                description=description,
                type=transaction_type,
                date=datetime.now(),
                user_id=current_user.id,
                category_id=category.id
            )
            db.session.add(new_transaction)
            current_user.update_balance(abs(amount), transaction_type)
            db.session.commit()

            return jsonify({
                'success': True, 
                'message': f'{transaction_type.capitalize()} added successfully',
                'new_balance': current_user.balance
            })

    recent_transactions = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.date.desc()).limit(5).all()
    categories = Category.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', balance=current_user.balance, recent_transactions=recent_transactions, categories=categories)


  

@app.route('/get_categories/<transaction_type>')
@login_required

def get_categories(transaction_type):
    if transaction_type not in ['income', 'expense']:
        return jsonify({'error': 'Invalid transaction type'}), 400
    
    categories = Category.query.filter_by(user_id=current_user.id, type=transaction_type).all()
    return jsonify([{'id': cat.id, 'name': cat.name} for cat in categories])

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not username or not email or not password or not confirm_password:
            flash('All fields are required.')
            return render_template('register.html')
        
        if not is_valid_email(email):
            flash('Please enter a valid email address.')
            return render_template('register.html')
        
        if not is_strong_password(password):
            flash('Password must be at least 8 characters long and contain uppercase, lowercase, digit, and special character.')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match.')
            return render_template('register.html')
        
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash('Username or email already exists.')
            return render_template('register.html')
        
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        
        create_default_categories(new_user.id)
        
        flash('Registered successfully. Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/api/monthly_summary')
@login_required
def monthly_summary():
    today = datetime.today()
    start_date = datetime(today.year, today.month, 1)
    end_date = datetime(today.year, today.month, monthrange(today.year, today.month)[1])

    income = db.session.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == current_user.id,
        Transaction.type == 'income',
        Transaction.date.between(start_date, end_date)
    ).scalar() or 0

    expenses = db.session.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == current_user.id,
        Transaction.type == 'expense',
        Transaction.date.between(start_date, end_date)
    ).scalar() or 0

    return jsonify({
        'income': float(income),
        'expenses': float(expenses)
    })

@app.route('/api/expense_distribution')
@login_required
def expense_distribution():
    today = datetime.today()
    start_date = datetime(today.year, today.month, 1)
    end_date = datetime(today.year, today.month, monthrange(today.year, today.month)[1])

    expenses = db.session.query(
        Category.name,
        func.sum(Transaction.amount)
    ).join(Transaction).filter(
        Transaction.user_id == current_user.id,
        Transaction.type == 'expense',
        Transaction.date.between(start_date, end_date)
    ).group_by(Category.name).all()

    return jsonify({
        'labels': [expense[0] for expense in expenses],
        'data': [float(expense[1]) for expense in expenses]
    })
@app.route('/api/spending_trends')
@login_required
def spending_trends():
    end_date = datetime.today()
    start_date = end_date - timedelta(days=30)

    expenses = db.session.query(
        func.date(Transaction.date),
        func.sum(Transaction.amount)
    ).filter(
        Transaction.user_id == current_user.id,
        Transaction.type == 'expense',
        Transaction.date.between(start_date, end_date)
    ).group_by(func.date(Transaction.date)).all()

    return jsonify({
        'labels':[expense[0] for expense in expenses],
        'data':[float(expense[1]) for expense in expenses]
    })