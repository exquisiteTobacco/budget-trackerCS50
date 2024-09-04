


# Budget Tracker

Budget Tracker is a web-based application designed to help users manage their personal finances effectively. Built with Flask and SQLAlchemy, this application provides an intuitive interface for tracking income, expenses, and overall financial health.

## Project Overview

The Budget Tracker application allows users to:

- Register and log in securely
- Add and categorize income and expenses
- View their current balance
- Analyze their spending habits through various charts
- Manage custom categories for transactions

## File Structure and Functionality

### `run.py`
This is the entry point of the application. It imports the Flask app instance and runs it in debug mode when executed directly.

### `createDB.py`
This script is responsible for creating the database tables. It should be run once before starting the application for the first time.

### `app/__init__.py`
This file initializes the Flask application and sets up important configurations:
- Configures the SQLAlchemy database URI
- Sets up the secret key for session management
- Initializes SQLAlchemy and Flask-Login

### `app/premade_categories.py`
This file contains a list of default categories for income and expenses. It also includes a function to create these categories for new users, ensuring they have a starting point for categorizing their transactions.

### `app/models.py`
This file defines the database models using SQLAlchemy:
- `User`: Represents a user of the application, storing credentials and balance
- `Category`: Represents transaction categories (income or expense)
- `Transaction`: Represents individual financial transactions

The `User` model includes methods for password hashing, balance updates, and user authentication.

### `app/routes.py`
This file contains all the route definitions and their corresponding logic:
- Authentication routes (login, logout, register)
- Dashboard route for the main application interface
- API routes for fetching data for charts (monthly summary, expense distribution, spending trends)
- Routes for adding new transactions and categories

### HTML Templates
- `login.html` and `register.html`: Provide forms for user authentication
- `dashboard.html`: The main interface where users interact with their financial data
- `index.html`: The landing page introducing the application
- `base.html`: The base template that other templates extend, providing a consistent layout

## Data Visualization with Chart.js

This project utilizes Chart.js, a powerful and flexible JavaScript charting library, to create interactive and visually appealing financial visualizations. Chart.js was chosen for its ease of use, responsiveness, and wide range of chart types.

### Implementation Details

- **Chart Types**: The application uses various chart types to represent financial data:
  - Bar charts for monthly income vs expenses comparison
  - Pie charts for expense distribution across categories
  - Line charts for spending trends over time

- **Data Flow**: Chart data is fetched from the server via AJAX calls to our API endpoints (e.g., `/api/monthly_summary`, `/api/expense_distribution`, `/api/spending_trends`). This approach ensures that charts always display the most up-to-date information without requiring a full page reload.

- **Responsive Design**: Chart.js automatically adjusts chart sizes based on the user's device, ensuring a consistent experience across desktop and mobile platforms.

- **Interactivity**: Users can interact with the charts (e.g., hovering over data points for more information), providing a more engaging and informative experience.

### Chart Customization

The charts have been customized to match the overall design aesthetic of the Budget Tracker application. This includes:

- Custom color schemes that are consistent with the application's theme
- Formatted tooltips that display currency values and percentages in a user-friendly manner
- Animations to make the data presentation more engaging

By leveraging Chart.js, the Budget Tracker provides users with intuitive, at-a-glance insights into their financial data, making it easier to understand spending patterns and make informed financial decisions.

## Design Choices and Rationale

1. **Flask Framework**: Chosen for its simplicity and flexibility, allowing for rapid development of web applications.

2. **SQLAlchemy ORM**: Used for database interactions, providing an abstraction layer that simplifies data management and allows for easy switching between database systems if needed in the future.

3. **Flask-Login**: Implemented for user session management, offering secure and easy-to-use authentication.

4. **Chart.js**: Selected for its robust features, ease of integration, and ability to create responsive, interactive charts that enhance data visualization.

5. **RESTful API Design**: Implemented API endpoints (e.g., `/api/monthly_summary`) to serve data for charts. This separation of concerns allows for potential future expansion, such as mobile app integration.

6. **Default Categories**: Provided a set of predefined categories to improve user onboarding, while still allowing for custom categories to be added.

7. **Password Security**: Implemented password hashing and validation rules to ensure user account security.

8. **Responsive Design**: The application, including charts, is designed to be responsive, accommodating various device sizes for a consistent user experience.

## Future Enhancements

1. **Budget Goals**: Implement a feature for users to set and track budget goals for different categories.

2. **Data Export**: Add functionality to export financial data for use in other applications or for record-keeping.

3. **Recurring Transactions**: Allow users to set up recurring transactions for regular income or expenses.

4. **Multi-Currency Support**: Expand the application to handle multiple currencies for international users.

5. **Financial Insights**: Implement more advanced analytics to provide personalized financial advice based on spending patterns.

6. **Advanced Chart Interactions**: Enhance Chart.js implementations to allow for more complex interactions, such as drilling down into specific data points or comparing multiple time periods.

## Getting Started

1. Clone the repository
2. Install required dependencies (consider adding a `requirements.txt` file)
3. Run `createDB.py` to initialize the database
4. Run `run.py` to start the application
5. Access the application through your web browser at `http://localhost:5000`

## Security Considerations

- The application uses environment variables for sensitive information like the database URL and secret key.
- Passwords are hashed before storage using werkzeug's security functions.
- Input validation is performed on the server-side to prevent malicious inputs.

Remember to replace the default secret key with a strong, unique key in a production environment, and ensure all debugging features are disabled before deployment.