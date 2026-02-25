from django.core.management.base import BaseCommand
from shop.models import Product
import requests
from io import BytesIO
from PIL import Image
import os


class Command(BaseCommand):
    help = 'Add high-quality product images from Unsplash'

    # High-quality Unsplash images for each product
    PRODUCT_IMAGES = {
        # Cakes
        'chocolate-delight-cake': 'https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=800&h=600&fit=crop',
        'vanilla-dream-cake': 'https://images.unsplash.com/photo-1621303837174-89787a7d4729?w=800&h=600&fit=crop',
        'red-velvet-cake': 'https://images.unsplash.com/photo-1614707267537-b85aaf00c4b7?w=800&h=600&fit=crop',
        'carrot-cake': 'https://images.unsplash.com/photo-1621303837693-aa2c4b3efc21?w=800&h=600&fit=crop',
        'lemon-drizzle-cake': 'https://images.unsplash.com/photo-1519869325930-281384f8e32d?w=800&h=600&fit=crop',
        'black-forest-cake': 'https://images.unsplash.com/photo-1606890737304-57a1ca8a5b62?w=800&h=600&fit=crop',
        'butterscotch-cake': 'https://images.unsplash.com/photo-1565958011703-44f9829ba187?w=800&h=600&fit=crop',
        'pineapple-cake': 'https://images.unsplash.com/photo-1464349095431-e9a21285b5f3?w=800&h=600&fit=crop',

        # Pastries
        'croissant': 'https://images.unsplash.com/photo-1555507036-ab1f40f8fe81?w=800&h=600&fit=crop',
        'pain-au-chocolat': 'https://images.unsplash.com/photo-1558961363-fa8fdfb98dca?w=800&h=600&fit=crop',
        'danish-pastry': 'https://images.unsplash.com/photo-1509365465985-25d11c17e812?w=800&h=600&fit=crop',
        'cinnamon-roll': 'https://images.unsplash.com/photo-1509365465985-25d11c17e812?w=800&h=600&fit=crop',
        'eclair': 'https://images.unsplash.com/photo-1525060608342-8988377a7350?w=800&h=600&fit=crop',
        'puff-pastry': 'https://images.unsplash.com/photo-1558305374-1eaa5cb93b95?w=800&h=600&fit=crop',
        'cream-roll': 'https://images.unsplash.com/photo-1607671122550-44d3c12c9f8a?w=800&h=600&fit=crop',

        # Breads
        'sourdough-bread': 'https://images.unsplash.com/photo-1509440159596-0249088772ff?w=800&h=600&fit=crop',
        'french-baguette': 'https://images.unsplash.com/photo-1549931319-a545dcf3bc73?w=800&h=600&fit=crop',
        'whole-wheat-bread': 'https://images.unsplash.com/photo-1595375807373-25b09e9ebc23?w=800&h=600&fit=crop',
        'ciabatta': 'https://images.unsplash.com/photo-1586444248302-8f3b8abb8c6a?w=800&h=600&fit=crop',
        'multigrain-bread': 'https://images.unsplash.com/photo-1534620808146-d33bb39128b2?w=800&h=600&fit=crop',
        'milk-bread': 'https://images.unsplash.com/photo-1565557623262-b51c2513a641?w=800&h=600&fit=crop',
        'brown-bread': 'https://images.unsplash.com/photo-1598373182133-52452f7691ef?w=800&h=600&fit=crop',

        # Cookies
        'chocolate-chip-cookies': 'https://images.unsplash.com/photo-1499636136210-6f4ee915583e?w=800&h=600&fit=crop',
        'oatmeal-raisin-cookies': 'https://images.unsplash.com/photo-1490578474895-699cd4e2cf59?w=800&h=600&fit=crop',
        'peanut-butter-cookies': 'https://images.unsplash.com/photo-1615485829824-18e1c2e3b332?w=800&h=600&fit=crop',
        'cashew-cookies': 'https://images.unsplash.com/photo-1599378697573-9e9e7ce1fa0b?w=800&h=600&fit=crop',
        'almond-cookies': 'https://images.unsplash.com/photo-156372976836-dca3fefc362e?w=800&h=600&fit=crop',
        'butter-cookies': 'https://images.unsplash.com/photo-1623962425072-5751d9c5e2e0?w=800&h=600&fit=crop',
        'coconut-cookies': 'https://images.unsplash.com/photo-1455619292465-dced43d6b759?w=800&h=600&fit=crop',

        # Custom Cakes
        'birthday-cake-package': 'https://images.unsplash.com/photo-1558636508-e0db3814bd1d?w=800&h=600&fit=crop',
        'wedding-cake': 'https://images.unsplash.com/photo-1535254973040-6877109c9581?w=800&h=600&fit=crop',
        'anniversary-cake': 'https://images.unsplash.com/photo-1562440499-64c9a111f713?w=800&h=600&fit=crop',
        'photo-cake': 'https://images.unsplash.com/photo-1576618148400-f54bed99fcf8?w=800&h=600&fit=crop',
        'tiered-cake': 'https://images.unsplash.com/photo-1522057302885-5878e497efad?w=800&h=600&fit=crop',
    }

    def handle(self, *args, **options):
        updated_count = 0

        for product_slug, image_url in self.PRODUCT_IMAGES.items():
            try:
                product = Product.objects.get(slug=product_slug)

                # Download image
                self.stdout.write(f'Downloading image for {product.name}...')
                response = requests.get(image_url, timeout=30)
                response.raise_for_status()

                # Save image to product
                from django.core.files import File
                from django.utils.text import slugify

                # Generate filename
                ext = image_url.split('.')[-1].split('?')[0]
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
                self.stdout.write(self.style.ERROR(f'Error adding image for {product_slug}: {str(e)}'))

        self.stdout.write(self.style.SUCCESS(f'\nSuccessfully added images for {updated_count} products!'))
