from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.db.models import Sum, Avg, Count
from .models import (
    User, Category, Product, Cart, CartItem,
    Order, OrderItem, Review, Newsletter, ContactMessage
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom User admin"""
    list_display = ['email', 'username', 'first_name', 'last_name', 'phone', 'is_staff', 'created_at']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'created_at']
    search_fields = ['email', 'username', 'first_name', 'last_name', 'phone']
    ordering = ['-created_at']

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('phone', 'address', 'city', 'state', 'postal_code', 'is_email_verified')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )

    readonly_fields = ['created_at', 'updated_at']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Category admin"""
    list_display = ['name', 'category_type', 'get_product_count', 'is_active', 'display_order', 'created_at']
    list_filter = ['category_type', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['is_active', 'display_order']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Product admin"""
    list_display = ['name', 'category', 'price', 'sale_price', 'stock', 'is_active', 'is_featured', 'views', 'created_at']
    list_filter = ['category', 'is_active', 'is_featured', 'created_at']
    search_fields = ['name', 'description', 'short_description']
    list_editable = ['price', 'sale_price', 'stock', 'is_active', 'is_featured']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at', 'get_current_price_display', 'get_average_rating', 'get_review_count']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'category', 'short_description', 'description')
        }),
        ('Pricing & Inventory', {
            'fields': ('price', 'sale_price', 'stock', 'is_active', 'is_featured')
        }),
        ('Images', {
            'fields': ('image', 'additional_images')
        }),
        ('Product Details', {
            'fields': ('weight', 'ingredients', 'allergens', 'nutritional_info')
        }),
        ('Pre-order Options', {
            'fields': ('requires_preorder', 'preparation_time'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('views', 'get_current_price_display', 'get_average_rating', 'get_review_count'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_current_price_display(self, obj):
        return obj.get_current_price()
    get_current_price_display.short_description = 'Current Price'


class CartItemInline(admin.TabularInline):
    """Cart item inline for Cart admin"""
    model = CartItem
    extra = 0
    readonly_fields = ['get_subtotal']

    def get_subtotal(self, obj):
        return obj.get_subtotal()
    get_subtotal.short_description = 'Subtotal'


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """Cart admin"""
    list_display = ['user', 'get_total_items', 'get_total_price', 'created_at', 'updated_at']
    search_fields = ['user__email', 'user__username']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [CartItemInline]


class OrderItemInline(admin.TabularInline):
    """Order item inline for Order admin"""
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'product_name', 'quantity', 'price', 'subtotal']
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Order admin with dashboard functionality"""
    list_display = ['order_number', 'customer_name', 'customer_email', 'status', 'payment_status', 'total', 'created_at']
    list_filter = ['status', 'payment_status', 'shipping_method', 'created_at']
    search_fields = ['order_number', 'customer_name', 'customer_email', 'customer_phone']
    readonly_fields = [
        'order_number', 'created_at', 'updated_at', 'confirmed_at',
        'shipped_at', 'delivered_at', 'get_order_summary'
    ]
    inlines = [OrderItemInline]

    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'user', 'status', 'payment_status', 'payment_id')
        }),
        ('Customer Details', {
            'fields': ('customer_name', 'customer_email', 'customer_phone')
        }),
        ('Shipping Information', {
            'fields': ('shipping_address', 'shipping_city', 'shipping_state',
                      'shipping_postal_code', 'shipping_method', 'shipping_cost')
        }),
        ('Order Totals', {
            'fields': ('subtotal', 'tax', 'discount', 'total')
        }),
        ('Additional Information', {
            'fields': ('notes', 'special_instructions', 'admin_notes'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'confirmed_at', 'shipped_at', 'delivered_at'),
            'classes': ('collapse',)
        }),
        ('Summary', {
            'fields': ('get_order_summary',),
            'classes': ('collapse',)
        }),
    )

    def get_order_summary(self, obj):
        """Display order summary"""
        items = obj.items.all()
        summary = "<table><tr><th>Product</th><th>Qty</th><th>Price</th><th>Subtotal</th></tr>"
        for item in items:
            summary += f"<tr><td>{item.product_name}</td><td>{item.quantity}</td><td>${item.price}</td><td>${item.subtotal}</td></tr>"
        summary += "</table>"
        return format_html(summary)
    get_order_summary.short_description = 'Order Summary'

    actions = ['mark_as_confirmed', 'mark_as_processing', 'mark_as_baking', 'mark_as_ready', 'mark_as_shipped', 'mark_as_delivered']

    def mark_as_confirmed(self, request, queryset):
        from django.utils import timezone
        for order in queryset:
            order.status = 'confirmed'
            order.confirmed_at = timezone.now()
            order.save()
        self.message_user(request, f'{queryset.count()} orders marked as confirmed.')
    mark_as_confirmed.short_description = 'Mark selected orders as confirmed'

    def mark_as_processing(self, request, queryset):
        for order in queryset:
            order.status = 'processing'
            order.save()
        self.message_user(request, f'{queryset.count()} orders marked as processing.')
    mark_as_processing.short_description = 'Mark selected orders as processing'

    def mark_as_baking(self, request, queryset):
        for order in queryset:
            order.status = 'baking'
            order.save()
        self.message_user(request, f'{queryset.count()} orders marked as baking.')
    mark_as_baking.short_description = 'Mark selected orders as baking'

    def mark_as_ready(self, request, queryset):
        for order in queryset:
            order.status = 'ready'
            order.save()
        self.message_user(request, f'{queryset.count()} orders marked as ready.')
    mark_as_ready.short_description = 'Mark selected orders as ready'

    def mark_as_shipped(self, request, queryset):
        from django.utils import timezone
        for order in queryset:
            order.status = 'shipped'
            order.shipped_at = timezone.now()
            order.save()
        self.message_user(request, f'{queryset.count()} orders marked as shipped.')
    mark_as_shipped.short_description = 'Mark selected orders as shipped'

    def mark_as_delivered(self, request, queryset):
        from django.utils import timezone
        for order in queryset:
            order.status = 'delivered'
            order.delivered_at = timezone.now()
            order.save()
        self.message_user(request, f'{queryset.count()} orders marked as delivered.')
    mark_as_delivered.short_description = 'Mark selected orders as delivered'

    # Dashboard functionality
    def has_dashboard_permission(self, request):
        return request.user.is_staff or request.user.is_superuser


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Review admin"""
    list_display = ['product', 'user', 'rating', 'title', 'is_active', 'created_at']
    list_filter = ['rating', 'is_active', 'created_at']
    search_fields = ['product__name', 'user__email', 'title', 'comment']
    list_editable = ['is_active']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    """Newsletter admin"""
    list_display = ['email', 'is_active', 'subscribed_at']
    list_filter = ['is_active', 'subscribed_at']
    search_fields = ['email']
    list_editable = ['is_active']


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    """Contact message admin"""
    list_display = ['name', 'email', 'phone', 'subject', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['name', 'email', 'subject', 'message']
    list_editable = ['is_read']
    readonly_fields = ['created_at', 'ip_address']

    actions = ['mark_as_read', 'mark_as_unread']

    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
        self.message_user(request, f'{queryset.count()} messages marked as read.')
    mark_as_read.short_description = 'Mark selected messages as read'

    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)
        self.message_user(request, f'{queryset.count()} messages marked as unread.')
    mark_as_unread.short_description = 'Mark selected messages as unread'


# Customize Admin Site
admin.site.site_header = 'Goodluck Bakery Administration'
admin.site.site_title = 'Goodluck Bakery Admin'
admin.site.index_title = 'Welcome to Goodluck Bakery Administration'

# Create a custom dashboard view
def get_dashboard_stats():
    """Get dashboard statistics"""
    from django.utils import timezone
    from datetime import timedelta

    today = timezone.now()
    last_30_days = today - timedelta(days=30)

    stats = {
        'total_orders': Order.objects.count(),
        'orders_last_30_days': Order.objects.filter(created_at__gte=last_30_days).count(),
        'total_revenue': Order.objects.filter(payment_status='paid').aggregate(total=Sum('total'))['total'] or 0,
        'revenue_last_30_days': Order.objects.filter(
            payment_status='paid',
            created_at__gte=last_30_days
        ).aggregate(total=Sum('total'))['total'] or 0,
        'total_products': Product.objects.count(),
        'active_products': Product.objects.filter(is_active=True).count(),
        'total_users': User.objects.count(),
        'pending_orders': Order.objects.filter(status='pending').count(),
        'average_order_value': Order.objects.filter(payment_status='paid').aggregate(
            avg=Avg('total')
        )['avg'] or 0,
    }
    return stats
