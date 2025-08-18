import re
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseBadRequest, JsonResponse, Http404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core.exceptions import ValidationError
from django.contrib.auth import logout
from django.db import transaction

from .models import Order
from shop.models import Cart
from .forms import SearchOrderForm
from .tasks import create_order
from luis_carlos_cooperativa.is_mobile import get_profile_template


@login_required
def continue_order_view(request):
    """
    Muestra el resumen del pedido, el crédito del usuario
    y permite ingresar la dirección dentro del colegio.
    """
    try:
        cart = Cart.objects.get(user=request.user)
    except Cart.DoesNotExist:
        return redirect('shop:cart_detail')

    items = cart.cart_items.select_related('product').all()
    if not items.exists():
        return redirect('shop:cart_detail')

    total = Decimal('0')
    out_of_stock_items = []

    for item in items:
        item.total = item.quantity * item.product.price
        if item.quantity > item.product.stock:
            out_of_stock_items.append(item.product)
        else:
            total += item.total

    credit = request.user.credit
    debt = request.user.debt
    has_enough_credit = credit >= total
    remaining_credit = credit - total if has_enough_credit else 0
    show_physical_payment = debt > 0 or not has_enough_credit

    full_name = getattr(request.user, 'get_full_name', lambda: '')()  # Nombre completo

    context = {
        'items': items,
        'total': total,
        'credit': credit,
        'debt': debt,
        'has_enough_credit': has_enough_credit,
        'remaining_credit': remaining_credit,
        'can_continue': has_enough_credit and not out_of_stock_items,
        'out_of_stock_items': out_of_stock_items,
        'show_physical_payment': show_physical_payment,
        'full_name': full_name,
        'school_address_choices':  Order._meta.get_field('school_address').choices
    }

    return render(request, "pages/orders/continue_order.html", context)



@login_required
@require_POST
def order_create_view(request):
    """
    Crea un pedido a partir del carrito y registra la dirección dentro del colegio.
    """
    user = request.user
    cart = get_object_or_404(Cart, user=user)

    if not cart.cart_items.exists():
        return JsonResponse({"error": "El carrito está vacío."}, status=400)

    total = Decimal(cart.get_total_cost())

    if user.credit < total:
        return JsonResponse({"error": "Saldo insuficiente."}, status=400)

    school_address = request.POST.get("school_address")
    valid_choices = dict(Order._meta.get_field("school_address").choices)

    if school_address not in valid_choices:
        return JsonResponse({"error": "Dirección escolar inválida."}, status=400)

    products = []
    for item in cart.cart_items.select_related('product'):
        product = item.product
        if item.quantity > product.stock:
            return JsonResponse({
                "error": f"Stock insuficiente para {product.name}."
            }, status=400)

        products.append({
            "product_id": product.id,
            "price": str(product.price),
            "quantity": item.quantity,
        })

    try:
        with transaction.atomic():
            user.credit -= total
            user.save()

            for item in cart.cart_items.select_related("product"):
                product = item.product
                if item.quantity > product.stock:
                    raise ValueError(f"Stock insuficiente para {product.name}.")
                product.stock -= item.quantity
                product.save()

            cart.cart_items.all().delete()

            create_order(
                user.code,
                products,
                paid=True,
                school_address=school_address
            )

        return JsonResponse({"success": "Pago procesado y orden creada."})
    except Exception as e:
        return JsonResponse({"error": f"Error interno: {str(e)}"}, status=500)


@login_required
def order_detail_view(request):
    """
    Muestra todos los pedidos del usuario.
    """
    orders = Order.objects.filter(user=request.user)
    form_search_order = SearchOrderForm()

    context = {
        'orders': orders,
        'form_search_order': form_search_order
    }

    return render(request, "pages/orders/search_orders.html", context)


@login_required
def order_search_view(request):
    """
    Permite buscar pedidos por nombre de producto.
    """
    form = SearchOrderForm(request.POST or None)
    orders = Order.objects.filter(user=request.user)
    orders_items = orders.none()

    if form.is_valid():
        search_query = form.cleaned_data.get('search_query')
        if search_query:
            orders_items = orders.filter(items__product__name__icontains=search_query).distinct()

    context = {
        'form': form,
        'orders': orders_items,
        'form_search_order': form,
    }

    return render(request, 'pages/orders/search_orders.html', context)


@login_required
@require_POST
def order_delete_view(request, order_id):
    """
    Elimina un pedido. Si no está pendiente, desactiva al usuario por seguridad.
    """
    order = get_object_or_404(Order, id=order_id, user=request.user)

    try:
        order.delete()
    except ValidationError:
        user = request.user
        user.is_active = False
        user.save()
        logout(request)
        return HttpResponseBadRequest(
            "No se puede eliminar un pedido que no esté pendiente. "
            "Has sido desactivado por seguridad. Contacta al soporte."
        )

    return redirect('orders:order_detail')
