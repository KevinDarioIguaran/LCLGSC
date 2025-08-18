from decimal import Decimal
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError

from .models import Order, OrderItem
from shop.models import Product
from django.contrib.auth import get_user_model
from background_task import background

User = get_user_model()


def create_order(user_code, products: list, paid: bool = False, school_address: str = ""):
    """
    Crea un pedido de manera asincrónica.
    """
    user = get_object_or_404(User, code=user_code)

    if not school_address:
        raise ValidationError("La dirección del colegio no puede estar vacía.")

    order = Order.objects.create(
        user=user,
        paid=paid,
        school_address=school_address
    )

    for p in products:
        try:
            product = Product.objects.get(id=p["product_id"])
        except Product.DoesNotExist:
            raise ValidationError(f"El producto con ID {p['product_id']} no existe.")

        OrderItem.objects.create(
            order=order,
            product=product,
            price=Decimal(p["price"]), 
            quantity=p["quantity"]
        )

    return order