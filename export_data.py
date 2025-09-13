import json
import os
import django

# Configurar entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', "luis_carlos_cooperativa.settings")
django.setup()

from shop.models import Product
from users.models import CustomUser


def export_data():
    data = {
        "users": [],
        "products": [],
    }

    # Exportar usuarios
    for user in CustomUser.objects.all():
        data["users"].append({
            "code": user.code,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_active": user.is_active,
            "is_staff": user.is_staff,
            "is_seller": user.is_seller,
            "cooperative_name": user.cooperative_name,
            "credit": float(user.credit),
            "secret_code" :  user.secret_code
        })

    # Exportar productos
    for product in Product.objects.select_related("category", "seller"):
        data["products"].append({
            "name": product.name,
            "slug": product.slug,
            "price": float(product.price),
            "category": product.category.name,
            "seller_code": product.seller.code,
            "image": product.image.url if product.image else None,
            "description": product.description,
            "available": product.available,
        })

    # Guardar en JSON
    with open("backup.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print("✅ Datos exportados a backup.json")


if __name__ == "__main__":
    export_data()
