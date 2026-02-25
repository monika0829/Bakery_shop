from django.core.management.base import BaseCommand
from shop.models import Product
from decimal import Decimal


class Command(BaseCommand):
    help = 'Update old products to INR pricing scale'

    def handle(self, *args, **options):
        # Get products with old USD pricing and convert to INR
        # Old products had prices like 2.49, 5.99, etc. (USD scale)
        # New products should be priced in INR (roughly 80x USD)

        products_to_update = Product.objects.filter(price__lt=100)
        for product in products_to_update:
            old_price = float(product.price)
            new_price = Decimal(str(old_price * 100))
            product.price = new_price
            if product.sale_price:
                old_sale = float(product.sale_price)
                product.sale_price = Decimal(str(old_sale * 100))
            product.save()
            self.stdout.write(f'Updated {product.name}: ${old_price} → ₹{new_price}')

        self.stdout.write(self.style.SUCCESS(f'Updated {products_to_update.count()} products to INR pricing'))
