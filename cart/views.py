from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
import json
from products.models import Product
from decimal import Decimal
from .models import Cart, CartItem, Coupon
import logging
from django.utils import timezone

# Set up logger
logger = logging.getLogger("security")

# Create your views here.


def get_session_cart(request):
    """Get the cart from session or initialize it"""
    return request.session.get("cart", {})


def calculate_cart_total(request):
    """Calculate the total value of the cart"""
    cart = get_session_cart(request)
    total = Decimal("0.00")

    for product_slug, quantity in cart.items():
        try:
            product = Product.objects.get(slug=product_slug)
            total += product.price * quantity
        except Product.DoesNotExist:
            # Skip products that don't exist
            continue

    return total


def sync_session_to_model(request):
    """
    Sync the session cart to the Cart model if user is authenticated
    """
    if not request.user.is_authenticated:
        return

    session_cart = request.session.get("cart", {})

    # Get or create Cart model for the user
    cart, created = Cart.objects.get_or_create(user=request.user)

    # Sync session cart to Cart model
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


# Simple cart implementation using session and localStorage
def add_to_cart(request, slug=None):
    """Add a product to the cart"""
    # Security check: Validate slug parameter
    if not slug:
        messages.error(request, "Invalid product specified.")
        return redirect("products:product_list")

    try:
        product = get_object_or_404(Product, slug=slug)

        # Security check: Ensure product is active and in stock
        if not product.is_active or product.stock <= 0:
            messages.error(request, "This product is not available at this time.")
            return redirect("products:product_detail", slug=slug)

        # Get or initialize the cart
        session_cart = get_session_cart(request)

        # If POST request, validate quantity from form
        if request.method == "POST":
            try:
                quantity = int(request.POST.get("quantity", 1))
                # Security check: Validate quantity range
                if quantity <= 0:
                    quantity = 1
                elif quantity > 20:  # Set a reasonable maximum
                    quantity = 20
                    messages.warning(
                        request, "Maximum quantity per product is 20 items."
                    )
            except (ValueError, TypeError):
                quantity = 1
        else:
            quantity = 1

        # Check if product is already in cart
        if slug in session_cart:
            # Security check: Validate maximum quantity
            current_qty = session_cart[slug]
            updated_qty = current_qty + quantity
            if updated_qty > 20:
                updated_qty = 20
                messages.warning(request, "Maximum quantity per product is 20 items.")
            session_cart[slug] = updated_qty
            messages.success(request, f"Updated {product.name} quantity in your cart.")
        else:
            # Add product to cart
            session_cart[slug] = quantity
            messages.success(request, f"Added {product.name} to your cart.")

        # Save the updated cart to session
        request.session["cart"] = session_cart
        request.session.modified = True

        # Calculate cart total
        cart_total = calculate_cart_total(request)

        # If user is logged in, sync session cart to model
        if request.user.is_authenticated:
            sync_session_to_model(request)

        # For AJAX requests, return JSON response
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse(
                {
                    "success": True,
                    "cart_total": cart_total,
                    "cart_count": sum(session_cart.values()),
                }
            )

        # Redirect based on source
        redirect_url = request.GET.get("next")
        if redirect_url:
            return redirect(redirect_url)
        return redirect("cart:view_cart")

    except Product.DoesNotExist:
        messages.error(request, "Product not found.")
        return redirect("products:product_list")
    except Exception as e:
        logger.error(f"Error adding to cart: {str(e)}", exc_info=True)
        messages.error(request, "An error occurred. Please try again.")
        return redirect("products:product_list")


def get_applied_coupon(request):
    """Get any applied coupon from the session"""
    coupon_id = request.session.get("coupon_id")
    if coupon_id:
        try:
            return Coupon.objects.get(pk=coupon_id, is_active=True)
        except Coupon.DoesNotExist:
            # If coupon doesn't exist or is inactive, remove it from session
            if "coupon_id" in request.session:
                del request.session["coupon_id"]
                request.session.modified = True
    return None


def calculate_discount(total, coupon):
    """Calculate discount amount based on coupon"""
    if not coupon or total < coupon.min_purchase:
        return Decimal("0.00")

    if coupon.discount_type == "percentage":
        return Decimal(total) * (coupon.value / Decimal("100"))
    else:  # fixed amount
        return min(coupon.value, total)  # Don't allow discount greater than total


def view_cart(request):
    """
    View to display the cart contents
    """
    cart = request.session.get("cart", {})
    total = Decimal("0.00")
    products = []

    # Create a list of items to remove (to avoid modifying dict during iteration)
    items_to_remove = []

    # First pass - collect data and items to remove
    for product_slug, quantity in list(cart.items()):
        try:
            product = Product.objects.get(slug=product_slug)
            products.append(
                {
                    "product": product,
                    "quantity": quantity,
                    "subtotal": product.price * quantity,
                }
            )
            total += product.price * quantity
        except Product.DoesNotExist:
            # Add to removal list instead of removing immediately
            items_to_remove.append(product_slug)

    # Second pass - remove non-existent products
    for product_slug in items_to_remove:
        del cart[product_slug]
        messages.warning(
            request, f"We removed a product that's no longer available from your cart."
        )

    # Update the session if we removed any items
    if items_to_remove:
        request.session["cart"] = cart
        request.session.modified = True

    # Get any applied coupon
    coupon = get_applied_coupon(request)

    # Calculate discount
    discount = calculate_discount(total, coupon)

    # Calculate subtotal (after discount)
    subtotal = total - discount

    # Calculate shipping, tax, and total
    shipping_cost = (
        Decimal("5.99") if total > 0 else Decimal("0.00")
    )  # Default shipping cost for Malaysia
    tax_rate = Decimal("0.06")  # 6% GST in Malaysia
    tax = subtotal * tax_rate
    final_total = subtotal + shipping_cost + tax

    # Count total items
    items_count = sum(cart.values())

    # Check if this is an AJAX request
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse(
            {
                "success": True,
                "cart_total": float(total),
                "discount": float(discount),
                "subtotal": float(subtotal),
                "shipping": float(shipping_cost),
                "tax": float(tax),
                "final_total": float(final_total),
                "items_count": items_count,
                "products_count": len(products),
                "coupon": (
                    {
                        "code": coupon.code,
                        "value": float(coupon.value),
                        "discount_type": coupon.discount_type,
                    }
                    if coupon
                    else None
                ),
            }
        )

    context = {
        "products": products,
        "total": total,
        "items_count": items_count,
        "coupon": coupon,
        "discount": discount,
        "subtotal": subtotal,
        "shipping_cost": shipping_cost,
        "tax": tax,
        "final_total": final_total,
    }

    return render(request, "cart/cart.html", context)


def remove_from_cart(request, slug):
    """Remove a product from the cart."""
    if request.method == "POST":
        try:
            # Get the cart from session
            cart = request.session.get("cart", {})

            # Check if the product exists in the cart
            if slug in cart:
                # Remove the product from the cart
                del cart[slug]

                # Update the cart in session
                request.session["cart"] = cart
                request.session.modified = True

                # Sync with model cart if user is authenticated
                if request.user.is_authenticated:
                    sync_session_to_model(request)

                # Calculate the new cart total
                cart_total = 0
                # Calculate total items count
                total_items = 0

                for product_slug, quantity in cart.items():
                    try:
                        product = Product.objects.get(slug=product_slug)
                        cart_total += float(product.price) * quantity
                        total_items += quantity
                    except Product.DoesNotExist:
                        # Skip products that don't exist
                        continue

                # Get coupon and calculate discount
                coupon = get_applied_coupon(request)
                discount = 0
                if coupon:
                    if coupon.discount_type == "percentage":
                        discount = cart_total * (float(coupon.value) / 100)
                    else:  # fixed amount
                        discount = min(
                            float(coupon.value), cart_total
                        )  # Don't exceed cart total

                # Calculate subtotal after discount
                subtotal = cart_total - discount

                # Calculate tax and shipping
                shipping_cost = 5.99 if cart_total > 0 else 0.00
                tax_rate = 0.06  # 6% GST in Malaysia
                tax = subtotal * tax_rate
                final_total = subtotal + shipping_cost + tax

                # Check if this is an AJAX request
                is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"

                if is_ajax:
                    return JsonResponse(
                        {
                            "success": True,
                            "cart_total": cart_total,
                            "subtotal": subtotal,
                            "discount": discount,
                            "shipping_cost": shipping_cost,
                            "tax": tax,
                            "final_total": final_total,
                            "total_items": total_items,
                            "message": "Product removed from cart",
                            "coupon": (
                                {
                                    "code": coupon.code,
                                    "value": float(coupon.value),
                                    "discount_type": coupon.discount_type,
                                }
                                if coupon
                                else None
                            ),
                        }
                    )
                else:
                    messages.success(request, "Product removed from cart")
                    return redirect("cart:view_cart")
            else:
                is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"

                if is_ajax:
                    return JsonResponse(
                        {
                            "success": False,
                            "message": "Product not found in cart",
                        },
                        status=404,
                    )
                else:
                    messages.error(request, "Product not found in cart")
                    return redirect("cart:view_cart")
        except Exception as e:
            # Determine if this is an AJAX request to return appropriate response
            is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"

            if is_ajax:
                return JsonResponse(
                    {
                        "success": False,
                        "message": f"Error removing product: {str(e)}",
                    },
                    status=400,
                )
            else:
                messages.error(request, f"Error removing product: {str(e)}")
                return redirect("cart:view_cart")

    # If not a POST request
    return redirect("cart:view_cart")


@login_required
@require_POST
def sync_cart(request):
    """Synchronize localStorage cart with session"""
    try:
        data = json.loads(request.body)
        cart = data.get("cart", {})

        # Update session cart
        request.session["cart"] = cart

        # Set session expiry
        request.session.set_expiry(60 * 60 * 24 * 30)  # 30 days

        # Also sync with model cart if user is authenticated
        if request.user.is_authenticated:
            sync_session_to_model(request)

        return JsonResponse(
            {"success": True, "message": "Cart synchronized successfully"}
        )
    except json.JSONDecodeError:
        return JsonResponse(
            {"success": False, "message": "Invalid JSON data"}, status=400
        )
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500)


def get_session_cart(request):
    """Get the cart from session for syncing with localStorage"""
    cart = request.session.get("cart", {})

    # Also get product details for each item in cart
    cart_items = []
    total = 0

    # Create a copy of the cart to avoid modification during iteration
    cart_copy = cart.copy()
    modified = False

    for product_slug, quantity in cart_copy.items():
        try:
            # Use filter instead of get to handle non-existent products gracefully
            product = Product.objects.filter(slug=product_slug).first()
            if product:
                subtotal = product.price * quantity
                total += subtotal
                cart_items.append(
                    {
                        "id": product.id,
                        "product": {
                            "id": product.id,
                            "name": product.name,
                            "slug": product.slug,
                            "price": float(product.price),
                            "image": product.image.url if product.image else None,
                        },
                        "quantity": quantity,
                        "subtotal": float(subtotal),
                    }
                )
            else:
                # If product doesn't exist, remove it from cart
                del cart[product_slug]
                modified = True
        except Exception as e:
            # Log any unexpected errors
            print(f"Error processing cart item with slug {product_slug}: {str(e)}")
            # Remove problematic item from cart
            del cart[product_slug]
            modified = True

    # Update session if cart was modified
    if modified:
        request.session["cart"] = cart
        request.session.modified = True

    return JsonResponse(
        {"success": True, "cart": cart, "cart_items": cart_items, "total": float(total)}
    )


@login_required
def clear_cart(request):
    """Clear the cart"""
    # Clear the cart in session
    request.session["cart"] = {}

    # Clear any applied coupon
    if "coupon_id" in request.session:
        del request.session["coupon_id"]

    request.session.modified = True

    # Also clear the model cart if user is authenticated
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            CartItem.objects.filter(cart=cart).delete()
            # Clear the coupon from the cart model as well
            cart.coupon = None
            cart.save()

    # If AJAX request, return JSON response
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse(
            {
                "success": True,
                "message": "Cart cleared successfully",
                "cart": {},
                "total_items": 0,
                "cart_total": 0,
                "discount": 0,
                "subtotal": 0,
                "shipping": 0,
                "tax": 0,
                "final_total": 0,
            }
        )

    messages.success(request, "Your cart has been cleared.")
    return redirect("cart:view_cart")


@require_POST
def update_quantity(request, slug):
    """Update the quantity of a product in the cart"""
    if not slug:
        return JsonResponse({"success": False, "error": "Invalid product"})

    try:
        # Security check: Validate product exists
        product = get_object_or_404(Product, slug=slug)

        # Get quantity from request
        try:
            quantity = int(request.POST.get("quantity", 1))
            # Security check: Validate quantity range
            if quantity <= 0:
                quantity = 1
            elif quantity > 20:  # Set a reasonable maximum
                quantity = 20
        except (ValueError, TypeError):
            quantity = 1

        # Get the cart from session directly (not using get_session_cart function)
        session_cart = request.session.get("cart", {})

        # Update quantity in session cart
        if slug in session_cart:
            session_cart[slug] = quantity
            request.session["cart"] = session_cart
            request.session.modified = True

            # Sync with model if user is authenticated
            if request.user.is_authenticated:
                sync_session_to_model(request)

            # Calculate updated cart total
            cart_total = calculate_cart_total(request)

            # Get coupon and calculate discount
            coupon = get_applied_coupon(request)
            discount = calculate_discount(cart_total, coupon)

            # Calculate subtotal (after discount)
            subtotal = cart_total - discount

            # Calculate item subtotal
            item_subtotal = product.price * quantity

            # Calculate tax (6%)
            tax = subtotal * Decimal("0.06")

            # Calculate shipping cost
            shipping_cost = Decimal("5.99") if cart_total > 0 else Decimal("0.00")

            # Calculate final total
            final_total = subtotal + tax + shipping_cost

            # Count total items
            items_count = sum(session_cart.values())

            return JsonResponse(
                {
                    "success": True,
                    "cart_total": float(cart_total),
                    "item_subtotal": float(item_subtotal),
                    "discount": float(discount),
                    "subtotal": float(subtotal),
                    "tax": float(tax),
                    "shipping": float(shipping_cost),
                    "final_total": float(final_total),
                    "items_count": items_count,
                    "coupon": (
                        {
                            "code": coupon.code,
                            "value": float(coupon.value),
                            "discount_type": coupon.discount_type,
                        }
                        if coupon
                        else None
                    ),
                }
            )
        else:
            return JsonResponse(
                {"success": False, "error": "Product not found in cart"}
            )

    except Product.DoesNotExist:
        return JsonResponse({"success": False, "error": "Product not found"})
    except Exception as e:
        logger.error(f"Error updating cart quantity: {str(e)}", exc_info=True)
        return JsonResponse({"success": False, "error": "An error occurred"})


@require_POST
def apply_coupon(request):
    """Apply a coupon code to the cart"""
    code = request.POST.get("coupon_code")
    if not code:
        messages.error(request, "Please enter a coupon code.")
        return redirect("cart:view_cart")

    try:
        # Get the coupon, ensuring it's active and valid date range
        coupon = Coupon.objects.get(
            code__iexact=code,
            is_active=True,
            valid_from__lte=timezone.now(),
            valid_to__gte=timezone.now(),
        )

        # Calculate cart total to check against minimum purchase
        cart_total = calculate_cart_total(request)

        if cart_total < coupon.min_purchase:
            messages.error(
                request,
                f"This coupon requires a minimum purchase of RM{coupon.min_purchase}.",
            )
            return redirect("cart:view_cart")

        # Store coupon ID in session
        request.session["coupon_id"] = coupon.id
        request.session.modified = True

        # If user is authenticated, also store in their cart model
        if request.user.is_authenticated:
            cart, _ = Cart.objects.get_or_create(user=request.user)
            cart.coupon = coupon
            cart.save()

        # Format message based on discount type
        if coupon.discount_type == "percentage":
            message = f"Coupon applied: {coupon.value}% off your order."
        else:
            message = f"Coupon applied: RM{coupon.value} off your order."

        messages.success(request, message)

        # Check if AJAX request
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            # Calculate discount
            discount = calculate_discount(cart_total, coupon)

            return JsonResponse(
                {
                    "success": True,
                    "message": message,
                    "discount": float(discount),
                    "discount_formatted": f"RM{discount:.2f}",
                    "coupon": {
                        "code": coupon.code,
                        "value": float(coupon.value),
                        "discount_type": coupon.discount_type,
                    },
                }
            )

        return redirect("cart:view_cart")

    except Coupon.DoesNotExist:
        messages.error(request, "This coupon code is invalid or expired.")

        # Check if AJAX request
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse(
                {
                    "success": False,
                    "message": "This coupon code is invalid or expired.",
                },
                status=400,
            )

        return redirect("cart:view_cart")
    except Exception as e:
        logger.error(f"Error applying coupon: {str(e)}", exc_info=True)
        messages.error(request, "An error occurred. Please try again.")

        # Check if AJAX request
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse(
                {"success": False, "message": "An error occurred. Please try again."},
                status=500,
            )

        return redirect("cart:view_cart")


@require_POST
def remove_coupon(request):
    """Remove the applied coupon from the cart"""
    # Remove coupon from session
    if "coupon_id" in request.session:
        del request.session["coupon_id"]
        request.session.modified = True

    # If user is authenticated, also remove from their cart model
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            if cart.coupon:
                cart.coupon = None
                cart.save()
        except Cart.DoesNotExist:
            pass

    messages.success(request, "Coupon has been removed.")

    # Check if AJAX request
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        # Recalculate cart totals
        cart_total = calculate_cart_total(request)
        shipping_cost = Decimal("5.99") if cart_total > 0 else Decimal("0.00")
        tax = cart_total * Decimal("0.06")
        final_total = cart_total + shipping_cost + tax

        return JsonResponse(
            {
                "success": True,
                "message": "Coupon has been removed.",
                "cart_total": float(cart_total),
                "subtotal": float(cart_total),
                "discount": 0,
                "shipping": float(shipping_cost),
                "tax": float(tax),
                "final_total": float(final_total),
            }
        )

    return redirect("cart:view_cart")
