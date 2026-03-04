from typing import List, Optional, Dict

class Client:
    """Represents a bank client's data."""
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

class Transaction:
    """Represents a single transaction."""
    def __init__(self, client_id: int, description: str, amount: float, balance: float, 
                 transaction_date: str, transaction_id: Optional[int] = None):
        self.transaction_id = transaction_id
        self.client_id = client_id
        self.transaction_date = transaction_date
        self.description = description
        self.amount = amount
        self.balance = balance

    def __str__(self) -> str:
        return f"{self.transaction_date:<12} {self.description:<15} {self.amount:>10.2f}  {self.balance:>10.2f}"
