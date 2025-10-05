import io
from PIL import Image, ImageOps
import pyvips

def convert_image_to_webp(image_file, quality=20, max_size=None):
    """
    Convierte una imagen a WebP corrigiendo orientación con Pillow.
    max_size: si se especifica, redimensiona la imagen proporcionalmente.
    Devuelve BytesIO listo para guardar en Django.
    """
    try:
        img = Image.open(image_file)
        img = ImageOps.exif_transpose(img)
        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGBA" if "A" in img.getbands() else "RGB")

        temp_buffer = io.BytesIO()
        img.save(temp_buffer, format="PNG")
        temp_bytes = temp_buffer.getvalue()
        temp_buffer.close()

        vips_image = pyvips.Image.new_from_buffer(temp_bytes, "", access="sequential")

        if max_size:
            max_dim = max(vips_image.width, vips_image.height)
            if max_dim > max_size:
                scale = max_size / max_dim
                vips_image = vips_image.resize(scale)

        webp_bytes = vips_image.write_to_buffer(".webp", Q=quality)
        return io.BytesIO(webp_bytes)

    except Exception as e:
        print(f"[ERROR] Conversion failed: {e}")
        return None
    














    
"""
import io
from PIL import Image, ImageOps

def convert_image_to_webp(image_file, quality=20, max_size=None):
#Convierte una imagen a WebP corrigiendo orientación con Pillow.
   # max_size: si se especifica, redimensiona la imagen proporcionalmente.
   # Devuelve BytesIO listo para guardar en Django.

    try:
        img = Image.open(image_file)
        img = ImageOps.exif_transpose(img)

        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGBA" if "A" in img.getbands() else "RGB")

        if max_size:
            max_dim = max(img.width, img.height)
            if max_dim > max_size:
                scale = max_size / max_dim
                new_size = (int(img.width * scale), int(img.height * scale))
                img = img.resize(new_size, Image.LANCZOS)

        buffer = io.BytesIO()
        img.save(buffer, format="WEBP", quality=quality)
        buffer.seek(0)
        return buffer

    except Exception as e:
        print(f"[ERROR] Conversion failed: {e}")
        return None
"""