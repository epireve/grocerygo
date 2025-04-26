import os
import sys
import django

# Add the project's root directory to Python's path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "grocerygo.settings")
django.setup()

from products.models import Category

# Categories to create
categories = [
    {
        "name": "Fresh Produce",
        "description": "Fresh fruits and vegetables sourced from local farms and global suppliers.",
        "active": True,
    },
    {
        "name": "Bakery",
        "description": "Freshly baked bread, pastries, and other baked goods.",
        "active": True,
    },
    {
        "name": "Pantry",
        "description": "Essential items for your pantry including canned goods, pasta, rice, and more.",
        "active": True,
    },
    {
        "name": "Specialty & Organic",
        "description": "Premium and organic products for health-conscious consumers.",
        "active": True,
    },
    {
        "name": "Vegetables",
        "description": "Fresh vegetables including leafy greens, root vegetables, and more.",
        "parent_name": "Fresh Produce",
        "active": True,
    },
    {
        "name": "Dairy",
        "description": "Milk, cheese, yogurt, and other dairy products.",
        "active": True,
    },
    {
        "name": "Fruits",
        "description": "Fresh seasonal and exotic fruits.",
        "parent_name": "Fresh Produce",
        "active": True,
    },
    {
        "name": "Snacks",
        "description": "Chips, crackers, nuts, and other snack foods.",
        "active": True,
    },
]

# Create categories
for category_data in categories:
    parent_name = category_data.pop("parent_name", None)

    # Check if category already exists
    if not Category.objects.filter(name=category_data["name"]).exists():
        # If category has a parent, find the parent
        if parent_name:
            try:
                parent = Category.objects.get(name=parent_name)
                category_data["parent"] = parent
            except Category.DoesNotExist:
                print(
                    f"Parent category '{parent_name}' doesn't exist. Creating {category_data['name']} without parent."
                )

        # Create the category
        category = Category.objects.create(**category_data)
        print(f"Created category: {category.name}")
    else:
        print(f"Category '{category_data['name']}' already exists. Skipping.")

print("Category creation completed!")
