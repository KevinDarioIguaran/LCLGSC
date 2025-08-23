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

from .models import Category, Product, Cart, CartItem
from .forms import SubmitProductForm, CartAddProductForm, CartUpdateProductForm
from luis_carlos_cooperativa.utils.validators import validate_images


def product_detail(request, id, slug, error=None):
    product = get_object_or_404(Product, id=id, slug=slug)

    quantity_range = range(1, 21) if product.stock >= 20 else range(1, product.stock + 1) if product.stock > 0 else None

    related_products_qs = (
        Product.objects.filter(category=product.category)
        .exclude(id=product.id)
        .order_by("-sales")
    )

    related_products = list(related_products_qs[:20]) if related_products_qs.count() > 10 else list(related_products_qs[:10])

    context = {
        'product': product,
        'product_id': product.id,
        'seller_user': product.get_name_seller,
        'related_products': related_products,
    }

    if error:
        context['error'] = error

    if quantity_range:
        context['quantity_range'] = quantity_range

    if product.stock > 0:
        context['form'] = CartAddProductForm()

    return render(request, 'pages/shop/product/product_detail.html', context)

def search_view(request):
    context = {'products': []}

    if 'name_product' in request.GET:
        name_product = request.GET.get('name_product')
        search_results = Product.objects.filter(name__icontains=name_product)

        category_dict = {}
        for product in search_results:
            category_name = product.category.name
            category_dict.setdefault(category_name, []).append(product)

        context = {
            'search_results': search_results,
            'categories': category_dict,
        }

    return render(request, 'pages/shop/search/search.html', context)

def search_by_category_view(request, category=None,):
    if not category:
        return redirect("shop:search")

    category_obj = get_object_or_404(Category, slug=category)
    search_results = Product.objects.filter(category=category_obj)


    context = {
        'search_results': search_results,
        'categories': category_obj,
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
            image = form.cleaned_data.get('image')

            if image:
                validation_error = validate_images(image)
                if validation_error:
                    return render(request, 'pages/shop/sell/sell.html', {'form': form, 'error_message': validation_error})

            product = form.save(commit=False)
            product.seller = request.user
            product.slug = slugify(product.name)
            product.available = False
            product.save()

            request.user.is_seller = True
            request.user.save()

            return redirect('home:home')

    else:
        form = SubmitProductForm()

    return render(request, 'pages/shop/sell/sell.html', {'form': form})

@require_POST
@login_required
def cart_add_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    cart, _ = Cart.objects.get_or_create(user=request.user)

    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product, defaults={"quantity": quantity})

    if not created:
        try:
            cart_item.quantity += quantity
            cart_item.save()
        except ValidationError:
            error = "No hay suficiente stock para el producto seleccionado"
            return product_detail(request, id=product.id, slug=product.slug, error=error)

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
    category_ids = Product.objects.filter(id__in=product_ids_in_cart).values_list("category_id", flat=True)

    related_products = Product.objects.filter(
        category_id__in=category_ids
    ).exclude(id__in=product_ids_in_cart)[:20]

    return render(
        request,
        "pages/shop/cart/cart_detail.html",
        {
            "cart": cart,
            "items": items,
            "related_products": related_products,
            "update_amount_items": update_amount_items,
        }
    )

@login_required
@require_POST
def cart_update(request, product_id):
    cart = get_object_or_404(Cart, user=request.user)
    product = get_object_or_404(Product, id=product_id)
    item = get_object_or_404(CartItem, cart=cart, product=product)

    form = CartUpdateProductForm(request.POST)
    if form.is_valid():
        quantity = form.cleaned_data['update']

        if quantity > product.stock:
            return JsonResponse({
                'success': False,
                'message': f'Solo hay {product.stock} unidades disponibles en stock.'
            }, status=400)

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

