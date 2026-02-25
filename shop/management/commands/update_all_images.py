from django.core.management.base import BaseCommand
from shop.models import Product
import requests
from io import BytesIO
from django.core.files import File
from django.utils.text import slugify


class Command(BaseCommand):
    help = 'Add all remaining product images with reliable URLs'

    # Comprehensive list with verified working URLs
    IMAGE_URLS = {
        # Cakes
        'carrot-cake': 'https://images.unsplash.com/photo-1606890737304-57a1ca8a5b62?w=800&h=600&fit=crop',
        'vanilla-dream-cake': 'https://images.unsplash.com/photo-1621303837174-89787a7d4729?w=800&h=600&fit=crop',

        # Pastries
        'puff-pastry': 'https://images.unsplash.com/photo-1509365465985-25d11c17e812?w=800&h=600&fit=crop',

        # Breads
        'brown-bread': 'https://images.unsplash.com/photo-1598373182133-52452f7691ef?w=800&h=600&fit=crop',
        'milk-bread': 'https://images.unsplash.com/photo-1565557623262-b51c2513a641?w=800&h=600&fit=crop',

        # Cookies
        'coconut-cookies': 'https://images.unsplash.com/photo-1499636136210-6f4ee915583e?w=800&h=600&fit=crop',
        'sugar-cookies': 'https://images.unsplash.com/photo-1490578474895-699cd4e2cf59?w=800&h=600&fit=crop',
        'macadamia-cookies': 'https://images.unsplash.com/photo-1464349095431-e9a21285b5f3?w=800&h=600&fit=crop',
    }

    def handle(self, *args, **options):
        updated_count = 0
        skipped_count = 0

        for product_slug, image_url in self.IMAGE_URLS.items():
            try:
                # Check if product already has image
                product = Product.objects.get(slug=product_slug)
                if product.image and product.image.name:
                    self.stdout.write(f'Skipping {product.name} (already has image)')
                    skipped_count += 1
                    continue

                # Download image
                self.stdout.write(f'Downloading image for {product.name}...')
                response = requests.get(image_url, timeout=30)
                response.raise_for_status()

                # Generate filename
                filename = f"{slugify(product.name)}.jpg"

                # Save to product's image field
                product.image.save(
                    filename,
                    File(BytesIO(response.content)),
                    save=True
                )

                updated_count += 1
                self.stdout.write(self.style.SUCCESS(f'✓ Added image for {product.name}'))

            except Product.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'Product not found: {product_slug}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error for {product_slug}: {str(e)}'))

        self.stdout.write(self.style.SUCCESS(f'\nUpdated: {updated_count} | Skipped: {skipped_count}'))
