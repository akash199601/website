import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'todoproject.settings')
django.setup()

from myapp.models import Product, Cart, CartItem

print("\nProducts in database:")
print("-" * 50)
for product in Product.objects.all():
    print(f"ID: {product.id}")
    print(f"Name: {product.name}")
    print(f"Price: Rs.{product.price}")
    print(f"Description: {product.description}")
    print("-" * 50)

print("\nCarts in database:")
print("-" * 50)
for cart in Cart.objects.all():
    print(f"Cart for user: {cart.user.username}")
    print("Items:")
    for item in cart.items.all():
        print(f"- {item.quantity}x {item.product.name} (Rs.{item.product.price} each)")
    print("-" * 50)
