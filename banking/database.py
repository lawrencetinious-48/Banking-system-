import sqlite3
from typing import List, Optional, Dict, Any
from contextlib import contextmanager
from datetime import datetime
from .models import Client, Transaction

DATABASE_FILE = "client.db"

@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def initialize_database():
    """Initialize database and create tables"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS clients(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    age INTEGER NOT NULL,
                    gender TEXT NOT NULL,
                    email_address TEXT NOT NULL,
                    ID_no TEXT NOT NULL UNIQUE,
                    country TEXT,
                    network TEXT,
                    phone_number TEXT,
                    next_of_kin_name TEXT,
                    next_of_kin_phone TEXT,
                    next_of_kin_network TEXT,
                    balance REAL DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_id INTEGER NOT NULL,
                    transaction_date TEXT NOT NULL,
                    description TEXT NOT NULL,
                    amount REAL NOT NULL,
                    balance REAL NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (client_id) REFERENCES clients(id)
                )
            """)
            print("Database initialized successfully")
    except Exception as error:
        print(f"Failed to initialize database: {error}")
        raise

# ===== Client CRUD Functions =====

def create_client(client_data: Dict[str, Any]) -> int:
    """Inserts a new client into the database."""
    sql = """
        INSERT INTO clients(name, age, gender, email_address, ID_no, country, network, phone_number, balance)
        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, (
            client_data['name'], client_data['age'], client_data['gender'],
            client_data['email'], client_data['ID_no'], client_data['country'],
            client_data['network'], client_data['phone'], client_data['balance']
        ))
        return cursor.lastrowid

def get_client_by_id(client_id: int) -> Optional[Client]:
    """Reads a single client from the database by ID."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clients WHERE id=?", (client_id,))
        row = cursor.fetchone()
        if row:
            return Client(
                client_id=row['id'], name=row['name'], age=row['age'], gender=row['gender'],
                email=row['email_address'], ID_no=row['ID_no'],
                country=row['country'], network=row['network'],
                phone=row['phone_number'], balance=row['balance']
            )
        return None

def get_all_clients() -> List[Client]:
    """Reads all clients from the database."""
    clients = []
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clients")
        for row in cursor.fetchall():
            clients.append(Client(
                client_id=row['id'], name=row['name'], age=row['age'], gender=row['gender'],
                email=row['email_address'], ID_no=row['ID_no'],
                country=row['country'], network=row['network'],
                phone=row['phone_number'], balance=row['balance']
            ))
    return clients

def update_client(client: Client) -> bool:
    """Updates a client's profile in the database."""
    sql = """
        UPDATE clients SET name=?, age=?, gender=?, email_address=?,
        country=?, network=?, phone_number=?, balance=?, updated_at=?
        WHERE id=?
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, (
            client.name, client.age, client.gender, client.email, client.country,
            client.network, client.phone, client.balance, datetime.now(), client.client_id
        ))
        return cursor.rowcount > 0

def delete_client_by_id(client_id: int) -> bool:
    """Deletes a client and their transactions."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM transactions WHERE client_id=?", (client_id,))
        cursor.execute("DELETE FROM clients WHERE id=?", (client_id,))
        return cursor.rowcount > 0

# ===== Transaction CRUD Functions =====

def create_transaction(client_id: int, description: str, amount: float, balance: float) -> None:
    """Save transaction to database and update client balance"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        transaction_date = datetime.now().strftime("%d/%m/%Y")
        
        cursor.execute("""
            INSERT INTO transactions(client_id, transaction_date, description, amount, balance)
            VALUES(?, ?, ?, ?, ?)
        """, 
        (client_id, transaction_date, description, amount, balance)
        )
        
        # Update client balance
        cursor.execute("UPDATE clients SET balance=? WHERE id=?", (balance, client_id))

def get_transactions_by_client_id(client_id: int) -> List[Transaction]:
    """Load transaction history from database"""
    transactions = []
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM transactions WHERE client_id=? ORDER BY created_at DESC",
            (client_id,)
        )
        for row in cursor.fetchall():
            transactions.append(Transaction(
                transaction_id=row['id'],
                client_id=row['client_id'],
                transaction_date=row['transaction_date'],
                description=row['description'],
                amount=row['amount'],
                balance=row['balance']
            ))
    return transactions
