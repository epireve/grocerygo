#!/usr/bin/env python3
"""
Test script to validate that product images are displaying correctly
on order confirmation pages after fixing the primary_image issue.
"""

import os
import sys
import django
import requests
from django.test import TestCase, Client
from django.contrib.auth.models import User
from products.models import Product, Category
from orders.models import Checkout, CheckoutItem, Address
from decimal import Decimal

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "grocerygo.settings")
django.setup()


def test_product_image_fields():
    """Test that products have the correct image field and images exist"""
    print("Testing product image fields and file existence...")

    # Check if products have image field (not primary_image)
    product = Product.objects.first()
    if product:
        print(f"✓ Product model has 'image' field: {hasattr(product, 'image')}")
        print(
            f"✗ Product model has 'primary_image' field: {hasattr(product, 'primary_image')}"
        )

        if product.image:
            print(f"✓ Product has image: {product.image}")

            # Check if image file exists
            image_path = f"media/{product.image}"
            if os.path.exists(image_path):
                print(f"✓ Image file exists: {image_path}")
            else:
                print(f"✗ Image file missing: {image_path}")
        else:
            print("✗ Product has no image set")
    else:
        print("✗ No products found in database")


def test_template_image_references():
    """Test that templates use correct image field references"""
    print("\nTesting template image field references...")

    template_files = [
        "templates/orders/order_confirmation.html",
        "templates/orders/order_detail.html",
        "templates/orders/checkout.html",
    ]

    for template_file in template_files:
        if os.path.exists(template_file):
            with open(template_file, "r") as f:
                content = f.read()

            # Check for correct usage
            if "item.product.image" in content:
                print(f"✓ {template_file} uses correct 'item.product.image'")
            else:
                print(f"? {template_file} doesn't contain 'item.product.image'")

            # Check for incorrect usage
            if "item.product.primary_image" in content:
                print(
                    f"✗ {template_file} still uses incorrect 'item.product.primary_image'"
                )
            else:
                print(
                    f"✓ {template_file} doesn't use incorrect 'item.product.primary_image'"
                )
        else:
            print(f"✗ Template file not found: {template_file}")


def test_order_confirmation_context():
    """Test that order confirmation view provides correct context"""
    print("\nTesting order confirmation context...")

    # Get a checkout with items
    checkout = Checkout.objects.filter(items__isnull=False).first()
    if checkout:
        print(f"✓ Found checkout #{checkout.id} with {checkout.items.count()} items")

        for item in checkout.items.all():
            product = item.product
            print(f"  Product: {product.name}")
            print(f"  Has image: {bool(product.image)}")
            if product.image:
                print(f"  Image path: {product.image}")
                # Check if image file exists
                full_path = f"media/{product.image}"
                print(f"  Image exists: {os.path.exists(full_path)}")
    else:
        print("✗ No checkouts with items found")


if __name__ == "__main__":
    print("=== Product Image Fix Validation ===")
    test_product_image_fields()
    test_template_image_references()
    test_order_confirmation_context()
    print("\n=== Validation Complete ===")
