from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from celery import shared_task

from .models import Order, OrderItem
from shop.models import Product
from django.contrib.auth import get_user_model

User = get_user_model()


@shared_task
def create_order(user_code, products: list, paid: bool = False):
    user = get_object_or_404(User, code=user_code)

    order = Order.objects.create(user=user, paid=paid)

    for p in products:
        try:
            product = Product.objects.get(id=p["product_id"])
        except Product.DoesNotExist:
            raise ValidationError(f"El producto con ID {p['product_id']} no existe.")

        OrderItem.objects.create(
            order=order,
            product=product,
            price=p["price"],
            quantity=p["quantity"]
        )
