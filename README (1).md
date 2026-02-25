# Goodluck Bakery - Django E-Commerce Platform

A complete e-commerce platform for Goodluck Bakery, built with Django 5, featuring a responsive Bootstrap 5 frontend, Stripe payment integration, and comprehensive admin dashboard.

## Features Implemented

### Core Features
- ✅ User Authentication System (Registration, Login, Password Reset)
- ✅ Product Catalog with 5 Categories (Cakes, Pastries, Breads, Cookies, Custom Cakes)
- ✅ Shopping Cart System (Add, Remove, Update Quantity)
- ✅ Order Processing with Status Tracking
- ✅ Admin Dashboard for Product and Order Management
- ✅ Responsive Frontend using Bootstrap 5

### Pages & Templates
- ✅ Home Page with Featured & New Products
- ✅ Shop Page with Filtering & Sorting
- ✅ Product Detail Pages with Reviews
- ✅ Category Product Pages
- ✅ Shopping Cart Page
- ✅ Checkout with Payment Form
- ✅ User Registration/Login Pages
- ✅ User Profile Page
- ✅ Order History & Detail Pages
- ✅ About Us Page
- ✅ Contact Page with Form

### Database Models
- ✅ User (Extended with address fields)
- ✅ Category (With types: cakes, pastries, breads, cookies, custom_cakes)
- ✅ Product (With pricing, inventory, reviews, nutritional info)
- ✅ Cart & CartItem (Shopping cart functionality)
- ✅ Order & OrderItem (Order processing with workflow)
- ✅ Review (Product ratings and comments)
- ✅ Newsletter (Email subscriptions)
- ✅ ContactMessage (Contact form submissions)

### Admin Features
- ✅ User Management
- ✅ Category Management
- ✅ Product Management (including inventory, pricing, featured status)
- ✅ Order Management with bulk status updates
- ✅ Review Moderation
- ✅ Newsletter Management
- ✅ Contact Message Management

## Installation & Setup

### Prerequisites
- Python 3.11+
- Virtual Environment (venv)
- MySQL or SQLite database

### Quick Start

1. **Activate Virtual Environment**
   ```bash
   source venv/bin/activate
   ```

2. **Run Migrations**
   ```bash
   python manage.py migrate
   ```

3. **Create Superuser**
   ```bash
   python manage.py createsuperuser
   ```
   Default superuser created: `admin` / `admin123`

4. **Populate Sample Data** (Optional)
   ```bash
   python manage.py populate_db
   ```

5. **Run Development Server**
   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```

6. **Access the Application**
   - Main Site: http://localhost:8000/
   - Admin Panel: http://localhost:8000/admin/

### Production Deployment with Gunicorn

1. **Collect Static Files**
   ```bash
   python manage.py collectstatic --noinput
   ```

2. **Start with Gunicorn**
   ```bash
   gunicorn goodluck_bakery.wsgi:application --bind 0.0.0.0:8000 --workers 3
   ```

## Environment Variables

The `.env` file contains:
```env
DEBUG=True
SECRET_KEY=xWIj4xDgIg1hfFqV
ALLOWED_HOSTS=localhost,127.0.0.1,ds613u232p80.drytis.ai,*
SITE_URL=https://ds613u232p80.drytis.ai
STRIPE_PUBLIC_KEY=
STRIPE_SECRET_KEY=
```

## Application URLs

### Public Pages
- `/` - Home
- `/about/` - About Us
- `/contact/` - Contact
- `/shop/` - Shop/Products
- `/product/<slug>/` - Product Detail
- `/category/<slug>/` - Category Products

### Authentication
- `/register/` - User Registration
- `/login/` - User Login
- `/logout/` - User Logout
- `/profile/` - User Profile

### Cart & Checkout
- `/cart/` - Shopping Cart
- `/checkout/` - Checkout
- `/orders/` - My Orders

### Admin
- `/admin/` - Django Admin Panel

## Default Login Credentials

**Admin User:**
- Username: `admin`
- Email: `admin@goodluckbakery.com`
- Password: `admin123`

## Database Schema

### Models Created:
1. **User** - Extended Django User with address fields
2. **Category** - Product categories with types
3. **Product** - Products with pricing, inventory, images
4. **Cart** - User shopping cart
5. **CartItem** - Items in cart
6. **Order** - Customer orders with status workflow
7. **OrderItem** - Items in orders
8. **Review** - Product reviews
9. **Newsletter** - Email subscriptions
10. **ContactMessage** - Contact form messages

## Sample Data

The `populate_db` management command creates:
- 5 Categories (Cakes, Pastries, Breads, Cookies, Custom Cakes)
- 28 Sample Products across all categories
- Pricing, inventory, and product descriptions

## Security Features

- ✅ CSRF Protection
- ✅ SQL Injection Prevention (prepared statements)
- ✅ XSS Protection (Django templates auto-escape)
- ✅ Password Validation
- ✅ Secure Password Hashing
- ✅ Session Management
- ✅ Login Required for Cart/Checkout
- ✅ Host Header Validation

## Technologies Used

- **Backend:** Django 5.2, Python 3.11
- **Frontend:** Bootstrap 5, HTML5, CSS3, JavaScript
- **Database:** SQLite (development)
- **Payment:** Stripe (integration ready)
- **Forms:** Django Crispy Forms with Bootstrap 5
- **Icons:** Font Awesome 6
- **Fonts:** Google Fonts (Playfair Display, Poppins)

## Deployment Status

**Live URL:** https://ds613u232p80.drytis.ai/

The application is currently running and accessible through the Caddy reverse proxy.

---

**Goodluck Bakery E-Commerce Platform**
*Version 1.0.0*
