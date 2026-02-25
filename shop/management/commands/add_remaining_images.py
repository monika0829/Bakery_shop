from django.core.management.base import BaseCommand
from shop.models import Product
import requests
from io import BytesIO
from django.core.files import File
from django.utils.text import slugify


class Command(BaseCommand):
    help = 'Add remaining product images with working Unsplash URLs'

    # Additional working Unsplash images
    REMAINING_IMAGES = {
        # Cakes
        'carrot-cake': 'https://images.unsplash.com/photo-1586985289688-ca2581a84ba7?w=800&h=600&fit=crop',
        'lemon-drizzle-cake': 'https://images.unsplash.com/photo-1601000938357-a8a7b7476953?w=800&h=600&fit=crop',

        # Pastries
        'croissant': 'https://images.unsplash.com/photo-1509365465985-25d11c17e812?w=800&h=600&fit=crop',
        'pain-au-chocolat': 'https://images.unsplash.com/photo-1558961363-fa8fdfb98dca?w=800&h=600&fit=crop',
        'eclair': 'https://images.unsplash.com/photo-1488477181946-6428a0291777?w=800&h=600&fit=crop',
        'puff-pastry': 'https://images.unsplash.com/photo-1551024601-bfd0882f7b70?w=800&h=600&fit=crop',
        'cream-roll': 'https://images.unsplash.com/photo-1558961363-fa8fdfb98dca?w=800&h=600&fit=crop',

        # Breads
        'whole-wheat-bread': 'https://images.unsplash.com/photo-1534620808146-d33bb39128b2?w=800&h=600&fit=crop',
        'ciabatta': 'https://images.unsplash.com/photo-1517433670267-08bbd4be890f?w=800&h=600&fit=crop',

        # Cookies
        'peanut-butter-cookies': 'https://images.unsplash.com/photo-1615486531077-e76180263c26?w=800&h=600&fit=crop',
        'cashew-cookies': 'https://images.unsplash.com/photo-1490578474895-699cd4e2cf59?w=800&h=600&fit=crop',
        'almond-cookies': 'https://images.unsplash.com/photo-1464349095431-e9a21285b5f3?w=800&h=600&fit=crop',
        'butter-cookies': 'https://images.unsplash.com/photo-1623962425072-5751d9c5e2e0?w=800&h=600&fit=crop',
        'coconut-cookies': 'https://images.unsplash.com/photo-1455619292465-dced43d6b759?w=800&h=600&fit=crop',

        # Custom Cakes
        'wedding-cake': 'https://images.unsplash.com/photo-1562440499-64c9a111f713?w=800&h=600&fit=crop',
        'photo-cake': 'https://images.unsplash.com/photo-1586985289688-ca2581a84ba7?w=800&h=600&fit=crop',
        'tiered-cake': 'https://images.unsplash.com/photo-1535254973040-6877109c9581?w=800&h=600&fit=crop',
    }

    def handle(self, *args, **options):
        updated_count = 0

        for product_slug, image_url in self.REMAINING_IMAGES.items():
            try:
                product = Product.objects.get(slug=product_slug)

                # Download image
                self.stdout.write(f'Downloading image for {product.name}...')
                response = requests.get(image_url, timeout=30)
                response.raise_for_status()

                # Generate filename
                ext = 'jpg'
                filename = f"{slugify(product.name)}.{ext}"

                # Save to product's image field
                product.image.save(
                    filename,
                    File(BytesIO(response.content)),
                    save=True
                )

                product.save()
                updated_count += 1
                self.stdout.write(self.style.SUCCESS(f'✓ Added image for {product.name}'))

            except Product.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'Product not found: {product_slug}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))

        self.stdout.write(self.style.SUCCESS(f'\nSuccessfully added images for {updated_count} products!'))
