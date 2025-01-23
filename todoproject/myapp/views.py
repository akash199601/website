from http import client
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Product, Cart, CartItem, Order, OrderItem
from django.views.decorators.csrf import csrf_exempt
from . import views
import json
import razorpay
from django.urls import reverse

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
    products = Product.objects.all()
    return render(request, 'home.html', {'products': products})

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

@login_required
def update_cart(request, product_id):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        product = get_object_or_404(Product, id=product_id)
        cart = Cart.objects.get(user=request.user)
        cart_item = get_object_or_404(CartItem, cart=cart, product=product)
        
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
        else:
            cart_item.delete()
            
    return redirect('cart')

@login_required
def remove_from_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = Cart.objects.get(user=request.user)
    CartItem.objects.filter(cart=cart, product=product).delete()
    return redirect('cart')

@login_required
def cart_view(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    
    # Calculate totals for each item and cart total
    cart_items = []
    cart_total = 0
    for item in cart.items.all():
        item_total = float(item.product.price) * item.quantity
        cart_items.append({
            'item': item,
            'total': item_total
        })
        cart_total += item_total
    
    return render(request, 'cart.html', {
        'cart': cart,
        'cart_items': cart_items,
        'cart_total': cart_total
    })

razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

# Add Razorpay Checkout
@login_required
def checkout(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    
    # Calculate totals for each item and cart total
    cart_items = []
    cart_total = 0
    for item in cart.items.all():
        item_total = float(item.product.price) * item.quantity
        cart_items.append({
            'item': item,
            'total': item_total
        })
        cart_total += item_total
    
    return render(request, 'checkout.html', {
        'cart_items': cart_items,
        'cart_total': cart_total
    })

@login_required
def process_checkout(request):
    if request.method == 'POST':
        # Get form data
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        city = request.POST.get('city')
        pincode = request.POST.get('pincode')
        
        # Get cart details
        cart = Cart.objects.get(user=request.user)
        cart_total = sum(item.product.price * item.quantity for item in cart.items.all())
        
        # Create Razorpay order
        order_amount = int(cart_total * 100)  # Convert to paisa
        order_currency = 'INR'
        
        # Create Razorpay Order
        razorpay_order = razorpay_client.order.create({
            'amount': order_amount,
            'currency': order_currency
        })
        
        # Save order details in session for verification
        request.session['razorpay_order_id'] = razorpay_order['id']
        request.session['shipping_details'] = {
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'phone': phone,
            'address': address,
            'city': city,
            'pincode': pincode
        }
        
        # Render payment page
        return render(request, 'payment.html', {
            'razorpay_key_id': settings.RAZORPAY_KEY_ID,
            'razorpay_order_id': razorpay_order['id'],
            'amount': cart_total,
            'callback_url': request.build_absolute_uri(reverse('payment_success'))
        })
    
    return redirect('checkout')

@login_required
def payment_success(request):
    if request.method == 'POST':
        razorpay_payment_id = request.POST.get('razorpay_payment_id')
        razorpay_order_id = request.POST.get('razorpay_order_id')
        razorpay_signature = request.POST.get('razorpay_signature')
        
        # Verify payment signature
        try:
            razorpay_client.utility.verify_payment_signature({
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_order_id': razorpay_order_id,
                'razorpay_signature': razorpay_signature
            })
        except Exception:
            messages.error(request, 'Invalid payment signature')
            return redirect('payment_cancel')
        
        # Get shipping details from session
        shipping_details = request.session.get('shipping_details', {})
        
        # Get cart and calculate total
        cart = Cart.objects.get(user=request.user)
        cart_total = sum(item.product.price * item.quantity for item in cart.items.all())
        
        # Create order
        order = Order.objects.create(
            user=request.user,
            first_name=shipping_details.get('first_name'),
            last_name=shipping_details.get('last_name'),
            email=shipping_details.get('email'),
            phone=shipping_details.get('phone'),
            address=shipping_details.get('address'),
            city=shipping_details.get('city'),
            pincode=shipping_details.get('pincode'),
            total_amount=cart_total,
            payment_id=razorpay_payment_id,
            order_id=razorpay_order_id,
            payment_status='completed'
        )
        
        # Create order items
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price * cart_item.quantity
            )
        
        # Clear cart and session data
        cart.items.all().delete()
        if 'shipping_details' in request.session:
            del request.session['shipping_details']
        if 'razorpay_order_id' in request.session:
            del request.session['razorpay_order_id']
        
        messages.success(request, 'Order placed successfully!')
        return render(request, 'success.html', {'order': order})
    
    return redirect('cart')

@login_required
def payment_cancel(request):
    messages.warning(request, 'Payment was cancelled')
    return redirect('cart')

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