// Goodluck Bakery - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Back to Top Button
    const backToTopButton = document.getElementById('backToTop');

    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 300) {
            backToTopButton.classList.remove('d-none');
            backToTopButton.classList.add('d-block');
        } else {
            backToTopButton.classList.remove('d-block');
            backToTopButton.classList.add('d-none');
        }
    });

    backToTopButton.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });

    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            alert.style.transition = 'opacity 0.5s';
            alert.style.opacity = '0';
            setTimeout(function() {
                alert.remove();
            }, 500);
        }, 5000);
    });

    // Product thumbnail gallery
    const thumbnails = document.querySelectorAll('.thumbnail');
    const mainImage = document.querySelector('.product-detail-img');

    thumbnails.forEach(function(thumbnail) {
        thumbnail.addEventListener('click', function() {
            const newSrc = this.src;
            mainImage.src = newSrc;

            // Update active state
            thumbnails.forEach(t => t.classList.remove('border-primary'));
            this.classList.add('border-primary');
        });
    });

    // Quantity controls
    const quantityInputs = document.querySelectorAll('.quantity-input');
    quantityInputs.forEach(function(input) {
        const min = parseInt(input.getAttribute('min')) || 1;
        const max = parseInt(input.getAttribute('max')) || 99;

        input.addEventListener('change', function() {
            let value = parseInt(this.value);
            if (isNaN(value) || value < min) {
                this.value = min;
            } else if (value > max) {
                this.value = max;
            }
        });
    });

    // Add to cart with feedback
    const addToCartForms = document.querySelectorAll('form[action*="add_to_cart"]');
    addToCartForms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            const button = form.querySelector('button[type="submit"]');
            if (button) {
                const originalHTML = button.innerHTML;
                button.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
                button.disabled = true;

                // Form will submit normally, this just shows loading state
            }
        });
    });

    // Search form enhancement
    const searchForm = document.querySelector('form[action*="shop"]');
    const searchInput = searchForm ? searchForm.querySelector('input[name="q"]') : null;

    if (searchInput) {
        searchInput.addEventListener('keyup', function(e) {
            if (e.key === 'Enter') {
                searchForm.submit();
            }
        });
    }

    // Lazy loading images
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver(function(entries, observer) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    if (img.dataset.src) {
                        img.src = img.dataset.src;
                        img.removeAttribute('data-src');
                    }
                    observer.unobserve(img);
                }
            });
        });

        const lazyImages = document.querySelectorAll('img[data-src]');
        lazyImages.forEach(function(img) {
            imageObserver.observe(img);
        });
    }

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(function(anchor) {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href !== '#' && href !== '') {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });

    // Navbar background on scroll
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 50) {
                navbar.classList.add('shadow-sm');
            } else {
                navbar.classList.remove('shadow-sm');
            }
        });
    }

    // Form validation enhancement
    const forms = document.querySelectorAll('form[data-validate]');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            let isValid = true;

            form.querySelectorAll('input[required], select[required], textarea[required]').forEach(function(field) {
                if (!field.value.trim()) {
                    field.classList.add('is-invalid');
                    isValid = false;
                } else {
                    field.classList.remove('is-invalid');
                }

                field.addEventListener('input', function() {
                    this.classList.remove('is-invalid');
                });
            });

            if (!isValid) {
                e.preventDefault();
            }
        });
    });

    // Price calculation for checkout
    const shippingOptions = document.querySelectorAll('input[name="shipping_method"]');
    shippingOptions.forEach(function(option) {
        option.addEventListener('change', updateOrderTotal);
    });

    function updateOrderTotal() {
        const selectedOption = document.querySelector('input[name="shipping_method"]:checked');
        if (selectedOption) {
            const shippingCosts = {
                'standard': 5.99,
                'express': 12.99,
                'pickup': 0
            };
            const subtotalElement = document.querySelector('#subtotal');
            const shippingElement = document.querySelector('#shipping-cost');
            const taxElement = document.querySelector('#tax');
            const totalElement = document.querySelector('#total');

            if (subtotalElement) {
                const subtotal = parseFloat(subtotalElement.textContent.replace('$', ''));
                const shipping = shippingCosts[selectedOption.value];
                const tax = subtotal * 0.08;
                const total = subtotal + shipping + tax;

                if (shippingElement) shippingElement.textContent = '$' + shipping.toFixed(2);
                if (taxElement) taxElement.textContent = '$' + tax.toFixed(2);
                if (totalElement) totalElement.textContent = '$' + total.toFixed(2);
            }
        }
    }

    // Image preview for file uploads
    const imageInputs = document.querySelectorAll('input[type="file"][accept*="image"]');
    imageInputs.forEach(function(input) {
        input.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    const preview = document.querySelector('#image-preview');
                    if (preview) {
                        preview.src = e.target.result;
                        preview.style.display = 'block';
                    }
                };
                reader.readAsDataURL(file);
            }
        });
    });

    // Confirm before delete
    const deleteButtons = document.querySelectorAll('[data-confirm]');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            const message = this.getAttribute('data-confirm') || 'Are you sure?';
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });

    // Copy to clipboard functionality
    const copyButtons = document.querySelectorAll('[data-copy]');
    copyButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            const textToCopy = this.getAttribute('data-copy');
            navigator.clipboard.writeText(textToCopy).then(function() {
                const originalText = button.innerHTML;
                button.innerHTML = '<i class="fas fa-check"></i> Copied!';
                setTimeout(function() {
                    button.innerHTML = originalText;
                }, 2000);
            });
        });
    });

    // Toggle password visibility
    const togglePasswordButtons = document.querySelectorAll('.toggle-password');
    togglePasswordButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            const passwordInput = document.querySelector(this.getAttribute('data-target'));
            const icon = this.querySelector('i');

            if (passwordInput.type === 'password') {
                passwordInput.type = 'text';
                icon.classList.remove('fa-eye');
                icon.classList.add('fa-eye-slash');
            } else {
                passwordInput.type = 'password';
                icon.classList.remove('fa-eye-slash');
                icon.classList.add('fa-eye');
            }
        });
    });

    // Character counter for textareas
    const textareasWithCounter = document.querySelectorAll('textarea[data-max-length]');
    textareasWithCounter.forEach(function(textarea) {
        const maxLength = parseInt(textarea.getAttribute('data-max-length'));
        const counter = document.createElement('small');
        counter.className = 'text-muted';
        counter.textContent = '0 / ' + maxLength;
        textarea.parentNode.appendChild(counter);

        textarea.addEventListener('input', function() {
            const currentLength = this.value.length;
            counter.textContent = currentLength + ' / ' + maxLength;

            if (currentLength > maxLength) {
                counter.classList.add('text-danger');
                textarea.value = textarea.value.substring(0, maxLength);
            } else {
                counter.classList.remove('text-danger');
            }
        });
    });

    // Loading overlay for AJAX requests
    function showLoading() {
        let overlay = document.querySelector('.spinner-overlay');
        if (!overlay) {
            overlay = document.createElement('div');
            overlay.className = 'spinner-overlay';
            overlay.innerHTML = '<div class="spinner-border text-light" role="status"><span class="visually-hidden">Loading...</span></div>';
            document.body.appendChild(overlay);
        }
        overlay.style.display = 'flex';
    }

    function hideLoading() {
        const overlay = document.querySelector('.spinner-overlay');
        if (overlay) {
            overlay.style.display = 'none';
        }
    }

    // Expose loading functions globally
    window.showLoading = showLoading;
    window.hideLoading = hideLoading;

    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Category filter on shop page
    const categoryFilter = document.querySelector('#category-filter');
    if (categoryFilter) {
        categoryFilter.addEventListener('change', function() {
            const url = new URL(window.location);
            url.searchParams.set('category', this.value);
            window.location = url.toString();
        });
    }

    // Sort products on shop page
    const sortSelect = document.querySelector('#sort-select');
    if (sortSelect) {
        sortSelect.addEventListener('change', function() {
            const url = new URL(window.location);
            url.searchParams.set('sort', this.value);
            window.location = url.toString();
        });
    }

    // Coupon code validation (placeholder)
    const couponForm = document.querySelector('#coupon-form');
    if (couponForm) {
        couponForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const couponCode = this.querySelector('input[name="coupon_code"]').value;
            // Add AJAX call to validate coupon
            console.log('Validating coupon:', couponCode);
        });
    }
});

// Stripe Payment Handler (if on payment page)
const stripe = Stripe(stripePublicKey);

function handlePayment(clientSecret) {
    const elements = stripe.elements({
        fonts: {
            cssSrc: 'https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600&display=swap'
        }
    });

    const cardElement = elements.create('card', {
        style: {
            base: {
                fontSize: '16px',
                color: '#32325d',
                fontFamily: 'Poppins, sans-serif',
                '::placeholder': {
                    color: '#aab7c4'
                }
            }
        }
    });

    cardElement.mount('#card-element');

    const form = document.querySelector('#payment-form');
    form.addEventListener('submit', async (event) => {
        event.preventDefault();

        const {error, paymentIntent} = await stripe.confirmCardPayment(
            clientSecret,
            {
                payment_method: {
                    card: cardElement,
                    billing_details: {
                        name: document.querySelector('#cardholder-name').value
                    }
                }
            }
        );

        if (error) {
            document.querySelector('#payment-errors').textContent = error.message;
        } else {
            window.location.href = '/payment/success/';
        }
    });
}

// Cart API helpers (for AJAX cart operations)
const CartAPI = {
    addItem: function(productId, quantity = 1) {
        return fetch('/cart/add/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: `product_id=${productId}&quantity=${quantity}`
        }).then(response => response.json());
    },

    updateItem: function(itemId, action) {
        return fetch('/cart/update/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: `item_id=${itemId}&action=${action}`
        }).then(response => response.json());
    },

    removeItem: function(itemId) {
        return fetch(`/cart/remove/${itemId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        }).then(response => response.json());
    },

    getCart: function() {
        return fetch('/cart/api/')
            .then(response => response.json());
    }
};

console.log('Goodluck Bakery - Loaded successfully');
