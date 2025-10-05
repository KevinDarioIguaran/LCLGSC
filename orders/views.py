import re
import json


from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseBadRequest, JsonResponse, Http404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core.exceptions import ValidationError
from django.contrib.auth import logout
from django.db import transaction
from django.db.models import F, Sum
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse

from .models import Order
from shop.models import Cart, Product, Category
from .forms import SearchOrderForm
from .tasks import create_order
from .generate_qr import order_qr

from shop.decorators import seller_required
from .models import Order, OrderItem, OrderCancelItem

@login_required
def continue_order_view(request):
    try:
        cart = Cart.objects.get(user=request.user)
    except Cart.DoesNotExist:
        return redirect('shop:cart_detail')

    items = cart.cart_items.select_related('product').all()
    if not items.exists():
        return redirect('shop:cart_detail')

    unavailable_items = [item for item in items if not item.product.available]
    if unavailable_items:
        return redirect('shop:cart_detail')

    total = Decimal('0')
    for item in items:
        item.total = item.quantity * item.product.price
        total += item.total

    credit = request.user.credit
    has_enough_credit = credit >= total
    remaining_credit = credit - total if has_enough_credit else 0

    full_name = getattr(request.user, 'get_full_name', lambda: '')()

    context = {
        'items': items,
        'total': total,
        'credit': credit,
        'has_enough_credit': has_enough_credit,
        'remaining_credit': remaining_credit,
        'can_continue': has_enough_credit,
        'full_name': full_name,
        'school_address_choices':  Order._meta.get_field('school_address').choices
    }

    return render(request, "pages/orders/continue_order.html", context)

@login_required
@require_POST
def order_create_view(request):
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

        products.append({
            "product_id": product.id,
            "price": str(product.price),
            "quantity": item.quantity,
        })

    try:
        with transaction.atomic():
            user.credit -= total
            user.save()

            cart.cart_items.all().delete()

            create_order(
                user.code,
                products,
                paid=True,
                school_address=school_address
            )

        return redirect("orders:order_list")
    except Exception as e:
        return HttpResponseBadRequest(f"Error al crear el pedido: {str(e)}")


@login_required
def order_list_view(request):
    orders = Order.objects.filter(user=request.user).exclude(donot_show=True).order_by('-created')
    form_search_order = SearchOrderForm()

    context = {
        'orders': orders,
        'form_search_order': form_search_order
    }

    return render(request, "pages/orders/search_orders.html", context)

@login_required
def order_donnot_show_view(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order.donot_show = True
    order.save(update_fields=["donot_show"])
    return redirect("orders:order_list")


@login_required
def order_search_view(request):
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
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.status != "pending":
        return HttpResponseBadRequest(
            "Solo se pueden eliminar pedidos pendientes."
        )


    total_amount = order.items.aggregate(
        total=Sum(F("price") * F("quantity"))
    )["total"] or Decimal("0.00")

    if hasattr(request.user, "credit"):
        request.user.credit = F("credit") + total_amount
        request.user.save(update_fields=["credit"])

    order.delete()

    return redirect("orders:order_list")

@login_required
def order_qr_view(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user, status="pending", donot_show=False)
    qr_code = order_qr(order.qr_code_data)
    return render(request, "pages/orders/order_qr.html", {
        "order": order,
        "qr_code": qr_code,
    })


@csrf_exempt
@login_required
@seller_required
def process_qr_view(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            order_id = data.get("order_id")
            qr_code = data.get("qr_code")
        except (json.JSONDecodeError, KeyError):
            return JsonResponse({"success": False, "message": "Datos inválidos."}, status=400)

        order = get_object_or_404(Order, id=order_id)

        if order.status != "pending":
            return JsonResponse({"success": False, "message": "La orden no está pendiente."}, status=400)

        if qr_code != order.qr_code_data:
            return JsonResponse({"success": False, "message": "QR incorrecto."}, status=400)

        order.status = "completed"
        order.seller_approved = request.user
        order.save(update_fields=["status", "seller_approved"])

        return JsonResponse({"success": True, "redirect_url": reverse("shop:pending_orders")})

    return JsonResponse({"success": False, "message": "Método no permitido."}, status=405)

@seller_required
@login_required
def order_cancel_stock_view(request, order_id):
    """
    Cancela la orden si al menos un producto está sin stock.
    - Los productos sin stock se registran en OrderCancelItem.
    - TODOS los productos permanecen en OrderItem.
    - Se reembolsa TODO el dinero de la orden (get_total_cost).
    - La orden se marca como 'cancelled_stock'.
    - Si algo falla, se revierte toda la operación.
    """
    order = get_object_or_404(Order, id=order_id)

    if order.status != "pending":
        return HttpResponseBadRequest("Solo se pueden modificar pedidos pendientes.")

    if request.method == "POST":
        product_ids = request.POST.getlist("cancel_products")

        if not product_ids:
            return HttpResponseBadRequest("Debes seleccionar al menos un producto.")

        try:
            with transaction.atomic():
                for item in order.items.all():
                    if str(item.product.id) in product_ids:
                        OrderCancelItem.objects.create(
                            order=order,
                            product=item.product,
                            price=item.price,
                            quantity=item.quantity,
                        )

                if order.paid:
                    refund_amount = order.get_total_cost()
                    if refund_amount > 0 and hasattr(order.user, "credit"):
                        order.user.credit = F("credit") + refund_amount
                        order.user.save(update_fields=["credit"])

                order.status = "cancelled"
                order.save(update_fields=["status"])

        except Exception as e:
            return HttpResponseBadRequest(f"Error al cancelar la orden: {str(e)}")

        return redirect("orders:order_list")

    context = {
        "order": order,
        "items": order.items.select_related("product"),
    }
    return render(request, "pages/shop/sell/cancel_stock.html", context)

@login_required
def order_detail_view(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    can_cancel = order.status == "pending"
    can_delete = order.status == "completed"

    context = {
        "order": order,
        "can_cancel": can_cancel,
        "can_delete": can_delete,
    }
    return render(request, "pages/orders/order_detail.html", context)

@login_required
@require_POST
def order_remove_view(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.status != "completed":
        return HttpResponseBadRequest("Solo se pueden eliminar pedidos completados.")

    order.donot_show = True
    order.save(update_fields=["donot_show"])

    return redirect("orders:order_list")