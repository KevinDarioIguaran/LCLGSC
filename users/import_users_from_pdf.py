import re
import os
import sys
import django
from PyPDF2 import PdfReader

# Agregar carpeta del manage.py al sys.path
sys.path.append(r"C:\Users\Go\Documents\luis_carlos_coperativa_repo")

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'luis_carlos_cooperativa.settings')
django.setup()

from users.models import CustomUser


def extract_students_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()

    # Ajusta este patrón según el formato exacto del texto extraído
    pattern = r"\d{4}-\d{5} [A-ZÑÁÉÍÓÚÜ]+ [A-ZÑÁÉÍÓÚÜ]+ [A-ZÑÁÉÍÓÚÜ]+(?: [A-ZÑÁÉÍÓÚÜ]+)*"
    matches = re.findall(pattern, text)

    students = []
    for match in matches:
        parts = match.split()
        code = parts[0]
        last_name = parts[1]  # Primer apellido
        first_name = parts[3]  # Primer nombre (ajustar si necesario)
        students.append((code, first_name.capitalize(), last_name.capitalize()))

    return students


def import_students(pdf_path):
    students = extract_students_from_pdf(pdf_path)
    print(f"Se encontraron {len(students)} estudiantes.")

    for code, first_name, last_name in students:
        if not CustomUser.objects.filter(code=code).exists():
            CustomUser.objects.create_user(
                code=code,
                first_name=first_name,
                last_name=last_name,
                password=None
            )



if __name__ == "__main__":
    import_students("planilla 102 (1).pdf")
