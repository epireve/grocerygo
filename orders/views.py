from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.http import require_POST
from .models import Order, OrderItem, ShippingAddress, Checkout, CheckoutItem
from cart.models import Cart, CartItem
from products.models import Product
from decimal import Decimal
import json

# Create your views here.


def ensure_cart_model_exists(request):
    """
    Ensure the user has a Cart model instance and that session cart items
    are properly synchronized to CartItem models
    """
    # Get or create Cart model for the user
    cart, created = Cart.objects.get_or_create(user=request.user)

    # Get session cart
    session_cart = request.session.get("cart", {})

    # Sync session cart to Cart model
    if session_cart:
        # Clear existing cart items first
        CartItem.objects.filter(cart=cart).delete()

        # Add items from session cart
        for product_slug, quantity in session_cart.items():
            try:
                product = Product.objects.get(slug=product_slug)
                CartItem.objects.create(cart=cart, product=product, quantity=quantity)
            except Product.DoesNotExist:
                # Skip products that don't exist
                pass

    return cart


@login_required
def checkout_view(request):
    """
    View for the checkout process.
    Handles the multi-step checkout flow including:
    - Shipping information collection
    - Payment method selection
    - Order review
    - Order submission
    """
    # Ensure cart model exists and is in sync with session
    cart = ensure_cart_model_exists(request)
    cart_items = cart.items.all()

    if not cart_items.exists():
        messages.warning(
            request, "Your cart is empty. Please add some items before checkout."
        )
        return redirect("cart:view_cart")

    # Calculate subtotal and total
    subtotal = Decimal("0.00")
    for item in cart_items:
        subtotal += item.product.price * item.quantity

    shipping_cost = Decimal("5.99")  # Default shipping cost
    tax_rate = Decimal("0.06")  # 6% GST in Malaysia (changed from 8%)
    tax = subtotal * tax_rate
    total = subtotal + shipping_cost + tax

    # Get or initialize the user's saved addresses
    saved_addresses = ShippingAddress.objects.filter(user=request.user)

    # Handle form submission
    if request.method == "POST":
        # Get form data
        form_data = request.POST
        checkout_step = form_data.get("checkout_step", "shipping")

        if checkout_step == "shipping":
            # Process shipping information
            use_saved_address = form_data.get("use_saved_address")

            if use_saved_address:
                # User selected a saved address
                try:
                    address_id = int(use_saved_address)
                    address = ShippingAddress.objects.get(
                        id=address_id, user=request.user
                    )
                    # Store the selected address ID in session for the next step
                    request.session["shipping_address_id"] = address_id
                    # Move to payment step
                    return redirect(reverse("orders:checkout") + "?step=payment")
                except (ValueError, ShippingAddress.DoesNotExist):
                    messages.error(
                        request, "Selected address not found. Please try again."
                    )
            else:
                # User is creating a new address
                # Validate form fields
                required_fields = [
                    "full_name",
                    "street_address",
                    "city",
                    "state",
                    "postal_code",
                    "country",
                    "phone",
                ]
                is_valid = True
                for field in required_fields:
                    if not form_data.get(field):
                        is_valid = False
                        messages.error(
                            request, f"{field.replace('_', ' ').title()} is required."
                        )

                if is_valid:
                    # Create new address
                    address = ShippingAddress(
                        user=request.user,
                        full_name=form_data.get("full_name"),
                        street_address=form_data.get("street_address"),
                        apartment_unit=form_data.get("apartment_unit", ""),
                        city=form_data.get("city"),
                        state=form_data.get("state"),
                        postal_code=form_data.get("postal_code"),
                        country=form_data.get("country"),
                        phone=form_data.get("phone"),
                        is_default=form_data.get("save_address") == "on",
                    )
                    address.save()

                    # Store the new address ID in session
                    request.session["shipping_address_id"] = address.id

                    # Move to payment step
                    return redirect(reverse("orders:checkout") + "?step=payment")

        elif checkout_step == "payment":
            # Process payment information
            payment_method = form_data.get("payment_method")

            if not payment_method:
                messages.error(request, "Please select a payment method.")
            else:
                # Store payment method in session
                request.session["payment_method"] = payment_method

                # Move to review step
                return redirect(reverse("orders:checkout") + "?step=review")

        elif checkout_step == "review":
            # Process order submission
            address_id = request.session.get("shipping_address_id")
            payment_method = request.session.get("payment_method")

            if not address_id or not payment_method:
                messages.error(request, "Please complete all checkout steps.")
                return redirect("orders:checkout")

            try:
                # Get the shipping address
                shipping_address = ShippingAddress.objects.get(
                    id=address_id, user=request.user
                )

                # Create the checkout/order
                checkout = Checkout(
                    user=request.user,
                    shipping_address=shipping_address,
                    payment_method=payment_method,
                    subtotal=subtotal,
                    shipping_cost=shipping_cost,
                    tax=tax,
                    total=total,
                    status="pending",  # Initial status
                )
                checkout.save()

                # Create checkout items
                for cart_item in cart_items:
                    checkout_item = CheckoutItem(
                        checkout=checkout,
                        product=cart_item.product,
                        price=cart_item.product.get_effective_price(),
                        quantity=cart_item.quantity,
                    )
                    checkout_item.save()

                    # Update product inventory (decrement)
                    product = cart_item.product
                    product.stock -= cart_item.quantity
                    product.save()

                # Clear the cart model items
                cart_items.delete()

                # Also clear the session cart
                request.session["cart"] = {}
                request.session.modified = True

                # Clear checkout session data
                if "shipping_address_id" in request.session:
                    del request.session["shipping_address_id"]
                if "payment_method" in request.session:
                    del request.session["payment_method"]

                # Show success message
                messages.success(request, "Your order has been placed successfully!")

                # Redirect to order confirmation
                return redirect("orders:order_confirmation", checkout_id=checkout.id)

            except ShippingAddress.DoesNotExist:
                messages.error(request, "Shipping address not found. Please try again.")
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")

    # Get the current checkout step
    current_step = request.GET.get("step", "shipping")

    # Prepare context based on current step
    context = {
        "cart_items": cart_items,
        "cart_count": cart_items.count(),
        "subtotal": subtotal,
        "shipping_cost": shipping_cost,
        "tax": tax,
        "total": total,
        "current_step": current_step,
    }

    if current_step == "shipping":
        context["saved_addresses"] = saved_addresses
    elif current_step == "payment":
        # Ensure shipping step is completed
        address_id = request.session.get("shipping_address_id")
        if not address_id:
            messages.warning(request, "Please complete the shipping information first.")
            return redirect("orders:checkout")

        try:
            shipping_address = ShippingAddress.objects.get(
                id=address_id, user=request.user
            )
            context["shipping_address"] = shipping_address
        except ShippingAddress.DoesNotExist:
            messages.error(
                request, "Selected shipping address not found. Please try again."
            )
            return redirect("orders:checkout")
    elif current_step == "review":
        # Ensure previous steps are completed
        address_id = request.session.get("shipping_address_id")
        payment_method = request.session.get("payment_method")

        if not address_id or not payment_method:
            messages.warning(request, "Please complete all previous checkout steps.")
            return redirect("orders:checkout")

        try:
            shipping_address = ShippingAddress.objects.get(
                id=address_id, user=request.user
            )
            context["shipping_address"] = shipping_address
            context["payment_method"] = payment_method
        except ShippingAddress.DoesNotExist:
            messages.error(
                request, "Selected shipping address not found. Please try again."
            )
            return redirect("orders:checkout")

    return render(request, "orders/checkout.html", context)


@login_required
def order_confirmation_view(request, checkout_id):
    """View for displaying order confirmation details after successful checkout"""
    try:
        checkout = Checkout.objects.get(id=checkout_id, user=request.user)
        checkout_items = CheckoutItem.objects.filter(checkout=checkout)

        context = {
            "order": checkout,
            "order_items": checkout_items,
        }

        return render(request, "orders/order_confirmation.html", context)
    except Checkout.DoesNotExist:
        messages.error(request, "Order not found.")
        return redirect("products:home")
