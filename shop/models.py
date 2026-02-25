from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import os


def get_product_image_path(instance, filename):
    """Generate path for product images"""
    return os.path.join('products', f'product_{instance.id}', filename)


class User(AbstractUser):
    """Extended User model with additional fields"""
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='Phone Number')
    address = models.TextField(blank=True, null=True, verbose_name='Address')
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name='City')
    state = models.CharField(max_length=100, blank=True, null=True, verbose_name='State')
    postal_code = models.CharField(max_length=20, blank=True, null=True, verbose_name='Postal Code')
    is_email_verified = models.BooleanField(default=False, verbose_name='Email Verified')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']

    def __str__(self):
        return self.email or self.username

    def get_full_address(self):
        """Return full address string"""
        parts = [self.address, self.city, self.state, self.postal_code]
        return ', '.join(filter(None, parts))


class Category(models.Model):
    """Product category model"""
    CATEGORY_CHOICES = [
        ('cakes', 'Cakes'),
        ('pastries', 'Pastries'),
        ('breads', 'Breads'),
        ('cookies', 'Cookies'),
        ('custom_cakes', 'Custom Cakes'),
    ]

    name = models.CharField(max_length=100, unique=True, verbose_name='Category Name')
    slug = models.SlugField(max_length=100, unique=True, verbose_name='Slug')
    description = models.TextField(blank=True, null=True, verbose_name='Description')
    image = models.ImageField(upload_to='categories/', blank=True, null=True, verbose_name='Category Image')
    category_type = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        unique=True,
        verbose_name='Category Type'
    )
    is_active = models.BooleanField(default=True, verbose_name='Is Active')
    display_order = models.IntegerField(default=0, verbose_name='Display Order')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name

    def get_product_count(self):
        """Return count of active products in this category"""
        return self.products.filter(is_active=True).count()


class Product(models.Model):
    """Product model"""
    name = models.CharField(max_length=200, verbose_name='Product Name')
    slug = models.SlugField(max_length=200, unique=True, verbose_name='Slug')
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name='Category'
    )
    description = models.TextField(verbose_name='Description')
    short_description = models.CharField(max_length=500, blank=True, verbose_name='Short Description')
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Price'
    )
    sale_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
        verbose_name='Sale Price',
        help_text='Leave blank if not on sale'
    )
    image = models.ImageField(upload_to=get_product_image_path, verbose_name='Product Image')
    additional_images = models.JSONField(
        blank=True,
        null=True,
        verbose_name='Additional Images',
        help_text='List of additional image URLs'
    )
    stock = models.IntegerField(default=0, validators=[MinValueValidator(0)], verbose_name='Stock Quantity')
    is_active = models.BooleanField(default=True, verbose_name='Is Active')
    is_featured = models.BooleanField(default=False, verbose_name='Is Featured')
    weight = models.CharField(max_length=50, blank=True, verbose_name='Weight', help_text='e.g., 500g, 1kg')
    ingredients = models.TextField(blank=True, verbose_name='Ingredients')
    allergens = models.TextField(blank=True, verbose_name='Allergens')
    nutritional_info = models.JSONField(
        blank=True,
        null=True,
        verbose_name='Nutritional Information',
        help_text='JSON format nutritional data'
    )
    preparation_time = models.IntegerField(
        blank=True,
        null=True,
        verbose_name='Preparation Time (minutes)',
        help_text='For custom cakes or made-to-order items'
    )
    requires_preorder = models.BooleanField(
        default=False,
        verbose_name='Requires Pre-order',
        help_text='Check if this item needs to be ordered in advance'
    )
    views = models.IntegerField(default=0, verbose_name='View Count')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['-is_featured', '-created_at']

    def __str__(self):
        return self.name

    def get_current_price(self):
        """Return current price (sale price if available, otherwise regular price)"""
        return self.sale_price if self.sale_price and self.sale_price < self.price else self.price

    def is_on_sale(self):
        """Check if product is on sale"""
        return self.sale_price is not None and self.sale_price < self.price

    def get_discount_percentage(self):
        """Calculate discount percentage"""
        if self.is_on_sale():
            return int(((self.price - self.sale_price) / self.price) * 100)
        return 0

    def get_average_rating(self):
        """Return average rating"""
        reviews = self.reviews.filter(is_active=True)
        if reviews:
            return round(sum(review.rating for review in reviews) / reviews.count(), 1)
        return 0

    def get_review_count(self):
        """Return count of active reviews"""
        return self.reviews.filter(is_active=True).count()

    def is_in_stock(self):
        """Check if product is in stock"""
        return self.stock > 0


class Cart(models.Model):
    """Shopping cart model"""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='cart',
        verbose_name='User'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')

    class Meta:
        verbose_name = 'Cart'
        verbose_name_plural = 'Carts'

    def __str__(self):
        return f"Cart of {self.user.email}"

    def get_total_items(self):
        """Return total number of items in cart"""
        return sum(item.quantity for item in self.items.all())

    def get_total_price(self):
        """Return total price of all items in cart"""
        total = 0
        for item in self.items.all():
            price = item.product.get_current_price()
            total += price * item.quantity
        return total

    def clear_cart(self):
        """Remove all items from cart"""
        self.items.all().delete()


class CartItem(models.Model):
    """Cart item model"""
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Cart'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='cart_items',
        verbose_name='Product'
    )
    quantity = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(99)],
        verbose_name='Quantity'
    )
    added_at = models.DateTimeField(auto_now_add=True, verbose_name='Added At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')

    class Meta:
        verbose_name = 'Cart Item'
        verbose_name_plural = 'Cart Items'
        unique_together = ['cart', 'product']
        ordering = ['-added_at']

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    def get_subtotal(self):
        """Return subtotal for this item"""
        return self.product.get_current_price() * self.quantity


class Order(models.Model):
    """Order status choices"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('baking', 'Baking'),
        ('ready', 'Ready for Pickup/Delivery'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    # Order fields
    order_number = models.CharField(max_length=50, unique=True, verbose_name='Order Number')
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='orders',
        verbose_name='User'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Order Status'
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending',
        verbose_name='Payment Status'
    )
    payment_id = models.CharField(max_length=255, blank=True, null=True, verbose_name='Payment ID')
    payment_method = models.CharField(max_length=50, default='stripe', verbose_name='Payment Method')

    # Customer details
    customer_name = models.CharField(max_length=200, verbose_name='Customer Name')
    customer_email = models.EmailField(verbose_name='Customer Email')
    customer_phone = models.CharField(max_length=20, verbose_name='Customer Phone')

    # Shipping/Delivery details
    shipping_address = models.TextField(verbose_name='Shipping Address')
    shipping_city = models.CharField(max_length=100, verbose_name='City')
    shipping_state = models.CharField(max_length=100, verbose_name='State')
    shipping_postal_code = models.CharField(max_length=20, verbose_name='Postal Code')
    shipping_method = models.CharField(max_length=50, default='standard', verbose_name='Shipping Method')
    shipping_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='Shipping Cost'
    )

    # Order details
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Subtotal')
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Tax')
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Discount')
    total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Total')

    # Additional fields
    notes = models.TextField(blank=True, verbose_name='Order Notes')
    admin_notes = models.TextField(blank=True, verbose_name='Admin Notes')
    special_instructions = models.TextField(blank=True, verbose_name='Special Instructions')

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    confirmed_at = models.DateTimeField(blank=True, null=True, verbose_name='Confirmed At')
    shipped_at = models.DateTimeField(blank=True, null=True, verbose_name='Shipped At')
    delivered_at = models.DateTimeField(blank=True, null=True, verbose_name='Delivered At')

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-created_at']

    def __str__(self):
        return f"Order {self.order_number}"

    def save(self, *args, **kwargs):
        """Generate order number if not exists"""
        if not self.order_number:
            from django.utils import timezone
            timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
            import random
            self.order_number = f"GLB-{timestamp}-{random.randint(1000, 9999)}"
        super().save(*args, **kwargs)

    def get_item_count(self):
        """Return total number of items"""
        return sum(item.quantity for item in self.items.all())


class OrderItem(models.Model):
    """Order item model"""
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Order'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        related_name='order_items',
        verbose_name='Product'
    )
    product_name = models.CharField(max_length=200, verbose_name='Product Name')
    product_slug = models.CharField(max_length=200, verbose_name='Product Slug')
    quantity = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Quantity'
    )
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Unit Price')
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Subtotal')
    special_requests = models.TextField(blank=True, verbose_name='Special Requests')

    class Meta:
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'

    def __str__(self):
        return f"{self.quantity} x {self.product_name}"

    def save(self, *args, **kwargs):
        """Calculate subtotal"""
        self.subtotal = self.price * self.quantity
        super().save(*args, **kwargs)


class Review(models.Model):
    """Product review model"""
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Product'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='User'
    )
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Rating'
    )
    title = models.CharField(max_length=200, verbose_name='Review Title')
    comment = models.TextField(verbose_name='Review Comment')
    is_active = models.BooleanField(default=True, verbose_name='Is Active')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')

    class Meta:
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        unique_together = ['product', 'user']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.product.name} ({self.rating}/5)"


class Newsletter(models.Model):
    """Newsletter subscription model"""
    email = models.EmailField(unique=True, verbose_name='Email')
    is_active = models.BooleanField(default=True, verbose_name='Is Active')
    subscribed_at = models.DateTimeField(auto_now_add=True, verbose_name='Subscribed At')

    class Meta:
        verbose_name = 'Newsletter Subscription'
        verbose_name_plural = 'Newsletter Subscriptions'
        ordering = ['-subscribed_at']

    def __str__(self):
        return self.email


class ContactMessage(models.Model):
    """Contact form message model"""
    name = models.CharField(max_length=200, verbose_name='Name')
    email = models.EmailField(verbose_name='Email')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Phone')
    subject = models.CharField(max_length=200, verbose_name='Subject')
    message = models.TextField(verbose_name='Message')
    is_read = models.BooleanField(default=False, verbose_name='Is Read')
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name='IP Address')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')

    class Meta:
        verbose_name = 'Contact Message'
        verbose_name_plural = 'Contact Messages'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.subject}"
