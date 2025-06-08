from django.db import models
from django.contrib.auth.models import User
from products.models import Product
from decimal import Decimal
from django.conf import settings
from .constants import STATUS_CHOICES, PAYMENT_METHOD_CHOICES


class BaseItemModel(models.Model):
    """
    Abstract base class for item models (CartItem, CheckoutItem, etc.)
    Contains common fields and methods for item models across the application.
    """

    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        abstract = True

    @property
    def total_price(self):
        """Calculate the total price for this item"""
        if hasattr(self, "price") and self.price is not None:
            return self.price * self.quantity
        elif hasattr(self.product, "price"):
            return self.product.price * self.quantity
        return Decimal("0.00")

    def save(self, *args, **kwargs):
        """
        Ensure price is set if not provided.
        """
        if not self.price and hasattr(self.product, "price"):
            self.price = self.product.price
        super().save(*args, **kwargs)


class Address(models.Model):
    """Model for storing shipping and billing addresses"""

    ADDRESS_TYPE_CHOICES = [
        ("shipping", "Shipping"),
        ("billing", "Billing"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="addresses"
    )
    address_type = models.CharField(max_length=10, choices=ADDRESS_TYPE_CHOICES)
    full_name = models.CharField(max_length=255)
    street_address = models.CharField(max_length=255)
    apartment_unit = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default="Malaysia")
    phone = models.CharField(
        max_length=50, blank=True, null=True
    )  # Changed from phone_number and made nullable
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Address"
        verbose_name_plural = "Addresses"
        ordering = ["-is_default", "-created_at"]

    def __str__(self):
        return f"{self.full_name} - {self.street_address}, {self.city}"

    def save(self, *args, **kwargs):
        # If this address is set as default, remove default status from other addresses
        if self.is_default:
            Address.objects.filter(
                user=self.user, address_type=self.address_type, is_default=True
            ).exclude(id=self.id).update(is_default=False)
        super().save(*args, **kwargs)


class OrderStatusHistory(models.Model):
    """Track order status changes for audit purposes"""

    checkout = models.ForeignKey(
        "Checkout", on_delete=models.CASCADE, related_name="status_history"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    notes = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Checkout #{self.checkout.id} - {self.status}"

    class Meta:
        verbose_name = "Order Status History"
        verbose_name_plural = "Order Status Histories"
        ordering = ["-created_at"]


class Checkout(models.Model):
    """Model for storing checkout information"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="checkouts"
    )
    shipping_address = models.ForeignKey(
        Address, on_delete=models.PROTECT, related_name="checkout_shipping_orders"
    )
    payment_method = models.CharField(
        max_length=50, choices=PAYMENT_METHOD_CHOICES, default="credit_card"
    )
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_cost = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("5.99")
    )
    tax = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Checkouts"

    def __str__(self):
        return f"Checkout #{self.id} - {self.user.username}"

    def get_status_display(self):
        """Return the human-readable status"""
        return dict(self.STATUS_CHOICES).get(self.status, self.status)

    def get_payment_method_display(self):
        """Return the human-readable payment method"""
        return dict(self.PAYMENT_METHOD_CHOICES).get(
            self.payment_method, self.payment_method
        )


class CheckoutItem(BaseItemModel):
    """Model for storing individual items within a checkout"""

    checkout = models.ForeignKey(
        Checkout, on_delete=models.CASCADE, related_name="items"
    )

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Checkout #{self.checkout.id}"
