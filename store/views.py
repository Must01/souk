from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Cart, CartItem
from urllib.parse import quote


def product_list(request):
    products = Product.objects.all()
    return render(request, 'store/product_list.html', {'products': products})

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # Get or create cart using session
    if not request.session.session_key:
        request.session.create()
    
    session_key = request.session.session_key
    cart, created = Cart.objects.get_or_create(session_key=session_key)
    
    # Get or create cart item
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product
    )
    
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    
    return redirect('product_list')

def view_cart(request):
    if not request.session.session_key:
        return render(request, 'store/cart.html', {'cart': None})
    
    try:
        cart = Cart.objects.get(session_key=request.session.session_key)
    except Cart.DoesNotExist:
        cart = None
    
    return render(request, 'store/cart.html', {'cart': cart})


def checkout(request):
    if not request.session.session_key:
        return redirect('product_list')
    
    try:
        cart = Cart.objects.get(session_key=request.session.session_key)
    except Cart.DoesNotExist:
        return redirect('product_list')
    
    # Build WhatsApp message
    message = "🛒 *New Order*\n\n"
    total = 0
    
    for item in cart.items.all():
        message += f"• {item.product.name}\n"
        message += f"  Price: {item.product.price} MAD\n"
        message += f"  Quantity: {item.quantity}\n"
        message += f"  Subtotal: {item.get_total()} MAD\n\n"
        total += item.get_total()
    
    message += f"*Total: {total} MAD*"
    
    # WhatsApp number (replace with real number)
    phone = "212705368180"
    whatsapp_url = f"https://wa.me/{phone}?text={quote(message)}"
    
    return redirect(whatsapp_url)