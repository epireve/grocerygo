#!/usr/bin/env python
import os
import sys
import django
import requests
import urllib.parse
import http.client
import json
import random
from io import BytesIO
from pathlib import Path
from django.core.files.base import ContentFile
from dotenv import load_dotenv
from PIL import Image
import time

# Setup Django
sys.path.append(str(Path(__file__).resolve().parent.parent))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "grocerygo.settings")
django.setup()

from products.models import Product, Category
from django.conf import settings

# Load environment variables
load_dotenv()
SERPER_API_KEY = os.getenv("SERPER_API_KEY")

if not SERPER_API_KEY:
    print("Error: SERPER_API_KEY not found in .env file")
    sys.exit(1)


def search_image_from_google(query, country="my"):
    """
    Search for images using Google Serper API
    Returns a list of image URLs
    """
    conn = http.client.HTTPSConnection("google.serper.dev")

    # Enhance query to improve chances of getting product images
    enhanced_query = f"{query} product photo"

    payload = json.dumps(
        {"q": enhanced_query, "gl": country}  # Country code (Malaysia)
    )

    headers = {"X-API-KEY": SERPER_API_KEY, "Content-Type": "application/json"}

    try:
        conn.request("POST", "/images", payload, headers)
        res = conn.getresponse()
        data = json.loads(res.read().decode("utf-8"))

        # Extract image URLs from response
        images = data.get("images", [])
        image_urls = [img.get("imageUrl") for img in images if img.get("imageUrl")]

        return image_urls
    except Exception as e:
        print(f"Error searching for image: {e}")
        return []


def download_image(url):
    """Download an image from a URL and return as ContentFile"""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return ContentFile(response.content)
        return None
    except Exception as e:
        print(f"Error downloading image from {url}: {e}")
        return None


def resize_image(image_content, max_width=800, max_height=800):
    """Resize image if it's too large"""
    try:
        img = Image.open(BytesIO(image_content.read()))

        # Reset file pointer
        image_content.seek(0)

        # Check if resizing is needed
        if img.width > max_width or img.height > max_height:
            img.thumbnail((max_width, max_height))
            output = BytesIO()
            img.save(output, format=img.format or "JPEG", quality=85)
            output.seek(0)
            return ContentFile(output.read())

        # If no resizing needed, return original content
        return image_content
    except Exception as e:
        print(f"Error resizing image: {e}")
        return image_content


def image_file_exists(file_path):
    """Check if the image file actually exists on the filesystem"""
    if not file_path:
        return False

    # Get the full path to the media file
    full_path = os.path.join(settings.MEDIA_ROOT, str(file_path))
    return os.path.exists(full_path)


def add_image_to_product(product, max_retries=3):
    """Add a relevant image to a product using Google search"""
    # Check if the image file actually exists
    if product.image and image_file_exists(product.image):
        print(f"Product already has image: {product.name}")
        return True

    # If the image field exists but file doesn't, clear it
    if product.image and not image_file_exists(product.image):
        print(
            f"Product {product.name} has image reference but file is missing. Clearing reference."
        )
        product.image = None
        product.save()

    # Create search query based on product name
    query = product.name

    # If product has a category, include it in the search
    if product.category:
        query = f"{product.name} {product.category.name}"

    for attempt in range(max_retries):
        image_urls = search_image_from_google(query)

        if not image_urls:
            print(f"No images found for {product.name}, retrying...")
            continue

        # Try images in order until one works
        for url in image_urls:
            try:
                image_content = download_image(url)
                if not image_content:
                    continue

                # Resize image if needed
                image_content = resize_image(image_content)

                # Create a filename based on the product slug
                filename = f"{product.slug}.jpg"

                # Save the image to the product
                product.image.save(filename, image_content, save=True)
                print(f"Added image to product: {product.name} (from {url})")
                return True

            except Exception as e:
                print(f"Error processing image for {product.name}: {e}")
                continue

        # Wait a bit before retrying to avoid rate limits
        time.sleep(1)

    print(f"Failed to add image to product {product.name} after {max_retries} attempts")
    return False


def add_image_to_category(category, max_retries=3):
    """Add a relevant image to a category using Google search"""
    # Check if the image file actually exists
    if category.image and image_file_exists(category.image):
        print(f"Category already has image: {category.name}")
        return True

    # If the image field exists but file doesn't, clear it
    if category.image and not image_file_exists(category.image):
        print(
            f"Category {category.name} has image reference but file is missing. Clearing reference."
        )
        category.image = None
        category.save()

    # Create search query based on category name
    query = f"{category.name} food category"

    for attempt in range(max_retries):
        image_urls = search_image_from_google(query)

        if not image_urls:
            print(f"No images found for category {category.name}, retrying...")
            continue

        # Try images in order until one works
        for url in image_urls:
            try:
                image_content = download_image(url)
                if not image_content:
                    continue

                # Resize image if needed
                image_content = resize_image(
                    image_content, max_width=1200, max_height=800
                )

                # Create a filename based on the category slug
                filename = f"category_{category.slug}.jpg"

                # Save the image to the category
                category.image.save(filename, image_content, save=True)
                print(f"Added image to category: {category.name} (from {url})")
                return True

            except Exception as e:
                print(f"Error processing image for category {category.name}: {e}")
                continue

        # Wait a bit before retrying to avoid rate limits
        time.sleep(1)

    print(
        f"Failed to add image to category {category.name} after {max_retries} attempts"
    )
    return False


def add_images_to_categories():
    """Add images to categories without images"""
    categories = Category.objects.filter(active=True)
    print(f"Found {categories.count()} active categories")

    for category in categories:
        add_image_to_category(category)
        # Add a delay to avoid hitting API rate limits
        time.sleep(1)


def add_images_to_featured_products():
    """Add images to featured products without images"""
    featured_products = Product.objects.filter(is_featured=True, parent=None)
    print(f"Found {featured_products.count()} featured products")

    for product in featured_products:
        add_image_to_product(product)
        # Add a delay to avoid hitting API rate limits
        time.sleep(1)


def add_images_to_products(limit=60):
    """Add images to non-featured products without images, limited to conserve API usage"""
    # Get products without images or with missing image files
    products_without_images = []
    for product in Product.objects.filter(parent=None).exclude(is_featured=True):
        if not product.image or not image_file_exists(product.image):
            products_without_images.append(product)
            if len(products_without_images) >= limit:
                break

    print(
        f"Adding images to {len(products_without_images)} products (limited to {limit})"
    )

    for product in products_without_images:
        add_image_to_product(product)
        # Add a delay to avoid hitting API rate limits
        time.sleep(1)


def mark_products_as_featured():
    """Mark some products as featured if we don't have enough"""
    featured_count = Product.objects.filter(is_featured=True, parent=None).count()

    if featured_count < 8:
        # Get non-featured parent products
        non_featured = Product.objects.filter(is_featured=False, parent=None)
        # Get categories to ensure diversity
        categories = Category.objects.all()

        need_to_feature = 8 - featured_count
        featured = 0

        # Try to get one product from each category first
        for category in categories:
            if featured >= need_to_feature:
                break

            product = non_featured.filter(category=category).first()
            if product:
                product.is_featured = True
                product.save()
                print(f"Marked as featured: {product.name}")
                featured += 1

        # If we still need more, just get random products
        if featured < need_to_feature:
            remaining = non_featured.exclude(is_featured=True)[
                : need_to_feature - featured
            ]
            for product in remaining:
                product.is_featured = True
                product.save()
                print(f"Marked as featured: {product.name}")


def main():
    """Main function to add images to products and categories"""
    print("Ensuring we have enough featured products...")
    mark_products_as_featured()

    print("\nAdding images to categories...")
    add_images_to_categories()

    print("\nAdding images to featured products...")
    add_images_to_featured_products()

    print("\nAdding images to selected non-featured products...")
    add_images_to_products(limit=60)

    print("\nDone! Product images have been updated using Google Images search.")


if __name__ == "__main__":
    main()
