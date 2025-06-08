"""
Constants for the orders app
"""

# Status choices for orders
STATUS_CHOICES = [
    ("pending", "Pending"),
    ("processing", "Processing"),
    ("shipped", "Shipped"),
    ("delivered", "Delivered"),
    ("cancelled", "Cancelled"),
]

# Payment method choices
PAYMENT_METHOD_CHOICES = [
    ("credit_card", "Credit Card"),
    ("bank_transfer", "Bank Transfer"),
    ("cash_on_delivery", "Cash on Delivery"),
    ("e_wallet", "E-Wallet"),
    ("paypal", "PayPal"),
]
