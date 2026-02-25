from django.core.management.base import BaseCommand
from shop.models import Category, Product, User
from decimal import Decimal


class Command(BaseCommand):
    help = 'Populate database with sample data (INR pricing)'

    def handle(self, *args, **options):
        # Create categories
        categories_data = [
            {'name': 'Cakes', 'slug': 'cakes', 'category_type': 'cakes', 'description': 'Delicious cakes for all occasions', 'display_order': 1},
            {'name': 'Pastries', 'slug': 'pastries', 'category_type': 'pastries', 'description': 'Freshly baked pastries', 'display_order': 2},
            {'name': 'Breads', 'slug': 'breads', 'category_type': 'breads', 'description': 'Artisan and regular breads', 'display_order': 3},
            {'name': 'Cookies', 'slug': 'cookies', 'category_type': 'cookies', 'description': 'Homemade cookies', 'display_order': 4},
            {'name': 'Custom Cakes', 'slug': 'custom-cakes', 'category_type': 'custom_cakes', 'description': 'Custom cakes for special events', 'display_order': 5},
        ]

        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults=cat_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created category: {category.name}'))

        # Create sample products with INR pricing
        products_data = [
            # Cakes (₹450-₹1,500 range)
            {'name': 'Chocolate Delight Cake', 'slug': 'chocolate-delight-cake', 'category': 'cakes', 'price': Decimal('899'), 'stock': 15, 'is_featured': True, 'description': 'Rich chocolate cake with chocolate ganache', 'short_description': 'Triple layer chocolate cake'},
            {'name': 'Vanilla Dream Cake', 'slug': 'vanilla-dream-cake', 'category': 'cakes', 'price': Decimal('749'), 'stock': 20, 'description': 'Classic vanilla sponge with buttercream frosting', 'short_description': 'Light and fluffy vanilla cake'},
            {'name': 'Red Velvet Cake', 'slug': 'red-velvet-cake', 'category': 'cakes', 'price': Decimal('999'), 'stock': 12, 'is_featured': True, 'description': 'Red velvet cake with cream cheese frosting', 'short_description': 'Popular red velvet classic'},
            {'name': 'Carrot Cake', 'slug': 'carrot-cake', 'category': 'cakes', 'price': Decimal('849'), 'stock': 10, 'description': 'Moist carrot cake with walnuts and cream cheese frosting', 'short_description': 'Homestyle carrot cake'},
            {'name': 'Lemon Drizzle Cake', 'slug': 'lemon-drizzle-cake', 'category': 'cakes', 'price': Decimal('699'), 'stock': 18, 'description': 'Zesty lemon cake with lemon glaze', 'short_description': 'Refreshing lemon cake'},
            {'name': 'Black Forest Cake', 'slug': 'black-forest-cake', 'category': 'cakes', 'price': Decimal('949'), 'stock': 14, 'is_featured': True, 'description': 'Classic black forest with cherry and cream', 'short_description': 'Traditional German recipe'},
            {'name': 'Butterscotch Cake', 'slug': 'butterscotch-cake', 'category': 'cakes', 'price': Decimal('799'), 'stock': 16, 'description': 'Rich butterscotch cake with caramel', 'short_description': 'Sweet butterscotch delight'},
            {'name': 'Pineapple Cake', 'slug': 'pineapple-cake', 'category': 'cakes', 'price': Decimal('699'), 'stock': 20, 'description': 'Fresh pineapple cream cake', 'short_description': 'Tropical pineapple treat'},

            # Pastries (₹50-₹200 range)
            {'name': 'Croissant', 'slug': 'croissant', 'category': 'pastries', 'price': Decimal('89'), 'stock': 50, 'description': 'Buttery French croissant', 'short_description': 'Classic butter croissant'},
            {'name': 'Pain au Chocolat', 'slug': 'pain-au-chocolat', 'category': 'pastries', 'price': Decimal('99'), 'stock': 40, 'description': 'Chocolate-filled croissant', 'short_description': 'Chocolate croissant'},
            {'name': 'Danish Pastry', 'slug': 'danish-pastry', 'category': 'pastries', 'price': Decimal('119'), 'stock': 30, 'description': 'Fruit Danish pastry', 'short_description': 'Fruit-filled Danish'},
            {'name': 'Cinnamon Roll', 'slug': 'cinnamon-roll', 'category': 'pastries', 'price': Decimal('109'), 'stock': 45, 'is_featured': True, 'description': 'Soft cinnamon roll with cream cheese glaze', 'short_description': 'Classic cinnamon roll'},
            {'name': 'Eclair', 'slug': 'eclair', 'category': 'pastries', 'price': Decimal('99'), 'stock': 25, 'description': 'Chocolate eclair with vanilla cream', 'short_description': 'Classic French eclair'},
            {'name': 'Puff Pastry', 'slug': 'puff-pastry', 'category': 'pastries', 'price': Decimal('79'), 'stock': 35, 'description': 'Crispy puff pastry', 'short_description': 'Flaky pastry treat'},
            {'name': 'Cream Roll', 'slug': 'cream-roll', 'category': 'pastries', 'price': Decimal('69'), 'stock': 40, 'description': 'Cream-filled pastry roll', 'short_description': 'Sweet cream roll'},

            # Breads (₹40-₹150 range)
            {'name': 'Sourdough Bread', 'slug': 'sourdough-bread', 'category': 'breads', 'price': Decimal('129'), 'stock': 20, 'is_featured': True, 'description': 'Artisan sourdough bread', 'short_description': 'Traditional sourdough'},
            {'name': 'French Baguette', 'slug': 'french-baguette', 'category': 'breads', 'price': Decimal('79'), 'stock': 40, 'description': 'Classic French baguette', 'short_description': 'Fresh baguette'},
            {'name': 'Whole Wheat Bread', 'slug': 'whole-wheat-bread', 'category': 'breads', 'price': Decimal('89'), 'stock': 30, 'description': 'Healthy whole wheat bread', 'short_description': 'Nutritious whole wheat'},
            {'name': 'Ciabatta', 'slug': 'ciabatta', 'category': 'breads', 'price': Decimal('99'), 'stock': 25, 'description': 'Italian ciabatta bread', 'short_description': 'Classic Italian bread'},
            {'name': 'Multigrain Bread', 'slug': 'multigrain-bread', 'category': 'breads', 'price': Decimal('119'), 'stock': 20, 'description': 'Healthy multigrain bread with seeds', 'short_description': 'Nutritious multigrain'},
            {'name': 'Milk Bread', 'slug': 'milk-bread', 'category': 'breads', 'price': Decimal('59'), 'stock': 50, 'description': 'Soft white milk bread', 'short_description': 'Everyday bread'},
            {'name': 'Brown Bread', 'slug': 'brown-bread', 'category': 'breads', 'price': Decimal('69'), 'stock': 45, 'description': 'Healthy brown bread', 'short_description': 'Fiber-rich bread'},

            # Cookies (₹30-₹150 per dozen range)
            {'name': 'Chocolate Chip Cookies', 'slug': 'chocolate-chip-cookies', 'category': 'cookies', 'price': Decimal('149'), 'stock': 60, 'is_featured': True, 'description': 'Classic chocolate chip cookies', 'short_description': 'Fresh baked cookies'},
            {'name': 'Oatmeal Raisin Cookies', 'slug': 'oatmeal-raisin-cookies', 'category': 'cookies', 'price': Decimal('129'), 'stock': 50, 'description': 'Healthy oatmeal raisin cookies', 'short_description': 'Chewy oatmeal cookies'},
            {'name': 'Peanut Butter Cookies', 'slug': 'peanut-butter-cookies', 'category': 'cookies', 'price': Decimal('139'), 'stock': 45, 'description': 'Rich peanut butter cookies', 'short_description': 'Classic peanut butter'},
            {'name': 'Cashew Cookies', 'slug': 'cashew-cookies', 'category': 'cookies', 'price': Decimal('169'), 'stock': 35, 'description': 'Cashew nut cookies', 'short_description': 'Gourmet cashew cookies'},
            {'name': 'Almond Cookies', 'slug': 'almond-cookies', 'category': 'cookies', 'price': Decimal('159'), 'stock': 40, 'description': 'Crunchy almond cookies', 'short_description': 'Nutty almond treats'},
            {'name': 'Butter Cookies', 'slug': 'butter-cookies', 'category': 'cookies', 'price': Decimal('119'), 'stock': 70, 'description': 'Classic butter cookies', 'short_description': 'Simple buttery goodness'},
            {'name': 'Coconut Cookies', 'slug': 'coconut-cookies', 'category': 'cookies', 'price': Decimal('109'), 'stock': 55, 'description': 'Sweet coconut cookies', 'short_description': 'Tropical coconut flavor'},

            # Custom Cakes (₹2,500-₹15,000 range)
            {'name': 'Birthday Cake Package', 'slug': 'birthday-cake-package', 'category': 'custom-cakes', 'price': Decimal('2499'), 'stock': 10, 'requires_preorder': True, 'preparation_time': 120, 'description': 'Custom birthday cake with personalized message', 'short_description': 'Custom birthday celebration cake'},
            {'name': 'Wedding Cake (per kg)', 'slug': 'wedding-cake', 'category': 'custom-cakes', 'price': Decimal('4999'), 'stock': 5, 'requires_preorder': True, 'preparation_time': 240, 'description': 'Elegant wedding cake, customizable design', 'short_description': 'Beautiful wedding cake'},
            {'name': 'Anniversary Cake', 'slug': 'anniversary-cake', 'category': 'custom-cakes', 'price': Decimal('3499'), 'stock': 8, 'requires_preorder': True, 'preparation_time': 180, 'description': 'Romantic anniversary cake', 'short_description': 'Special anniversary cake'},
            {'name': 'Photo Cake', 'slug': 'photo-cake', 'category': 'custom-cakes', 'price': Decimal('2999'), 'stock': 10, 'requires_preorder': True, 'preparation_time': 180, 'description': 'Cake with edible photo print', 'short_description': 'Personalized photo cake'},
            {'name': 'Tiered Cake (2-tier)', 'slug': 'tiered-cake', 'category': 'custom-cakes', 'price': Decimal('5999'), 'stock': 5, 'requires_preorder': True, 'preparation_time': 240, 'description': 'Beautiful two-tier celebration cake', 'short_description': 'Grand tiered cake'},
        ]

        for prod_data in products_data:
            category_slug = prod_data.pop('category')
            category = Category.objects.get(slug=category_slug)
            prod_data['category'] = category

            product, created = Product.objects.get_or_create(
                slug=prod_data['slug'],
                defaults=prod_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created product: {product.name} - ₹{prod_data["price"]}'))

        self.stdout.write(self.style.SUCCESS('Database populated successfully with INR pricing!'))
