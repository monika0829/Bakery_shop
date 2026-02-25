from django.core.management.base import BaseCommand
from shop.models import Product
import requests
from io import BytesIO
from django.core.files import File
from django.utils.text import slugify


class Command(BaseCommand):
    help = 'Add final product images'

    # Final set of working images
    FINAL_IMAGES = {
        'carrot-cake': 'https://images.unsplash.com/photo-1563729787697-47c87bdabeff?w=800&h=600&fit=crop',
        'lemon-drizzle-cake': 'https://images.unsplash.com/photo-1464349095431-e9a21285b5f3?w=800&h=600&fit=crop',
        'pain-au-chocolat': 'https://images.unsplash.com/photo-1509365465985-25d11c17e812?w=800&h=600&fit=crop',
        'puff-pastry': 'https://images.unsplash.com/photo-1551024601-bfd0882f7b70?w=800&h=600&fit=crop',
        'cream-roll': 'https://images.unsplash.com/photo-1488477181946-6428a0291777?w=800&h=600&fit=crop',
        'peanut-butter-cookies': 'https://images.unsplash.com/photo-1490578474895-699cd4e2cf59?w=800&h=600&fit=crop',
        'butter-cookies': 'https://images.unsplash.com/photo-1464349095431-e9a21285b5f3?w=800&h=600&fit=crop',
        'coconut-cookies': 'https://images.unsplash.com/photo-1563729787697-47c87bdabeff?w=800&h=600&fit=crop',
        'photo-cake': 'https://images.unsplash.com/photo-1558636508-e0db3814bd1d?w=800&h=600&fit=crop',
        'tiered-cake': 'https://images.unsplash.com/photo-1614707267537-b85aaf00c4b7?w=800&h=600&fit=crop',
    }

    def handle(self, *args, **options):
        updated_count = 0

        for product_slug, image_url in self.FINAL_IMAGES.items():
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

        self.stdout.write(self.style.SUCCESS(f'\nSuccessfully added {updated_count} images!'))
