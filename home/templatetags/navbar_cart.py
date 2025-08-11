from django import template
from shop.models import Cart  

register = template.Library()

@register.simple_tag(takes_context=True)
def cart_tag(context):
    """Retorna el carrito del usuario"""
    request = context.get('request')

    if request and request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        return cart
    
    return None  


