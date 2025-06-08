from django.test import TestCase
from django.apps import apps


class DeprecatedModelsTest(TestCase):
    """Tests to ensure deprecated models are truly removed"""

    def test_deprecated_models_do_not_exist(self):
        """Test that the deprecated models are not available"""
        # These models should not be installed
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
