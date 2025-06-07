from django.core.management.base import BaseCommand
from products.models import Category, Product
from decimal import Decimal


class Command(BaseCommand):
    help = "Create test products for pagination testing"

    def handle(self, *args, **options):
        # Get or create a test category
        category, created = Category.objects.get_or_create(
            name="Test Category",
            defaults={
                "slug": "test-category",
                "description": "Test category for pagination",
                "active": True,
            },
        )

        if created:
            self.stdout.write(self.style.SUCCESS("Created test category"))

        # Create 20 test products
        for i in range(1, 21):
            product, created = Product.objects.get_or_create(
                name=f"Test Product {i}",
                defaults={
                    "slug": f"test-product-{i}",
                    "description": f"Description for test product {i}",
                    "price": Decimal(f"{10 + i}.99"),
                    "category": category,
                    "stock": 100,
                    "is_active": True,
                    "is_featured": i % 3 == 0,  # Every 3rd product is featured
                },
            )

            if created:
                self.stdout.write(f"Created test product {i}")

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully created test data. "
                f"Total products: {Product.objects.count()}, "
                f"Total categories: {Category.objects.count()}"
            )
        )
