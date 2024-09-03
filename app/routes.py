from flask import render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_user, login_required, logout_user, current_user
from app import app, db
from app.models import User, Category, Transaction
from app.premade_categories import create_default_categories
from datetime import datetime
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