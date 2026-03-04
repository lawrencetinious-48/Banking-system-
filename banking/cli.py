import sys
from typing import Optional, Dict
import cowsay
import phonenumbers as pn
from phonenumbers import geocoder, carrier

from . import database as db
from .models import Client
from .services import TransactionService

# ===== Configuration =====
DEFAULT_PHONE = "+256709862572"
LOG_FILE = "banking.log"

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

# ===== Client Menu System =====
def client_menu(client: Client):
    """Client menu for managing account"""
    transaction_service = TransactionService(client)
    
    while True:
        print(f"\n===== CLIENT MENU ({client.name}) =====")
        print(f"Current Balance: {transaction_service.get_balance():.2f}")
        print("1. Deposit")
        print("2. Withdraw")
        print("3. View Balance")
        print("4. Transaction History")
        print("5. Update Profile")
        print("6. Exit")

        choice = input("\nEnter your choice (1-6): ").strip()

        try:
            if choice == "1":
                amount = float(input("Enter deposit amount: "))
                transaction_service.deposit(amount)

            elif choice == "2":
                amount = float(input("Enter withdrawal amount: "))
                transaction_service.withdraw(amount)
            
            elif choice == "3":
                print(f"\nYour current balance: {transaction_service.get_balance():.2f}")

            elif choice == "4":
                history = transaction_service.get_transaction_history()
                display_history(history)

            elif choice == "5":
                update_client_profile(client)

            elif choice == "6":
                print("Thank you for using our banking system. Goodbye!")
                break
            
            else:
                print("Invalid choice. Please enter 1-6.")
        except ValueError:
            print("Invalid input. Please enter a valid amount.")
        except Exception as error:
            print(f"Error in client menu: {error}")

def display_history(history):
    """Display transaction history"""
    if not history:
        print("No transactions found.")
        return
    
    print("\n--- Transaction History ---")
    print(f"{'Date':<12} {'Description':<15} {'Amount':<12} {'Balance':<12}")
    print("-" * 51)
    for trans in history:
        print(trans)


def update_client_profile(client: Client) -> None:
    """Update client profile information"""
    print("\n--- Update Profile ---")
    print("1. Update Email")
    print("2. Update Age")
    print("3. Update Phone")
    print("4. Back to Menu")
    
    choice = input("Select option (1-4): ").strip()
    
    try:
        if choice == "1":
            client.email = get_email()
            print("Email updated.")
        elif choice == "2":
            client.age = get_age()
            print("Age updated.")
        elif choice == "3":
            info = get_phone_info()
            client.phone = info["phone"]
            client.country = info["country"]
            client.network = info["network"]
            print("Phone information updated.")
        elif choice == "4":
            return
        else:
            print("Invalid choice.")
        
        if choice in ["1", "2", "3"]:
            db.update_client(client)
            print(f"Client {client.client_id} profile updated")
    except Exception as error:
        print(f"Error updating profile: {error}")

def view_all_clients() -> None:
    """Display all clients in database"""
    clients = db.get_all_clients()
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
            client = db.get_client_by_id(client_id)
            if client:
                print(f"\nFound: {client}")
                return client
            print("Client not found.")
        elif choice == "2":
            name = input("Enter client name: ").strip().lower()
            clients = db.get_all_clients()
            # This is inefficient, a new DB function would be better
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
            if db.delete_client_by_id(client.client_id):
                print("Client deleted successfully.")
            else:
                print("Client not found or could not be deleted.")
        except Exception as error:
            print(f"Failed to delete client: {error}")
    else:
        print("Deletion cancelled.")

def main():
    """Main entry point for the banking system"""
    db.initialize_database()
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
        if choice == "1":
            print("\n--- Create New Client Account ---")
            client_data = {
                "name": get_name(),
                "age": get_age(),
                "gender": get_gender(),
                "email": get_email(),
                "ID_no": get_ID_no(),
                "balance": 0.0,
                **get_phone_info()
            }
                
            try:
                client_id = db.create_client(client_data)
                client = db.get_client_by_id(client_id)
                print(f"\n✓ Client created successfully!")
                print(client)
            except Exception as e:
                print(f"Failed to create client account: {e}")
            
        elif choice == "2":
            try:
                client_id = int(input("\nEnter client ID: ").strip())
                client = db.get_client_by_id(client_id)
                if client:
                    print(f"\n✓ Welcome {client.name}!")
                    client_menu(client)
                else:
                    print("Client not found.")
            except ValueError:
                print("Invalid client ID.")
            
        elif choice == "3":
            view_all_clients()
            
        elif choice == "4":
            search_client()
            
        elif choice == "5":
            delete_client()
            
        elif choice == "6":
            print("\n--- System Logs ---")
            try:
                with open(LOG_FILE, "r") as file:
                    logs = file.readlines()
                    for log in logs[-10:]:
                        print(log.strip())
            except FileNotFoundError:
                print("No logs found yet.")
            
        elif choice == "7":
            print(cowsay.tux("Thank you for using Banking Management System!. Exiting..."))
            break
            
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
