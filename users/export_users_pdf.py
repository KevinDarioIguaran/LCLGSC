# scripts/export_users_pdf.py

import os
import django
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import sys

# Agregar carpeta del manage.py al sys.path
sys.path.append(r"C:\Users\Go\Documents\luis_carlos_coperativa_repo")

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'luis_carlos_cooperativa.settings')
django.setup()

from users.models import CustomUser  # Ajusta según tu app

def export_users_to_pdf(output_path="usuarios_secret_codes.pdf"):
    # Obtener usuarios
    users = CustomUser.objects.all().order_by("code")

    # Crear PDF
    c = canvas.Canvas(output_path, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 16)
    c.drawString(200, height - 50, "Listado de Usuarios y Códigos Secretos")

    c.setFont("Helvetica", 12)
    y_position = height - 90

    for user in users:
        line = f"Código secreto: {user.secret_code} | Nombre: {user.first_name} {user.last_name}"
        c.drawString(50, y_position, line)
        y_position -= 20

        if y_position < 50:
            c.showPage()
            c.setFont("Helvetica", 12)
            y_position = height - 50

    c.save()
    print(f"PDF generado en: {output_path}")


if __name__ == "__main__":
    export_users_to_pdf()
