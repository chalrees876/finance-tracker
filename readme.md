# Budget Tracker

A Django-based personal finance application that helps you manage your money using zero-based budgeting principles. Track your income, expenses, and budget allocations with an intuitive interface inspired by modern financial tools.

## Features

- Zero-based budgeting system
- Real-time budget tracking and reporting
- Transaction management with payee and account tracking
- Category-based budget organization
- Monthly budget rollovers
- Secure user authentication
- Responsive design for all devices

## Quick Start

### Prerequisites

- Python 3.8+
- Django 4.2+
- PostgreSQL (recommended) or SQLite

### Installation

1. Clone the repository:
https://github.com/chalrees876/finance-tracker.git
cd FinanceTracker
2. Create a virtual environment:
python -m venv venv
source venv/bin/activate
3. instll dependencies:
pip install -r requirements.txt
4. Set up your database:
python manage.py migrate
5. Create a superuser (optional)
python manage.py createsuperuser
6. Run the dev server:
python manage.py runserver
7. Visit `http://localhost:8000` in your browser

### Default Setup

New users automatically get starter categories including:

- Bills (Rent, Utilities, Groceries)
- Needs Expenses (Healthcare, Maintenance)
- Wants (Dining, Entertainment)
- Future Planning (Savings, Investments)

Plus default checking and savings accounts.

## Project Structure
FinanceTracker/
├── tracker/ # Main Django application
├── templates/ # HTML templates
├── static/ # CSS and static files
├── manage.py
└── requirements.txt

## Key Models

- Accounts: Bank accounts and credit cards
- Categories: Budget categories organized in groups
- Transactions: Income and expense records
- BudgetAllocations: Monthly budget plans
- Payees: Transaction counterparts

## Development

This project uses:

- Django 5.2 for the web framework
- PostgreSQL for data persistence
- HTML/CSS for the frontend
- Django templates for rendering

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see LICENSE file for details.

---

For questions or support, please open an issue in the GitHub repository.
