import os
import django
import random
from decimal import Decimal
import sys

# Agregar carpeta del manage.py al sys.path
sys.path.append(r"C:\Users\Go\Documents\luis_carlos_coperativa_repo")

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'luis_carlos_cooperativa.settings')
django.setup()

from users.models import CustomUser  # Cambia 'users' si tu app se llama distinto

# Asignar crédito aleatorio
for user in CustomUser.objects.all():
    user.credit = Decimal(random.randint(1000, 5000))
    user.save()
    print(f"Asignado crédito {user.credit} a {user.code}")

print("Créditos asignados correctamente.")
