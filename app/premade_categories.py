from app import db
from app.models import Category

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