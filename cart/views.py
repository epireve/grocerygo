from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import datetime, timedelta
from products.models import Product

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

    # If AJAX request, return JSON response
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse(
            {
                "success": True,
                "message": f"{product.name} added to your cart.",
                "cart": cart,
            }
        )

    # Otherwise redirect to product detail
    return redirect("products:product_detail", slug=product.slug)


def view_cart(request):
    """View the cart contents"""
    # Get cart from session
    cart = request.session.get("cart", {})
    cart_items = []
    total = 0

    # Create a copy of the cart to avoid modification during iteration
    cart_copy = cart.copy()

    for product_slug, quantity in cart_copy.items():
        try:
            # Replace get_object_or_404 with direct query to handle non-existent products
            product = Product.objects.filter(slug=product_slug).first()
            if product:
                subtotal = product.price * quantity
                total += subtotal
                cart_items.append(
                    {
                        "id": product.id,  # Keep ID for remove function
                        "product": product,
                        "quantity": quantity,
                        "subtotal": subtotal,
                    }
                )
            else:
                # If product no longer exists, remove from cart
                if product_slug in cart:
                    del cart[product_slug]
                    request.session["cart"] = cart
        except Exception as e:
            # Log any unexpected errors
            print(f"Error processing cart item with slug {product_slug}: {str(e)}")
            # Remove problematic item from cart
            if product_slug in cart:
                del cart[product_slug]
                request.session["cart"] = cart

    context = {"cart_items": cart_items, "total": total}
    return render(request, "cart/cart.html", context)


def remove_from_cart(request, item_id):
    """Remove an item from the cart"""
    # Get the product by ID
    product = get_object_or_404(Product, id=item_id)
    cart = request.session.get("cart", {})

    # Remove the product by slug
    if product.slug in cart:
        del cart[product.slug]
        request.session["cart"] = cart
        messages.success(request, f"{product.name} removed from your cart.")

    # If AJAX request, return JSON response
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse(
            {
                "success": True,
                "message": f"{product.name} removed from your cart.",
                "cart": cart,
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

    for product_slug, quantity in cart.items():
        try:
            product = get_object_or_404(Product, slug=product_slug)
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
        except Product.DoesNotExist:
            # If product doesn't exist, skip it
            continue

    return JsonResponse(
        {"success": True, "cart": cart, "cart_items": cart_items, "total": float(total)}
    )


def clear_cart(request):
    """Clear the cart"""
    request.session["cart"] = {}

    # If AJAX request, return JSON response
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse(
            {"success": True, "message": "Cart cleared successfully", "cart": {}}
        )

    messages.success(request, "Your cart has been cleared.")
    return redirect("cart:view_cart")
