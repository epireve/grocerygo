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
    if str(product.id) in cart:
        cart[str(product.id)] += quantity
    else:
        cart[str(product.id)] = quantity

    request.session["cart"] = cart
    messages.success(request, f"{product.name} added to your cart.")
    return redirect("products:product_detail", slug=product.slug)


def view_cart(request):
    """View the cart contents"""
    cart = request.session.get("cart", {})
    cart_items = []
    total = 0

    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=product_id)
        subtotal = product.price * quantity
        total += subtotal
        cart_items.append(
            {
                "id": product_id,
                "product": product,
                "quantity": quantity,
                "subtotal": subtotal,
            }
        )

    context = {"cart_items": cart_items, "total": total}
    return render(request, "cart/cart.html", context)


def remove_from_cart(request, item_id):
    """Remove an item from the cart"""
    cart = request.session.get("cart", {})

    if str(item_id) in cart:
        del cart[str(item_id)]
        request.session["cart"] = cart
        messages.success(request, "Item removed from your cart.")

    return redirect("cart:view_cart")
