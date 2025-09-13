import os
import json
import django
from decimal import Decimal
from django.core.files import File
import glob

# Configuración Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', "luis_carlos_cooperativa.settings")
django.setup()

from shop.models import Product, Category
from users.models import CustomUser

# Rutas base
BASE_DIR = r"C:\Users\Go\Documents\luis_carlos_coperativa_repo"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# Colores para consola
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def import_data(input_file="backup.json"):
    backup_path = os.path.join(BASE_DIR, input_file)
    if not os.path.exists(backup_path):
        print(f"{YELLOW}Archivo JSON no encontrado: {backup_path}{RESET}")
        return

    with open(backup_path, "r", encoding="latin-1") as f:
        data = json.load(f)

    missing_images = []

    # Usuarios
    for u in data.get("users", []):
        user, created = CustomUser.objects.update_or_create(
            code=u["code"],
            defaults={
                "first_name": u.get("first_name", ""),
                "last_name": u.get("last_name", ""),
                "is_active": u.get("is_active", True),
                "is_staff": u.get("is_staff", False),
                "secret_code": u.get("secret_code", ""),
                "is_seller": u.get("is_seller", False),
                "cooperative_name": u.get("cooperative_name", ""),
                "credit": Decimal(u.get("credit", 0)),
            },
        )
        print(f"{GREEN}{'Usuario creado:' if created else 'Usuario actualizado:'} {user.code}{RESET}")

    # Productos
    for p in data.get("products", []):
        category, _ = Category.objects.get_or_create(
            name=p["category"],
            defaults={"slug": p["category"].lower().replace(" ", "-")}
        )

        try:
            seller = CustomUser.objects.get(code=p["seller_code"])
        except CustomUser.DoesNotExist:
            print(f"{YELLOW}Vendedor no encontrado: {p['seller_code']} para producto {p['name']}{RESET}")
            continue

        product, created = Product.objects.update_or_create(
            slug=p["slug"],
            defaults={
                "name": p["name"],
                "price": Decimal(p.get("price", 0)),
                "category": category,
                "seller": seller,
                "description": p.get("description", ""),
                "available": p.get("available", True),
            },
        )

        # Asignar imagen
        if "image" in p and p["image"]:
            image_rel_path = p["image"].lstrip("/media/").replace("/", os.sep)
            image_pattern = os.path.join(MEDIA_ROOT, os.path.splitext(image_rel_path)[0] + "*.webp")
            found_images = glob.glob(image_pattern)
            if found_images:
                image_path = found_images[0]  # Tomar la primera coincidencia
                with open(image_path, "rb") as f:
                    product.image.save(os.path.basename(image_path), File(f), save=True)
                print(f"{GREEN}Imagen asignada: {product.name}{RESET}")
            else:
                missing_images.append((product.name, image_rel_path))
                print(f"{YELLOW}Imagen no encontrada: {image_rel_path}{RESET}")

        print(f"{BLUE}{'Producto creado:' if created else 'Producto actualizado:'} {product.name}{RESET}")

    if missing_images:
        print(f"\n{YELLOW}Productos con imágenes faltantes:{RESET}")
        for name, path in missing_images:
            print(f" - {name}: {path}")
    else:
        print(f"\n{GREEN}Todas las imágenes fueron asignadas correctamente.{RESET}")

if __name__ == "__main__":
    import_data("backup.json")
