from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.crypto import get_random_string
from .models import Order, OrderItem, Address
from products.models import Product
import uuid
import decimal

# Create your views here.


@login_required
def checkout_view(request):
    """View for checkout process"""
    # Get cart from session
    cart = request.session.get("cart", {})

    # If cart is empty, redirect to cart
    if not cart:
        messages.error(request, "Your cart is empty. Please add items before checkout.")
        return redirect("cart:view_cart")

    # Process cart items
    cart_items = []
    subtotal = decimal.Decimal("0.00")
    shipping_cost = decimal.Decimal("5.00")  # Fixed shipping cost for now
    tax_rate = decimal.Decimal("0.06")  # 6% tax rate

    for product_slug, quantity in cart.items():
        try:
            product = Product.objects.get(slug=product_slug)
            item_subtotal = product.price * quantity
            subtotal += item_subtotal
            cart_items.append(
                {"product": product, "quantity": quantity, "subtotal": item_subtotal}
            )
        except Product.DoesNotExist:
            # If product no longer exists, remove from cart
            del cart[product_slug]

    # Calculate totals
    tax = (subtotal * tax_rate).quantize(
        decimal.Decimal("0.01"), rounding=decimal.ROUND_HALF_UP
    )
    total = (subtotal + shipping_cost + tax).quantize(
        decimal.Decimal("0.01"), rounding=decimal.ROUND_HALF_UP
    )

    # Get user's addresses
    addresses = None
    if request.user.is_authenticated:
        addresses = Address.objects.filter(user=request.user)

    # Handle form submission
    if request.method == "POST":
        # In a real implementation, you would process payment here
        # For demo purposes, we'll just create the order

        # Create order with a unique order number
        order_number = f"ORD-{get_random_string(8).upper()}"

        # Get selected addresses
        shipping_address_id = request.POST.get("shipping_address")
        if shipping_address_id:
            shipping_address = Address.objects.get(
                id=shipping_address_id, user=request.user
            )
        else:
            messages.error(request, "Please select a shipping address.")
            return redirect("orders:checkout")

        # Create order
        order = Order.objects.create(
            user=request.user,
            order_number=order_number,
            shipping_address=shipping_address,
            billing_address=shipping_address,  # Use same address for billing for now
            order_status="pending",
            payment_method="credit_card",  # Default payment method
            payment_status=False,  # Not paid yet
            subtotal=subtotal,
            shipping_cost=shipping_cost,
            tax=tax,
            total=total,
        )

        # Create order items
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item["product"],
                price=item["product"].price,
                quantity=item["quantity"],
            )

        # Clear the cart
        request.session["cart"] = {}

        # Show success message
        messages.success(
            request,
            f"Order {order_number} placed successfully! Thank you for your purchase.",
        )

        # Redirect to order detail
        return redirect("accounts:order_detail", order_id=order.id)

    # Prepare context for rendering template
    context = {
        "cart_items": cart_items,
        "subtotal": subtotal,
        "shipping_cost": shipping_cost,
        "tax": tax,
        "total": total,
        "addresses": addresses,
    }

    return render(request, "orders/checkout.html", context)
