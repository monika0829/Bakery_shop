from django import template
from decimal import Decimal

register = template.Library()


@register.filter
def inr_price(value):
    """Format price as Indian Rupees with proper formatting (₹)"""
    try:
        amount = Decimal(str(value))

        # Simple formatting for typical bakery prices
        # Format as ₹XXX.XX or ₹X,XXX.XX for thousands
        formatted_amount = f"{amount:,.2f}"

        # For lakhs and above
        if amount >= 100000:
            lakhs = amount / 100000
            return f"₹{lakhs:.2f} L"

        return f"₹{formatted_amount}"
    except (ValueError, TypeError, AttributeError):
        return "₹0.00"


@register.filter
def rupee(value):
    """Simple Rupee symbol prefix"""
    try:
        return f"₹{float(value):.2f}"
    except (ValueError, TypeError):
        return "₹0.00"


@register.filter
def star_range(value):
    """Return a range of numbers for star rating display"""
    try:
        return range(int(value))
    except (ValueError, TypeError):
        return range(0)


@register.filter
def multiply(value, arg):
    """Multiply value by arg"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def add(value, arg):
    """Add arg to value"""
    try:
        return float(value) + float(arg)
    except (ValueError, TypeError):
        return 0
