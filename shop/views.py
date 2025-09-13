from decimal import Decimal
from urllib import request
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils.text import slugify
from django.views.decorators.http import require_POST
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.db.models import Avg
from django.conf import settings

from .decorators import seller_required
from .models import Category, Product, Cart, CartItem

from orders.models import Order
from .forms import SubmitProductForm, CartAddProductForm, CartUpdateProductForm, CooperativeForm, CreditRechargeForm
from luis_carlos_cooperativa.utils.validators import validate_images

User = settings.AUTH_USER_MODEL

def product_detail(request, id, slug, error=None):
    product = get_object_or_404(Product, id=id, slug=slug, available=True)

    related_products_qs = (
        Product.objects.filter(category=product.category, available=True)  
        .exclude(id=product.id)
        .order_by("-offer_active", "-sales")
    )

    related_products = list(related_products_qs[:20]) if related_products_qs.count() > 10 else list(related_products_qs[:10])

    context = {
        'product': product,
        'product_id': product.id,
        'seller_user': product.get_name_seller,
        'related_products': related_products,
        'quantity_range': range(1, 21),
    }

    if error:
        context['error'] = error

    if not (request.user.is_authenticated and getattr(request.user, "is_seller", False) and product.seller == request.user):
        context['form'] = CartAddProductForm()

    return render(request, 'pages/shop/product/product_detail.html', context)

def search_view(request):
    context = {'products': []}

    if 'name_product' in request.GET:
        name_product = request.GET.get('name_product')
        search_results = Product.objects.filter(name__icontains=name_product, available=True).order_by("-offer_active", "-sales")

        category_dict = {}
        for product in search_results:
            category_name = product.category.name
            category_dict.setdefault(category_name, []).append(product)

        context = {
            'search_results': search_results,
            'categories': category_dict,
        }

    return render(request, 'pages/shop/search/search.html', context)

def search_by_category_view(request, category=None):
    if not category:
        return redirect("shop:search")

    category_obj = get_object_or_404(Category, slug=category)
    search_results = Product.objects.filter(category=category_obj, available=True).order_by("-offer_active", "-sales")

    category_dict = {}
    if search_results.exists():
        category_dict[category_obj.name] = list(search_results)

    context = {
        'search_results': search_results,
        'categories': category_dict,
    }

    if not search_results.exists():
        context['errors'] = 'No hay productos en esta categoría.'

    return render(request, 'pages/shop/search/search_by_category.html', context)

@login_required
def sell_view(request):
    if not request.user.is_seller:
        return redirect('home:home')

    if request.method == 'POST':
        form = SubmitProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save(seller=request.user) 
            return redirect('shop:list_my_products')
    else:
        form = SubmitProductForm()

    return render(request, 'pages/shop/sell/sell.html', {'form': form})


@seller_required
@login_required
def edit_product_view(request, product_id):    
    product = get_object_or_404(Product, id=product_id, seller=request.user)

    if request.method == 'POST':
        form = SubmitProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save(seller=request.user, instance=product)  
            return redirect('shop:list_my_products')
    else:
        form = SubmitProductForm(initial={
            'category': product.category,
            'name': product.name,
            'price': product.price,
            'description': product.description,
            'discount_percent': product.discount_percent,
            'offer_active': product.offer_active,
            'available': product.available,
        })

    return render(
        request,
        'pages/shop/sell/edit_product.html',
        {'form': form, 'product': product}
    )

@require_POST
@login_required
def cart_add_view(request, product_id):
    product = get_object_or_404(Product, id=product_id, available=True)
    
    if product.seller == request.user:
       messages.error(request, "No puedes agregar tu propio producto al carrito.")
       return redirect("shop:product_detail", id=product.id, slug=product.slug)
    
    form = CartAddProductForm(request.POST)
    if not form.is_valid():
        return redirect("shop:product_detail", id=product.id, slug=product.slug)
    
    quantity = form.cleaned_data['quantity']
    
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product, defaults={"quantity": quantity})

    if not created:
        cart_item.quantity += quantity
        cart_item.save()

    return redirect("shop:cart_detail")

@login_required
def cart_remove_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    try:
        cart = Cart.objects.get(user=request.user)
        CartItem.objects.filter(cart=cart, product=product).delete()
    except Cart.DoesNotExist:
        pass

    return redirect("shop:cart_detail")

@login_required
def cart_detail_view(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = cart.cart_items.select_related("product").all() 
    update_amount_items = {}

    for item in items:
        form = CartUpdateProductForm(initial={'quantity': item.quantity})
        update_amount_items[item.product.id] = form

    product_ids_in_cart = items.values_list("product_id", flat=True)
    category_ids = Product.objects.filter(
        id__in=product_ids_in_cart
    ).values_list("category_id", flat=True)

    related_products = Product.objects.filter(
        category_id__in=category_ids,
        available=True
    ).exclude(
        id__in=product_ids_in_cart
    ).exclude(
        seller=request.user if getattr(request.user, "is_seller", False) else None
    )[:20]

    has_unavailable = any(not item.product.available for item in items)

    return render(
        request,
        "pages/shop/cart/cart_detail.html",
        {
            "cart": cart,
            "items": items,
            "related_products": related_products,
            "update_amount_items": update_amount_items,
            "has_unavailable": has_unavailable,
        }
    )

@login_required
@require_POST
def cart_update(request, product_id):
    cart = get_object_or_404(Cart, user=request.user)
    product = get_object_or_404(Product, id=product_id, available=True)
    item = get_object_or_404(CartItem, cart=cart, product=product)

    form = CartUpdateProductForm(request.POST)
    if form.is_valid():
        quantity = form.cleaned_data['update']
        item.quantity = quantity
        item.save()

        return JsonResponse({
            'success': True,
            'message': 'Cantidad actualizada correctamente.',
            'quantity': item.quantity
        })

    return JsonResponse({
        'success': False,
        'message': 'Formulario inválido.'
    }, status=400)


@seller_required
@login_required
def list_my_products(request):
    products = Product.objects.filter(seller=request.user, available=True).order_by('-created') 
    categories = Category.objects.all()

    return render(request, 'pages/shop/sell/my_products.html', {
        'products': products,
        'categories': categories,
        'query': '',
        'selected_category': ''
    })

@seller_required
@login_required
def search_my_products(request):
    query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')

    products = Product.objects.filter(seller=request.user, available=True).order_by('-created')  

    if query:
        products = products.filter(name__icontains=query)

    if category_id.isdigit():
        products = products.filter(category_id=category_id)

    categories = Category.objects.all()

    return render(request, 'pages/shop/sell/my_products.html', {
        'products': products,
        'categories': categories,
        'query': query,
        'selected_category': category_id
    })


@seller_required
@login_required
def delete_product_view(request, product_id):    
    product = get_object_or_404(Product, id=product_id, seller=request.user)

    if request.method == "POST":
        product.delete()
        return redirect("shop:list_my_products")

    return redirect("shop:list_my_products")

@seller_required
@login_required
def seller_recharge_credit(request):
    if request.method == 'POST':
        form = CreditRechargeForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('shop:seller_recharge_credit')
    else:
        form = CreditRechargeForm(user=request.user)

    return render(request, 'pages/shop/sell/recharge_credit.html', {'form': form})


@seller_required
@login_required
def pending_orders_view(request):
    orders = Order.objects.filter(status='pending').exclude(user=request.user)
    return render(request, 'pages/shop/sell/pending_orders.html', {'orders': orders})

@seller_required
@login_required
def analyze_cooperative_view(request):
    products = Product.objects.filter(seller=request.user, available=True)
    avg_sales = products.aggregate(avg_sales=Avg('sales'))['avg_sales'] or 0
    total_products = products.count()

    context = {
        'avg_sales': avg_sales,
        'total_products': total_products,
        'products': products
    }
    return render(request, 'pages/shop/sell/analysis.html', context)

@seller_required
@login_required
def edit_cooperative_view(request):
    user = request.user

    if request.method == 'POST':
        form = CooperativeForm(request.POST, request.FILES, user=user)
        if form.is_valid():
            form.save()
            return redirect('shop:seller_dashboard')
    else:
        form = CooperativeForm(user=user)

    return render(request, 'pages/shop/sell/edit_cooperative.html', {'form': form})

@seller_required
@login_required
def order_detail_view(request, order_id):
    order = get_object_or_404(Order, id=order_id, status="pending")
    return render(request, 'pages/shop/sell/order_detail.html', {'order': order})


@seller_required
@login_required
def mark_order_completed_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if order.status != 'completed':
        order.status = 'completed'
        order.save()

    return redirect('shop:pending_orders')
