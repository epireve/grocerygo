#!/usr/bin/env python3
"""
Test script to verify that the Checkout model's get_status_display and
get_payment_method_display methods work correctly after the fix.
"""

import os
import sys
import django

# Add the project directory to the Python path
sys.path.append("/Users/invoture/dev.local/grocerygo")

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "grocerygo.settings")
django.setup()

from orders.models import Checkout, Address
from django.contrib.auth.models import User
from decimal import Decimal


def test_checkout_display_methods():
    """Test that get_status_display and get_payment_method_display work correctly"""
    print("Testing Checkout model display methods...")

    try:
        # Get or create a test user
        user, created = User.objects.get_or_create(
            username="testuser_fix",
            defaults={
                "email": "test@example.com",
                "first_name": "Test",
                "last_name": "User",
            },
        )
        if created:
            user.set_password("testpass123")
            user.save()
            print(f"Created test user: {user.username}")
        else:
            print(f"Using existing test user: {user.username}")

        # Get or create a test address
        address, created = Address.objects.get_or_create(
            user=user,
            address_type="shipping",
            full_name="Test User",
            defaults={
                "street_address": "123 Test St",
                "city": "Test City",
                "state": "Test State",
                "postal_code": "12345",
                "country": "Malaysia",
                "phone": "123-456-7890",
            },
        )
        if created:
            print(f"Created test address: {address}")
        else:
            print(f"Using existing test address: {address}")

        # Create a test checkout
        checkout = Checkout.objects.create(
            user=user,
            shipping_address=address,
            payment_method="credit_card",
            subtotal=Decimal("10.00"),
            shipping_cost=Decimal("5.99"),
            tax=Decimal("0.60"),
            total=Decimal("16.59"),
            status="pending",
        )
        print(f"Created test checkout: {checkout}")

        # Test get_status_display method
        print("\n=== Testing get_status_display ===")
        try:
            status_display = checkout.get_status_display()
            print(f"✅ checkout.get_status_display() = '{status_display}'")
            print(f"   Raw status: '{checkout.status}'")
        except Exception as e:
            print(f"❌ checkout.get_status_display() failed: {e}")
            return False

        # Test get_payment_method_display method
        print("\n=== Testing get_payment_method_display ===")
        try:
            payment_display = checkout.get_payment_method_display()
            print(f"✅ checkout.get_payment_method_display() = '{payment_display}'")
            print(f"   Raw payment method: '{checkout.payment_method}'")
        except Exception as e:
            print(f"❌ checkout.get_payment_method_display() failed: {e}")
            return False

        # Test with different status values
        print("\n=== Testing different status values ===")
        test_statuses = ["pending", "processing", "shipped", "delivered", "cancelled"]
        for test_status in test_statuses:
            checkout.status = test_status
            checkout.save()
            try:
                display = checkout.get_status_display()
                print(f"✅ status '{test_status}' -> display '{display}'")
            except Exception as e:
                print(f"❌ status '{test_status}' failed: {e}")
                return False

        # Test with different payment methods
        print("\n=== Testing different payment methods ===")
        test_methods = [
            "credit_card",
            "bank_transfer",
            "cash_on_delivery",
            "e_wallet",
            "paypal",
        ]
        for test_method in test_methods:
            checkout.payment_method = test_method
            checkout.save()
            try:
                display = checkout.get_payment_method_display()
                print(f"✅ payment method '{test_method}' -> display '{display}'")
            except Exception as e:
                print(f"❌ payment method '{test_method}' failed: {e}")
                return False

        # Clean up - delete the test checkout
        checkout.delete()
        print(f"\n✅ Test completed successfully! Cleaned up test checkout.")
        return True

    except Exception as e:
        print(f"❌ Test failed with unexpected error: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("CHECKOUT MODEL FIX VERIFICATION TEST")
    print("=" * 60)

    success = test_checkout_display_methods()

    print("\n" + "=" * 60)
    if success:
        print("🎉 ALL TESTS PASSED! The fix is working correctly.")
        print("The order confirmation page should now display properly.")
    else:
        print("❌ TESTS FAILED! There may still be issues with the fix.")
    print("=" * 60)
