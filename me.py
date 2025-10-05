import random
from datetime import datetime
from django.utils.timezone import make_aware
import os
import django

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', "luis_carlos_cooperativa.settings")
django.setup()

from users.models import CustomUser  
from shop.models import Product
from orders.models import Order, OrderItem


def random_date(year: int):
    """Generate a random valid date within the given year."""
    month = random.randint(1, 12)

    if month == 2:  # February
        if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
            day = random.randint(1, 29)
        else:
            day = random.randint(1, 28)
    elif month in [4, 6, 9, 11]:
        day = random.randint(1, 30)
    else:
        day = random.randint(1, 31)

    hour = random.randint(0, 23)
    minute = random.randint(0, 59)

    return make_aware(datetime(year, month, day, hour, minute))


def create_fake_orders(n=1000, year=2025):
    """Generate n fake orders with random dates for user 2013-00015 and random products."""
    try:
        user = CustomUser.objects.get(code="2013-00015")
    except CustomUser.DoesNotExist:
        print("User with code 2013-00015 not found.")
        return

    products = list(Product.objects.all())
    if not products:
        print("No products found in the database.")
        return

    for i in range(1, n + 1):
        created_date = random_date(year)

        order = Order.objects.create(
            user=user,
            created=created_date,   
            paid='True',
            school_address=random.choice([
                "classroom_01", "classroom_02", "cooperative", "rectory"
            ]),
            status="completed"
        )

        num_products = random.randint(1, min(5, len(products)))  
        selected_products = random.sample(products, num_products)

        print(f"\n Order {i}/{n} created:")
        print(f"   - Date: {created_date}")
        print(f"   - Paid: {order.paid}")
        print(f"   - Address: {order.school_address}")
        print(f"   - Products:")

        for product in selected_products:
            quantity = random.randint(1, 5)
            OrderItem.objects.create(
                order=order,
                product=product,
                price=product.price,
                quantity=quantity
            )
            print(f"     • {product.name} x{quantity} (${product.price})")

    print(f"\nOK:  {n} fake orders created for user 2013-00015 with random products.")


if __name__ == "__main__":
    create_fake_orders(n=1000, year=2025)
