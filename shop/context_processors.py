from django.conf import settings
from .models import Cart, Category


def cart_context(request):
    """Add cart information to all templates"""
    cart_items_count = 0
    cart_total = 0

    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            cart_items_count = cart.get_total_items()
            cart_total = cart.get_total_price()
        except Cart.DoesNotExist:
            pass

    return {
        'cart_items_count': cart_items_count,
        'cart_total': cart_total,
    }


def categories_context(request):
    """Add categories to all templates"""
    categories = Category.objects.filter(is_active=True)
    return {
        'categories': categories,
        'site_url': getattr(settings, 'SITE_URL', 'http://localhost:8000'),
    }
