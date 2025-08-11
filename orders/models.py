from django.db import models
from shop.models import Product
from users.models import CustomUser
from datetime import date

class Order(models.Model):
    user = models.ForeignKey(
        CustomUser,
        related_name='order',
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
        choices=[
            ('pending', 'Pendiente'),
            ('processing', 'En proceso'),
            ('completed', 'Completado'),
            ('reimbursing', 'Reembolsando'),
            ('refunded', 'Reembolsado'),
        ],
        default='pending',
        verbose_name='Estado del pedido'
    )


    donot_show = models.BooleanField(
        default=False,
        null=True,
        blank=True,
    )

    id = models.AutoField(primary_key=True, unique=True, verbose_name='ID', help_text='ID del pedido')

    class Meta:
        ordering = ['-created']
        indexes = [models.Index(fields=['-created'])]

    def __str__(self):
        return f'Order {self.id}'

    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())
    
    def get_status_display(self):
        return dict(self._meta.get_field('status').choices).get(self.status, 'Unknown')
    
    def clean_delete(self):
        if self.status in ['processing', 'reimbursing']:
            raise ValueError("No se puede eliminar un pedido en estado 'En proceso' o 'Reembolsando'.")
   
    def get_arrival_time_display(self):
        return self.arrival_time.strftime('%d/%m/%Y %H:%M') if self.arrival_time else 'Sin fecha'
    
    

    
    def get_all_items(self):
        return self.items.all()
    
    def delete(self, *args, **kwargs):
        self.clean_delete()
        super().delete(*args, **kwargs) 

    def clean(self):
        """
        - Si donot_show es True, no se permite calificación ni comentario.
        """
        if self.donot_show:
            raise ValueError("No se puede calificar ni comentar este pedido.")

        

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True)  
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return str(self.id)

    def get_cost(self):
        return self.price * self.quantity

    def save(self, *args, **kwargs):
        if not self.price:
            self.price = self.product.price
        super().save(*args, **kwargs)
        
    def get_total_cost(self):
        return self.get_cost()

