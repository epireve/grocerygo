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


def add_beverage_products():
    """Add beverage products"""

    # Ensure the Beverages category exists
    beverages = create_category_if_not_exists(
        "Beverages", description="Refreshing drinks to quench your thirst"
    )

    # Create subcategories
    soft_drinks = create_category_if_not_exists(
        "Soft Drinks", beverages, "Carbonated and non-carbonated sweet beverages"
    )
    juices = create_category_if_not_exists(
        "Juices", beverages, "Fresh and packaged fruit and vegetable juices"
    )
    coffee_tea = create_category_if_not_exists(
        "Coffee & Tea", beverages, "Coffee, tea, and related products"
    )
    water = create_category_if_not_exists(
        "Water", beverages, "Still, sparkling, and flavored water"
    )

    # Soft Drinks Products
    soft_drink_products = [
        {
            "name": "Cola / Kola",
            "price": 2.50,
            "category": soft_drinks,
            "description": "Classic carbonated cola beverage.",
            "variants": [
                ("Regular (1.5L)", 2.50),
                ("Diet (1.5L)", 2.50),
                ("Zero Sugar (1.5L)", 2.50),
                ("Can (330ml)", 1.20),
                ("Can Pack (6x330ml)", 6.90),
                ("Bottle Pack (4x1.5L)", 9.50),
            ],
        },
        {
            "name": "Lemon Lime Soda / Soda Limau",
            "price": 2.30,
            "category": soft_drinks,
            "description": "Refreshing citrus-flavored carbonated drink.",
            "variants": [
                ("Regular (1.5L)", 2.30),
                ("Zero Sugar (1.5L)", 2.30),
                ("Can (330ml)", 1.20),
                ("Can Pack (6x330ml)", 6.50),
                ("Bottle Pack (4x1.5L)", 8.90),
                ("Mini Cans (8x250ml)", 7.90),
            ],
        },
        {
            "name": "Root Beer / Bir Akar",
            "price": 2.40,
            "category": soft_drinks,
            "description": "Traditional root-flavored carbonated soft drink.",
            "variants": [
                ("Regular (1.5L)", 2.40),
                ("Diet (1.5L)", 2.40),
                ("Can (330ml)", 1.20),
                ("Can Pack (6x330ml)", 6.70),
                ("Bottle Pack (4x1.5L)", 9.20),
                ("Zero Sugar (1.5L)", 2.40),
            ],
        },
        {
            "name": "Orange Soda / Soda Oren",
            "price": 2.30,
            "category": soft_drinks,
            "description": "Bubbly orange-flavored carbonated beverage.",
            "variants": [
                ("Regular (1.5L)", 2.30),
                ("Zero Sugar (1.5L)", 2.30),
                ("Can (330ml)", 1.20),
                ("Can Pack (6x330ml)", 6.50),
                ("Bottle Pack (4x1.5L)", 8.90),
                ("Mini Cans (8x250ml)", 7.90),
            ],
        },
        {
            "name": "Energy Drink / Minuman Tenaga",
            "price": 3.90,
            "category": soft_drinks,
            "description": "Caffeine and taurine-based beverage designed to provide mental and physical stimulation.",
            "variants": [
                ("Original (250ml)", 3.90),
                ("Sugar Free (250ml)", 3.90),
                ("Tropical (250ml)", 3.90),
                ("Can Pack (4x250ml)", 14.90),
                ("Large Can (500ml)", 5.90),
                ("Premium (250ml)", 4.90),
            ],
            "is_featured": True,
        },
    ]

    # Juices Products
    juice_products = [
        {
            "name": "Orange Juice / Jus Oren",
            "price": 5.90,
            "category": juices,
            "description": "Refreshing juice made from sweet oranges.",
            "variants": [
                ("Not From Concentrate (1L)", 5.90),
                ("From Concentrate (1L)", 4.90),
                ("No Added Sugar (1L)", 6.50),
                ("With Pulp (1L)", 6.20),
                ("Calcium Enriched (1L)", 6.90),
                ("Organic (1L)", 8.90),
            ],
        },
        {
            "name": "Apple Juice / Jus Epal",
            "price": 5.50,
            "category": juices,
            "description": "Sweet juice pressed from fresh apples.",
            "variants": [
                ("Pure (1L)", 5.50),
                ("From Concentrate (1L)", 4.50),
                ("No Added Sugar (1L)", 6.20),
                ("Cloudy (1L)", 5.90),
                ("Organic (1L)", 8.50),
                ("Kids Pack (6x200ml)", 7.90),
            ],
        },
        {
            "name": "Mixed Fruit Juice / Jus Campuran",
            "price": 6.20,
            "category": juices,
            "description": "Blend of various fruits for a tropical flavor.",
            "variants": [
                ("Tropical Mix (1L)", 6.20),
                ("Berry Mix (1L)", 6.50),
                ("Sunshine Mix (1L)", 6.20),
                ("No Added Sugar (1L)", 7.20),
                ("Kids Pack (6x200ml)", 8.20),
                ("Organic (1L)", 9.20),
            ],
        },
        {
            "name": "Mango Juice / Jus Mangga",
            "price": 6.50,
            "category": juices,
            "description": "Sweet and exotic juice made from ripe mangoes.",
            "variants": [
                ("Pure (1L)", 6.50),
                ("From Concentrate (1L)", 5.50),
                ("No Added Sugar (1L)", 7.20),
                ("Alphonso Mango (1L)", 8.90),
                ("Organic (1L)", 9.50),
                ("Kids Pack (6x200ml)", 8.50),
            ],
            "is_featured": True,
        },
        {
            "name": "Vegetable Juice / Jus Sayuran",
            "price": 7.90,
            "category": juices,
            "description": "Nutritious blend of vegetables for health-conscious consumers.",
            "variants": [
                ("Mixed Veggie (1L)", 7.90),
                ("Tomato (1L)", 6.90),
                ("Green Blend (1L)", 8.90),
                ("Carrot (1L)", 7.50),
                ("Low Sodium (1L)", 8.20),
                ("Organic (1L)", 10.90),
            ],
        },
    ]

    # Coffee & Tea Products
    coffee_tea_products = [
        {
            "name": "Instant Coffee / Kopi Segera",
            "price": 12.90,
            "category": coffee_tea,
            "description": "Quick and convenient coffee powder for easy preparation.",
            "variants": [
                ("Classic (200g)", 12.90),
                ("Gold Blend (200g)", 15.90),
                ("Decaf (200g)", 14.90),
                ("Strong (200g)", 13.90),
                ("Premium (200g)", 18.90),
                ("Value Pack (400g)", 24.90),
            ],
        },
        {
            "name": "Ground Coffee / Kopi Kisar",
            "price": 18.90,
            "category": coffee_tea,
            "description": "Freshly ground coffee beans for a richer flavor.",
            "variants": [
                ("Medium Roast (250g)", 18.90),
                ("Dark Roast (250g)", 18.90),
                ("Light Roast (250g)", 18.90),
                ("Espresso Blend (250g)", 19.90),
                ("Single Origin (250g)", 22.90),
                ("Organic (250g)", 24.90),
            ],
        },
        {
            "name": "Tea Bags / Uncang Teh",
            "price": 8.90,
            "category": coffee_tea,
            "description": "Convenient tea bags for quick brewing.",
            "variants": [
                ("Black Tea (50 bags)", 8.90),
                ("Green Tea (50 bags)", 9.90),
                ("Earl Grey (50 bags)", 10.90),
                ("Chamomile (25 bags)", 10.90),
                ("Peppermint (25 bags)", 10.90),
                ("Assorted (40 bags)", 12.90),
            ],
        },
        {
            "name": "Ready-to-Drink Coffee / Kopi Siap Minum",
            "price": 4.90,
            "category": coffee_tea,
            "description": "Pre-brewed coffee in convenient bottles and cans.",
            "variants": [
                ("Latte (250ml)", 4.90),
                ("Black (250ml)", 4.50),
                ("Mocha (250ml)", 5.20),
                ("Vanilla (250ml)", 5.20),
                ("Can Pack (4x250ml)", 18.90),
                ("No Sugar (250ml)", 4.90),
            ],
            "is_featured": True,
        },
        {
            "name": "Bubble Tea Kit / Kit Teh Boba",
            "price": 15.90,
            "category": coffee_tea,
            "description": "Make your own bubble tea at home with this convenient kit.",
            "variants": [
                ("Classic Milk Tea", 15.90),
                ("Brown Sugar", 16.90),
                ("Matcha", 17.90),
                ("Taro", 17.90),
                ("Fruit Tea", 16.90),
                ("Family Pack", 28.90),
            ],
        },
    ]

    # Water Products
    water_products = [
        {
            "name": "Mineral Water / Air Mineral",
            "price": 1.20,
            "category": water,
            "description": "Pure, refreshing mineral water.",
            "variants": [
                ("500ml", 1.20),
                ("1.5L", 2.20),
                ("6-Pack (6x500ml)", 6.90),
                ("12-Pack (12x500ml)", 12.90),
                ("Sports Cap (750ml)", 2.50),
                ("Premium (1L)", 3.90),
            ],
        },
        {
            "name": "Sparkling Water / Air Berkarbonat",
            "price": 2.90,
            "category": water,
            "description": "Refreshing carbonated water with no sugar or calories.",
            "variants": [
                ("Plain (500ml)", 2.90),
                ("Lemon (500ml)", 3.20),
                ("Lime (500ml)", 3.20),
                ("Berry (500ml)", 3.50),
                ("4-Pack (4x500ml)", 11.50),
                ("Premium (750ml)", 4.90),
            ],
        },
        {
            "name": "Alkaline Water / Air Alkali",
            "price": 3.50,
            "category": water,
            "description": "Water with a higher pH level than regular water.",
            "variants": [
                ("1L", 3.50),
                ("500ml", 1.90),
                ("6-Pack (6x500ml)", 10.90),
                ("2L", 5.90),
                ("Premium (1L)", 4.90),
                ("Sport (750ml)", 2.90),
            ],
        },
        {
            "name": "Flavored Water / Air Perisa",
            "price": 2.50,
            "category": water,
            "description": "Lightly flavored water with minimal calories.",
            "variants": [
                ("Lemon (500ml)", 2.50),
                ("Strawberry (500ml)", 2.50),
                ("Peach (500ml)", 2.50),
                ("Cucumber (500ml)", 2.50),
                ("Mixed Berry (500ml)", 2.50),
                ("6-Pack Assorted (6x500ml)", 14.50),
            ],
        },
        {
            "name": "Coconut Water / Air Kelapa",
            "price": 3.90,
            "category": water,
            "description": "Natural hydrating drink rich in electrolytes.",
            "variants": [
                ("Pure (330ml)", 3.90),
                ("With Pulp (330ml)", 4.20),
                ("No Added Sugar (330ml)", 4.50),
                ("Pineapple Flavor (330ml)", 4.50),
                ("Tetra Pack (1L)", 9.90),
                ("4-Pack (4x330ml)", 15.50),
            ],
        },
    ]

    # Combine all products
    all_products = (
        soft_drink_products + juice_products + coffee_tea_products + water_products
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

    print(f"Added {len(all_products)} beverage products with variants")


def main():
    """Main function to add beverage products"""
    print("Adding beverage products...")
    add_beverage_products()
    print("Done!")


if __name__ == "__main__":
    main()
