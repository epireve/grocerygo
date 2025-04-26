#!/usr/bin/env python
import os
import sys
import django
from decimal import Decimal
from pathlib import Path
import random

# Setup Django
sys.path.append(str(Path(__file__).resolve().parent.parent))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "grocerygo.settings")
django.setup()

from products.models import Category, Product
from django.utils.text import slugify


def create_category_if_not_exists(name, parent=None, description=""):
    """Create a category if it doesn't exist"""
    slug = slugify(name)
    category, created = Category.objects.get_or_create(
        slug=slug,
        defaults={
            "name": name,
            "description": description,
            "parent": parent,
            "active": True,
        },
    )
    if created:
        print(f"Created category: {name}")
    return category


def create_product(
    name, price, category, description="", variants=None, is_featured=False
):
    """Create a product with variants"""
    slug = slugify(name)

    # Create the main product
    product, created = Product.objects.get_or_create(
        slug=slug,
        defaults={
            "name": name,
            "description": description,
            "price": Decimal(str(price)),
            "category": category,
            "is_active": True,
            "is_featured": is_featured,
            "stock": 100,
        },
    )

    if created:
        print(f"Created product: {name}")
    else:
        print(f"Product already exists: {name}")
        return product

    # Create variants if provided
    if variants and created:
        for variant_name, variant_price in variants:
            variant_slug = slugify(f"{name}-{variant_name}")
            variant, v_created = Product.objects.get_or_create(
                slug=variant_slug,
                defaults={
                    "name": f"{name} - {variant_name}",
                    "description": f"{description} - {variant_name}",
                    "price": Decimal(str(variant_price)),
                    "category": category,
                    "is_active": True,
                    "parent": product,
                    "stock": 100,
                },
            )
            if v_created:
                print(f"  Created variant: {variant.name}")

    return product


def add_bakery_products():
    """Add bakery products"""

    # Ensure the Bakery category exists
    bakery = create_category_if_not_exists(
        "Bakery", description="Fresh bread, pastries, cakes, and other baked goods"
    )

    # Create subcategories
    bread = create_category_if_not_exists(
        "Bread", bakery, "Fresh bread, buns, and rolls"
    )
    pastries = create_category_if_not_exists(
        "Pastries", bakery, "Sweet and savory pastries"
    )
    cakes = create_category_if_not_exists(
        "Cakes", bakery, "Celebration cakes and everyday desserts"
    )
    cookies = create_category_if_not_exists(
        "Cookies", bakery, "Freshly baked cookies and biscuits"
    )
    asian_bakery = create_category_if_not_exists(
        "Asian Bakery", bakery, "Traditional Asian baked goods"
    )

    # Bread Products
    bread_products = [
        {
            "name": "White Bread / Roti Putih",
            "price": 3.50,
            "category": bread,
            "description": "Soft, fluffy white bread perfect for sandwiches and toast.",
            "variants": [
                ("Regular Loaf", 3.50),
                ("Jumbo Loaf", 5.50),
                ("Thick Sliced", 3.80),
                ("Thin Sliced", 3.80),
                ("No Crust", 4.50),
                ("Wheat Germ", 4.20),
            ],
            "is_featured": True,
        },
        {
            "name": "Wholemeal Bread / Roti Gandum",
            "price": 4.50,
            "category": bread,
            "description": "Nutritious bread made with whole wheat flour for extra fiber.",
            "variants": [
                ("Regular Loaf", 4.50),
                ("Jumbo Loaf", 6.50),
                ("High Fiber", 5.20),
                ("Multi-grain", 5.50),
                ("Organic", 7.90),
                ("Seeds & Nuts", 6.50),
            ],
        },
        {
            "name": "Artisan Bread / Roti Artisan",
            "price": 8.90,
            "category": bread,
            "description": "Handcrafted bread with traditional methods and premium ingredients.",
            "variants": [
                ("Sourdough", 8.90),
                ("Ciabatta", 7.90),
                ("Baguette", 6.90),
                ("Focaccia", 8.90),
                ("Rye Bread", 9.90),
                ("Country Loaf", 10.90),
            ],
        },
        {
            "name": "Dinner Rolls / Roti Bulat",
            "price": 5.90,
            "category": bread,
            "description": "Small, soft rolls perfect for dinner or making sliders.",
            "variants": [
                ("Plain (6pcs)", 5.90),
                ("Whole Wheat (6pcs)", 6.90),
                ("Brioche (6pcs)", 8.90),
                ("Mini Buns (10pcs)", 7.90),
                ("Butter Rolls (6pcs)", 7.50),
                ("Sesame Topped (6pcs)", 6.50),
            ],
        },
        {
            "name": "Flatbread / Roti Pipih",
            "price": 4.90,
            "category": bread,
            "description": "Thin, versatile bread for wraps, pizza bases, or as a side.",
            "variants": [
                ("Pita Bread (5pcs)", 4.90),
                ("Naan (3pcs)", 5.90),
                ("Lebanese Bread (4pcs)", 6.90),
                ("Chapati (5pcs)", 5.50),
                ("Tortillas (8pcs)", 7.90),
                ("Garlic Naan (3pcs)", 6.90),
            ],
        },
    ]

    # Pastry Products
    pastry_products = [
        {
            "name": "Croissant / Kroisan",
            "price": 3.90,
            "category": pastries,
            "description": "Flaky, buttery pastry perfect for breakfast or a snack.",
            "variants": [
                ("Plain", 3.90),
                ("Butter", 4.90),
                ("Chocolate", 5.90),
                ("Almond", 6.90),
                ("Mini (3pcs)", 7.90),
                ("Premium", 7.50),
            ],
        },
        {
            "name": "Danish Pastry / Pastri Danish",
            "price": 4.90,
            "category": pastries,
            "description": "Sweet pastry with various fillings.",
            "variants": [
                ("Custard", 4.90),
                ("Apple", 5.50),
                ("Raisin", 5.50),
                ("Cinnamon", 5.90),
                ("Mixed Berry", 6.50),
                ("Cream Cheese", 6.90),
            ],
            "is_featured": True,
        },
        {
            "name": "Puff Pastry / Pastri Berlapis",
            "price": 5.90,
            "category": pastries,
            "description": "Light, flaky pastry in various savory and sweet options.",
            "variants": [
                ("Chicken Curry", 5.90),
                ("Beef", 6.90),
                ("Tuna", 6.50),
                ("Sardine", 6.50),
                ("Apple Turnover", 5.90),
                ("Chocolate", 5.90),
            ],
        },
        {
            "name": "Donuts / Donat",
            "price": 2.50,
            "category": pastries,
            "description": "Sweet, fried pastry with various toppings and fillings.",
            "variants": [
                ("Glazed", 2.50),
                ("Chocolate", 2.80),
                ("Strawberry", 2.80),
                ("Custard Filled", 3.20),
                ("Cinnamon Sugar", 2.50),
                ("Assorted Box (6pcs)", 15.90),
            ],
        },
        {
            "name": "Scones / Skon",
            "price": 4.90,
            "category": pastries,
            "description": "Traditional British pastry perfect with jam and cream.",
            "variants": [
                ("Plain (2pcs)", 4.90),
                ("Raisin (2pcs)", 5.50),
                ("Cheese (2pcs)", 5.90),
                ("Chocolate Chip (2pcs)", 5.90),
                ("Cranberry (2pcs)", 5.90),
                ("Mixed Box (6pcs)", 15.90),
            ],
        },
    ]

    # Cake Products
    cake_products = [
        {
            "name": "Birthday Cake / Kek Hari Jadi",
            "price": 42.90,
            "category": cakes,
            "description": "Celebration cake for birthdays and special occasions.",
            "variants": [
                ('Chocolate - 6"', 42.90),
                ('Vanilla - 6"', 42.90),
                ('Red Velvet - 6"', 49.90),
                ('Chocolate - 8"', 59.90),
                ('Vanilla - 8"', 59.90),
                ("Custom Design", 69.90),
            ],
        },
        {
            "name": "Cheesecake / Kek Keju",
            "price": 38.90,
            "category": cakes,
            "description": "Creamy dessert with a biscuit base.",
            "variants": [
                ('Classic - 7"', 38.90),
                ('Blueberry - 7"', 42.90),
                ('Chocolate - 7"', 42.90),
                ('Strawberry - 7"', 42.90),
                ('Oreo - 7"', 44.90),
                ("Mini (4pcs)", 24.90),
            ],
        },
        {
            "name": "Cupcakes / Kek Cawan",
            "price": 4.90,
            "category": cakes,
            "description": "Individual cakes with frosting, perfect for parties.",
            "variants": [
                ("Vanilla", 4.90),
                ("Chocolate", 4.90),
                ("Red Velvet", 5.90),
                ("Assorted (6pcs)", 27.90),
                ("Mini (12pcs)", 32.90),
                ("Deluxe (6pcs)", 36.90),
            ],
        },
        {
            "name": "Sponge Cake / Kek Span",
            "price": 18.90,
            "category": cakes,
            "description": "Light, airy cake that's versatile and not too sweet.",
            "variants": [
                ('Plain - 7"', 18.90),
                ('Chocolate - 7"', 21.90),
                ('Pandan - 7"', 21.90),
                ('Orange - 7"', 21.90),
                ("Roll Cake", 16.90),
                ("Swiss Roll", 17.90),
            ],
        },
        {
            "name": "Brownies / Kek Coklat Badam",
            "price": 4.50,
            "category": cakes,
            "description": "Rich, fudgy chocolate dessert with a dense texture.",
            "variants": [
                ("Classic", 4.50),
                ("Walnut", 5.50),
                ("Fudge", 5.50),
                ("Caramel", 5.90),
                ("Cheesecake Swirl", 6.90),
                ("Box (6pcs)", 25.90),
            ],
            "is_featured": True,
        },
    ]

    # Cookie Products
    cookie_products = [
        {
            "name": "Chocolate Chip Cookies / Biskut Cip Coklat",
            "price": 12.90,
            "category": cookies,
            "description": "Classic cookies with chocolate chunks or chips.",
            "variants": [
                ("Regular (10pcs)", 12.90),
                ("Soft Baked (8pcs)", 14.90),
                ("Jumbo (6pcs)", 15.90),
                ("Dark Chocolate (10pcs)", 13.90),
                ("White Chocolate (10pcs)", 13.90),
                ("Triple Chocolate (8pcs)", 15.90),
            ],
        },
        {
            "name": "Butter Cookies / Biskut Mentega",
            "price": 11.90,
            "category": cookies,
            "description": "Crisp, melt-in-your-mouth cookies made with premium butter.",
            "variants": [
                ("Classic (15pcs)", 11.90),
                ("Danish Style (12pcs)", 13.90),
                ("Shortbread (12pcs)", 13.90),
                ("Chocolate Dipped (10pcs)", 14.90),
                ("Gift Tin", 29.90),
                ("Assorted Box", 25.90),
            ],
        },
        {
            "name": "Oatmeal Cookies / Biskut Oat",
            "price": 13.90,
            "category": cookies,
            "description": "Nutritious cookies made with whole oats.",
            "variants": [
                ("Plain (10pcs)", 13.90),
                ("Raisin (10pcs)", 14.90),
                ("Chocolate Chip (10pcs)", 15.90),
                ("Cranberry (10pcs)", 15.90),
                ("Low Sugar (10pcs)", 16.90),
                ("Honey (10pcs)", 14.90),
            ],
        },
        {
            "name": "Macaron / Makaron",
            "price": 4.50,
            "category": cookies,
            "description": "Delicate French cookie sandwiches with ganache filling.",
            "variants": [
                ("Vanilla", 4.50),
                ("Chocolate", 4.50),
                ("Pistachio", 4.90),
                ("Rose", 4.90),
                ("Assorted (6pcs)", 25.90),
                ("Luxury Box (12pcs)", 49.90),
            ],
        },
        {
            "name": "Pineapple Tarts / Tart Nanas",
            "price": 22.90,
            "category": cookies,
            "description": "Traditional festive cookies with sweet pineapple jam filling.",
            "variants": [
                ("Classic (15pcs)", 22.90),
                ("Open Face (18pcs)", 22.90),
                ("Ball Shape (20pcs)", 24.90),
                ("Premium (15pcs)", 28.90),
                ("Gift Box (25pcs)", 38.90),
                ("Mini (30pcs)", 28.90),
            ],
        },
    ]

    # Asian Bakery Products
    asian_bakery_products = [
        {
            "name": "Bao / Pau",
            "price": 3.50,
            "category": asian_bakery,
            "description": "Steamed buns with various fillings, a popular Asian snack.",
            "variants": [
                ("Chicken", 3.50),
                ("BBQ Pork", 3.50),
                ("Red Bean", 3.20),
                ("Vegetable", 3.20),
                ("Custard", 3.20),
                ("Assorted (6pcs)", 19.90),
            ],
        },
        {
            "name": "Kaya Bun / Roti Kaya",
            "price": 2.90,
            "category": asian_bakery,
            "description": "Soft bread with coconut jam filling.",
            "variants": [
                ("Traditional", 2.90),
                ("Mini (3pcs)", 7.50),
                ("Butter", 3.20),
                ("Pandan", 3.20),
                ("Premium", 3.90),
                ("Special", 4.50),
            ],
        },
        {
            "name": "Egg Tart / Tart Telur",
            "price": 2.90,
            "category": asian_bakery,
            "description": "Flaky pastry shell filled with sweet egg custard.",
            "variants": [
                ("Traditional", 2.90),
                ("Portuguese Style", 3.50),
                ("Pandan", 3.20),
                ("Mini (3pcs)", 7.90),
                ("Premium", 3.90),
                ("Box (6pcs)", 16.90),
            ],
            "is_featured": True,
        },
        {
            "name": "Red Bean Bun / Roti Kacang Merah",
            "price": 2.80,
            "category": asian_bakery,
            "description": "Soft bread filled with sweet red bean paste.",
            "variants": [
                ("Traditional", 2.80),
                ("Mini (3pcs)", 7.20),
                ("With Butter", 3.20),
                ("Crispy Top", 3.50),
                ("Premium", 3.90),
                ("Special", 4.20),
            ],
        },
        {
            "name": "Coffee Bun / Roti Kopi",
            "price": 3.90,
            "category": asian_bakery,
            "description": "Sweet bun with a coffee-flavored crispy cookie topping.",
            "variants": [
                ("Classic", 3.90),
                ("Butter Filled", 4.50),
                ("Chocolate Filled", 4.50),
                ("Custard Filled", 4.50),
                ("Premium", 5.20),
                ("Mini (3pcs)", 10.90),
            ],
        },
    ]

    # Combine all products
    all_products = (
        bread_products
        + pastry_products
        + cake_products
        + cookie_products
        + asian_bakery_products
    )

    # Set a few random products as featured if not already set
    featured_count = sum(1 for p in all_products if p.get("is_featured", False))
    needed_featured = max(0, 3 - featured_count)

    if needed_featured > 0:
        non_featured = [
            i for i, p in enumerate(all_products) if not p.get("is_featured", False)
        ]
        featured_indices = random.sample(
            non_featured, min(needed_featured, len(non_featured))
        )
        for i in featured_indices:
            all_products[i]["is_featured"] = True

    # Create all products
    for product_data in all_products:
        create_product(
            name=product_data["name"],
            price=product_data["price"],
            category=product_data["category"],
            description=product_data["description"],
            variants=product_data.get("variants"),
            is_featured=product_data.get("is_featured", False),
        )

    print(f"Added {len(all_products)} bakery products with variants")


def main():
    """Main function to add bakery products"""
    print("Adding bakery products...")
    add_bakery_products()
    print("Done!")


if __name__ == "__main__":
    main()
