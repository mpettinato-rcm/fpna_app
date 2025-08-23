from django import template
import locale

register = template.Library()

@register.filter
def accounting_format(value):
    """
    Format numbers in accounting style:
    - Commas for thousands
    - No decimal places
    - Negative numbers in parentheses
    """
    if value is None or value == 0:
        return "-"
    
    try:
        # Convert to float if it's not already
        num_value = float(value)
        
        # Round to whole number
        num_value = round(num_value)
        
        # Format with commas
        if num_value < 0:
            # For negative numbers, show in parentheses
            formatted = f"({abs(num_value):,})"
        else:
            # For positive numbers, show normally
            formatted = f"{num_value:,}"
        
        return formatted
    except (ValueError, TypeError):
        return str(value)

@register.filter
def percentage_format(value):
    """
    Format percentages with one decimal place
    """
    if value is None or value == 0:
        return "-"
    
    try:
        num_value = float(value)
        return f"{num_value:.1f}%"
    except (ValueError, TypeError):
        return str(value)