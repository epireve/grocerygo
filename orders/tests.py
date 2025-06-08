from django.contrib.auth.models import User
from django.db import IntegrityError
from django.db.models import ProtectedError
from decimal import Decimal

from products.models import Product, Category
from .models import Address, Checkout, CheckoutItem, OrderStatusHistory
from .constants import STATUS_CHOICES, PAYMENT_METHOD_CHOICES
from .test_utils import FixedSchemaTestCase


class AddressModelTest(FixedSchemaTestCase):
    """Tests for the Address model after migrations"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpassword"
        )

    def test_address_creation(self):
        """Test that an address can be created with all fields"""
        address = Address.objects.create(
            user=self.user,
            address_type="shipping",
            full_name="Test User",
            street_address="123 Test St",
            apartment_unit="Apt 4B",  # Testing the renamed field
            city="Test City",
            state="Test State",
            postal_code="12345",
            country="Malaysia",
            phone="555-1234",
            is_default=True,
        )

        self.assertEqual(address.apartment_unit, "Apt 4B")
        self.assertEqual(address.user, self.user)
        self.assertEqual(address.address_type, "shipping")

    def test_default_address_behavior(self):
        """Test that setting an address as default removes default status from other addresses"""
        # Create first default address
        address1 = Address.objects.create(
            user=self.user,
            address_type="shipping",
            full_name="Test User",
            street_address="123 Test St",
            apartment_unit="Apt 1",
            city="Test City",
            state="Test State",
            postal_code="12345",
            country="Malaysia",
            is_default=True,
        )

        # Create second default address of same type
        address2 = Address.objects.create(
            user=self.user,
            address_type="shipping",
            full_name="Test User",
            street_address="456 Test Ave",
            apartment_unit="Apt 2",
            city="Test City",
            state="Test State",
            postal_code="12345",
            country="Malaysia",
            is_default=True,
        )

        # Refresh from database
        address1.refresh_from_db()
        address2.refresh_from_db()

        # First address should no longer be default
        self.assertFalse(address1.is_default)
        self.assertTrue(address2.is_default)

    def test_multiple_default_addresses_different_types(self):
        """Test that a user can have multiple default addresses of different types"""
        # Create default shipping address
        shipping_address = Address.objects.create(
            user=self.user,
            address_type="shipping",
            full_name="Test User",
            street_address="123 Test St",
            apartment_unit="Apt 1",
            city="Test City",
            state="Test State",
            postal_code="12345",
            country="Malaysia",
            is_default=True,
        )

        # Create default billing address
        billing_address = Address.objects.create(
            user=self.user,
            address_type="billing",
            full_name="Test User",
            street_address="123 Test St",
            apartment_unit="Apt 1",
            city="Test City",
            state="Test State",
            postal_code="12345",
            country="Malaysia",
            is_default=True,
        )

        # Both should be default since they're different types
        self.assertTrue(shipping_address.is_default)
        self.assertTrue(billing_address.is_default)


class OrderStatusHistoryTest(FixedSchemaTestCase):
    """Tests for the OrderStatusHistory model after migrations"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpassword"
        )

        self.address = Address.objects.create(
            user=self.user,
            address_type="shipping",
            full_name="Test User",
            street_address="123 Test St",
            apartment_unit="Apt 4B",
            city="Test City",
            state="Test State",
            postal_code="12345",
            country="Malaysia",
            is_default=True,
        )

        self.checkout = Checkout.objects.create(
            user=self.user,
            shipping_address=self.address,
            payment_method="credit_card",
            subtotal=Decimal("100.00"),
            shipping_cost=Decimal("5.99"),
            tax=Decimal("10.00"),
            total=Decimal("115.99"),
            status="pending",
        )

    def test_status_history_creation(self):
        """Test that order status history is correctly associated with checkout"""
        status_history = OrderStatusHistory.objects.create(
            checkout=self.checkout,
            status="processing",
            notes="Order is being processed",
            created_by=self.user,
        )

        self.assertEqual(status_history.checkout, self.checkout)
        self.assertEqual(status_history.status, "processing")

    def test_status_history_relationship(self):
        """Test the relationship between checkout and status history"""
        # Create multiple status updates
        OrderStatusHistory.objects.create(
            checkout=self.checkout,
            status="processing",
            notes="Order is being processed",
            created_by=self.user,
        )

        OrderStatusHistory.objects.create(
            checkout=self.checkout,
            status="shipped",
            notes="Order has been shipped",
            created_by=self.user,
        )

        # Test related_name access
        self.assertEqual(self.checkout.status_history.count(), 2)

        # Test ordering
        latest_status = self.checkout.status_history.first()
        self.assertEqual(latest_status.status, "shipped")


class DeprecatedModelsTest(FixedSchemaTestCase):
    """Tests to ensure deprecated models are truly removed"""

    def test_deprecated_models_do_not_exist(self):
        """Test that the deprecated models are not available"""
        from django.apps import apps

        # These models should not exist
        self.assertFalse(apps.is_installed("orders.Order"))
        self.assertFalse(apps.is_installed("orders.OrderItem"))
        self.assertFalse(apps.is_installed("orders.ShippingAddress"))

        # Try to get the models which should raise an exception
        with self.assertRaises(LookupError):
            apps.get_model("orders", "Order")

        with self.assertRaises(LookupError):
            apps.get_model("orders", "OrderItem")

        with self.assertRaises(LookupError):
            apps.get_model("orders", "ShippingAddress")
