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


def add_produce_products():
    """Add produce products"""

    # Ensure the Produce category exists
    produce = create_category_if_not_exists(
        "Produce", description="Fresh fruits and vegetables"
    )

    # Create subcategories
    fruits = create_category_if_not_exists(
        "Fruits", produce, "Fresh and seasonal fruits"
    )
    vegetables = create_category_if_not_exists(
        "Vegetables", produce, "Fresh and seasonal vegetables"
    )
    organic = create_category_if_not_exists(
        "Organic Produce", produce, "Organically grown fruits and vegetables"
    )

    # Fruits Products
    fruit_products = [
        {
            "name": "Apples / Epal",
            "price": 1.80,
            "category": fruits,
            "description": "Crisp and sweet apples rich in fiber and antioxidants.",
            "variants": [
                ("Red Delicious (1kg)", 1.80),
                ("Granny Smith (1kg)", 2.10),
                ("Fuji (1kg)", 2.30),
                ("Pink Lady (1kg)", 2.50),
                ("Royal Gala (1kg)", 2.20),
                ("Golden Delicious (1kg)", 1.90),
            ],
            "is_featured": True,
        },
        {
            "name": "Bananas / Pisang",
            "price": 0.90,
            "category": fruits,
            "description": "Energy-rich, sweet fruits packed with potassium.",
            "variants": [
                ("Regular (1kg)", 0.90),
                ("Cavendish (1kg)", 1.10),
                ("Baby Banana (1kg)", 1.50),
                ("Organic (1kg)", 1.80),
                ("Plantains (1kg)", 1.40),
                ("Red Banana (1kg)", 1.90),
            ],
        },
        {
            "name": "Oranges / Oren",
            "price": 1.40,
            "category": fruits,
            "description": "Juicy citrus fruit high in vitamin C.",
            "variants": [
                ("Valencia (1kg)", 1.40),
                ("Navel (1kg)", 1.60),
                ("Blood Orange (1kg)", 2.20),
                ("Mandarin (1kg)", 1.80),
                ("Cara Cara (1kg)", 2.00),
                ("Organic (1kg)", 2.40),
            ],
        },
        {
            "name": "Grapes / Anggur",
            "price": 4.90,
            "category": fruits,
            "description": "Sweet, bite-sized fruits that come in bunches.",
            "variants": [
                ("Red Seedless (500g)", 4.90),
                ("Green Seedless (500g)", 4.90),
                ("Black Seedless (500g)", 5.50),
                ("Cotton Candy (400g)", 7.90),
                ("Concord (500g)", 5.90),
                ("Organic (500g)", 6.90),
            ],
        },
        {
            "name": "Berries / Beri",
            "price": 8.90,
            "category": fruits,
            "description": "Small, flavorful fruits packed with antioxidants.",
            "variants": [
                ("Strawberries (250g)", 8.90),
                ("Blueberries (125g)", 9.90),
                ("Raspberries (125g)", 10.90),
                ("Blackberries (125g)", 10.90),
                ("Mixed Berries (250g)", 12.90),
                ("Organic Berries (250g)", 14.90),
            ],
        },
        {
            "name": "Tropical Fruits / Buah Tropika",
            "price": 5.90,
            "category": fruits,
            "description": "Exotic fruits from tropical regions.",
            "variants": [
                ("Mango (1pc)", 5.90),
                ("Pineapple (1pc)", 6.90),
                ("Papaya (1pc)", 5.50),
                ("Dragon Fruit (1pc)", 7.90),
                ("Kiwi (4pcs)", 5.90),
                ("Passion Fruit (5pcs)", 8.90),
            ],
        },
        {
            "name": "Melons / Tembikai",
            "price": 7.90,
            "category": fruits,
            "description": "Refreshing, sweet fruits with high water content.",
            "variants": [
                ("Watermelon (slice)", 7.90),
                ("Honeydew (slice)", 8.50),
                ("Cantaloupe (slice)", 8.50),
                ("Watermelon (whole)", 15.90),
                ("Honeydew (whole)", 12.90),
                ("Cantaloupe (whole)", 12.90),
            ],
        },
    ]

    # Vegetables Products
    vegetable_products = [
        {
            "name": "Leafy Greens / Sayuran Hijau",
            "price": 2.90,
            "category": vegetables,
            "description": "Nutritious green vegetables full of vitamins and minerals.",
            "variants": [
                ("Spinach (250g)", 2.90),
                ("Kale (250g)", 3.50),
                ("Lettuce (1 head)", 3.20),
                ("Cabbage (1 head)", 2.50),
                ("Bok Choy (500g)", 3.50),
                ("Mixed Greens (250g)", 3.90),
            ],
        },
        {
            "name": "Tomatoes / Tomato",
            "price": 1.90,
            "category": vegetables,
            "description": "Versatile fruits commonly used as vegetables in cooking.",
            "variants": [
                ("Regular (500g)", 1.90),
                ("Cherry (250g)", 2.90),
                ("Roma (500g)", 2.50),
                ("Vine-Ripened (500g)", 3.50),
                ("Heirloom (500g)", 4.90),
                ("Organic (500g)", 3.90),
            ],
            "is_featured": True,
        },
        {
            "name": "Onions / Bawang",
            "price": 1.50,
            "category": vegetables,
            "description": "Aromatic bulb vegetables that add flavor to many dishes.",
            "variants": [
                ("Yellow (500g)", 1.50),
                ("Red (500g)", 1.80),
                ("White (500g)", 1.70),
                ("Shallots (250g)", 2.50),
                ("Spring Onions (bunch)", 1.20),
                ("Sweet Onions (500g)", 2.20),
            ],
        },
        {
            "name": "Potatoes / Kentang",
            "price": 1.40,
            "category": vegetables,
            "description": "Starchy root vegetables versatile for many cooking methods.",
            "variants": [
                ("Russet (1kg)", 1.40),
                ("Red (1kg)", 1.60),
                ("Yellow (1kg)", 1.80),
                ("Sweet Potatoes (1kg)", 2.50),
                ("Baby Potatoes (500g)", 2.20),
                ("Purple Potatoes (500g)", 3.50),
            ],
        },
        {
            "name": "Peppers / Lada",
            "price": 2.90,
            "category": vegetables,
            "description": "Colorful vegetables that range from sweet to spicy.",
            "variants": [
                ("Bell Peppers (500g)", 2.90),
                ("Chili Peppers (100g)", 1.90),
                ("Jalapenos (200g)", 2.50),
                ("Habanero (100g)", 3.50),
                ("Capsicum Mix (500g)", 3.90),
                ("Bird's Eye Chili (100g)", 2.20),
            ],
        },
        {
            "name": "Root Vegetables / Sayuran Akar",
            "price": 2.20,
            "category": vegetables,
            "description": "Vegetables that grow underground and are rich in nutrients.",
            "variants": [
                ("Carrots (500g)", 2.20),
                ("Beets (500g)", 2.50),
                ("Radishes (bunch)", 1.90),
                ("Turnips (500g)", 2.30),
                ("Parsnips (500g)", 2.80),
                ("Ginger (250g)", 2.90),
            ],
        },
        {
            "name": "Asian Vegetables / Sayuran Asia",
            "price": 3.50,
            "category": vegetables,
            "description": "Traditional vegetables commonly used in Asian cuisine.",
            "variants": [
                ("Bok Choy (500g)", 3.50),
                ("Chinese Broccoli (250g)", 3.90),
                ("Lotus Root (300g)", 4.50),
                ("Daikon (500g)", 3.20),
                ("Bitter Gourd (500g)", 3.80),
                ("Water Spinach (250g)", 2.90),
            ],
        },
    ]

    # Organic Products
    organic_products = [
        {
            "name": "Organic Salad Mix / Campuran Salad Organik",
            "price": 5.90,
            "category": organic,
            "description": "Pesticide-free mixed greens, ready to serve.",
            "variants": [
                ("Baby Greens (200g)", 5.90),
                ("Herb Mix (200g)", 6.50),
                ("Spring Mix (200g)", 6.20),
                ("Mediterranean (200g)", 6.90),
                ("Superfood Mix (200g)", 7.50),
                ("Family Size (400g)", 10.90),
            ],
        },
        {
            "name": "Organic Vegetable Box / Kotak Sayuran Organik",
            "price": 15.90,
            "category": organic,
            "description": "Assorted organic vegetables harvested weekly.",
            "variants": [
                ("Small Box", 15.90),
                ("Medium Box", 25.90),
                ("Large Box", 35.90),
                ("Premium Box", 45.90),
                ("Family Box", 55.90),
                ("Seasonal Special", 39.90),
            ],
            "is_featured": True,
        },
        {
            "name": "Organic Fruit Box / Kotak Buah Organik",
            "price": 18.90,
            "category": organic,
            "description": "Selection of seasonal organic fruits.",
            "variants": [
                ("Small Box", 18.90),
                ("Medium Box", 28.90),
                ("Large Box", 38.90),
                ("Premium Box", 48.90),
                ("Family Box", 58.90),
                ("Tropical Mix", 42.90),
            ],
        },
        {
            "name": "Organic Mushrooms / Cendawan Organik",
            "price": 4.90,
            "category": organic,
            "description": "Organically grown mushrooms with rich earthy flavors.",
            "variants": [
                ("Button (200g)", 4.90),
                ("Shiitake (150g)", 6.90),
                ("Portobello (200g)", 5.90),
                ("Oyster (150g)", 6.50),
                ("Mixed Varieties (200g)", 7.90),
                ("Gourmet Selection (150g)", 9.90),
            ],
        },
        {
            "name": "Organic Herbs / Herba Organik",
            "price": 3.90,
            "category": organic,
            "description": "Fresh organic herbs to enhance your cooking.",
            "variants": [
                ("Basil (bunch)", 3.90),
                ("Cilantro (bunch)", 3.50),
                ("Mint (bunch)", 3.50),
                ("Rosemary (bunch)", 3.90),
                ("Thyme (bunch)", 3.90),
                ("Mixed Herbs (pack)", 5.90),
            ],
        },
    ]

    # Combine all products
    all_products = fruit_products + vegetable_products + organic_products

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

    print(f"Added {len(all_products)} produce products with variants")


def main():
    """Main function to add produce products"""
    print("Adding produce products...")
    add_produce_products()
    print("Done!")


if __name__ == "__main__":
    main()
