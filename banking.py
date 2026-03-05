# ==================== Project Details ====================
# Date: 2026-01-28 (Updated: )
# By: Mulindwa Lawrence Tinious
# Project: Banking Management System (Storage: SQLite)
# Notes: Enhanced with bug fixes, refactoring, and new features

import sqlite3 
from typing import List, Optional, Dict, Tuple
import re
import sys
from contextlib import contextmanager
from datetime import datetime
import cowsay
import phonenumbers as pn
from phonenumbers import geocoder, carrier

# ===== Configuration =====
TRANSACTION_FILE = "client.json"
DATABASE_FILE = "client.db"
DEFAULT_PHONE = "+256709862572"
LOG_FILE = "banking.log"

# ===== Database Management =====
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

initialize_database()
class Client:
    """Represents a bank client"""
    def __init__(self, name: str, age: int, gender: str, email: str, 
                 ID_no: str, country: str = "", network: str = "", 
                 phone: str = "", client_id: Optional[int] = None, balance: float = 0.0):
        self.client_id = client_id
        self.name = name
        self.age = int(age)
        self.gender = gender
        self.email = email
        self.ID_no = ID_no
        self.country = country
        self.network = network
        self.phone = phone
        self.balance = float(balance)

    def __str__(self) -> str:
        return (
            f"ID: {self.client_id} | Name: {self.name} | Age: {self.age} | Gender: {self.gender} | "
            f"Email: {self.email} | Country: {self.country} | Balance: {self.balance:.2f}"
        )

    def to_dict(self) -> dict:
        return {
            "client_id": self.client_id,
            "name": self.name,
            "age": self.age,
            "gender": self.gender,
            "email": self.email,
            "ID_no": self.ID_no,
            "country": self.country,
            "network": self.network,
            "phone": self.phone,
            "balance": self.balance
        }
    
    def save_to_db(self) -> bool:
        """Save or update client in database"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                if self.client_id:  # Update
                    cursor.execute("""
                        UPDATE clients SET name=?, age=?, gender=?, email_address=?,
                        country=?, network=?, phone_number=?, balance=?, updated_at=?
                        WHERE id=?
                    """, (self.name, self.age, self.gender, self.email, self.country,
                          self.network, self.phone, self.balance, datetime.now(), self.client_id))
                    self.client_id
                else:  # Insert
                    cursor.execute("""
                        INSERT INTO clients(name, age, gender, email_address, ID_no,
                        country, network, phone_number, balance)
                        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (self.name, self.age, self.gender, self.email, self.ID_no,
                          self.country, self.network, self.phone, self.balance))
                    self.client_id = cursor.lastrowid
            return True
        except Exception as error:
            f"Failed to save client: {error}"
            return False

    @staticmethod
    def get_by_id(client_id: int) -> Optional['Client']:
        """Retrieve client from database by ID"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM clients WHERE id=?", (client_id,))
                row = cursor.fetchone()
                if row:
                    return Client(
                        name=row['name'], age=row['age'], gender=row['gender'],
                        email=row['email_address'], ID_no=row['ID_no'],
                        country=row['country'], network=row['network'],
                        phone=row['phone_number'], client_id=row['id'], 
                        balance=row['balance']
                    )
        except Exception as error:
            f"Failed to retrieve client: {error}"
        return None

    @staticmethod
    def get_all() -> List['Client']:
        """Retrieve all clients from database"""
        clients = []
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM clients")
                for row in cursor.fetchall():
                    clients.append(Client(
                        name=row['name'], age=row['age'], gender=row['gender'],
                        email=row['email_address'], ID_no=row['ID_no'],
                        country=row['country'], network=row['network'],
                        phone=row['phone_number'], client_id=row['id'],
                        balance=row['balance']
                    ))
        except Exception as error:
            f"Failed to retrieve clients: {error}"
        return clients

# ===== Input Validation Helpers =====
def get_name() -> str:
    """Get and validate user name"""
    while True:
        user_name = input("Enter your name: ").title().strip()
        if not user_name:
            print("Name cannot be empty.")
            continue
        if not user_name.replace(" ", "").isalpha():
            print("Invalid name. Use letters only.")
            continue
        return user_name

def get_age() -> int:
    """Get and validate user age"""
    while True:
        try:
            age = int(input("Enter your age: ").strip())
            if 18 <= age <= 120:
                return age
            print("Age must be between 18 and 120.")
        except ValueError:
            print("Invalid age. Please enter a number.")

def get_gender() -> str:
    """Get and validate user gender"""
    genders = ["male", "female", "other"]
    while True:
        user_input = input(f"Enter your gender {genders}: ").strip().lower()
        if user_input in genders:
            return user_input
        print(f"Invalid input. Choose from {genders}.")

def get_email() -> str:
    """Get and validate user email"""
    while True:
        user_email = input("Enter your email: ").strip().lower()
        if "@" in user_email and "." in user_email and len(user_email) > 5:
            return user_email
        print("Invalid email format.")

def get_ID_no() -> str:
    """Get and validate National ID"""
    while True:
        user_input = input("Enter your National ID (9 digits): ").strip()
        if user_input.isdigit() and len(user_input) == 9:
            return user_input
        print("Invalid National ID. Must be 9 digits.")

def get_phone_info() -> Dict[str, str]:
    """Get and validate phone number information"""
    while True:
        user_input = input(f"Enter your phone number (e.g. {DEFAULT_PHONE}): ").strip()
        try:
            user_number = pn.parse(user_input)
            if not pn.is_valid_number(user_number):
                print("Invalid phone number.")
                continue
            
            location = geocoder.description_for_number(user_number, "en")
            network = carrier.name_for_number(user_number, "en")
            
            return {
                "country": location or "Unknown",
                "network": network or "Unknown",
                "phone": pn.format_number(user_number, pn.PhoneNumberFormat.INTERNATIONAL)
            }
        except pn.NumberParseException:
            print("Invalid phone number format.")

def get_next_of_kin() -> Optional[Dict[str, str]]:
    print("\n--- Next of Kin Information ---")
    add_kin = input("Do you want to add next of kin? (yes/no): ").strip().lower()
    if add_kin != 'y':
        return None
    
    while True:
        try:
            user_name = input("Enter next of kin name: ").title().strip()
            if not user_name or not user_name.isalpha():
                print("Invalid name. Use letters only.")
                continue
            
            phone_info = get_phone_info()
            return {
                "name": user_name,
                "phone": phone_info["phone"],
                "network": phone_info["network"]
            }
        except Exception as error:
            print(f"Error getting next of kin: {error}")
            print("Error processing next of kin information.")

# ===== Transactions Management =====
class Transactions:
    """Manages client transactions"""
    pattern = r"(\d{2}/\d{2}/\d{4})\s+(.+?)\s+(-?\d+\.\d{2})\s+(\d+\.\d{2})"

    def __init__(self, client_id: int, balance: float = 0.0):
        self.client_id = client_id
        self.balance = balance
        self.transaction_history: List[Dict] = []
        self.load_transactions()

    def load_transactions(self) -> None:
        """Load transaction history from database"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM transactions WHERE client_id=? ORDER BY created_at DESC",
                    (self.client_id,)
                )
                for row in cursor.fetchall():
                    self.transaction_history.append({
                        "date": row['transaction_date'],
                        "description": row['description'],
                        "amount": row['amount'],
                        "balance": row['balance']
                    })
        except Exception as error:
            print(f"failed to load transactions: {error}")

    def deposit(self, amount: float) -> bool:
        try:
            if amount <= 0:
                print("Deposit amount must be positive.")
                return False
            
            self.balance += amount
            self._save_transaction("Deposit", amount)
            print(f"Deposit successful. New balance: {self.balance:.3f}")
            return True
        except Exception as error:
            print(f"Deposit failed: {error}")
            return False

    def withdraw(self, amount: float) -> bool:
        try:
            if amount <= 0:
                print("Withdrawal amount must be positive.")
                return False
            if amount > self.balance:
                print(f"Insufficient funds. Available balance: {self.balance:.3f}")
                return False
            
            self.balance -= amount
            self._save_transaction("Withdrawal", -amount)
            print(f"Withdrawal successful. New balance: {self.balance:.4f}")
            return True
        except Exception as error:
            print(f"Withdrawal failed: {error}")
            return False

    def _save_transaction(self, description: str, amount: float) -> None:
        """Save transaction to database and update client balance"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                transaction_date = datetime.now().strftime("%d/%m/%Y")
                
                cursor.execute("""
                    INSERT INTO transactions(client_id, transaction_date, description, amount, balance)
                    VALUES(?, ?, ?, ?, ?)
                """, 
                (self.client_id, transaction_date, description, amount, self.balance)
                )
                
                # Update client balance
                cursor.execute("UPDATE clients SET balance=? WHERE id=?", (self.balance, self.client_id))

                print(f"Transaction saved - Client {self.client_id}: {description} {amount}")
        except Exception as error:
            print(f"Failed to save transaction: {error}")

    def parse_transaction_text(self, text: str) -> None:
        """Parse transaction text and add to history"""
        matches = re.findall(self.pattern, text)
        for match in matches:
            self.transaction_history.append({
                "date": match[0],
                "description": match[1],
                "amount": float(match[2]),
                "balance": float(match[3])
            })

    def get_balance(self) -> float:
        """Get current balance"""
        return self.balance

    def display_history(self) -> None:
        """Display transaction history"""
        if not self.transaction_history:
            print("No transactions found.")
            return
        
        print("\n--- Transaction History ---")
        print(f"{'Date':<12} {'Description':<15} {'Amount':<12} {'Balance':<12}")
        print("-" * 51)
        for trans in self.transaction_history:
            print(f"{trans['date']:<12} {trans['description']:<15} {trans['amount']:>10.2f}  {trans['balance']:>10.2f}")


# ===== Client Menu System =====
def client_menu(client: Client):
    """Client menu for managing account"""
    assert client.client_id is not None, "Client must have an ID"
    transaction = Transactions(client.client_id, client.balance)
    
    while True:
        print(f"\n===== CLIENT MENU ({client.name}) =====")
        print(f"Current Balance: {transaction.get_balance():.2f}")
        print("1. Deposit")
        print("2. Withdraw")
        print("3. View Balance")
        print("4. Transaction History")
        print("5. Update Profile")
        print("6. Exit")

        choice = input("\nEnter your choice (1-6): ").strip()

        try:
            match choice:
                case "1":
                    amount = float(input("Enter deposit amount: "))
                    transaction.deposit(amount)
                    client.balance = transaction.get_balance()
                    client.save_to_db()

                case "2":
                    amount = float(input("Enter withdrawal amount: "))
                    transaction.withdraw(amount)
                    client.balance = transaction.get_balance()
                    client.save_to_db()
                
                case "3":
                    print(f"\nYour current balance: {transaction.get_balance():.2f}")

                case "4":
                    transaction.display_history()

                case "5":
                    update_client_profile(client)

                case "6":
                    print("Thank you for using our banking system. Goodbye!")
                    break
                
                case _:
                    print("Invalid choice. Please enter 1-6.")
        except ValueError:
            print("Invalid input. Please enter a valid amount.")
        except Exception as error:
            print(f"Error in client menu: {error}")

def update_client_profile(client: Client) -> None:
    """Update client profile information"""
    print("\n--- Update Profile ---")
    print("1. Update Email")
    print("2. Update Age")
    print("3. Update Phone")
    print("4. Back to Menu")
    
    choice = input("Select option (1-4): ").strip()
    
    try:
        match choice:
            case "1":
                client.email = get_email()
                print("Email updated.")
            case "2":
                client.age = get_age()
                print("Age updated.")
            case "3":
                info = get_phone_info()
                client.phone = info["phone"]
                client.country = info["country"]
                client.network = info["network"]
                print("Phone information updated.")
            case "4":
                return
            case _:
                print("Invalid choice.")
        
        if choice in ["1", "2", "3"]:
            client.save_to_db()
            print(f"Client {client.client_id} profile updated")
    except Exception as error:
        print(f"Error updating profile: {error}")
        print("Error updating profile.")

def view_all_clients() -> None:
    """Display all clients in database"""
    clients = Client.get_all()
    if not clients:
        print("No clients found.")
        return
    
    print("\n===== ALL CLIENTS =====")
    print(f"{'ID':<5} {'Name':<20} {'Age':<5} {'Email':<25} {'Balance':<12}")
    print("-" * 67)
    for client in clients:
        print(f"{client.client_id:<5} {client.name:<20} {client.age:<5} {client.email:<25} {client.balance:>10.2f}")

def search_client() -> Optional[Client]:
    """Search for a client by ID or name"""
    print("\n--- Search Client ---")
    print("1. Search by ID")
    print("2. Search by Name")
    
    choice = input("Select search method (1-2): ").strip()
    
    try:
        if choice == "1":
            client_id = int(input("Enter client ID: ").strip())
            client = Client.get_by_id(client_id)
            if client:
                print(f"\nFound: {client}")
                return client
            print("Client not found.")
        elif choice == "2":
            name = input("Enter client name: ").strip().lower()
            clients = Client.get_all()
            for client in clients:
                if client.name.lower() == name:
                    print(f"\nFound: {client}")
                    return client
            print("Client not found.")
        else:
            print("Invalid choice.")
    except ValueError:
        print("Invalid input.")
    
    return None

def delete_client() -> None:
    """Delete a client account"""
    client = search_client()
    if not client:
        return
    
    confirm = input(f"\nAre you sure you want to delete {client.name}? (yes/no): ").strip().lower()
    if confirm == "yes":
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM transactions WHERE client_id=?", (client.client_id,))
                cursor.execute("DELETE FROM clients WHERE id=?", (client.client_id,))
                print(f"Client {client.client_id} deleted")
                print("Client deleted successfully.")
        except Exception as error:
            print(f"Failed to delete client: {error}")
            print("Error deleting client.")
    else:
        print("Deletion cancelled.")

def main():
    """Main entry point for the banking system"""
    print("Banking Management System started")
    
    while True:
        print("\n" + "="*50)
        print("===== BANKING MANAGEMENT SYSTEM =====")
        print("="*50)
        print("1. Create Client Account")
        print("2. Access Client Account")
        print("3. View All Clients")
        print("4. Search Client")
        print("5. Delete Client Account")
        print("6. View System Logs")
        print("7. Exit")
        print("="*50)
        
        choice = input("\nEnter your choice: ").strip()
        match choice:
            case "1":
                print("\n--- Create New Client Account ---")
                name = get_name()
                age = get_age()
                gender = get_gender()
                email = get_email()
                id_no = get_ID_no()
                phone_info = get_phone_info()
                    
                client = Client(
                    name=name,
                    age=age,
                    gender=gender,
                    email=email,
                    ID_no=id_no,
                    country=phone_info["country"],
                    network=phone_info["network"],
                    phone=phone_info["phone"],
                    balance=0.0
                )
                    
                if client.save_to_db():
                    print(f"\n✓ Client created successfully!")
                    print(client)
                else:
                    print("Failed to create client account.")
                
            case "2":
                try:
                    client_id = int(input("\nEnter client ID: ").strip())
                    client = Client.get_by_id(client_id)
                    if client:
                        print(f"\n✓ Welcome {client.name}!")
                        client_menu(client)
                    else:
                        print("Client not found.")
                except ValueError:
                    print("Invalid client ID.")
                
            case "3":
                view_all_clients()
                
            case "4":
                search_client()
                
            case "5":
                delete_client()
                
            case "6":
                print("\n--- System Logs ---")
                try:
                    with open(LOG_FILE, "r") as file:
                        logs = file.readlines()
                        for log in logs[-10:]:  # Show last 10 logs
                            print(log.strip())
                except FileNotFoundError:
                    print("No logs found yet.")
                
            case "7":
                print(cowsay.tux("Thank you for using Banking Management System!. Exiting...")) #type:ignore
                break
                
            case _:
                print("Invalid choice. Please enter: ")

if __name__ == "__main__":
    main()