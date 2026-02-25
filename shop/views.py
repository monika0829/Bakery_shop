from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Q, F, Sum, Avg, Count, Prefetch
from django.utils import timezone
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import stripe
import json
import os

from .models import (
    Product, Category, Cart, CartItem, Order, OrderItem,
    Review, Newsletter, ContactMessage
)
from .forms import (
    CustomUserCreationForm, UserProfileForm, ReviewForm,
    ContactForm, CheckoutForm, AddToCartForm, NewsletterForm
)
from goodluck_bakery.settings import STRIPE_SECRET_KEY, SITE_URL


# Stripe Configuration
stripe.api_key = STRIPE_SECRET_KEY


# ============================================
# HOME & GENERAL VIEWS
# ============================================

def home(request):
    """Home page view"""
    featured_products = Product.objects.filter(
        is_active=True,
        is_featured=True
    ).select_related('category')[:8]

    new_products = Product.objects.filter(
        is_active=True
    ).select_related('category').order_by('-created_at')[:8]

    categories = Category.objects.filter(is_active=True)

    # Check if on sale
    for product in featured_products:
        product.current_price = product.get_current_price()
        product.is_on_sale = product.is_on_sale()

    for product in new_products:
        product.current_price = product.get_current_price()
        product.is_on_sale = product.is_on_sale()

    context = {
        'featured_products': featured_products,
        'new_products': new_products,
        'categories': categories,
    }
    return render(request, 'shop/home.html', context)


def about(request):
    """About page view"""
    return render(request, 'shop/about.html')


def contact(request):
    """Contact page view"""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact_message = form.save(commit=False)
            contact_message.ip_address = request.META.get('REMOTE_ADDR')
            contact_message.save()
            messages.success(request, 'Thank you for your message! We will get back to you soon.')
            return redirect('contact')
    else:
        form = ContactForm()

    return render(request, 'shop/contact.html', {'form': form})


# ============================================
# PRODUCT CATALOG VIEWS
# ============================================

def shop(request):
    """Shop page with all products"""
    products = Product.objects.filter(is_active=True).select_related('category')
    categories = Category.objects.filter(is_active=True)

    # Get filter parameters
    category_slug = request.GET.get('category')
    sort_by = request.GET.get('sort', 'name')
    search_query = request.GET.get('q', '')

    # Filter by category
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug, is_active=True)
        products = products.filter(category=category)

    # Search functionality
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(short_description__icontains=search_query)
        )

    # Sort products
    sort_options = {
        'name': 'name',
        'price_low': 'price',
        'price_high': '-price',
        'newest': '-created_at',
        'rating': '-reviews__rating',
    }
    products = products.order_by(sort_options.get(sort_by, 'name'))

    # Add price and rating to each product
    for product in products:
        product.current_price = product.get_current_price()
        product.is_on_sale = product.is_on_sale()

    context = {
        'products': products,
        'categories': categories,
        'selected_category': category_slug,
        'sort_by': sort_by,
        'search_query': search_query,
    }
    return render(request, 'shop/shop.html', context)


def product_detail(request, slug):
    """Product detail page"""
    product = get_object_or_404(
        Product.objects.select_related('category').prefetch_related('reviews__user'),
        slug=slug,
        is_active=True
    )

    # Increment view count
    Product.objects.filter(pk=product.pk).update(views=F('views') + 1)

    # Get related products from same category
    related_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(pk=product.pk)[:4]

    # Get reviews
    reviews = product.reviews.filter(is_active=True).select_related('user')

    # Check if user has reviewed
    user_reviewed = False
    if request.user.is_authenticated:
        user_reviewed = Review.objects.filter(
            product=product,
            user=request.user
        ).exists()

    # Add to cart form
    cart_form = AddToCartForm()

    context = {
        'product': product,
        'current_price': product.get_current_price(),
        'is_on_sale': product.is_on_sale(),
        'discount_percent': product.get_discount_percentage(),
        'average_rating': product.get_average_rating(),
        'review_count': product.get_review_count(),
        'related_products': related_products,
        'reviews': reviews,
        'user_reviewed': user_reviewed,
        'cart_form': cart_form,
    }
    return render(request, 'shop/product_detail.html', context)


def category_products(request, slug):
    """Products by category"""
    category = get_object_or_404(Category, slug=slug, is_active=True)
    products = Product.objects.filter(
        category=category,
        is_active=True
    ).select_related('category')

    for product in products:
        product.current_price = product.get_current_price()
        product.is_on_sale = product.is_on_sale()

    context = {
        'category': category,
        'products': products,
    }
    return render(request, 'shop/category_products.html', context)


# ============================================
# CART VIEWS
# ============================================

def get_or_create_cart(user):
    """Get or create cart for user"""
    cart, created = Cart.objects.get_or_create(user=user)
    return cart


@login_required
def cart(request):
    """Shopping cart page"""
    cart = get_or_create_cart(request.user)
    cart_items = cart.items.select_related('product').all()

    # Calculate subtotal for each item
    total_items = cart.get_total_items()
    subtotal = cart.get_total_price()

    context = {
        'cart_items': cart_items,
        'total_items': total_items,
        'subtotal': subtotal,
    }
    return render(request, 'shop/cart.html', context)


@login_required
@require_POST
def add_to_cart(request):
    """Add product to cart"""
    product_id = request.POST.get('product_id')
    quantity = int(request.POST.get('quantity', 1))

    if not product_id:
        return HttpResponseBadRequest('Product ID is required')

    product = get_object_or_404(Product, id=product_id, is_active=True)

    if quantity > product.stock:
        messages.error(request, f'Sorry, only {product.stock} items available in stock.')
        return redirect('product_detail', slug=product.slug)

    cart = get_or_create_cart(request.user)
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': quantity}
    )

    if not created:
        new_quantity = cart_item.quantity + quantity
        if new_quantity > product.stock:
            messages.error(request, f'Sorry, only {product.stock} items available in stock.')
            return redirect('product_detail', slug=product.slug)
        cart_item.quantity = new_quantity
        cart_item.save()

    messages.success(request, f'{product.name} added to cart!')
    return redirect('cart')


@login_required
@require_POST
def update_cart(request):
    """Update cart item quantity"""
    item_id = request.POST.get('item_id')
    action = request.POST.get('action')

    if not item_id:
        return HttpResponseBadRequest('Item ID is required')

    cart_item = get_object_or_404(
        CartItem.objects.select_related('product', 'cart'),
        id=item_id,
        cart__user=request.user
    )

    if action == 'increase':
        if cart_item.quantity < cart_item.product.stock:
            cart_item.quantity += 1
            messages.success(request, 'Cart updated!')
        else:
            messages.warning(request, 'Maximum stock reached!')
    elif action == 'decrease':
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            messages.success(request, 'Cart updated!')
        else:
            messages.warning(request, 'Minimum quantity is 1!')
    elif action == 'remove':
        cart_item.delete()
        messages.success(request, 'Item removed from cart!')
        return redirect('cart')

    cart_item.save()
    return redirect('cart')


@login_required
def remove_from_cart(request, item_id):
    """Remove item from cart"""
    cart_item = get_object_or_404(
        CartItem,
        id=item_id,
        cart__user=request.user
    )
    cart_item.delete()
    messages.success(request, 'Item removed from cart!')
    return redirect('cart')


# ============================================
# CHECKOUT & ORDER VIEWS
# ============================================

@login_required
def checkout(request):
    """Checkout page"""
    cart = get_or_create_cart(request.user)
    cart_items = cart.items.select_related('product').all()

    if not cart_items:
        messages.warning(request, 'Your cart is empty!')
        return redirect('shop')

    subtotal = cart.get_total_price()

    if request.method == 'POST':
        form = CheckoutForm(request.POST, user=request.user)
        if form.is_valid():
            # Calculate shipping cost (INR)
            shipping_method = form.cleaned_data['shipping_method']
            shipping_costs = {
                'standard': 49,
                'express': 99,
                'pickup': 0,
            }
            shipping_cost = shipping_costs.get(shipping_method, 49)
            tax = subtotal * 0.05  # 5% GST for food items
            total = subtotal + shipping_cost + tax

            # Create order
            order = Order.objects.create(
                user=request.user,
                customer_name=form.cleaned_data['shipping_name'],
                customer_email=form.cleaned_data['shipping_email'],
                customer_phone=form.cleaned_data['shipping_phone'],
                shipping_address=form.cleaned_data['shipping_address'],
                shipping_city=form.cleaned_data['shipping_city'],
                shipping_state=form.cleaned_data['shipping_state'],
                shipping_postal_code=form.cleaned_data['shipping_postal_code'],
                shipping_method=shipping_method,
                shipping_cost=shipping_cost,
                subtotal=subtotal,
                tax=round(tax, 2),
                total=round(total, 2),
                notes=form.cleaned_data['order_notes'],
            )

            # Create order items
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    product_name=item.product.name,
                    product_slug=item.product.slug,
                    quantity=item.quantity,
                    price=item.product.get_current_price()
                )

            # Save address to user profile if requested
            if form.cleaned_data.get('save_address'):
                request.user.address = form.cleaned_data['shipping_address']
                request.user.city = form.cleaned_data['shipping_city']
                request.user.state = form.cleaned_data['shipping_state']
                request.user.postal_code = form.cleaned_data['shipping_postal_code']
                request.user.save()

            # Create Stripe payment intent
            try:
                intent = stripe.PaymentIntent.create(
                    amount=int(total * 100),  # Amount in cents
                    currency='usd',
                    metadata={
                        'order_id': order.id,
                        'order_number': order.order_number,
                    },
                    description=f'Goodluck Bakery Order {order.order_number}'
                )

                context = {
                    'order': order,
                    'stripe_public_key': request.build_absolute_uri('/')[:-1],
                    'client_secret': intent.client_secret,
                    'subtotal': subtotal,
                    'shipping_cost': shipping_cost,
                    'tax': round(tax, 2),
                    'total': round(total, 2),
                }
                return render(request, 'shop/payment.html', context)

            except stripe.error.StripeError as e:
                messages.error(request, f'Payment error: {str(e)}')
                order.delete()
                return redirect('checkout')
    else:
        form = CheckoutForm(user=request.user)

    context = {
        'form': form,
        'cart_items': cart_items,
        'subtotal': subtotal,
        'stripe_public_key': os.getenv('STRIPE_PUBLIC_KEY', ''),
    }
    return render(request, 'shop/checkout.html', context)


@login_required
@require_POST
@csrf_exempt
def stripe_webhook(request):
    """Stripe webhook handler"""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET', '')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError:
        return HttpResponseBadRequest('Invalid payload')
    except stripe.error.SignatureVerificationError:
        return HttpResponseBadRequest('Invalid signature')

    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        order_id = payment_intent['metadata'].get('order_id')

        if order_id:
            order = Order.objects.get(id=order_id)
            order.payment_status = 'paid'
            order.payment_id = payment_intent['id']
            order.status = 'confirmed'
            order.confirmed_at = timezone.now()
            order.save()

            # Update product stock
            for item in order.items.all():
                if item.product:
                    Product.objects.filter(id=item.product.id).update(
                        stock=F('stock') - item.quantity
                    )

            # Clear cart
            cart = Cart.objects.get(user=order.user)
            cart.clear_cart()

    return JsonResponse({'status': 'success'})


@login_required
def payment_success(request):
    """Payment success page"""
    return render(request, 'shop/payment_success.html')


@login_required
def payment_cancel(request):
    """Payment cancelled page"""
    messages.warning(request, 'Payment was cancelled.')
    return redirect('cart')


@login_required
def order_confirmation(request, order_number):
    """Order confirmation page"""
    order = get_object_or_404(
        Order.objects.prefetch_related('items__product'),
        order_number=order_number,
        user=request.user
    )
    return render(request, 'shop/order_confirmation.html', {'order': order})


@login_required
def user_orders(request):
    """User orders list"""
    orders = Order.objects.filter(
        user=request.user
    ).prefetch_related('items').order_by('-created_at')
    return render(request, 'shop/user_orders.html', {'orders': orders})


@login_required
def order_detail(request, order_number):
    """Order detail page"""
    order = get_object_or_404(
        Order.objects.prefetch_related('items__product'),
        order_number=order_number,
        user=request.user
    )
    return render(request, 'shop/order_detail.html', {'order': order})


# ============================================
# USER AUTHENTICATION VIEWS
# ============================================

def register(request):
    """User registration view"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, 'Account created successfully! Welcome to Goodluck Bakery!')
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'shop/register.html', {'form': form})


def login_view(request):
    """Login view"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if not remember_me:
                request.session.set_expiry(0)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'shop/login.html')


def logout_view(request):
    """Logout view"""
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('home')


class CustomPasswordResetView(PasswordResetView):
    """Custom password reset view"""
    template_name = 'shop/password_reset.html'
    email_template_name = 'shop/emails/password_reset_email.html'
    success_url = reverse_lazy('password_reset_done')


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    """Custom password reset confirm view"""
    template_name = 'shop/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')


@login_required
def profile(request):
    """User profile view"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)

    orders = Order.objects.filter(user=request.user).order_by('-created_at')[:5]

    context = {
        'form': form,
        'recent_orders': orders,
    }
    return render(request, 'shop/profile.html', context)


# ============================================
# REVIEW VIEWS
# ============================================

@login_required
@require_POST
def add_review(request, product_id):
    """Add product review"""
    product = get_object_or_404(Product, id=product_id, is_active=True)

    # Check if user already reviewed
    if Review.objects.filter(product=product, user=request.user).exists():
        messages.warning(request, 'You have already reviewed this product.')
        return redirect('product_detail', slug=product.slug)

    form = ReviewForm(request.POST)
    if form.is_valid():
        review = form.save(commit=False)
        review.product = product
        review.user = request.user
        review.save()
        messages.success(request, 'Thank you for your review!')
    else:
        messages.error(request, 'Please correct the errors in your review.')

    return redirect('product_detail', slug=product.slug)


# ============================================
# NEWSLETTER VIEW
# ============================================

@require_POST
def newsletter_subscribe(request):
    """Newsletter subscription"""
    form = NewsletterForm(request.POST)
    if form.is_valid():
        email = form.cleaned_data['email']
        obj, created = Newsletter.objects.get_or_create(
            email=email,
            defaults={'is_active': True}
        )
        if created:
            messages.success(request, 'Thank you for subscribing to our newsletter!')
        else:
            messages.info(request, 'You are already subscribed to our newsletter.')
    else:
        messages.error(request, 'Please enter a valid email address.')

    return redirect('home')
