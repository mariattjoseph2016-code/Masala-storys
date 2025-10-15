from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest, HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
import re
from accounts.models import Address
from catalog.models import Product


SESSION_KEY = 'cart_items'
ORDERS_KEY = 'orders'
WISHLIST_KEY = 'wishlist_items'


def _get_cart(request: HttpRequest) -> dict:
    return request.session.get(SESSION_KEY, {})


def _save_cart(request: HttpRequest, cart: dict) -> None:
    request.session[SESSION_KEY] = cart
    request.session.modified = True


def _get_wishlist(request: HttpRequest) -> dict:
    return request.session.get(WISHLIST_KEY, {})


def _save_wishlist(request: HttpRequest, wishlist: dict) -> None:
    request.session[WISHLIST_KEY] = wishlist
    request.session.modified = True


@login_required
def add_to_cart(request: HttpRequest, product_id: int) -> HttpResponse:
    product = get_object_or_404(Product, id=product_id)
    cart = _get_cart(request)
    qty = 1
    if request.method == 'POST':
        try:
            qty = max(1, int(request.POST.get('qty', '1')))
        except ValueError:
            qty = 1
    cart[str(product_id)] = cart.get(str(product_id), 0) + qty
    _save_cart(request, cart)
    return redirect('cart:view')


@login_required
def remove_from_cart(request: HttpRequest, product_id: int) -> HttpResponse:
    cart = _get_cart(request)
    cart.pop(str(product_id), None)
    _save_cart(request, cart)
    return redirect('cart:view')


@login_required
def clear_cart(request: HttpRequest) -> HttpResponse:
    _save_cart(request, {})
    return redirect('cart:view')


def view_cart(request: HttpRequest) -> HttpResponse:
    cart = _get_cart(request)
    product_ids = [int(pid) for pid in cart.keys()]
    products = Product.objects.filter(id__in=product_ids)
    id_to_quantity = {int(pid): qty for pid, qty in cart.items()}

    items = []
    total = 0
    for product in products:
        qty = id_to_quantity.get(product.id, 0)
        line_total = (product.sale_price or product.mrp or 0) * qty
        total += line_total
        items.append({
            'product': product,
            'quantity': qty,
            'line_total': line_total,
        })

    context = { 'items': items, 'total': total }
    return render(request, 'cart/cart.html', context)


@login_required
def buy_now(request: HttpRequest, product_id: int) -> HttpResponse:
    product = get_object_or_404(Product, id=product_id)
    # For a simple flow, overwrite cart with single item
    _save_cart(request, {str(product_id): 1})
    return render(request, 'cart/buy_now.html', { 'product': product })


@login_required
def payment(request: HttpRequest) -> HttpResponse:
    # In a real app, integrate payment gateway here
    cart = _get_cart(request)
    product_ids = [int(pid) for pid in cart.keys()]
    products = Product.objects.filter(id__in=product_ids)
    id_to_quantity = {int(pid): qty for pid, qty in cart.items()}
    total = 0.0
    for p in products:
        qty = id_to_quantity.get(p.id, 0)
        price_f = float(p.sale_price or p.mrp or 0)
        total += price_f * qty
    # Require at least one saved address before proceeding
    if not Address.objects.filter(user=request.user).exists():
        messages.info(request, 'Please add a delivery address before making a payment.')
        return redirect('accounts:profile')

    if request.method == 'POST':
        card_number = (request.POST.get('card_number') or '').replace(' ', '')
        expiry = (request.POST.get('expiry') or '').strip()
        cvv = (request.POST.get('cvv') or '').strip()

        # Server-side validations mirroring client
        if not (card_number.isdigit() and len(card_number) == 16):
            return render(request, 'cart/payment.html', { 'total': total, 'error': 'Card number must be exactly 16 digits.' })

        m = re.match(r'^(0[1-9]|1[0-2])/(\d{2}|\d{4})$', expiry)
        if not m:
            return render(request, 'cart/payment.html', { 'total': total, 'error': 'Invalid expiry format.' })
        month = int(m.group(1)); year = int(m.group(2)); year = 2000 + year if year < 100 else year
        # End of expiry month
        exp_date = datetime(year, month, 1) + timedelta(days=32)
        exp_date = exp_date.replace(day=1) - timedelta(milliseconds=1)
        if exp_date < datetime.now():
            return render(request, 'cart/payment.html', { 'total': total, 'error': 'Card expired.' })

        if not re.match(r'^\d{3}$', cvv):
            return render(request, 'cart/payment.html', { 'total': total, 'error': 'CVV must be exactly 3 digits.' })

        # Build order and reduce stock
        items = []
        for p in products:
            qty = id_to_quantity.get(p.id, 0)
            price = float(p.sale_price or p.mrp or 0)
            
            # Reduce stock
            if p.stock_quantity >= qty:
                p.stock_quantity -= qty
                p.save()
            else:
                return render(request, 'cart/payment.html', { 'total': total, 'error': f'Insufficient stock for {p.name}. Only {p.stock_quantity} available.' })
            
            items.append({
                'product_id': p.id,
                'name': p.name,
                'quantity': qty,
                'price': price,
                'line_total': price * qty,
            })
        order = {
            'id': int(datetime.now().timestamp()),
            'ordered_at': datetime.now().isoformat(),
            'arrival_date': (datetime.now() + timedelta(days=7)).date().isoformat(),
            'paid': True,
            'total': total,
            'items': items,
        }
        orders = request.session.get(ORDERS_KEY, [])
        orders.insert(0, order)
        request.session[ORDERS_KEY] = orders
        _save_cart(request, {})
        messages.success(request, 'Payment successful! Your order has been placed.')
        return redirect('cart:orders')

    return render(request, 'cart/payment.html', { 'total': total })


@login_required
def orders(request: HttpRequest) -> HttpResponse:
    orders = request.session.get(ORDERS_KEY, [])
    return render(request, 'cart/orders.html', { 'orders': orders })


@login_required
def order_detail(request: HttpRequest, order_id: int) -> HttpResponse:
    orders = request.session.get(ORDERS_KEY, [])
    order = None
    
    # Find the order by ID
    for o in orders:
        if o['id'] == order_id:
            order = o
            break
    
    if not order:
        messages.error(request, 'Order not found.')
        return redirect('cart:orders')
    
    return render(request, 'cart/order_detail.html', { 'order': order })


# Wishlist views
@login_required
def wishlist_view(request: HttpRequest) -> HttpResponse:
    wishlist = _get_wishlist(request)
    product_ids = [int(pid) for pid in wishlist.keys()]
    products = Product.objects.filter(id__in=product_ids)
    return render(request, 'cart/wishlist.html', { 'products': products })


@login_required
def wishlist_add(request: HttpRequest, product_id: int) -> HttpResponse:
    get_object_or_404(Product, id=product_id)
    wishlist = _get_wishlist(request)
    wishlist[str(product_id)] = 1
    _save_wishlist(request, wishlist)
    messages.success(request, 'Added to wishlist')
    return redirect('cart:wishlist')


@login_required
def wishlist_remove(request: HttpRequest, product_id: int) -> HttpResponse:
    wishlist = _get_wishlist(request)
    wishlist.pop(str(product_id), None)
    _save_wishlist(request, wishlist)
    return redirect('cart:wishlist')


@login_required
def wishlist_move_to_cart(request: HttpRequest, product_id: int) -> HttpResponse:
    # Move single item from wishlist to cart (qty 1)
    get_object_or_404(Product, id=product_id)
    wishlist = _get_wishlist(request)
    wishlist.pop(str(product_id), None)
    _save_wishlist(request, wishlist)
    cart = _get_cart(request)
    cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    _save_cart(request, cart)
    messages.success(request, 'Moved to cart')
    return redirect('cart:view')


