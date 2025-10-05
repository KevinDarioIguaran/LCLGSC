import uuid

from django.db import models
from shop.models import Product
from users.models import CustomUser
from datetime import date

from django.db import models
from django.core.exceptions import ValidationError
from users.models import CustomUser  

class Order(models.Model):
    user = models.ForeignKey(
        CustomUser,
        related_name='orders',
        on_delete=models.CASCADE,
        verbose_name='Usuario'
    )
    created = models.DateTimeField(auto_now_add=True)
    paid = models.BooleanField(default=False)
    
    arrival_time = models.DateTimeField(
        verbose_name='Fecha de entrega',
        blank=True,
        null=True,
        help_text='Fecha de entrega del pedido'
    )

    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pendiente'),
            ('approved', 'Aprobado'),       
            ('completed', 'Completado'),
            ('refunded', 'Reembolsado'),
            ('cancelled', 'Stock agotado'),
        ],
        default='pending',
        verbose_name='Estado del pedido'
    )

    donot_show = models.BooleanField(
        default=False,
        null=True,
        blank=True,
    )

    school_address = models.CharField(
        max_length=30,
        choices=[
            ('classroom_01', 'Salón 01'),
            ('classroom_02', 'Salón 02'),
            ('classroom_03', 'Salón 03'),
            ('classroom_04', 'Salón 04'),
            ('classroom_05', 'Salón 05'),
            ('classroom_06', 'Salón 06'),
            ('classroom_07', 'Salón 07'),
            ('classroom_08', 'Salón 08'),
            ('classroom_09', 'Salón 09'),
            ('classroom_10', 'Salón 10'),
            ('classroom_11', 'Salón 11'),
            ('classroom_12', 'Salón 12'),
            ('classroom_13', 'Salón 13'),
            ('classroom_14', 'Salón 14'),
            ('classroom_15', 'Salón 15'),
            ('classroom_16', 'Salón 16'),
            ('classroom_system_1', 'Salón de sistemas 1'),
            ('classroom_system_2', 'Salón de sistemas 2'),
            ('classroom_system_3', 'Salón Solar'),
            ('coordination', 'Coordinación'),
            ('rectory', 'Rectoría'),
            ('staff_room', 'Sala de profesores'),
            ('cooperative', 'Cooperativa')
        ],
        blank=True,
        null=True,
        verbose_name="Ubicación escolar"
    )

    id = models.AutoField(
        primary_key=True,
        unique=True,
        verbose_name='ID',
        help_text='ID del pedido'
    )

    qr_code_data = models.CharField(max_length=255, null=True, blank=True)

    seller_approved = models.ForeignKey(
        CustomUser,
        related_name='approved_orders',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Aprobado por'
    )

    class Meta:
        ordering = ['-created']
        indexes = [models.Index(fields=['-created'])]

    def __str__(self):
        return f'Order {self.id} - {self.user.code}'
    
    def get_total_cost(self):
        total = sum(item.get_cost() for item in self.items.all())
        if self.school_address != "cooperative":
            total += 300
        return total
    
    def clean_delete(self):
        if self.status in ['processing', 'reimbursing']:
            raise ValidationError("No se puede eliminar un pedido en estado 'En proceso' o 'Reembolsando'.")
   
    def get_arrival_time_display(self):
        return self.arrival_time.strftime('%d/%m/%Y %H:%M') if self.arrival_time else 'Sin fecha'
    
    def get_all_items(self):
        return self.items.all()
    
    def delete(self, *args, **kwargs):
        self.clean_delete()
        super().delete(*args, **kwargs) 

    def clean(self):
        if self.donot_show:
            raise ValidationError("No se puede calificar ni comentar este pedido.")
        if self.seller_approved and not getattr(self.seller_approved, 'is_seller', False):
            raise ValidationError("El usuario que aprueba la orden debe ser vendedor.")

    def save(self, *args, **kwargs):
        if not self.qr_code_data:
            self.qr_code_data = str(uuid.uuid4()) 
        super().save(*args, **kwargs)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True)  
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'{self.product.name} x {self.quantity}'

    def get_cost(self):
        return self.price * self.quantity

    def save(self, *args, **kwargs):
        if not self.price:
            self.price = self.product.price
        super().save(*args, **kwargs)
        
    def get_total_cost(self):
        return self.get_cost()

class OrderCancelItem(models.Model):
    order = models.ForeignKey(Order, related_name='cancel_items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_cancel_items', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'{self.product.name} x {self.quantity}'

    def get_cost(self):
        return self.price * self.quantity

    def save(self, *args, **kwargs):
        if not self.price:
            self.price = self.product.price
        super().save(*args, **kwargs)

    def get_total_cost(self):
        return self.get_cost()