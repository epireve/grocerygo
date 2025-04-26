from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import datetime, timedelta
from products.models import Product
from decimal import Decimal
from .models import Cart, CartItem

# Create your views here.


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

    # Also update the cart model if user is authenticated
    if request.user.is_authenticated:
        sync_session_to_model(request)

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

    # Calculate shipping, tax, and total
    shipping_cost = (
        Decimal("5.99") if total > 0 else Decimal("0.00")
    )  # Default shipping cost for Malaysia
    tax_rate = Decimal("0.06")  # 6% GST in Malaysia
    tax = total * tax_rate
    final_total = total + shipping_cost + tax

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
    """Update the quantity of an item in the cart."""
    quantity = request.POST.get("quantity")
    if not quantity:
        return JsonResponse({"error": "No quantity provided"}, status=400)

    try:
        quantity = int(quantity)
        if quantity < 1:
            return JsonResponse({"error": "Quantity must be at least 1"}, status=400)
    except ValueError:
        return JsonResponse({"error": "Invalid quantity provided"}, status=400)

    # Get the product
    product = get_object_or_404(Product, slug=slug)

    # Access the cart from session
    cart = request.session.get("cart", {})

    # Update the quantity
    if slug in cart:
        cart[slug] = quantity

        # Update the session
        request.session["cart"] = cart
        request.session.modified = True

        # Also update the model cart if user is authenticated
        if request.user.is_authenticated:
            sync_session_to_model(request)

        # Calculate the new cart total and item counts
        cart_total = Decimal("0.00")
        total_items = 0

        for product_slug, qty in cart.items():
            try:
                p = Product.objects.get(slug=product_slug)
                cart_total += p.price * qty
                total_items += qty
            except Product.DoesNotExist:
                # Skip products that don't exist
                continue

        # Calculate shipping, tax, and total using the same rates as view_cart
        shipping_cost = Decimal("5.99") if cart_total > 0 else Decimal("0.00")
        tax_rate = Decimal("0.06")  # 6% GST in Malaysia
        tax = cart_total * tax_rate
        final_total = cart_total + shipping_cost + tax

        # Calculate the subtotal for the specific product being updated
        item_subtotal = product.price * quantity

        return JsonResponse(
            {
                "success": True,
                "quantity": quantity,
                "price": float(product.price),
                "item_subtotal": f"RM{float(item_subtotal):.2f}",
                "cart_total": f"RM{float(cart_total):.2f}",
                "total_items": total_items,
                "tax": f"RM{float(tax):.2f}",
                "shipping_cost": f"RM{float(shipping_cost):.2f}",
                "final_total": f"RM{float(final_total):.2f}",
            }
        )

    return JsonResponse({"error": "Product not found in cart"}, status=404)
