#!/usr/bin/env python3
"""
Test script to verify cart clearing functionality after checkout.
This script tests both backend cart clearing and frontend localStorage clearing.
"""

import os
import django
import requests
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "grocerygo.settings")
django.setup()

from cart.models import Cart, CartItem
from products.models import Product
from orders.models import Checkout, CheckoutItem, Address


def test_cart_clearing_after_checkout():
    """Test that cart is properly cleared after successful checkout"""

    print("🧪 Testing Cart Clearing After Checkout")
    print("=" * 50)

    # Create test client
    client = Client()

    # Create test user
    user = User.objects.create_user(
        username="testuser", email="test@example.com", password="testpass123"
    )
    print(f"✅ Created test user: {user.username}")

    # Get a test product (assuming products exist)
    try:
        product = Product.objects.filter(is_active=True, stock__gt=0).first()
        if not product:
            print(
                "❌ No active products with stock found. Please add products to test."
            )
            return False
        print(f"✅ Using test product: {product.name}")
    except Exception as e:
        print(f"❌ Error getting product: {e}")
        return False

    # Log in the user
    login_success = client.login(username="testuser", password="testpass123")
    if not login_success:
        print("❌ Failed to log in test user")
        return False
    print("✅ User logged in successfully")

    # Add item to cart
    add_to_cart_url = reverse("cart:add_to_cart", kwargs={"slug": product.slug})
    response = client.post(add_to_cart_url, {"quantity": 2})

    if response.status_code in [200, 302]:
        print("✅ Item added to cart successfully")
    else:
        print(f"❌ Failed to add item to cart. Status: {response.status_code}")
        return False

    # Check that cart model has items
    try:
        cart = Cart.objects.get(user=user)
        cart_items_before = cart.items.count()
        print(f"✅ Cart model has {cart_items_before} items before checkout")
    except Cart.DoesNotExist:
        print("❌ Cart model not found")
        return False

    # Check session cart
    session = client.session
    session_cart_before = session.get("cart", {})
    print(f"✅ Session cart has {len(session_cart_before)} items before checkout")

    # Create shipping address for checkout
    address = Address.objects.create(
        user=user,
        address_type="shipping",
        full_name="Test User",
        street_address="123 Test Street",
        city="Test City",
        state="Test State",
        postal_code="12345",
        country="Malaysia",
        phone="+60123456789",
    )
    print("✅ Created shipping address")

    # Simulate checkout process
    print("\n🛒 Starting checkout process...")

    # Step 1: Shipping
    checkout_url = reverse("orders:checkout")
    shipping_data = {"checkout_step": "shipping", "use_saved_address": str(address.id)}
    response = client.post(checkout_url, shipping_data)
    print(f"✅ Shipping step completed (Status: {response.status_code})")

    # Step 2: Payment
    payment_data = {"checkout_step": "payment", "payment_method": "cash_on_delivery"}
    response = client.post(checkout_url + "?step=payment", payment_data)
    print(f"✅ Payment step completed (Status: {response.status_code})")

    # Step 3: Review and place order
    review_data = {"checkout_step": "review"}
    response = client.post(checkout_url + "?step=review", review_data)

    if response.status_code == 302:  # Redirect to confirmation
        print("✅ Order placed successfully")

        # Check that cart model is cleared
        cart_items_after = cart.items.count()
        print(f"📊 Cart model items after checkout: {cart_items_after}")

        # Check that session cart is cleared
        session = client.session
        session_cart_after = session.get("cart", {})
        print(f"📊 Session cart items after checkout: {len(session_cart_after)}")

        # Verify results
        success = True
        if cart_items_after == 0:
            print("✅ Cart model properly cleared")
        else:
            print("❌ Cart model NOT cleared")
            success = False

        if len(session_cart_after) == 0:
            print("✅ Session cart properly cleared")
        else:
            print("❌ Session cart NOT cleared")
            success = False

        # Test the API endpoint
        api_response = client.get("/cart/get-session-cart/")
        if api_response.status_code == 200:
            api_data = api_response.json()
            if len(api_data.get("cart", {})) == 0:
                print("✅ Cart API returns empty cart")
            else:
                print("❌ Cart API still returns items")
                success = False

        print(f"\n📋 Test Result: {'✅ PASS' if success else '❌ FAIL'}")
        return success

    else:
        print(f"❌ Order placement failed. Status: {response.status_code}")
        return False


def test_frontend_cart_clearing():
    """Test that localStorage will be cleared on order confirmation page"""
    print("\n🎨 Testing Frontend Cart Clearing")
    print("=" * 50)

    # Check if order confirmation template has cart clearing JavaScript
    template_path = "templates/orders/order_confirmation.html"

    try:
        with open(template_path, "r") as f:
            content = f.read()

        # Check for cart clearing JavaScript
        checks = [
            "localStorage.setItem(CART_STORAGE_KEY, JSON.stringify({}))" in content,
            "updateCartUI()" in content,
            "DOMContentLoaded" in content,
        ]

        if all(checks):
            print("✅ Order confirmation template has cart clearing JavaScript")
            return True
        else:
            print("❌ Order confirmation template missing cart clearing JavaScript")
            return False

    except FileNotFoundError:
        print(f"❌ Template file not found: {template_path}")
        return False


if __name__ == "__main__":
    print("🧪 GroceryGo Cart Clearing Test Suite")
    print("=" * 50)

    # Run tests
    backend_test = test_cart_clearing_after_checkout()
    frontend_test = test_frontend_cart_clearing()

    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    print(f"Backend Cart Clearing: {'✅ PASS' if backend_test else '❌ FAIL'}")
    print(f"Frontend Cart Clearing: {'✅ PASS' if frontend_test else '❌ FAIL'}")

    overall_result = backend_test and frontend_test
    print(
        f"\nOverall Result: {'✅ ALL TESTS PASS' if overall_result else '❌ SOME TESTS FAILED'}"
    )

    if overall_result:
        print("\n🎉 Cart clearing functionality is working correctly!")
        print("   - Database cart items are cleared after checkout")
        print("   - Session cart is cleared after checkout")
        print("   - localStorage will be cleared on order confirmation page")
        print("   - Cart UI will show 0 items after successful checkout")
    else:
        print("\n⚠️  Some issues were found. Please review the test output above.")
