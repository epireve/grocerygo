from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import datetime, timedelta
from products.models import Product
from decimal import Decimal

# Create your views here.


# Simple cart implementation using session and localStorage
def add_to_cart(request, slug=None):
    """Add a product to the cart"""
    # If no slug provided, redirect to products page
    if not slug:
        # If AJAX request, return error
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"error": "Product slug is required"}, status=400)
        messages.error(request, "Product not found")
        return redirect("products:product_list")

    product = get_object_or_404(Product, slug=slug)
    cart = request.session.get("cart", {})

    # Get quantity from POST if form submission, or query param if direct link
    if request.method == "POST":
        quantity = int(request.POST.get("quantity", 1))
    else:
        quantity = int(request.GET.get("quantity", 1))

    # If product is already in cart, update quantity
    if product.slug in cart:
        cart[product.slug] += quantity
    else:
        cart[product.slug] = quantity

    # Update cart session
    request.session["cart"] = cart

    # Set cart expiry to 30 days
    request.session.set_expiry(60 * 60 * 24 * 30)  # 30 days in seconds

    # Add success message
    messages.success(request, f"{product.name} added to your cart.")

    # Calculate total items count
    total_items = sum(cart.values())

    # If AJAX request, return JSON response
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse(
            {
                "success": True,
                "message": f"{product.name} added to your cart.",
                "cart": cart,
                "total_items": total_items,
            }
        )

    # Otherwise redirect to product detail
    return redirect("products:product_detail", slug=product.slug)


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

    context = {
        "products": products,
        "total": total,
    }

    return render(request, "cart/cart.html", context)


def remove_from_cart(request, slug):
    """Remove an item from the cart"""
    cart = request.session.get("cart", {})

    # Check if the product exists in the database
    product = Product.objects.filter(slug=slug).first()

    # Get product name for success message
    product_name = product.name if product else "Product"

    # Remove the product by slug
    if slug in cart:
        del cart[slug]
        request.session["cart"] = cart
        request.session.modified = True
        messages.success(request, f"{product_name} removed from your cart.")

    # Calculate total items count
    total_items = sum(cart.values())

    # If AJAX request, return JSON response
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse(
            {
                "success": True,
                "message": f"{product_name} removed from your cart.",
                "cart": cart,
                "total_items": total_items,
            }
        )

    return redirect("cart:view_cart")


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


def clear_cart(request):
    """Clear the cart"""
    # Clear the cart in session
    request.session["cart"] = {}
    request.session.modified = True

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


def update_quantity(request, slug):
    """Update the quantity of a product in the cart."""
    if request.method == "POST":
        try:
            quantity = int(request.POST.get("quantity", 1))
            # Ensure quantity is at least 1
            quantity = max(1, quantity)

            # Get the cart from session
            cart = request.session.get("cart", {})

            # Check if the product exists
            product = get_object_or_404(Product, slug=slug)

            # Check if this is an AJAX request - moved outside the if block
            is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"

            # Check if the product exists in the cart
            if slug in cart:
                # Update the quantity
                cart[slug] = quantity

                # Update the cart in session
                request.session["cart"] = cart
                request.session.modified = True

                # Calculate the new subtotal for this item
                item_subtotal = float(product.price) * quantity

                # Calculate the new cart total
                cart_total = 0
                # Calculate total items count
                total_items = 0

                # Create a copy of the cart to avoid modification during iteration
                cart_copy = cart.copy()

                for product_slug, item_quantity in cart_copy.items():
                    try:
                        prod = Product.objects.get(slug=product_slug)
                        cart_total += float(prod.price) * item_quantity
                        total_items += item_quantity
                    except Product.DoesNotExist:
                        # Skip products that don't exist
                        # Optionally remove it from the actual cart
                        if product_slug in cart:
                            del cart[product_slug]
                            request.session["cart"] = cart
                            request.session.modified = True
                        continue

                if is_ajax:
                    return JsonResponse(
                        {
                            "success": True,
                            "item_subtotal": f"RM{item_subtotal:.2f}",
                            "cart_total": f"RM{cart_total:.2f}",
                            "total_items": total_items,
                            "message": f"Quantity updated to {quantity}",
                        }
                    )
                else:
                    messages.success(request, f"Quantity updated to {quantity}")
                    return redirect("cart:view_cart")
            else:
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
            if "is_ajax" not in locals():
                is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"

            if is_ajax:
                return JsonResponse(
                    {
                        "success": False,
                        "message": f"Error updating quantity: {str(e)}",
                    },
                    status=400,
                )
            else:
                messages.error(request, f"Error updating quantity: {str(e)}")
                return redirect("cart:view_cart")

    # If not a POST request
    return redirect("cart:view_cart")
