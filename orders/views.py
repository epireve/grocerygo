from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.views.decorators.http import require_POST
from .models import Address, Checkout, CheckoutItem
from cart.models import Cart, CartItem
from products.models import Product
from decimal import Decimal
import logging
from accounts.decorators import owner_required
from accounts.utils import sanitize_user_input

logger = logging.getLogger("security")

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
    try:
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
        saved_addresses = Address.objects.filter(
            user=request.user, address_type="shipping"
        )

        # Handle form submission
        if request.method == "POST":
            # Get form data
            form_data = request.POST
            checkout_step = form_data.get("checkout_step", "shipping")
            logger.info(f"Processing checkout step: {checkout_step}")

            if checkout_step == "shipping":
                # Process shipping information
                use_saved_address = form_data.get("use_saved_address")
                logger.info(f"Using saved address: {use_saved_address}")

                if use_saved_address:
                    # User selected a saved address
                    try:
                        address_id = int(use_saved_address)
                        address = Address.objects.get(
                            id=address_id, user=request.user, address_type="shipping"
                        )
                        # Store the selected address ID in session for the next step
                        request.session["shipping_address_id"] = address_id
                        logger.info(
                            f"Saved address {address_id} selected and stored in session"
                        )
                        # Move to payment step
                        return redirect(reverse("orders:checkout") + "?step=payment")
                    except (ValueError, Address.DoesNotExist) as e:
                        logger.error(f"Error selecting saved address: {str(e)}")
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
                    missing_fields = []
                    for field in required_fields:
                        if not form_data.get(field):
                            is_valid = False
                            missing_fields.append(field)
                            messages.error(
                                request,
                                f"{field.replace('_', ' ').title()} is required.",
                            )

                    if not is_valid:
                        logger.error(
                            f"Missing required fields: {', '.join(missing_fields)}"
                        )

                    if is_valid:
                        # Create new address with sanitized input
                        try:
                            address = Address(
                                user=request.user,
                                address_type="shipping",
                                full_name=sanitize_user_input(
                                    form_data.get("full_name")
                                ),
                                street_address=sanitize_user_input(
                                    form_data.get("street_address")
                                ),
                                apartment_unit=sanitize_user_input(
                                    form_data.get("apartment_unit", "")
                                ),
                                city=sanitize_user_input(form_data.get("city")),
                                state=sanitize_user_input(form_data.get("state")),
                                postal_code=sanitize_user_input(
                                    form_data.get("postal_code")
                                ),
                                country=sanitize_user_input(form_data.get("country")),
                                phone=sanitize_user_input(form_data.get("phone")),
                                is_default=form_data.get("save_address") == "on",
                            )
                            address.save()
                            logger.info(f"New address created with ID: {address.id}")

                            # Store the new address ID in session
                            request.session["shipping_address_id"] = address.id
                            logger.info(
                                f"New address ID {address.id} stored in session"
                            )

                            # Move to payment step
                            return redirect(
                                reverse("orders:checkout") + "?step=payment"
                            )
                        except Exception as e:
                            logger.error(f"Error creating new address: {str(e)}")
                            messages.error(
                                request, "Error saving address. Please try again."
                            )

            elif checkout_step == "payment":
                # Process payment information
                payment_method = form_data.get("payment_method")
                logger.info(f"Selected payment method: {payment_method}")

                if not payment_method:
                    logger.error("No payment method selected")
                    messages.error(request, "Please select a payment method.")
                else:
                    # Store payment method in session
                    request.session["payment_method"] = payment_method
                    logger.info(f"Payment method {payment_method} stored in session")

                    # Move to review step
                    return redirect(reverse("orders:checkout") + "?step=review")

            elif checkout_step == "review":
                # Process order submission
                address_id = request.session.get("shipping_address_id")
                payment_method = request.session.get("payment_method")
                logger.info(
                    f"Processing order with address_id: {address_id}, payment_method: {payment_method}"
                )

                if not address_id:
                    logger.error(
                        "Missing shipping address in session during order review."
                    )
                    messages.error(
                        request,
                        "Shipping address is missing. Please complete the shipping step.",
                    )
                    return redirect(reverse("orders:checkout") + "?step=shipping")
                if not payment_method:
                    logger.error(
                        "Missing payment method in session during order review."
                    )
                    messages.error(
                        request,
                        "Payment method is missing. Please complete the payment step.",
                    )
                    return redirect(reverse("orders:checkout") + "?step=payment")

                try:
                    # Get the shipping address
                    shipping_address = Address.objects.get(
                        id=address_id, user=request.user, address_type="shipping"
                    )
                    logger.info(f"Found shipping address: {shipping_address}")

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
                    logger.info(f"Created new checkout with ID: {checkout.id}")

                    # Create checkout items
                    for cart_item in cart_items:
                        checkout_item = CheckoutItem(
                            checkout=checkout,
                            product=cart_item.product,
                            price=cart_item.product.get_effective_price(),
                            quantity=cart_item.quantity,
                        )
                        checkout_item.save()
                        logger.info(
                            f"Created checkout item for product: {cart_item.product.name}, quantity: {cart_item.quantity}"
                        )

                        # Update product inventory (decrement)
                        product = cart_item.product
                        product.stock -= cart_item.quantity
                        if product.stock < 0:
                            product.stock = 0
                        product.save()
                        logger.info(
                            f"Updated stock for product {product.name} to {product.stock}"
                        )

                    # Clear the cart model items
                    cart_items.delete()
                    logger.info("Cleared cart items")

                    # Also clear the session cart
                    request.session["cart"] = {}
                    request.session.modified = True
                    logger.info("Cleared session cart")

                    # Clear checkout session data
                    if "shipping_address_id" in request.session:
                        del request.session["shipping_address_id"]
                    if "payment_method" in request.session:
                        del request.session["payment_method"]
                    logger.info("Cleared checkout session data")

                    # Show success message
                    messages.success(
                        request, "Your order has been placed successfully!"
                    )

                    # Redirect to order confirmation
                    logger.info(
                        f"Redirecting to order confirmation for checkout ID: {checkout.id}"
                    )
                    return redirect("orders:order_confirmation", pk=checkout.id)

                except Address.DoesNotExist:
                    logger.error(f"Shipping address not found for ID: {address_id}")
                    messages.error(
                        request, "Shipping address not found. Please try again."
                    )
                    return redirect(reverse("orders:checkout") + "?step=shipping")
                except Exception as e:
                    logger.error(f"Order creation failed: {str(e)}", exc_info=True)
                    messages.error(
                        request,
                        f"An error occurred while processing your order. Please try again.",
                    )
                    return redirect(reverse("orders:checkout") + "?step=review")

        # Get the current checkout step
        current_step = request.GET.get("step", "shipping")
        logger.info(f"Current checkout step: {current_step}")

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
                logger.warning(
                    "Attempting to access payment step without shipping address"
                )
                messages.warning(
                    request, "Please complete the shipping information first."
                )
                return redirect("orders:checkout")

            try:
                shipping_address = Address.objects.get(
                    id=address_id, user=request.user, address_type="shipping"
                )
                context["shipping_address"] = shipping_address
            except Address.DoesNotExist:
                logger.error(
                    f"Selected shipping address not found for ID: {address_id}"
                )
                messages.error(request, "Selected shipping address not found.")
                return redirect("orders:checkout")
        elif current_step == "review":
            # Ensure shipping and payment steps are completed
            address_id = request.session.get("shipping_address_id")
            payment_method = request.session.get("payment_method")
            logger.info(
                f"Review step - address_id: {address_id}, payment_method: {payment_method}"
            )

            if not address_id or not payment_method:
                logger.warning("Attempting to access review step without required data")
                messages.warning(request, "Please complete all checkout steps.")
                return redirect("orders:checkout")

            try:
                shipping_address = Address.objects.get(
                    id=address_id, user=request.user, address_type="shipping"
                )
                context["shipping_address"] = shipping_address
                context["payment_method"] = payment_method
            except Address.DoesNotExist:
                logger.error(
                    f"Selected shipping address not found for ID: {address_id}"
                )
                messages.error(request, "Selected shipping address not found.")
                return redirect("orders:checkout")

        return render(request, "orders/checkout.html", context)

    except Exception as e:
        logger.error(f"Unexpected error in checkout process: {str(e)}", exc_info=True)
        messages.error(request, "An unexpected error occurred. Please try again later.")
        return redirect("cart:view_cart")


@login_required
def order_confirmation_view(request, pk):
    """
    View for order confirmation page after checkout is complete.
    """
    try:
        logger.info(f"Accessing order confirmation for checkout ID: {pk}")
        logger.info(f"User: {request.user.username} (ID: {request.user.id})")
        checkout = get_object_or_404(Checkout, id=pk, user=request.user)
        logger.info(f"Found checkout: {checkout}")
        logger.info(f"Checkout user: {checkout.user.username} (ID: {checkout.user.id})")
        checkout_items = checkout.items.all()
        logger.info(f"Found {checkout_items.count()} checkout items")

        context = {
            "order": checkout,
            "order_items": checkout_items,
        }

        return render(request, "orders/order_confirmation.html", context)
    except Exception as e:
        logger.error(f"Error displaying order confirmation: {str(e)}", exc_info=True)
        messages.error(
            request, "An error occurred while displaying your order confirmation."
        )
        return redirect("core:home")


@login_required
def order_history_view(request):
    """
    View for displaying order history for the logged-in user.
    """
    try:
        checkouts = Checkout.objects.filter(user=request.user).order_by("-created_at")

        context = {
            "checkouts": checkouts,
        }

        return render(request, "orders/order_history.html", context)
    except Exception as e:
        logger.error(f"Error displaying order history: {str(e)}", exc_info=True)
        messages.error(
            request, "An error occurred while retrieving your order history."
        )
        return redirect("core:home")


@login_required
@owner_required(Checkout)
def order_detail_view(request, pk):
    """
    View for displaying details of a specific order.
    """
    try:
        checkout = get_object_or_404(Checkout, id=pk, user=request.user)
        checkout_items = checkout.items.all()

        context = {
            "checkout": checkout,
            "checkout_items": checkout_items,
        }

        return render(request, "orders/order_detail.html", context)
    except Exception as e:
        logger.error(f"Error displaying order detail: {str(e)}", exc_info=True)
        messages.error(
            request, "An error occurred while retrieving your order details."
        )
        return redirect("orders:order_history")


@login_required
@owner_required(Checkout)
@require_POST
def cancel_order_view(request, pk):
    """
    View for cancelling an order.
    """
    try:
        checkout = get_object_or_404(Checkout, id=pk, user=request.user)

        # Only allow cancellation if order is in pending or processing state
        if checkout.status not in ["pending", "processing"]:
            messages.error(request, "This order cannot be cancelled at this time.")
            return redirect("orders:order_detail", pk=pk)

        # Update order status
        checkout.status = "cancelled"
        checkout.save()

        # Return items to inventory
        for item in checkout.items.all():
            product = item.product
            product.stock += item.quantity
            product.save()

        logger.info(f"Order cancelled: ID={checkout.id}, User={request.user.username}")

        messages.success(request, "Your order has been cancelled successfully.")
        return redirect("orders:order_detail", pk=pk)
    except Exception as e:
        logger.error(f"Error cancelling order: {str(e)}", exc_info=True)
        messages.error(request, "An error occurred while cancelling your order.")
        return redirect("orders:order_detail", pk=pk)
