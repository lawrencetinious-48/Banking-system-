from typing import Optional
from . import database as db
from .models import Client

class TransactionService:
    def __init__(self, client: Client):
        self.client = client

    def deposit(self, amount: float) -> bool:
        if amount <= 0:
            print("Deposit amount must be positive.")
            return False
        
        self.client.balance += amount
        db.create_transaction(self.client.client_id, "Deposit", amount, self.client.balance)
        db.update_client(self.client)
        print(f"Deposit successful. New balance: {self.client.balance:.2f}")
        return True

    def withdraw(self, amount: float) -> bool:
        if amount <= 0:
            print("Withdrawal amount must be positive.")
            return False
        if amount > self.client.balance:
            print(f"Insufficient funds. Available balance: {self.client.balance:.2f}")
            return False
        
        self.client.balance -= amount
        db.create_transaction(self.client.client_id, "Withdrawal", -amount, self.client.balance)
        db.update_client(self.client)
        print(f"Withdrawal successful. New balance: {self.client.balance:.2f}")
        return True

    def get_balance(self) -> float:
        return self.client.balance

    def get_transaction_history(self):
        return db.get_transactions_by_client_id(self.client.client_id)
