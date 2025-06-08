#!/usr/bin/env python
"""
Test script to verify admin fixes are working properly.
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "grocerygo.settings")
django.setup()

from orders.models import CheckoutItem, Address, Checkout
from django.contrib.auth.models import User


def test_admin_fixes():
    """Test that our admin fixes resolve the issues."""
    print("Testing admin fixes...")

    # Test 1: Check address data exists
    address_count = Address.objects.count()
    print(f"✓ Address records found: {address_count}")

    if address_count > 0:
        print("✓ Address data has been restored successfully")
        for addr in Address.objects.all():
            print(f"  - {addr.full_name}: {addr.street_address}, {addr.city}")
    else:
        print("✗ No address data found")

    # Test 2: Check checkout items exist
    checkout_item_count = CheckoutItem.objects.count()
    print(f"✓ CheckoutItem records found: {checkout_item_count}")

    if checkout_item_count > 0:
        print("✓ CheckoutItem data exists")
        # Test the total_price property works
        item = CheckoutItem.objects.first()
        print(f"  - Sample item total_price: {item.total_price}")
    else:
        print("✗ No checkout item data found")

    # Test 3: Check admin configuration
    from orders.admin import CheckoutItemAdmin

    admin_instance = CheckoutItemAdmin(CheckoutItem, None)

    print("✓ Admin configuration:")
    print(f"  - list_display: {admin_instance.list_display}")
    print(f"  - readonly_fields: {admin_instance.readonly_fields}")

    # Test the get_total_price method exists
    if hasattr(admin_instance, "get_total_price"):
        print("✓ get_total_price method exists in admin")
        if checkout_item_count > 0:
            item = CheckoutItem.objects.first()
            total = admin_instance.get_total_price(item)
            print(f"  - Method returns: {total}")
    else:
        print("✗ get_total_price method missing from admin")

    print("\nTest completed!")


if __name__ == "__main__":
    test_admin_fixes()
