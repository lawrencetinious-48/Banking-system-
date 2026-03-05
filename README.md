# Banking Management System

A Python-based banking management system with SQLite storage for managing client accounts and transactions.

## Features

- Create and manage client accounts
- Perform deposits and withdrawals
- View transaction history
- Update client profile information
- Search clients by ID or name
- Delete client accounts
- Phone number validation with country and carrier detection

## Installation & Setup

### Prerequisites

- Python 3.8+

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run the Application

```bash
# Run using package syntax
python -m banking

# Or run directly
python banking/cli.py
```

## Usage

Upon launching, you'll see the main menu with options to:
1. Create a new client account
2. Access an existing client account
3. View all clients
4. Search for a client
5. Delete a client account

## Project Structure

```
banking/
├── __init__.py     # Package marker
├── __main__.py     # Entry point
├── models.py       # Data classes (Client, Transaction)
├── database.py     # Data Access Layer
├── services.py     # Business logic
└── cli.py          # User interface
```

## Dependencies

- cowsay==5.0
- phonenumbers==8.12.52
