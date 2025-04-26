from django.db import models
from django.contrib.auth.models import User
from products.models import Product


class Address(models.Model):
    # Address Type Choices
    ADDRESS_TYPE_CHOICES = (
        ("shipping", "Shipping"),
        ("billing", "Billing"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses")
    address_type = models.CharField(max_length=10, choices=ADDRESS_TYPE_CHOICES)
    full_name = models.CharField(max_length=100)
    street_address = models.CharField(max_length=255)
    apartment_address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default="Malaysia")
    phone_number = models.CharField(max_length=20)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.full_name} - {self.street_address}, {self.city}"

    class Meta:
        verbose_name = "Address"
        verbose_name_plural = "Addresses"
        ordering = ["-is_default", "-created_at"]


class Order(models.Model):
    # Order Status Choices
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    )

    # Payment Method Choices
    PAYMENT_CHOICES = (
        ("credit_card", "Credit Card"),
        ("bank_transfer", "Bank Transfer"),
        ("cash_on_delivery", "Cash on Delivery"),
        ("e_wallet", "E-Wallet"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    order_number = models.CharField(max_length=50, unique=True)
    shipping_address = models.ForeignKey(
        Address,
        related_name="shipping_orders",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    billing_address = models.ForeignKey(
        Address,
        related_name="billing_orders",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    order_status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="pending"
    )
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES)
    payment_status = models.BooleanField(default=False)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.order_number} - {self.user.username}"

    def save(self, *args, **kwargs):
        # Calculate total if not provided
        if not self.total:
            self.total = self.subtotal + self.shipping_cost + self.tax
        super().save(*args, **kwargs)

    @property
    def order_items_count(self):
        return self.items.count()

    @property
    def get_status_display_class(self):
        """Return CSS class based on order status"""
        status_classes = {
            "pending": "bg-yellow-100 text-yellow-800",
            "processing": "bg-blue-100 text-blue-800",
            "shipped": "bg-purple-100 text-purple-800",
            "delivered": "bg-green-100 text-green-800",
            "cancelled": "bg-red-100 text-red-800",
        }
        return status_classes.get(self.order_status, "")

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        ordering = ["-created_at"]


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    price = models.DecimalField(
        max_digits=10, decimal_places=2
    )  # Price at time of purchase
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    @property
    def total_price(self):
        return self.price * self.quantity

    class Meta:
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"


class OrderStatusHistory(models.Model):
    """Track order status changes for audit purposes"""

    order = models.ForeignKey(
        Order, related_name="status_history", on_delete=models.CASCADE
    )
    status = models.CharField(max_length=20, choices=Order.STATUS_CHOICES)
    notes = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.order.order_number} - {self.status}"

    class Meta:
        verbose_name = "Order Status History"
        verbose_name_plural = "Order Status History"
        ordering = ["-created_at"]
