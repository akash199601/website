from django import template

print("Loading custom filters...")  # Add this line for debugging

register = template.Library()

@register.filter
def multiply(value, arg):
    return float(value) * float(arg)