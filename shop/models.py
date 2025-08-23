from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MinLengthValidator, MinValueValidator, MaxValueValidator
from django.urls import reverse
from django.utils.translation import gettext_lazy as _  
from django.core.exceptions import ValidationError

from django.db.models import Sum, F
from django.conf import settings

class Category(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name=_("Nombre de la categoría"),
        help_text=_("Incluya el nombre de la categoría.")  
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name=_("Slug de la categoría"),
        help_text=_("URL amigable para la categoría.")
    )


    sales = models.IntegerField(
        default=0,
        verbose_name=_("Ventas"),
        help_text=_("Número de ventas de la categoría.")
    )
    

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name'])
        ]
        verbose_name = _('categoria')
        verbose_name_plural = _('categorias')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:search_by_category', args=[self.slug])

    def get_price_ranges(self):
        if self.price_ranges:
            return self.price_ranges
        else:
            return False
    
    def has_products(self):
        return self.product.exists()



class Product(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='product',
        verbose_name=_("Categoría"),
        help_text=_("Seleccione la categoría correspondiente.")
    )

    name = models.CharField(
        max_length=100,
        verbose_name=_("Nombre del producto"),
        help_text=_("Nombre descriptivo del producto.")
    )
    slug = models.SlugField(
        max_length=200,
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("Precio"),
        validators=[MinValueValidator(0)],
        help_text=_("Precio del producto en unidades monetarias.")
    )
    description = models.TextField(
        blank=True,
        verbose_name=_("Descripción"),
        help_text=_("Detalles del producto, incluyendo ingredientes, uso, etc."),
        max_length=350,
    )
    stock = models.IntegerField(
        validators=[MinValueValidator(0)],
        verbose_name=_("Stock"),
        help_text=_("Cantidad disponible del producto."),
        default=0
    )
    sales = models.IntegerField(
        default=0,
        verbose_name=_("Ventas"),
        help_text=_("Número de veces que el producto ha sido vendido.")
    )
    reviews_count = models.IntegerField(
        default=0,
        verbose_name=_("Comentarios"),
        help_text=_("Número de comentarios que ha recibido el producto."),
    )
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name=_("Vendedor"),
        help_text=_("Vendedor que ofrece este producto.")
    )
    available = models.BooleanField(
        verbose_name=_("Está disponible"),
        default=True,
        help_text=_("Si el producto está disponible para compra.")
    )
    created = models.DateField(
        auto_now_add=True,
        verbose_name=_("Fecha de creación"),
        help_text=_("Fecha en la que se creó el producto.")
    )
    updated = models.DateField(
        auto_now=True,
        verbose_name=_("Fecha de actualización"),
        help_text=_("Fecha en la que se actualizó el producto.")
    )
    image = models.ImageField(
        upload_to='product_images/',
        verbose_name=_("Imagen principal"),
        help_text=_("Imagen representativa del producto.")
    )

    class Meta:
        ordering = ['name'] 
        indexes = [
            models.Index(fields=['id', 'slug']),
            models.Index(fields=['price']),
            models.Index(fields=['-created']),
        ]
        verbose_name = _("Producto")
        verbose_name_plural = _("Productos")

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('shop:product_detail', args=[self.id, self.slug])
    
    def get_name_seller(self):
        return self.seller.get_full_name()
    
    def is_available(self):
        return self.available
    
    def get_image_url(self):
        if self.image:
            return self.image.url
        return None

    def delete(self, *args, **kwargs):
        if self.image:
            self.image.delete(save=False)
        super().delete(*args, **kwargs)

class Cart(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="items"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    paid = models.BooleanField(
        default=False,
        verbose_name=_("¿Carrito pagado?"),
        help_text=_("Indica si el carrito ha sido pagado."),
    )

    class Meta:
        verbose_name = "Carrito"
        verbose_name_plural = "Carritos"

    def __str__(self):
        return _("Carrito de {code}").format(code=self.user.code)


    def get_total(self):
        total = self.cart_items.aggregate(
            total=Sum(F("product__price") * F("quantity"))
        )['total'] or 0
        return total
    
    def get_total_cost(self):
        return sum(item.quantity * item.product.price for item in self.cart_items.select_related("product"))

    def get_cart_items_data(self):
        return [
            {
                'product_id': item.product.id,
                'price': float(item.product.price),
                'quantity': item.quantity
            }
            for item in self.cart_items.select_related("product")
        ]

    def mark_as_paid(self):
        self.paid = True
        self.save(update_fields=["paid"])


    def clear_cart(self):
        self.cart_items.all().delete()

    def total_items (self):
        return self.cart_items.count()

class CartItem(models.Model):
    cart = models.ForeignKey("Cart", on_delete=models.CASCADE, related_name="cart_items")
    product = models.ForeignKey("Product", on_delete=models.CASCADE, related_name="cart_items")
    quantity = models.PositiveIntegerField(verbose_name=_("Cantidad"))

    class Meta:
        unique_together = ('cart', 'product')


    def clean(self):

        if self.quantity is None:
            raise ValidationError("La cantidad no puede ser None.")

        if self.product.stock is None:
            raise ValidationError("El stock del producto no está definido.")

        if self.quantity > int(self.product.stock):
            raise ValidationError("No hay suficiente stock disponible.")



    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} en el carrito de {self.cart.user.code}"

class ShowBestOffers(models.Model):
    category = models.ForeignKey(
        "Category",
        on_delete=models.CASCADE,
        related_name="best_offers",
        verbose_name=_("Categoría en oferta"),
        help_text=_("Categoría que se muestra como mejor oferta."),
        null=True,
        blank=True,
    )
    image = models.ImageField(
        upload_to='best_offers_images/',
        verbose_name=_("Imagen de la oferta"),
        help_text=_("Imagen representativa de la oferta."),
    )
    active = models.BooleanField(
        default=True,
        verbose_name=_("¿Oferta activa?"),
        help_text=_("Indica si la oferta está activa y debe mostrarse.")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Fecha de creación")
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Fecha de actualización")
    )

    class Meta:
        verbose_name = _("Mejor oferta")
        verbose_name_plural = _("Mejores ofertas")
        ordering = ['-created_at']
        unique_together = ('category', 'active')

    def clean(self):
        if not self.image:
            raise ValidationError(_("Debe subir una imagen para la oferta."))

        if self.active:
            qs = ShowBestOffers.objects.filter(category=self.category, active=True)
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            if qs.exists():
                raise ValidationError(_("Ya existe una oferta activa para esta categoría."))

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        if not self.category:
            return "Oferta sin categoría"
        return f"Oferta en  {self.category.name} ({'Activa' if self.active else 'Inactiva'})"
    
    def delete(self, *args, **kwargs):
        if self.image:
            self.image.delete(save=False)
        super().delete(*args, **kwargs)
