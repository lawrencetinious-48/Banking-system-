# Banking System Refactoring Documentation

This document explains the architectural changes made to the Banking Management System, the reasoning behind each decision, and suggestions for further improvements.

---

## Summary of Changes

The original monolithic `banking.py` file (~620 lines) was refactored into a modular Python package structure following the recommendations in `review.md`.

### Before (Single File)
```
banking.py          # Everything in one file
```

### After (Modular Package)
```
banking/
├── __init__.py     # Package marker
├── __main__.py     # Entry point (python -m banking)
├── models.py       # Data classes (Client, Transaction)
├── database.py     # Data Access Layer (CRUD operations)
├── services.py     # Business logic (TransactionService)
└── cli.py          # User interface
requirements.txt    # Dependency management
```

---

## Detailed Changes

### 1. Package Structure Created

**What Changed:**
- Created `banking/` directory as a Python package
- Added `__init__.py` to mark it as a package
- Added `__main__.py` to allow `python -m banking` execution

**Why This Approach:**
- Enables running the application with `python -m banking`
- Standard Python package convention
- Makes the codebase pip-installable in the future

---

### 2. Models Separated (`models.py`)

**What Changed:**
- Extracted `Client` and `Transaction` classes to `models.py`
- Removed database methods from `Client` class (no more `save_to_db()`, `get_by_id()`, `get_all()`)
- Classes now serve as pure data containers (POPOs - Plain Old Python Objects)

**Original Code (banking.py:79-179):**
```python
class Client:
    def save_to_db(self) -> bool:  # Database logic mixed with model
        ...
    @staticmethod
    def get_by_id(client_id: int):  # More database logic
        ...
```

**New Code (models.py):**
```python
class Client:
    # Pure data container - no database methods
    def to_dict(self) -> dict:
        ...
```

**Why This Approach:**
- **Single Responsibility Principle**: Models only represent data structure
- **Testability**: Can test models without database dependency
- **Reusability**: Models can be used with different storage backends

---

### 3. Data Access Layer Created (`database.py`)

**What Changed:**
- All database operations consolidated into dedicated functions
- Created explicit CRUD functions:
  - `create_client()` - Insert new client
  - `get_client_by_id()` - Read single client
  - `get_all_clients()` - Read all clients
  - `update_client()` - Update client
  - `delete_client_by_id()` - Delete client and transactions
  - `create_transaction()` - Insert transaction
  - `get_transactions_by_client_id()` - Read transaction history
- Preserved the excellent `get_db_connection()` context manager

**Why This Approach:**
- **Centralized SQL**: All queries in one place for easy maintenance
- **Database Agnostic**: Switching from SQLite to PostgreSQL requires changes only here
- **Clear API**: Functions document exactly what database operations are available
- **Transaction Safety**: Proper rollback handling via context manager

---

### 4. Business Logic Extracted (`services.py`)

**What Changed:**
- Created `TransactionService` class to handle banking operations
- Encapsulates deposit, withdrawal, and balance logic
- Coordinates between models and database layer

**Original Code (banking.py:274-382):**
```python
class Transactions:
    # Mixed concerns: business logic + database + regex parsing
    pattern = r"(\d{2}/\d{2}/\d{4})\s+..."
    def _save_transaction(self, ...):
        with get_db_connection() as conn:  # Direct DB access
            ...
```

**New Code (services.py):**
```python
class TransactionService:
    def deposit(self, amount: float) -> bool:
        # Pure business logic
        self.client.balance += amount
        db.create_transaction(...)  # Delegates to DAL
```

**Why This Approach:**
- **Separation of Concerns**: Business rules isolated from infrastructure
- **Testability**: Can mock database layer for unit testing
- **Clarity**: Business logic is explicit and easy to understand

---

### 5. CLI Simplified (`cli.py`)

**What Changed:**
- User interface code kept in dedicated file
- Uses `if/elif` instead of `match/case` for broader Python compatibility
- Imports and uses services/database modules

**Why if/elif Over match/case:**
- `match/case` requires Python 3.10+
- `if/elif` works with Python 3.8+ (more compatible)
- Functionally equivalent for this use case

---

### 6. Dependencies Documented (`requirements.txt`)

**What Changed:**
- Created `requirements.txt` with pinned versions:
  ```
  cowsay==5.0
  phonenumbers==8.12.52
  ```

**Why This Approach:**
- Reproducible installations with `pip install -r requirements.txt`
- Version pinning prevents breaking changes
- Standard Python practice for dependency management

---

## Nitpicks and Minor Issues

### In `services.py`

1. **Double update on transaction (lines 15-16):**
   ```python
   db.create_transaction(...)  # Already updates balance in database
   db.update_client(self.client)  # Redundant update
   ```
   The `create_transaction()` function in `database.py:149-150` already updates the client balance. The second `update_client()` call is redundant.

2. **Inconsistent balance formatting:**
   - Original used `.3f` and `.4f` in some places
   - Current code uses `.2f` consistently (good)

### In `cli.py`

1. **Inefficient search by name (lines 209-216):**
   ```python
   clients = db.get_all_clients()
   for client in clients:
       if client.name.lower() == name:
   ```
   Comment at line 211 acknowledges this. Consider adding a `get_client_by_name()` function to `database.py`.

2. **Unused LOG_FILE constant (line 13):**
   Referenced at line 305 but the log viewing feature doesn't actually write logs anywhere. This is carried over from the original code.

3. **Unused import (line 4):**
   `cowsay` is imported but only used once at exit. Consider moving the import inside the function.

### In `database.py`

1. **Missing index on transactions table:**
   The `client_id` column in the `transactions` table would benefit from an index for faster queries:
   ```sql
   CREATE INDEX IF NOT EXISTS idx_transactions_client_id ON transactions(client_id);
   ```

2. **Inconsistent error handling:**
   - `initialize_database()` uses `raise` after printing error
   - Other functions silently return `None` or `False`
   Consider consistent error handling strategy.

### In `models.py`

1. **Unused import (line 1):**
   ```python
   from typing import List, Optional, Dict
   ```
   `List` and `Dict` are imported but not used.

---

## Code That Was Removed

### 1. `get_next_of_kin()` Function
The original code had a `get_next_of_kin()` function (lines 251-272) that was never called in the main flow. It was correctly removed as dead code.

### 2. `parse_transaction_text()` Method
The `Transactions` class had a regex-based text parser (original lines 356-365) that was never used. Correctly removed.

### 3. Assertion in client_menu
Original code had:
```python
assert client.client_id is not None, "Client must have an ID"
```
Replaced with proper control flow. Assertions shouldn't be used for runtime validation.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                       cli.py                            │
│                   (User Interface)                      │
│         Input validation, menus, display                │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                    services.py                          │
│                  (Business Logic)                       │
│        TransactionService: deposit, withdraw            │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                    database.py                          │
│                (Data Access Layer)                      │
│         CRUD operations, SQL queries                    │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                    models.py                            │
│                   (Data Models)                         │
│           Client, Transaction (POPOs)                   │
└─────────────────────────────────────────────────────────┘
```

---

## Running the Application

```bash
# Install dependencies
pip install -r requirements.txt

# Run using package syntax
python -m banking

# Or run directly
python banking/cli.py
```

---

## Recommended Future Improvements

1. **Add Unit Tests**: Create `tests/` directory with pytest tests for each module
2. **Add Logging**: Replace print statements with proper logging module
3. **Add Configuration**: Use environment variables or config file for database path
4. **Add Type Checking**: Run mypy for static type analysis
5. **Add Input Sanitization**: Strengthen email validation with regex or email-validator library
6. **Add Database Migrations**: Consider using alembic for schema changes
7. **Add Search by Name**: Implement efficient name search in database layer

---

## Files Changed Summary

| File | Status | Description |
|------|--------|-------------|
| `banking.py` | Deleted | Original monolithic file |
| `banking/__init__.py` | Created | Package marker (empty) |
| `banking/__main__.py` | Created | Package entry point |
| `banking/models.py` | Created | Data classes |
| `banking/database.py` | Created | Data access layer |
| `banking/services.py` | Created | Business logic |
| `banking/cli.py` | Created | User interface |
| `requirements.txt` | Created | Dependencies |
| `.gitignore` | Created | Git ignore rules |
