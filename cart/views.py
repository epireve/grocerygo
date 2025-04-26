from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from products.models import Product

# Create your views here.


# Simple cart implementation using session
def add_to_cart(request, slug):
    """Add a product to the cart"""
    product = get_object_or_404(Product, slug=slug)
    cart = request.session.get("cart", {})

    quantity = int(request.POST.get("quantity", 1))

    # If product is already in cart, update quantity
    if product.slug in cart:
        cart[product.slug] += quantity
    else:
        cart[product.slug] = quantity

    request.session["cart"] = cart
    messages.success(request, f"{product.name} added to your cart.")
    return redirect("products:product_detail", slug=product.slug)


def view_cart(request):
    """View the cart contents"""
    cart = request.session.get("cart", {})
    cart_items = []
    total = 0

    for product_slug, quantity in cart.items():
        product = get_object_or_404(Product, slug=product_slug)
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

    return redirect("cart:view_cart")
