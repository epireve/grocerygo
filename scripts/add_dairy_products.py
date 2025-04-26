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


def add_dairy_products():
    """Add dairy products"""

    # Ensure the Dairy category exists
    dairy = create_category_if_not_exists(
        "Dairy",
        description="Fresh dairy products and alternatives",
    )

    # Create subcategories
    milk = create_category_if_not_exists(
        "Milk & Alternatives", dairy, "Milk and non-dairy alternatives"
    )
    yogurt = create_category_if_not_exists(
        "Yogurt", dairy, "Yogurt and fermented milk products"
    )
    cheese = create_category_if_not_exists("Cheese", dairy, "Various types of cheese")
    butter = create_category_if_not_exists(
        "Butter & Margarine", dairy, "Butter, margarine and spreads"
    )

    # Milk Products
    milk_products = [
        {
            "name": "Fresh Milk / Susu Segar",
            "price": 6.90,
            "category": milk,
            "description": "Fresh, pasteurized cow's milk.",
            "variants": [
                ("Full Cream (1L)", 6.90),
                ("Low Fat (1L)", 6.90),
                ("Skim (1L)", 7.20),
                ("High Calcium (1L)", 7.50),
                ("A2 (1L)", 10.90),
                ("Organic (1L)", 12.90),
            ],
            "is_featured": True,
        },
        {
            "name": "UHT Milk / Susu UHT",
            "price": 5.90,
            "category": milk,
            "description": "Long-life milk that doesn't require refrigeration until opened.",
            "variants": [
                ("Full Cream (1L)", 5.90),
                ("Low Fat (1L)", 5.90),
                ("Skim (1L)", 6.20),
                ("Flavored Chocolate (1L)", 6.90),
                ("Flavored Strawberry (1L)", 6.90),
                ("Value Pack (6x1L)", 32.90),
            ],
        },
        {
            "name": "Soy Milk / Susu Soya",
            "price": 6.50,
            "category": milk,
            "description": "Plant-based milk alternative made from soybeans.",
            "variants": [
                ("Original (1L)", 6.50),
                ("Unsweetened (1L)", 6.50),
                ("Calcium Enriched (1L)", 7.20),
                ("Chocolate (1L)", 7.50),
                ("Organic (1L)", 9.90),
                ("Value Pack (3x1L)", 18.90),
            ],
        },
        {
            "name": "Almond Milk / Susu Badam",
            "price": 8.90,
            "category": milk,
            "description": "Dairy-free milk made from almonds.",
            "variants": [
                ("Original (1L)", 8.90),
                ("Unsweetened (1L)", 8.90),
                ("Vanilla (1L)", 9.50),
                ("Chocolate (1L)", 9.90),
                ("Barista Blend (1L)", 10.90),
                ("Organic (1L)", 12.90),
            ],
        },
        {
            "name": "Oat Milk / Susu Oat",
            "price": 9.90,
            "category": milk,
            "description": "Plant-based milk made from oats, creamy texture ideal for coffee.",
            "variants": [
                ("Original (1L)", 9.90),
                ("Barista Blend (1L)", 10.90),
                ("Chocolate (1L)", 10.50),
                ("Low Fat (1L)", 9.90),
                ("Organic (1L)", 12.90),
                ("Value Pack (3x1L)", 27.90),
            ],
        },
    ]

    # Yogurt Products
    yogurt_products = [
        {
            "name": "Greek Yogurt / Yogurt Yunani",
            "price": 7.50,
            "category": yogurt,
            "description": "Thick, creamy yogurt with high protein content.",
            "variants": [
                ("Plain (500g)", 7.50),
                ("Strawberry (500g)", 8.20),
                ("Blueberry (500g)", 8.20),
                ("Honey (500g)", 8.50),
                ("Low Fat (500g)", 7.90),
                ("0% Fat (500g)", 8.90),
            ],
        },
        {
            "name": "Regular Yogurt / Yogurt Biasa",
            "price": 5.90,
            "category": yogurt,
            "description": "Creamy fermented milk product, good for gut health.",
            "variants": [
                ("Plain (500g)", 5.90),
                ("Strawberry (500g)", 6.50),
                ("Mixed Fruit (500g)", 6.50),
                ("Vanilla (500g)", 6.50),
                ("Low Fat (500g)", 6.90),
                ("Set Yogurt (500g)", 7.20),
            ],
        },
        {
            "name": "Drinking Yogurt / Yogurt Minuman",
            "price": 3.90,
            "category": yogurt,
            "description": "Thin, drinkable yogurt perfect for on-the-go.",
            "variants": [
                ("Original (250ml)", 3.90),
                ("Strawberry (250ml)", 3.90),
                ("Mango (250ml)", 3.90),
                ("Mixed Berry (250ml)", 3.90),
                ("Family Size (1L)", 9.90),
                ("Probiotic (250ml)", 4.90),
            ],
        },
        {
            "name": "Fruit Yogurt / Yogurt Buah",
            "price": 2.50,
            "category": yogurt,
            "description": "Yogurt with real fruit pieces, perfect for snacking.",
            "variants": [
                ("Strawberry (125g)", 2.50),
                ("Blueberry (125g)", 2.50),
                ("Peach (125g)", 2.50),
                ("Mixed Fruit (125g)", 2.50),
                ("Pack of 4 (4x125g)", 9.50),
                ("Pack of 8 (8x125g)", 18.50),
            ],
        },
        {
            "name": "Plant-Based Yogurt / Yogurt Tumbuhan",
            "price": 8.90,
            "category": yogurt,
            "description": "Dairy-free yogurt alternatives made from plant milk.",
            "variants": [
                ("Coconut (400g)", 8.90),
                ("Soy (400g)", 8.90),
                ("Almond (400g)", 9.90),
                ("Oat (400g)", 9.90),
                ("Plain (400g)", 8.90),
                ("Berry (400g)", 9.50),
            ],
            "is_featured": True,
        },
    ]

    # Cheese Products
    cheese_products = [
        {
            "name": "Cheddar Cheese / Keju Cheddar",
            "price": 12.90,
            "category": cheese,
            "description": "Versatile, sharp cheese perfect for cooking and snacking.",
            "variants": [
                ("Mild (250g)", 12.90),
                ("Sharp (250g)", 14.90),
                ("Mature (250g)", 16.90),
                ("Sliced (200g)", 13.90),
                ("Grated (200g)", 13.90),
                ("Block (500g)", 22.90),
            ],
        },
        {
            "name": "Mozzarella / Keju Mozzarella",
            "price": 10.90,
            "category": cheese,
            "description": "Soft, mild cheese that melts perfectly for pizzas and pasta.",
            "variants": [
                ("Block (250g)", 10.90),
                ("Shredded (250g)", 12.90),
                ("Fresh (125g)", 15.90),
                ("Low Moisture (250g)", 12.90),
                ("Sliced (200g)", 13.90),
                ("Mini Balls (200g)", 16.90),
            ],
        },
        {
            "name": "Cream Cheese / Keju Krim",
            "price": 9.90,
            "category": cheese,
            "description": "Soft, spreadable cheese perfect for bagels and baking.",
            "variants": [
                ("Original (250g)", 9.90),
                ("Light (250g)", 9.90),
                ("Herb & Garlic (250g)", 10.90),
                ("Strawberry (250g)", 10.90),
                ("Spreadable (250g)", 10.50),
                ("Whipped (250g)", 11.90),
            ],
            "is_featured": True,
        },
        {
            "name": "Feta Cheese / Keju Feta",
            "price": 14.90,
            "category": cheese,
            "description": "Brined curd white cheese, essential for Mediterranean dishes.",
            "variants": [
                ("Block (200g)", 14.90),
                ("Crumbled (200g)", 15.90),
                ("Light (200g)", 15.90),
                ("In Brine (250g)", 16.90),
                ("Marinated (200g)", 18.90),
                ("Organic (200g)", 19.90),
            ],
        },
        {
            "name": "Processed Cheese / Keju Proses",
            "price": 8.90,
            "category": cheese,
            "description": "Convenient sliced cheese for sandwiches and burgers.",
            "variants": [
                ("Slices (12pcs)", 8.90),
                ("Spreadable (200g)", 8.90),
                ("Blocks (250g)", 9.90),
                ("Singles (24pcs)", 15.90),
                ("Low Fat (12pcs)", 9.90),
                ("Value Pack (24pcs)", 16.90),
            ],
        },
    ]

    # Butter Products
    butter_products = [
        {
            "name": "Butter / Mentega",
            "price": 8.90,
            "category": butter,
            "description": "Rich and creamy butter for cooking, baking, and spreading.",
            "variants": [
                ("Salted (250g)", 8.90),
                ("Unsalted (250g)", 8.90),
                ("Cultured (250g)", 12.90),
                ("Herb (250g)", 10.90),
                ("Garlic (250g)", 10.90),
                ("Large Block (500g)", 16.90),
            ],
        },
        {
            "name": "Margarine / Marjerin",
            "price": 6.90,
            "category": butter,
            "description": "Plant-based spread good for baking and cooking.",
            "variants": [
                ("Regular (500g)", 6.90),
                ("Low Fat (500g)", 7.50),
                ("Olive Oil (500g)", 8.90),
                ("Block (250g)", 4.90),
                ("Tub (1kg)", 12.90),
                ("Baking (500g)", 7.90),
            ],
        },
        {
            "name": "Spreadable Butter / Mentega Sapuan",
            "price": 9.90,
            "category": butter,
            "description": "Butter blended with oil for easy spreading straight from the fridge.",
            "variants": [
                ("Regular (250g)", 9.90),
                ("Light (250g)", 9.90),
                ("With Olive Oil (250g)", 10.90),
                ("With Canola Oil (250g)", 10.90),
                ("Sea Salt (250g)", 10.90),
                ("Organic (250g)", 13.90),
            ],
        },
        {
            "name": "Plant-Based Butter / Mentega Tumbuhan",
            "price": 10.90,
            "category": butter,
            "description": "Dairy-free butter alternatives made from plant oils.",
            "variants": [
                ("Original (250g)", 10.90),
                ("Olive Oil (250g)", 11.90),
                ("Organic (250g)", 13.90),
                ("Salted (250g)", 10.90),
                ("Baking (250g)", 11.90),
                ("Spreadable (250g)", 11.90),
            ],
        },
        {
            "name": "Ghee / Minyak Ghee",
            "price": 12.90,
            "category": butter,
            "description": "Clarified butter with a nutty flavor, perfect for high-heat cooking.",
            "variants": [
                ("Regular (250g)", 12.90),
                ("Organic (250g)", 16.90),
                ("Grass-Fed (250g)", 18.90),
                ("Large Jar (500g)", 23.90),
                ("Premium (250g)", 19.90),
                ("Flavored (250g)", 15.90),
            ],
        },
    ]

    # Combine all products
    all_products = milk_products + yogurt_products + cheese_products + butter_products

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

    print(f"Added {len(all_products)} dairy products with variants")


def main():
    """Main function to add dairy products"""
    print("Adding dairy products...")
    add_dairy_products()
    print("Done!")


if __name__ == "__main__":
    main()
