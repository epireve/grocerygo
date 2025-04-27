from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.urls import reverse
import json
from datetime import datetime, timedelta
from products.models import Product
from decimal import Decimal
from .models import Cart, CartItem
import logging

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

    # Calculate shipping, tax, and total
    shipping_cost = (
        Decimal("5.99") if total > 0 else Decimal("0.00")
    )  # Default shipping cost for Malaysia
    tax_rate = Decimal("0.06")  # 6% GST in Malaysia
    tax = total * tax_rate
    final_total = total + shipping_cost + tax

    # Count total items
    items_count = sum(cart.values())

    # Check if this is an AJAX request
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse(
            {
                "success": True,
                "cart_total": float(total),
                "shipping": float(shipping_cost),
                "tax": float(tax),
                "final_total": float(final_total),
                "items_count": items_count,
                "products_count": len(products),
            }
        )

    context = {
        "products": products,
        "total": total,
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

                # Calculate tax and shipping
                shipping_cost = 5.99 if cart_total > 0 else 0.00
                tax_rate = 0.06  # 6% GST in Malaysia
                tax = cart_total * tax_rate
                final_total = cart_total + shipping_cost + tax

                # Check if this is an AJAX request
                is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"

                if is_ajax:
                    return JsonResponse(
                        {
                            "success": True,
                            "cart_total": f"RM{cart_total:.2f}",
                            "shipping_cost": f"RM{shipping_cost:.2f}",
                            "tax": f"RM{tax:.2f}",
                            "final_total": f"RM{final_total:.2f}",
                            "total_items": total_items,
                            "message": "Product removed from cart",
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
    request.session.modified = True

    # Also clear the model cart if user is authenticated
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            CartItem.objects.filter(cart=cart).delete()

    # If AJAX request, return JSON response
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse(
            {
                "success": True,
                "message": "Cart cleared successfully",
                "cart": {},
                "total_items": 0,
                "cart_total": "RM0.00",
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

            # Calculate item subtotal
            item_subtotal = product.price * quantity

            # Calculate tax (6%)
            tax = cart_total * Decimal("0.06")

            # Calculate shipping cost
            shipping_cost = Decimal("5.99")

            # Calculate final total
            final_total = cart_total + tax + shipping_cost

            # Count total items
            items_count = sum(session_cart.values())

            return JsonResponse(
                {
                    "success": True,
                    "cart_total": float(cart_total),
                    "item_subtotal": float(item_subtotal),
                    "tax": float(tax),
                    "shipping": float(shipping_cost),
                    "final_total": float(final_total),
                    "items_count": items_count,
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
