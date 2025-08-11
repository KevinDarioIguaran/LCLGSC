from PIL import Image, UnidentifiedImageError
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
from django.utils.translation import gettext_lazy as _
from luis_carlos_cooperativa.settings import MAX_FILE_SIZE_IMAGES, VALID_EXTENSIONS_IMAGES

VALID_FORMATS = ['jpg', 'jpeg', 'png', 'webp']
MAX_WIDTH = 8000
MAX_HEIGHT = 8000

def validate_images(image):
    """
    Valida una sola imagen con seguridad:
    - Archivo subido válido.
    - Extensión permitida.
    - Tamaño permitido.
    - Formato real permitido.
    - Coincidencia entre extensión y formato real.
    - Dimensiones máximas.
    """
    if not image:
        return  

    if not hasattr(image, "name"):
        raise ValidationError(_("Archivo no válido."))

    if not isinstance(image, (InMemoryUploadedFile, TemporaryUploadedFile)):
        raise ValidationError(_(f"{image.name}: No es un archivo subido válido."))

    ext = image.name.rsplit('.', 1)[-1].lower()
    if ext not in VALID_EXTENSIONS_IMAGES or ext == 'svg':
        raise ValidationError(_(f"{image.name}: Extensión no permitida (solo JPG, JPEG, PNG, WEBP)."))

    if image.size > MAX_FILE_SIZE_IMAGES:
        raise ValidationError(_(f"{image.name}: Excede el tamaño máximo permitido (5 MB)."))

    try:
        with Image.open(image) as img:
            img.verify()  
            image.seek(0)
            img = Image.open(image)
            img.load()

            format_real = img.format.lower()

            if format_real not in VALID_FORMATS:
                raise ValidationError(_(f"{image.name}: Formato no permitido ({format_real.upper()})."))

            if ext != format_real and not (ext == 'jpg' and format_real == 'jpeg'):
                raise ValidationError(_(f"{image.name}: Extensión no coincide con el formato real ({format_real.upper()})."))

            if img.width > MAX_WIDTH or img.height > MAX_HEIGHT:
                raise ValidationError(_(f"{image.name}: Dimensiones demasiado grandes ({img.width}x{img.height})."))

    except (UnidentifiedImageError, IOError, AttributeError, OSError):
        raise ValidationError(_(f"{image.name}: Archivo no válido o dañado."))

    finally:
        try:
            image.seek(0)
        except Exception:
            pass
