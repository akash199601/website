from http import client
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Product, Cart, CartItem
from django.views.decorators.csrf import csrf_exempt
from . import views
import json
import razorpay

def signup_login_view(request):
    if request.method == 'POST':
        if 'signup' in request.POST:  # Handle Signup
            return handle_signup(request)
        elif 'login' in request.POST:  # Handle Login
            return handle_login(request)

    return render(request, 'signup_login.html')

def handle_signup(request):
    first_name = request.POST.get('first_name')
    last_name = request.POST.get('last_name')
    email = request.POST.get('email')
    username = request.POST.get('username')
    password1 = request.POST.get('password1')
    password2 = request.POST.get('password2')

    # Check if passwords match
    if password1 != password2:
        messages.error(request, "Passwords do not match.")
        return redirect('signup_login')

    # Check if username already exists
    if User.objects.filter(username=username).exists():
        messages.error(request, "Username is already taken. Please choose a different one.")
        return redirect('signup_login')

    # Check if email already exists
    if User.objects.filter(email=email).exists():
        messages.error(request, "Email is already registered. Use a different email.")
        return redirect('signup_login')

    # Create new user
    user = User.objects.create_user(
        username=username,
        first_name=first_name,
        last_name=last_name,
        email=email,
        password=password1
    )
    user.save()
    messages.success(request, "Account created successfully! You can now log in.")
    return redirect('signup_login')

def handle_login(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    user = authenticate(request, username=username, password=password)

    if user is not None:
        login(request, user)
        messages.success(request, f"Welcome, {user.first_name}!")
        return redirect('home')
    else:
        messages.error(request, "Invalid username or password.")
        return redirect('signup_login')

def home(request):
    if not request.user.is_authenticated:
        return redirect('signup_login')
    return render(request, 'home.html')

def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('signup_login')


# home page
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'product_detail.html', {'product': product})

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, _ = Cart.objects.get_or_create(user=request.user)

    # Check if product is already in the cart
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('cart')  # Redirect to cart page

# View cart
@login_required
def cart_view(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    return render(request, 'cart.html', {'cart': cart})

razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

# Add Razorpay Checkout
@login_required
def checkout(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    total_price = sum(item.product.price * item.quantity for item in cart.items.all())

    if total_price == 0:
        messages.error(request, "Your cart is empty! Add items before checkout.")
        return redirect("cart")

    try:
        order = razorpay_client.order.create({
            "amount": int(total_price * 100),
            "currency": "INR",
            "payment_capture": "1",
        })

        return render(request, 'checkout.html', {
            "cart": cart,
            "total_price": total_price,
            "razorpay_order_id": order['id'],
            "razorpay_key_id": settings.RAZORPAY_KEY_ID,
            "currency": "INR",
        })
    except Exception as e:
        messages.error(request, f"Error creating Razorpay order: {str(e)}")
        return redirect("cart")

# Payment success
@login_required
def payment_success(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart.items.all().delete()
    messages.success(request, "Payment successful! Your order is placed.")
    return render(request, 'success.html')

# Payment cancel view
def payment_cancel(request):
    messages.error(request, "Payment failed or cancelled. Please try again.")
    return render(request, 'cancel.html')

# Razorpay webhook to verify payment success
@csrf_exempt
def razorpay_webhook(request):
    if request.method == 'POST':
        try:
            payload = request.body.decode('utf-8')
            signature = request.headers.get('X-Razorpay-Signature')
            razorpay_client.utility.verify_webhook_signature(payload, signature, settings.RAZORPAY_WEBHOOK_SECRET)
            event = json.loads(payload)

            if event.get('event') == 'payment.captured':
                return JsonResponse({"status": "success", "message": "Payment captured."})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})

    return JsonResponse({"status": "error", "message": "Invalid request method."})