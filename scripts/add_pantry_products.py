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


def add_pantry_products():
    """Add pantry products"""

    # Ensure the Pantry category exists
    pantry = create_category_if_not_exists(
        "Pantry", description="Essential staples and ingredients for your kitchen"
    )

    # Create subcategories
    rice_grains = create_category_if_not_exists(
        "Rice & Grains", pantry, "Rice, pasta, noodles, and other grains"
    )
    canned_goods = create_category_if_not_exists(
        "Canned Goods", pantry, "Preserved fruits, vegetables, and proteins"
    )
    cooking_oils = create_category_if_not_exists(
        "Cooking Oils", pantry, "Oils for cooking and baking"
    )
    condiments = create_category_if_not_exists(
        "Condiments & Sauces", pantry, "Flavor enhancers for your dishes"
    )
    baking = create_category_if_not_exists(
        "Baking Supplies", pantry, "Ingredients for baking"
    )

    # Rice & Grains Products
    rice_grain_products = [
        {
            "name": "White Rice / Beras Putih",
            "price": 5.90,
            "category": rice_grains,
            "description": "Premium quality white rice, a staple in many Asian dishes.",
            "variants": [
                ("1kg Pack", 5.90),
                ("5kg Pack", 25.90),
                ("10kg Pack", 49.90),
                ("Jasmine", 6.90),
                ("Basmati", 8.90),
                ("Short Grain", 7.90),
            ],
            "is_featured": True,
        },
        {
            "name": "Brown Rice / Beras Perang",
            "price": 6.90,
            "category": rice_grains,
            "description": "Wholesome brown rice with more fiber and nutrients than white rice.",
            "variants": [
                ("1kg Pack", 6.90),
                ("5kg Pack", 32.90),
                ("Organic", 9.90),
                ("Red Rice", 8.90),
                ("Black Rice", 10.90),
                ("Mixed Grain", 9.90),
            ],
        },
        {
            "name": "Pasta / Pasta",
            "price": 4.50,
            "category": rice_grains,
            "description": "Italian pasta in various shapes for versatile meal options.",
            "variants": [
                ("Spaghetti", 4.50),
                ("Penne", 4.50),
                ("Fusilli", 4.50),
                ("Linguine", 4.90),
                ("Whole Wheat", 5.90),
                ("Gluten-Free", 7.90),
            ],
        },
        {
            "name": "Instant Noodles / Mi Segera",
            "price": 3.90,
            "category": rice_grains,
            "description": "Quick and convenient noodles ready in minutes.",
            "variants": [
                ("Chicken (5pcs)", 3.90),
                ("Curry (5pcs)", 3.90),
                ("Seafood (5pcs)", 4.50),
                ("Spicy (5pcs)", 4.50),
                ("Tom Yum (5pcs)", 4.90),
                ("Premium (5pcs)", 7.90),
            ],
        },
        {
            "name": "Specialty Rice / Beras Istimewa",
            "price": 12.90,
            "category": rice_grains,
            "description": "Special rice varieties for specific dishes.",
            "variants": [
                ("Sushi Rice", 12.90),
                ("Glutinous Rice", 9.90),
                ("Biryani Rice", 10.90),
                ("Paella Rice", 14.90),
                ("Wild Rice", 16.90),
                ("Quinoa", 19.90),
            ],
        },
    ]

    # Canned Goods Products
    canned_products = [
        {
            "name": "Canned Tuna / Tuna Tin",
            "price": 6.90,
            "category": canned_goods,
            "description": "Convenient and versatile canned tuna for salads, sandwiches, and more.",
            "variants": [
                ("In Water", 6.90),
                ("In Oil", 6.90),
                ("Chunk Light", 7.50),
                ("Solid White", 8.90),
                ("Spicy", 7.90),
                ("Premium", 9.90),
            ],
        },
        {
            "name": "Canned Sardines / Sardin Tin",
            "price": 5.50,
            "category": canned_goods,
            "description": "Nutritious sardines packed in oil or tomato sauce.",
            "variants": [
                ("In Tomato Sauce", 5.50),
                ("In Oil", 5.50),
                ("In Chili Sauce", 5.90),
                ("In Brine", 5.50),
                ("Spicy", 5.90),
                ("Premium", 7.90),
            ],
            "is_featured": True,
        },
        {
            "name": "Canned Vegetables / Sayur Tin",
            "price": 4.50,
            "category": canned_goods,
            "description": "Preserved vegetables ready to use in your recipes.",
            "variants": [
                ("Corn", 4.50),
                ("Peas", 4.50),
                ("Mixed Vegetables", 4.90),
                ("Mushrooms", 5.50),
                ("Asparagus", 7.90),
                ("Bamboo Shoots", 5.90),
            ],
        },
        {
            "name": "Canned Fruits / Buah Tin",
            "price": 5.90,
            "category": canned_goods,
            "description": "Sweet fruits preserved in light syrup.",
            "variants": [
                ("Peaches", 5.90),
                ("Pineapple", 5.90),
                ("Mixed Fruits", 6.50),
                ("Mandarin Oranges", 6.90),
                ("Lychee", 7.50),
                ("Longan", 7.50),
            ],
        },
        {
            "name": "Canned Beans / Kacang Tin",
            "price": 4.90,
            "category": canned_goods,
            "description": "Ready-to-use beans for quick meals and side dishes.",
            "variants": [
                ("Baked Beans", 4.90),
                ("Red Kidney Beans", 4.90),
                ("Chickpeas", 4.90),
                ("Black Beans", 5.50),
                ("Lentils", 5.50),
                ("Mixed Beans", 5.90),
            ],
        },
    ]

    # Cooking Oils Products
    oil_products = [
        {
            "name": "Vegetable Oil / Minyak Sayuran",
            "price": 8.90,
            "category": cooking_oils,
            "description": "All-purpose cooking oil for everyday use.",
            "variants": [
                ("1L Bottle", 8.90),
                ("2L Bottle", 16.90),
                ("5L Bottle", 39.90),
                ("Premium", 11.90),
                ("Blended", 9.90),
                ("Spray Bottle", 12.90),
            ],
        },
        {
            "name": "Olive Oil / Minyak Zaitun",
            "price": 19.90,
            "category": cooking_oils,
            "description": "Premium olive oil for cooking and dressing.",
            "variants": [
                ("Extra Virgin (500ml)", 19.90),
                ("Pure (500ml)", 16.90),
                ("Light (500ml)", 15.90),
                ("Spray Bottle", 18.90),
                ("Premium (500ml)", 25.90),
                ("Organic (500ml)", 29.90),
            ],
        },
        {
            "name": "Coconut Oil / Minyak Kelapa",
            "price": 12.90,
            "category": cooking_oils,
            "description": "Natural coconut oil for cooking and beauty uses.",
            "variants": [
                ("500ml Jar", 12.90),
                ("Virgin (500ml)", 16.90),
                ("Refined (500ml)", 14.90),
                ("Organic (500ml)", 19.90),
                ("Cold Pressed (500ml)", 18.90),
                ("Cooking Spray", 15.90),
            ],
        },
        {
            "name": "Sesame Oil / Minyak Bijan",
            "price": 9.90,
            "category": cooking_oils,
            "description": "Aromatic oil for Asian cuisine.",
            "variants": [
                ("250ml Bottle", 9.90),
                ("500ml Bottle", 18.90),
                ("Pure", 11.90),
                ("Toasted", 12.90),
                ("Premium", 15.90),
                ("Organic", 16.90),
            ],
        },
        {
            "name": "Specialty Oils / Minyak Khas",
            "price": 15.90,
            "category": cooking_oils,
            "description": "Special oils for specific cooking purposes.",
            "variants": [
                ("Avocado Oil", 15.90),
                ("Grapeseed Oil", 13.90),
                ("Walnut Oil", 19.90),
                ("Truffle Oil", 29.90),
                ("Peanut Oil", 12.90),
                ("Rice Bran Oil", 14.90),
            ],
            "is_featured": True,
        },
    ]

    # Condiments Products
    condiment_products = [
        {
            "name": "Soy Sauce / Kicap",
            "price": 5.90,
            "category": condiments,
            "description": "Essential seasoning for Asian cuisine.",
            "variants": [
                ("Light (500ml)", 5.90),
                ("Dark (500ml)", 5.90),
                ("Low Sodium (500ml)", 7.50),
                ("Premium (500ml)", 9.90),
                ("Japanese Style (500ml)", 12.90),
                ("Organic (500ml)", 13.90),
            ],
        },
        {
            "name": "Chili Sauce / Sos Cili",
            "price": 4.90,
            "category": condiments,
            "description": "Spicy sauce to add heat to your dishes.",
            "variants": [
                ("Regular (340g)", 4.90),
                ("Extra Hot (340g)", 4.90),
                ("Sweet (340g)", 5.20),
                ("Garlic (340g)", 5.50),
                ("Sriracha (430ml)", 8.90),
                ("Premium (340g)", 7.90),
            ],
        },
        {
            "name": "Tomato Ketchup / Sos Tomato",
            "price": 4.50,
            "category": condiments,
            "description": "Classic tomato condiment for burgers, fries, and more.",
            "variants": [
                ("Regular (340g)", 4.50),
                ("Spicy (340g)", 4.90),
                ("No Added Sugar (340g)", 5.90),
                ("Organic (340g)", 7.90),
                ("Squeezable (567g)", 7.50),
                ("Value Size (1kg)", 9.90),
            ],
        },
        {
            "name": "Oyster Sauce / Sos Tiram",
            "price": 6.90,
            "category": condiments,
            "description": "Rich, savory sauce for stir-fries and marinades.",
            "variants": [
                ("Regular (510g)", 6.90),
                ("Premium (510g)", 9.90),
                ("Vegetarian (510g)", 8.90),
                ("Low Sodium (510g)", 8.50),
                ("Squeeze Bottle (355ml)", 8.90),
                ("Value Size (907g)", 12.90),
            ],
        },
        {
            "name": "Fish Sauce / Sos Ikan",
            "price": 5.90,
            "category": condiments,
            "description": "Traditional Southeast Asian sauce made from fermented fish.",
            "variants": [
                ("Regular (700ml)", 5.90),
                ("Premium (700ml)", 8.90),
                ("Thai Style (700ml)", 7.90),
                ("Vietnamese Style (700ml)", 7.90),
                ("Low Sodium (700ml)", 8.50),
                ("Organic (500ml)", 11.90),
            ],
        },
    ]

    # Baking Supplies Products
    baking_products = [
        {
            "name": "All-Purpose Flour / Tepung",
            "price": 3.90,
            "category": baking,
            "description": "Versatile flour for all your baking needs.",
            "variants": [
                ("1kg Pack", 3.90),
                ("2kg Pack", 7.50),
                ("Self-Rising", 4.50),
                ("Cake Flour", 4.90),
                ("Bread Flour", 4.90),
                ("Whole Wheat", 4.90),
            ],
        },
        {
            "name": "Sugar / Gula",
            "price": 3.50,
            "category": baking,
            "description": "Sweetener for baking and cooking.",
            "variants": [
                ("White (1kg)", 3.50),
                ("Brown (1kg)", 4.50),
                ("Caster (1kg)", 4.90),
                ("Icing (500g)", 3.90),
                ("Palm Sugar (500g)", 5.90),
                ("Coconut Sugar (500g)", 6.90),
            ],
        },
        {
            "name": "Baking Powder & Soda / Serbuk Penaik",
            "price": 2.90,
            "category": baking,
            "description": "Essential leavening agents for baking.",
            "variants": [
                ("Baking Powder (100g)", 2.90),
                ("Baking Soda (100g)", 2.90),
                ("Double Acting (100g)", 3.50),
                ("Aluminum Free (100g)", 3.90),
                ("Cream of Tartar (100g)", 4.90),
                ("Premium (100g)", 4.50),
            ],
        },
        {
            "name": "Vanilla Extract / Ekstrak Vanila",
            "price": 9.90,
            "category": baking,
            "description": "Flavor enhancer for baked goods and desserts.",
            "variants": [
                ("Pure (100ml)", 9.90),
                ("Imitation (100ml)", 5.90),
                ("Vanilla Bean Paste (100ml)", 14.90),
                ("Bourbon Vanilla (100ml)", 12.90),
                ("Organic (100ml)", 15.90),
                ("Mexican Vanilla (100ml)", 16.90),
            ],
        },
        {
            "name": "Chocolate Chips / Cip Coklat",
            "price": 8.90,
            "category": baking,
            "description": "Sweet morsels for cookies, cakes, and desserts.",
            "variants": [
                ("Semi-Sweet (250g)", 8.90),
                ("Milk Chocolate (250g)", 8.90),
                ("Dark Chocolate (250g)", 9.90),
                ("White Chocolate (250g)", 9.90),
                ("Mini Chips (250g)", 8.90),
                ("Chunks (250g)", 10.90),
            ],
        },
    ]

    # Combine all products
    all_products = (
        rice_grain_products
        + canned_products
        + oil_products
        + condiment_products
        + baking_products
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

    print(f"Added {len(all_products)} pantry products with variants")


def main():
    """Main function to add pantry products"""
    print("Adding pantry products...")
    add_pantry_products()
    print("Done!")


if __name__ == "__main__":
    main()
