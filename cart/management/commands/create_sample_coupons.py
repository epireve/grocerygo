from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from cart.models import Coupon


class Command(BaseCommand):
    help = "Creates sample discount coupons for testing"

    def handle(self, *args, **options):
        # Delete existing coupons
        Coupon.objects.all().delete()
        self.stdout.write(self.style.WARNING("Deleted all existing coupons"))

        # Current time for validity ranges
        now = timezone.now()

        # Create percentage discount coupon
        coupon1 = Coupon.objects.create(
            code="WELCOME10",
            discount_type="percentage",
            value=10,  # 10% off
            min_purchase=50.00,  # Minimum RM50 purchase
            valid_from=now,
            valid_to=now + timedelta(days=30),  # Valid for 30 days
            is_active=True,
        )

        # Create fixed amount discount coupon
        coupon2 = Coupon.objects.create(
            code="SAVE20RM",
            discount_type="fixed",
            value=20.00,  # RM20 off
            min_purchase=100.00,  # Minimum RM100 purchase
            valid_from=now,
            valid_to=now + timedelta(days=14),  # Valid for 14 days
            is_active=True,
        )

        # Create expired coupon for testing
        coupon3 = Coupon.objects.create(
            code="EXPIRED25",
            discount_type="percentage",
            value=25,  # 25% off
            min_purchase=0.00,  # No minimum purchase
            valid_from=now - timedelta(days=60),  # Started 60 days ago
            valid_to=now - timedelta(days=30),  # Ended 30 days ago
            is_active=True,
        )

        # Create inactive coupon for testing
        coupon4 = Coupon.objects.create(
            code="INACTIVE15",
            discount_type="percentage",
            value=15,  # 15% off
            min_purchase=25.00,  # Minimum RM25 purchase
            valid_from=now,
            valid_to=now + timedelta(days=30),  # Valid for 30 days
            is_active=False,
        )

        # Create future coupon for testing
        coupon5 = Coupon.objects.create(
            code="FUTURE30",
            discount_type="percentage",
            value=30,  # 30% off
            min_purchase=200.00,  # Minimum RM200 purchase
            valid_from=now + timedelta(days=10),  # Starts in 10 days
            valid_to=now + timedelta(days=40),  # Valid for 30 days after start
            is_active=True,
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully created {Coupon.objects.count()} sample coupons:"
            )
        )
        self.stdout.write(f"1. {coupon1} (Valid, Percentage)")
        self.stdout.write(f"2. {coupon2} (Valid, Fixed Amount)")
        self.stdout.write(f"3. {coupon3} (Expired)")
        self.stdout.write(f"4. {coupon4} (Inactive)")
        self.stdout.write(f"5. {coupon5} (Future)")
