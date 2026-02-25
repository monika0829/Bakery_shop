from django.core.management.base import BaseCommand
from shop.models import Category
import requests
from io import BytesIO
from django.core.files import File
from django.utils.text import slugify


class Command(BaseCommand):
    help = 'Add category images'

    CATEGORY_IMAGES = {
        'cakes': 'https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=1200&h=600&fit=crop',
        'pastries': 'https://images.unsplash.com/photo-1509365465985-25d11c17e812?w=1200&h=600&fit=crop',
        'breads': 'https://images.unsplash.com/photo-1509440159596-0249088772ff?w=1200&h=600&fit=crop',
        'cookies': 'https://images.unsplash.com/photo-1499636136210-6f4ee915583e?w=1200&h=600&fit=crop',
        'custom-cakes': 'https://images.unsplash.com/photo-1535254973040-6877109c9581?w=1200&h=600&fit=crop',
    }

    def handle(self, *args, **options):
        updated_count = 0

        for category_type, image_url in self.CATEGORY_IMAGES.items():
            try:
                category = Category.objects.get(category_type=category_type)

                # Download image
                self.stdout.write(f'Downloading image for {category.name}...')
                response = requests.get(image_url, timeout=30)
                response.raise_for_status()

                # Generate filename
                filename = f"{slugify(category.name)}.jpg"

                # Save to category's image field
                category.image.save(
                    filename,
                    File(BytesIO(response.content)),
                    save=True
                )

                updated_count += 1
                self.stdout.write(self.style.SUCCESS(f'✓ Added image for {category.name}'))

            except Category.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'Category not found: {category_type}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))

        self.stdout.write(self.style.SUCCESS(f'\nSuccessfully added {updated_count} category images!'))
