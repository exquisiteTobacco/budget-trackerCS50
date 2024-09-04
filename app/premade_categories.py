from app import db
from app.models import Category

DEFAULT_CATEGORIES = [
    # Income categories
    ("Salary", "income"),
    ("Freelance", "income"),
    ("Investments", "income"),
    ("Gifts", "income"),
    
    # Expense categories
    ("Housing", "expense"),
    ("Utilities", "expense"),
    ("Groceries", "expense"),
    ("Transportation", "expense"),
    ("Healthcare", "expense"),
    ("Insurance", "expense"),
    ("Dining Out", "expense"),
    ("Entertainment", "expense"),
    ("Shopping", "expense"),
    ("Education", "expense"),
    ("Personal Care", "expense"),
    ("Debt Payments", "expense"),
    ("Savings", "expense"),
    ("Charity/Donations", "expense")
]

def create_default_categories(user_id):
    for category_name, category_type in DEFAULT_CATEGORIES:
        category = Category(name=category_name, type=category_type, user_id=user_id)
        db.session.add(category)
    db.session.commit()